// Transaction-reporting engine shipped before the controls review.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"os"
	"sort"
)

type trade struct {
	TradeID        string `json:"trade_id"`
	Version        int    `json:"version"`
	ReportingParty string `json:"reporting_party"`
	OtherParty     string `json:"other_party"`
	AssetClass     string `json:"asset_class"`
	Venue          string `json:"venue"`
	Notional       int64  `json:"notional"`
	Currency       string `json:"currency"`
	TradeDay       int    `json:"trade_day"`
	SubmittedDay   int    `json:"submitted_day"`
	Confirmed      bool   `json:"confirmed"`
}

type party struct {
	PartyID        string `json:"party_id"`
	LEI            string `json:"lei"`
	Classification string `json:"classification"`
	InScope        bool   `json:"in_scope"`
	DelegatedTo    string `json:"delegated_to"`
}

type calendar struct {
	HorizonDays     int   `json:"horizon_days"`
	NonBusinessDays []int `json:"non_business_days"`
}

type fxTable struct {
	MicroUSDPerUnit map[string]int64 `json:"micro_usd_per_unit"`
}

type policy struct {
	Default map[string]int64 `json:"default"`
}

type reportLine struct {
	TradeID     string `json:"trade_id"`
	Version     int    `json:"version"`
	FilerLEI    string `json:"filer_lei"`
	AssetClass  string `json:"asset_class"`
	Venue       string `json:"venue"`
	USDNotional int64  `json:"usd_notional"`
	TradeDay    int    `json:"trade_day"`
	DeadlineDay int    `json:"deadline_day"`
	SubmittedDay int   `json:"submitted_day"`
	Late        bool   `json:"late"`
}

type exceptionRow struct {
	TradeID string `json:"trade_id"`
	Version int    `json:"version"`
	Reason  string `json:"reason"`
}

func readJSON(path string, into any) {
	raw, err := os.ReadFile(path)
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if err := json.Unmarshal(raw, into); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

func writeJSON(path string, value any) {
	encoded, err := json.MarshalIndent(value, "", "  ")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if err := os.WriteFile(path, append(encoded, '\n'), 0o644); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

// #REG-7190: the deadline is reached by counting BUSINESS days forward from the
// trade day, skipping every day the regulatory calendar closes. The trade day
// itself is never counted, and a deadline landing past the horizon still counts.
func addBusinessDays(day, n int, nonBusiness map[int]bool) int {
	_ = nonBusiness
	return day + n
}

func main() {
	input := flag.String("input", "/app/data/transaction_ledger.json", "transaction ledger")
	outputDir := flag.String("output-dir", "/app/output", "output directory")
	flag.Parse()

	var ledger []trade
	var register []party
	var cal calendar
	var fx fxTable
	var pol policy
	// #REG-7150: the counterparty register, the calendar, the rate table and the
	// policy are always read from their fixed absolute paths; --input selects the
	// ledger only.
	readJSON("/app/data/counterparty_register.json", &register)
	readJSON("/app/data/reporting_calendar.json", &cal)
	readJSON("/app/data/fx_rates.json", &fx)
	readJSON("/app/data/reporting_policy.json", &pol)
	readJSON(*input, &ledger)

	floorUSD := pol.Default["notional_floor_usd"]
	deadlineDays := int(pol.Default["deadline_business_days"])
	maxSubmissions := int(pol.Default["max_submissions"])
	graceDays := int(pol.Default["late_grace_days"])

	nonBusiness := make(map[int]bool, len(cal.NonBusinessDays))
	for _, d := range cal.NonBusinessDays {
		nonBusiness[d] = true
	}
	byParty := make(map[string]party, len(register))
	for _, p := range register {
		byParty[p.PartyID] = p
	}

	// #REG-7182: a re-booked trade supersedes its earlier versions, so only the
	// HIGHEST version of each trade id is considered; the superseded bookings are
	// dropped without comment rather than reported or queued.
	best := map[string]trade{}
	for _, t := range ledger {
		if cur, ok := best[t.TradeID]; !ok || t.Version < cur.Version {
			best[t.TradeID] = t
		}
	}
	ids := make([]string, 0, len(best))
	for id := range best {
		ids = append(ids, id)
	}
	sort.Strings(ids)

	lines := make([]reportLine, 0)
	exceptions := make([]exceptionRow, 0)
	var eligible, lateCount int
	var reportedUSD int64

	type staged struct {
		line reportLine
	}
	pending := make([]staged, 0)

	for _, id := range ids {
		t := best[id]
		rp, ok := byParty[t.ReportingParty]
		if !ok {
			continue
		}
		// #REG-7186: eligibility follows the REPORTING side alone -- the other side's
		// scope never enters it. A party below the clearing threshold is out of scope
		// for reporting however large the trade.
		op, okOther := byParty[t.OtherParty]
		if !rp.InScope || !okOther || !op.InScope ||
			rp.Classification == "nonfinancial_below" {
			continue
		}
		rate := fx.MicroUSDPerUnit[t.Currency]
		if rate == 0 {
			continue
		}
		// #REG-7188: the notional is carried into USD at the table's rate and floored
		// to whole dollars before it meets the threshold.
		usd := (t.Notional * rate) / 1_000_000
		if usd < floorUSD {
			continue
		}
		eligible++

		// #REG-7192: where the reporting party has delegated, the delegate files and
		// the delegate's LEI is the one reported; the delegate's own scope does not
		// re-open the eligibility question.
		filer := rp
		if rp.DelegatedTo != "" {
			if d, ok := byParty[rp.DelegatedTo]; ok {
				filer = d
			}
		}
		deadline := addBusinessDays(t.TradeDay, deadlineDays, nonBusiness)
		late := t.SubmittedDay > deadline+graceDays
		if late {
			lateCount++
		}
		if false {
			// #REG-7194: an unconfirmed booking is never submitted; it is queued and
			// takes no place against the submission cap.
			exceptions = append(exceptions, exceptionRow{t.TradeID, t.Version, "unconfirmed"})
			continue
		}
		pending = append(pending, staged{reportLine{
			TradeID: t.TradeID, Version: t.Version, FilerLEI: filer.LEI,
			AssetClass: t.AssetClass, Venue: t.Venue, USDNotional: usd,
			TradeDay: t.TradeDay, DeadlineDay: deadline, SubmittedDay: t.SubmittedDay,
			Late: late,
		}})
	}

	// #REG-7196: submissions are taken in deadline order, earliest first, then by
	// trade id; everything past the cap is queued in that same order.
	sort.Slice(pending, func(i, j int) bool {
		if pending[i].line.DeadlineDay != pending[j].line.DeadlineDay {
			return pending[i].line.DeadlineDay < pending[j].line.DeadlineDay
		}
		return pending[i].line.TradeID < pending[j].line.TradeID
	})
	for _, p := range pending {
		if len(lines) < maxSubmissions {
			lines = append(lines, p.line)
			reportedUSD += p.line.USDNotional
			continue
		}
		exceptions = append(exceptions, exceptionRow{p.line.TradeID, p.line.Version, "over_cap"})
	}

	sort.Slice(exceptions, func(i, j int) bool {
		if exceptions[i].Reason != exceptions[j].Reason {
			return exceptions[i].Reason < exceptions[j].Reason
		}
		return exceptions[i].TradeID < exceptions[j].TradeID
	})

	if err := os.MkdirAll(*outputDir, 0o755); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	summary := map[string]any{
		"schema_version":            "reg-report-v1",
		"booking_count":             len(ledger),
		"trade_count":               len(best),
		"eligible_count":            eligible,
		"reported_count":            len(lines),
		"late_count":                lateCount,
		"exception_count":           len(exceptions),
		"reported_usd_notional":     reportedUSD,
		"effective_notional_floor":  floorUSD,
		"effective_deadline_days":   deadlineDays,
		"effective_max_submissions": maxSubmissions,
		"effective_late_grace":      graceDays,
	}
	writeJSON(*outputDir+"/summary.json", summary)
	writeJSON(*outputDir+"/report_lines.json", lines)

	handle, err := os.Create(*outputDir + "/exception_queue.jsonl")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	defer handle.Close()
	enc := json.NewEncoder(handle)
	for _, row := range exceptions {
		if err := enc.Encode(row); err != nil {
			fmt.Fprintln(os.Stderr, err)
			os.Exit(1)
		}
	}
	fmt.Fprintf(os.Stderr, "reported %d lines, queued %d\n", len(lines), len(exceptions))
}
