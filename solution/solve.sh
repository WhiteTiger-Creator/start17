#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export GOCACHE=/tmp/gocache GO111MODULE=off GOPATH=/tmp/gopath

# --- Step 1: rebuild the authoritative transaction ledger (#REG-7170) -------
# The migration left /app/data/transaction_ledger.json holding a truncated
# prefix. Replay the migration journal onto the pre-migration snapshot and write
# the result back to that path.

go run "${SCRIPT_DIR}/recover_ledger.go"

# --- Step 2: restore the engine and produce the reporting artifacts ---------

cp "${SCRIPT_DIR}/build_report_fixed.go" /app/workflow/build_report.go
go run /app/workflow/build_report.go --output-dir /app/output
