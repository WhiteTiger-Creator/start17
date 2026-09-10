// Stage one of the reference: rebuild the transaction ledger the reference-data
// migration truncated at /app/data/transaction_ledger.json.
//
// Governed by #REG-7170 (replay semantics) and #REG-7174 (shape of the result).
package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
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
	// UseNumber, because a journal change carries its value as `any`: the default
	// decoder turns every JSON number into a float64, and a notional past 2^53
	// loses its last digits on the way in -- 9007199254740993 arrives as
	// 9007199254740992 and the amendment silently writes the wrong figure. A
	// json.Number keeps the text and ParseInt reads it exactly.
	dec := json.NewDecoder(bytes.NewReader(raw))
	dec.UseNumber()
	if err := dec.Decode(into); err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
	// A recovery source is one JSON document and nothing else. Decode stops at
	// the end of the first value it reads, so a file carrying a valid document
	// followed by anything at all was accepted and replayed; a journal that has
	// been appended to or truncated mid-write is a malformed recovery log, and
	// the authoritative ledger is not rebuilt from one.
	if _, err := dec.Token(); err != io.EOF {
		fmt.Fprintf(os.Stderr, "%s carries trailing content after its JSON document\n", path)
		os.Exit(1)
	}
}

// setField applies one amendment. #REG-7170 says an amend overwrites THE NAMED
// FIELD in place without naming a subset, so every one of the nine mutable
// booking fields is handled here. trade_id and version are left out on purpose:
// they are the key the change is matched on, so an amendment cannot rewrite the
// identity of the booking it is addressed to. The shipped journal only ever
// amends venue and notional, which is why a narrower handler happened to agree
// with it; a conforming journal that amends any other field would not.
func setField(t *trade, field string, value any) {
	str := func(dst *string) {
		if s, ok := value.(string); ok {
			*dst = s
		}
	}
	num := func(set func(int64)) {
		switch v := value.(type) {
		case json.Number:
			if n, err := v.Int64(); err == nil {
				set(n)
			}
		case float64:
			set(int64(v))
		case string:
			if n, err := strconv.ParseInt(v, 10, 64); err == nil {
				set(n)
			}
		}
	}
	switch field {
	case "reporting_party":
		str(&t.ReportingParty)
	case "other_party":
		str(&t.OtherParty)
	case "asset_class":
		str(&t.AssetClass)
	case "venue":
		str(&t.Venue)
	case "currency":
		str(&t.Currency)
	case "notional":
		num(func(n int64) { t.Notional = n })
	case "trade_day":
		num(func(n int64) { t.TradeDay = int(n) })
	case "submitted_day":
		num(func(n int64) { t.SubmittedDay = int(n) })
	case "confirmed":
		switch v := value.(type) {
		case bool:
			t.Confirmed = v
		case string:
			if b, err := strconv.ParseBool(v); err == nil {
				t.Confirmed = b
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
