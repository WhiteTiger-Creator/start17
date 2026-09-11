// Stage two of the reference: the corrected transaction-reporting engine.
//
// Every governing value is traced to its final dated entry in
// /app/incident/compliance_governance_log.md; reporting_contract.json supplies
// the output contract only and no derivation rule.
package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"math/bits"
	"os"
	"path/filepath"
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
// The contract puts deadline_business_days no higher than the calendar's
// horizon_days, so the walk always terminates inside the horizon. The guard
// below is a backstop against a calendar that closes every day within it, and
// it REPORTS rather than breaking quietly: the old form returned whatever day
// it had reached, which is a deadline the calendar never placed, and every
// lateness verdict after it was measured against a number nobody chose.
func addBusinessDays(day, n int, nonBusiness map[int]bool, horizon int) int {
	// The walk consumes BUSINESS days while the day index counts calendar days,
	// so a bound of day+horizon is not a bound on the walk at all: reaching n
	// business days needs n days plus every closure crossed on the way. Walking
	// n business days can therefore never take more than n + (number of closed
	// days the calendar lists) steps, which is the backstop used here -- a real
	// upper bound rather than one that hard-exits on deadline_business_days the
	// contract lists as valid. Days past the horizon are business days: nothing
	// closes them.
	d := day
	limit := day + n + len(nonBusiness) + 1
	for n > 0 {
		d++
		if !nonBusiness[d] {
			n--
		}
		if d > limit {
			fmt.Fprintf(os.Stderr,
				"the deadline walk for a trade on day %d did not terminate\n", day)
			os.Exit(1)
		}
	}
	return d
}

// The policy is read from its fixed absolute path, and any field the file omits
// keeps its governed baseline. A missing Go map key is zero, not the baseline,
// so the fallback has to be explicit.
func policyValue(pol policy, field string, baseline int64) int64 {
	if value, ok := pol.Default[field]; ok {
		return value
	}
	return baseline
}


// usdOf carries a notional into whole US dollars at a micro-dollar rate without
// letting the intermediate wrap. Both figures are non-negative under the
// contract, so the unsigned 128-bit path is exact and the quotient fits an
// int64 as #REG-7188 states.
func usdOf(notional, microUSDPerUnit int64) int64 {
	hi, lo := bits.Mul64(uint64(notional), uint64(microUSDPerUnit))
	quo, _ := bits.Div64(hi, lo, 1_000_000)
	return int64(quo)
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

	floorUSD := policyValue(pol, "notional_floor_usd", 1000000)
	deadlineDays := int(policyValue(pol, "deadline_business_days", 1))
	maxSubmissions := int(policyValue(pol, "max_submissions", 2500))
	graceDays := int(policyValue(pol, "late_grace_days", 0))

	nonBusiness := make(map[int]bool, len(cal.NonBusinessDays))
	horizonDays := cal.HorizonDays
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
		if cur, ok := best[t.TradeID]; !ok || t.Version > cur.Version {
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
		if !rp.InScope || rp.Classification == "nonfinancial_below" {
			continue
		}
		// The two-value lookup, not a zero sentinel: #REG-7188 turns on whether
		// the table CARRIES the currency, and reading a missing key as zero also
		// silently skipped a currency the table carries at a rate of nought,
		// which is a rate rather than an absence.
		rate, carried := fx.MicroUSDPerUnit[t.Currency]
		if !carried {
			continue
		}
		// #REG-7188: the notional is carried into USD at the table's rate and floored
		// to whole dollars before it meets the threshold, and the conversion is the
		// ARITHMETIC value of notional*rate/1e6 rather than whatever a 64-bit
		// register holds. The book carries notionals whose product with the rate
		// passes the int64 ceiling while the dollar figure sits far inside it, so the
		// multiply is carried at 128 bits and the divide comes back down: bits.Mul64
		// gives the full product as a high/low pair and bits.Div64 divides it,
		// panicking only where the quotient would not fit, which #REG-7188 says it
		// always does.
		usd := usdOf(t.Notional, rate)
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
		deadline := addBusinessDays(t.TradeDay, deadlineDays, nonBusiness, horizonDays)
		// #REG-7214: late_count is taken over every ELIGIBLE booking, here, before
		// the confirmation check below and before the cap further down. A booking
		// queued as unconfirmed or displaced by the cap was still late; the figure
		// measures timeliness, not the size of the file.
		late := t.SubmittedDay > deadline+graceDays
		if late {
			lateCount++
		}
		if !t.Confirmed {
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

	// The output directory is one this run may empty and fill, which the
	// directory holding its own inputs is not: clearing /app/data would take
	// away the very documents the contract requires back byte for byte, so a
	// run handed that path says so and stops before writing or clearing
	// anything at all.
	if cleaned, err := filepath.Abs(filepath.Clean(*outputDir)); err == nil && cleaned == "/app/data" {
		fmt.Fprintf(os.Stderr, "%s holds this run's own inputs and is not an output directory\n", cleaned)
		os.Exit(1)
	}
	if err := os.MkdirAll(*outputDir, 0o755); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	// The run leaves the output directory holding the three contracted files and
	// nothing else, so anything an earlier run left there is cleared first. The
	// CONTENTS go and the directory itself stays: the run does not own the path it
	// is given, and under an unprivileged uid removing it would be refused outright.
	// Every error here is reported. Both the read and the removals had their
	// failures dropped, so a stale entry the run could not remove left the output
	// carrying more than the three contracted files while the run still exited
	// nought. A run that cannot meet the contract says so and stops.
	stale, err := os.ReadDir(*outputDir)
	if err != nil {
		fmt.Fprintf(os.Stderr, "cannot read the output directory %s: %v\n", *outputDir, err)
		os.Exit(1)
	}
	for _, e := range stale {
		target := filepath.Join(*outputDir, e.Name())
		if err := os.RemoveAll(target); err != nil {
			fmt.Fprintf(os.Stderr, "cannot clear %s from the output directory: %v\n", target, err)
			os.Exit(1)
		}
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
