// Stage one of the reference: rebuild the transaction ledger the reference-data
// migration truncated at /app/data/transaction_ledger.json.
//
// Governed by #REG-7170 (replay semantics) and #REG-7174 (shape of the result).
package main

import (
	"encoding/json"
	"fmt"
	"os"
	"sort"
	"strconv"
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

type change struct {
	Seq      int    `json:"seq"`
	TradeKey string `json:"trade_key"`
	Kind     string `json:"kind"`
	Field    string `json:"field"`
	Value    any    `json:"value"`
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

func setField(t *trade, field string, value any) {
	switch field {
	case "venue":
		if s, ok := value.(string); ok {
			t.Venue = s
		}
	case "asset_class":
		if s, ok := value.(string); ok {
			t.AssetClass = s
		}
	case "notional":
		switch v := value.(type) {
		case float64:
			t.Notional = int64(v)
		case string:
			if n, err := strconv.ParseInt(v, 10, 64); err == nil {
				t.Notional = n
			}
		}
	}
}

func key(t trade) string { return t.TradeID + "#" + strconv.Itoa(t.Version) }

func main() {
	var snapshot []trade
	var journal []change
	readJSON("/app/data/ledger_snapshot_pre_migration.json", &snapshot)
	readJSON("/app/data/ledger_journal.json", &journal)

	live := make(map[string]*trade, len(snapshot))
	for i := range snapshot {
		t := snapshot[i]
		live[key(t)] = &t
	}
	// #REG-7170: a withdrawal takes the booking out but the migrator keeps it, so a
	// later reinstatement returns it exactly as it then stood -- an amendment posted
	// before survives, one posted while it was out is lost.
	held := map[string]trade{}

	sort.Slice(journal, func(i, j int) bool { return journal[i].Seq < journal[j].Seq })
	for _, c := range journal {
		switch c.Kind {
		case "amend":
			if t, ok := live[c.TradeKey]; ok {
				setField(t, c.Field, c.Value)
			}
		case "withdraw":
			if t, ok := live[c.TradeKey]; ok {
				held[c.TradeKey] = *t
				delete(live, c.TradeKey)
			}
		case "reinstate":
			if t, ok := held[c.TradeKey]; ok {
				restored := t
				live[c.TradeKey] = &restored
				delete(held, c.TradeKey)
			}
		}
	}

	out := make([]trade, 0, len(live))
	for _, t := range live {
		out = append(out, *t)
	}
	// #REG-7174: ascending trade id, then version.
	sort.Slice(out, func(i, j int) bool {
		if out[i].TradeID != out[j].TradeID {
			return out[i].TradeID < out[j].TradeID
		}
		return out[i].Version < out[j].Version
	})

	encoded, err := json.MarshalIndent(out, "", "  ")
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	if err := os.WriteFile("/app/data/transaction_ledger.json", append(encoded, '\n'), 0o644); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	fmt.Fprintf(os.Stderr, "recovered %d bookings\n", len(out))
}
