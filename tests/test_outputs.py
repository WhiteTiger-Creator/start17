"""Verifier tests for this task.

Every test below corresponds to something instruction.md states is graded.
Shared machinery lives in harness.py.
"""

from harness import *  # noqa: F401,F403

@pytest.fixture(scope="session")
def primary_outputs():
    return _run_pipeline()


@pytest.fixture(scope="session")
def alternate_outputs():
    return _run_pipeline(input_path=ALT_INPUT)






# --------------------------------------------------------------------------
# Step one: the truncated ledger must be rebuilt before anything is filed
# --------------------------------------------------------------------------
def test_recovery_sources_are_intact():
    """Every rule source is read, not rewritten."""
    live = {n: hashlib.sha256(Path(p).read_bytes()).hexdigest() for n, p in (
        ("snapshot", SNAPSHOT_PATH), ("journal", JOURNAL_PATH),
        ("register", DATA / "counterparty_register.json"),
        ("calendar", DATA / "reporting_calendar.json"), ("fx", DATA / "fx_rates.json"),
        ("policy", DATA / "reporting_policy.json"), ("log", LOG_PATH))}
    assert _digest(live) == FIXTURE["rule_sources_digest"]


def test_ledger_was_recovered():
    """The rebuilt ledger matches the governed replay exactly."""
    recovered = _load_json(LEDGER_PATH)
    assert len(recovered) == FIXTURE["recovered_booking_count"]
    assert _digest(recovered) == FIXTURE["recovered_ledger_digest"]


def test_recovered_bookings_carry_only_the_declared_fields():
    """Migrator bookkeeping never survives the replay."""
    for row in _load_json(LEDGER_PATH):
        assert set(row) == BOOKING_KEYS


def test_recovered_ledger_is_sorted():
    """The ledger ascends by trade id then version."""
    rows = _load_json(LEDGER_PATH)
    keys = [(r["trade_id"], r["version"]) for r in rows]
    assert keys == sorted(keys)


def test_wrong_replays_differ_from_the_governed_ledger():
    """Three plausible misreadings of the replay each give a different ledger."""
    expected = FIXTURE["recovered_ledger_digest"]
    assert FIXTURE["shipped_truncated_digest"] != expected
    snapshot = {f'{r["trade_id"]}#{r["version"]}': r for r in _load_json(SNAPSHOT_PATH)}
    journal = _load_json(JOURNAL_PATH)

    def replay(by_seq: bool, reinstate_from_snapshot: bool):
        live = {k: dict(v) for k, v in snapshot.items()}
        held = {}
        for c in (sorted(journal, key=lambda x: x["seq"]) if by_seq else journal):
            k, kind = c["trade_key"], c["kind"]
            if kind == "amend" and k in live:
                live[k][c["field"]] = c["value"]
            elif kind == "withdraw" and k in live:
                held[k] = dict(live.pop(k))
            elif kind == "reinstate":
                if reinstate_from_snapshot:
                    if k in snapshot and k not in live:
                        live[k] = dict(snapshot[k])
                elif k in held:
                    live[k] = held.pop(k)
        rows = sorted(live.values(), key=lambda r: (r["trade_id"], r["version"]))
        return _digest(rows)

    # the governed reading: by sequence, a reinstatement returning the held state.
    # It must reproduce the sealed digest, or the three below differ only because
    # this helper does not model the replay at all.
    assert replay(True, False) == expected, (
        "the governed replay does not reproduce the sealed ledger, so the "
        "misreadings below prove nothing")
    assert replay(False, False) != expected, "a replay in file order"
    assert replay(True, True) != expected, "a reinstatement re-reading the snapshot"

    # and the third misreading the recovery draft proposed: concatenate the
    # snapshot with the journal and keep the last row seen for each booking
    concatenated = {k: dict(v) for k, v in snapshot.items()}
    for change in journal:
        concatenated[change["trade_key"]] = dict(change)
    rows = sorted(concatenated.values(),
                  key=lambda r: (str(r.get("trade_id", "")), r.get("version", 0)))
    assert _digest(rows) != expected, "a plain concatenation"


# --------------------------------------------------------------------------
# Step two: the return itself
# --------------------------------------------------------------------------
def test_primary_summary_matches_fixture(primary_outputs):
    """Every summary field matches the sealed reference run."""
    _, summary, _, _ = primary_outputs
    assert summary == FIXTURE["primary"]["summary"]


def test_primary_artifacts_match_fixture(primary_outputs):
    """The report lines and the exception queue match the sealed digests."""
    _, _, lines, queue = primary_outputs
    assert _digest(lines) == FIXTURE["primary"]["lines_digest"]
    assert _digest(queue) == FIXTURE["primary"]["queue_digest"]


def test_alternate_ledger_matches_fixture(alternate_outputs):
    """A held-out ledger the agent never sees produces the sealed result."""
    _, summary, lines, queue = alternate_outputs
    assert summary == FIXTURE["alternate"]["summary"]
    assert _digest(lines) == FIXTURE["alternate"]["lines_digest"]
    assert _digest(queue) == FIXTURE["alternate"]["queue_digest"]


def test_output_dir_contains_exactly_three_files(primary_outputs):
    """A run writes the three contracted artifacts and nothing else."""
    out_dir, _, _, _ = primary_outputs
    assert sorted(p.name for p in out_dir.iterdir()) == [
        "exception_queue.jsonl", "report_lines.json", "summary.json"]


def test_the_artifacts_are_serialised_exactly_as_the_contract_states(primary_outputs):
    """Read off the raw bytes, which every other check throws away by parsing.

    The contract fixes a serialisation for all four documents and nothing here
    looked at one, so a run emitting the summary compactly, or the queue with an
    indent, matched every sealed digest. Each rule below is quoted from the
    contract section that governs the file.
    """
    out_dir = primary_outputs[0]
    spec = SPEC["outputs"]

    for name, section in (("summary.json", "summary"),
                          ("report_lines.json", "report_lines")):
        raw = (out_dir / name).read_text(encoding="utf-8")
        stated = spec[section]["serialisation"]
        assert "two-space indent" in stated and "trailing newline" in stated, stated
        assert raw.endswith("\n") and not raw.endswith("\n\n"), (
            f"{name} must end in exactly one newline")
        decoded = json.loads(raw)
        assert raw == json.dumps(decoded, indent=2) + "\n", (
            f"{name} is not the contract's two-space indent")

    raw = (out_dir / "exception_queue.jsonl").read_text(encoding="utf-8")
    assert "compact JSON object per line" in spec["exception_queue"]["serialisation"]
    assert raw.endswith("\n"), "the queue must end in a newline"
    for line in raw.splitlines():
        assert line.strip(), "the queue carries a blank line"
        assert line == json.dumps(json.loads(line), separators=(",", ":")), (
            "a queue line is not compact JSON")

    # the rebuilt ledger is a graded artifact too, and carries its own rule
    raw = LEDGER_PATH.read_text(encoding="utf-8")
    stated = SPEC["reconciled_inputs"]["transaction_ledger"]["serialisation"]
    assert "two-space indent" in stated and "trailing newline" in stated, stated
    assert raw.endswith("\n") and not raw.endswith("\n\n")
    assert raw == json.dumps(json.loads(raw), indent=2) + "\n", (
        "the rebuilt ledger is not the contract's two-space indent")


def test_summary_schema_and_types(primary_outputs):
    """The summary carries exactly the contracted fields at the contracted types."""
    _, summary, _, _ = primary_outputs
    assert set(summary) == SUMMARY_KEYS
    for field, kind in SPEC["outputs"]["summary"]["field_types"].items():
        value = summary[field]
        if kind == "integer":
            assert isinstance(value, int) and not isinstance(value, bool), field
        else:
            assert isinstance(value, str), field


def test_report_schema_and_ordering(primary_outputs):
    """Report lines carry the contracted fields and the contracted order."""
    _, _, lines, _ = primary_outputs
    keys = [(l["deadline_day"], l["trade_id"]) for l in lines]
    assert keys == sorted(keys)
    for l in lines:
        assert set(l) == LINE_KEYS
        assert isinstance(l["late"], bool)
        assert l["deadline_day"] > l["trade_day"]


def test_queue_schema_and_ordering(primary_outputs):
    """Exception rows carry the contracted fields and the contracted order."""
    _, _, _, queue = primary_outputs
    keys = [(r["reason"], r["trade_id"]) for r in queue]
    assert keys == sorted(keys)
    for r in queue:
        assert set(r) == EXCEPTION_KEYS
        assert r["reason"] in EXCEPTION_REASONS


def test_only_the_highest_version_of_a_trade_is_considered(primary_outputs):
    """No trade id appears twice, and the version filed is its highest booking."""
    _, _, lines, queue = primary_outputs
    ids = [l["trade_id"] for l in lines] + [r["trade_id"] for r in queue]
    assert len(ids) == len(set(ids))
    highest = {}
    for b in _load_json(LEDGER_PATH):
        highest[b["trade_id"]] = max(highest.get(b["trade_id"], 0), b["version"])
    for l in lines:
        assert l["version"] == highest[l["trade_id"]]


def test_every_reported_line_clears_the_threshold(primary_outputs):
    """No line below the policy floor reaches the return."""
    _, summary, lines, _ = primary_outputs
    for l in lines:
        assert l["usd_notional"] >= summary["effective_notional_floor"]


def test_reported_filers_are_in_scope_on_the_reporting_side(primary_outputs):
    """Every filed line traces to a reporting party the register admits."""
    _, _, lines, _ = primary_outputs
    register = {p["party_id"]: p for p in _load_json(DATA / "counterparty_register.json")}
    by_lei = {p["lei"]: p for p in register.values()}
    booking = {b["trade_id"]: b for b in _load_json(LEDGER_PATH)}
    for l in lines[:200]:
        rp = register[booking[l["trade_id"]]["reporting_party"]]
        assert rp["in_scope"] and rp["classification"] != "nonfinancial_below"
        assert l["filer_lei"] in by_lei


def test_summary_counts_track_the_artifacts(primary_outputs):
    """The summary's own totals agree with the artifacts beside it."""
    _, summary, lines, queue = primary_outputs
    assert summary["booking_count"] == len(_load_json(LEDGER_PATH))
    assert summary["reported_count"] == len(lines)
    assert summary["exception_count"] == len(queue)
    assert summary["reported_usd_notional"] == sum(l["usd_notional"] for l in lines)
    assert summary["reported_count"] <= summary["effective_max_submissions"]


def test_both_exception_reasons_occur(primary_outputs):
    """The graded run exercises every documented exception reason."""
    _, _, _, queue = primary_outputs
    assert {r["reason"] for r in queue} == EXCEPTION_REASONS


def test_the_cap_actually_binds(primary_outputs):
    """More bookings are eligible than the cap admits, so the cap is load-bearing."""
    _, summary, _, _ = primary_outputs
    assert summary["reported_count"] == summary["effective_max_submissions"]
    assert summary["eligible_count"] > summary["effective_max_submissions"]


# --------------------------------------------------------------------------
# Each reversed rule, pinned on an instance where the drafts disagree
# --------------------------------------------------------------------------
def _party(pid, *, in_scope=True, cls="financial", delegated=""):
    return {"party_id": pid, "lei": f"LEI-{pid}", "classification": cls,
            "in_scope": in_scope, "delegated_to": delegated}


def _booking(tid, version=1, *, rp="CP-A", op="CP-B", notional=5_000_000,
             trade_day=10, submitted_day=11, confirmed=True):
    return {"trade_id": tid, "version": version, "reporting_party": rp, "other_party": op,
            "asset_class": "rates", "venue": "otc", "notional": notional,
            "currency": "USD", "trade_day": trade_day, "submitted_day": submitted_day,
            "confirmed": confirmed}


def _probe(bookings, parties, *, non_business=(), floor=1_000_000, deadline_days=1,
           max_submissions=1000, grace=0):
    """Run the submitted engine over a crafted world and return its artifacts."""
    names = ("counterparty_register.json", "reporting_calendar.json",
             "fx_rates.json", "reporting_policy.json")
    saved = {n: (DATA / n).read_text(encoding="utf-8") for n in names}
    staged = _CWORK / f"probe-{next(_run_ctr)}.json"
    try:
        _write_json(DATA / "counterparty_register.json", parties)
        _write_json(DATA / "reporting_calendar.json",
                    {"horizon_days": 260, "non_business_days": list(non_business)})
        _write_json(DATA / "fx_rates.json", {"micro_usd_per_unit": {"USD": 1_000_000}})
        _write_json(DATA / "reporting_policy.json", {"default": {
            "notional_floor_usd": floor, "deadline_business_days": deadline_days,
            "max_submissions": max_submissions, "late_grace_days": grace}})
        _write_json(staged, bookings)
        os.chmod(staged, 0o644)
        return _run_pipeline(input_path=staged)
    finally:
        for n, text in saved.items():
            (DATA / n).write_text(text, encoding="utf-8")


def test_obligation_follows_the_reporting_side_alone():
    """A trade files even where the other side is out of scope.

    The both-sides draft would drop TR-1 entirely; the governed rule files it
    because the reporting party is in scope.
    """
    _, summary, lines, _ = _probe(
        [_booking("TR-1", rp="CP-A", op="CP-B")],
        [_party("CP-A", in_scope=True), _party("CP-B", in_scope=False)])
    assert summary["eligible_count"] == 1
    assert [l["trade_id"] for l in lines] == ["TR-1"]


def test_a_party_below_the_clearing_threshold_files_nothing():
    """Classification alone can put the reporting side out of scope."""
    _, summary, lines, _ = _probe(
        [_booking("TR-1", rp="CP-A")],
        [_party("CP-A", in_scope=True, cls="nonfinancial_below"), _party("CP-B")])
    assert summary["eligible_count"] == 0 and lines == []


def test_the_highest_version_supersedes_the_earlier_bookings():
    """A re-booking replaces what came before it, and only once.

    Version 2 carries a notional above the floor while version 1 sits below it,
    so the first-version interim would file nothing at all.
    """
    _, summary, lines, _ = _probe(
        [_booking("TR-1", 1, notional=10_000), _booking("TR-1", 2, notional=9_000_000)],
        [_party("CP-A"), _party("CP-B")])
    assert summary["trade_count"] == 1
    assert [(l["trade_id"], l["version"], l["usd_notional"]) for l in lines] == [("TR-1", 2, 9_000_000)]


def test_the_deadline_counts_business_days_across_the_calendar():
    """The deadline steps over closed days rather than counting calendar days.

    Days 11 and 12 are closed, so one business day after day 10 is day 13; a
    calendar offset would land on day 11 and call the day-13 submission late.
    """
    _, _, lines, _ = _probe(
        [_booking("TR-1", trade_day=10, submitted_day=13)],
        [_party("CP-A"), _party("CP-B")], non_business=(11, 12))
    assert [(l["deadline_day"], l["late"]) for l in lines] == [(13, False)]


def test_a_late_submission_is_still_filed_and_counted():
    """Lateness is a flag on the return, not a reason to withhold it."""
    _, summary, lines, _ = _probe(
        [_booking("TR-1", trade_day=10, submitted_day=20)],
        [_party("CP-A"), _party("CP-B")])
    assert summary["late_count"] == 1
    assert [l["late"] for l in lines] == [True]


def test_an_unconfirmed_booking_is_queued_without_consuming_the_cap():
    """The unconfirmed trade is queued, and the confirmed one still files.

    With a cap of one, filing the unconfirmed booking would push the confirmed
    one out; the governed rule keeps the place free.
    """
    _, summary, lines, queue = _probe(
        [_booking("TR-1", trade_day=10, confirmed=False),
         _booking("TR-2", trade_day=10, confirmed=True)],
        [_party("CP-A"), _party("CP-B")], max_submissions=1)
    assert [l["trade_id"] for l in lines] == ["TR-2"]
    assert [(r["trade_id"], r["reason"]) for r in queue] == [("TR-1", "unconfirmed")]
    assert summary["eligible_count"] == 2


def test_delegation_moves_the_filer_but_not_the_eligibility():
    """The delegate's LEI is reported; its own scope does not re-open eligibility."""
    _, _, lines, _ = _probe(
        [_booking("TR-1", rp="CP-A")],
        [_party("CP-A", delegated="CP-C"), _party("CP-B"), _party("CP-C", in_scope=False)])
    assert [l["filer_lei"] for l in lines] == ["LEI-CP-C"]


def test_a_delegation_is_not_followed_past_the_first_delegate():
    """#REG-7192: the chain is not walked to its end.

    A delegation is the arrangement between one reporting party and one delegate,
    so a delegate that has itself delegated is no concern of this line. The rule
    was implicit -- the engine resolved one hop and the graded register happens to
    contain six parties whose delegate has also delegated, pinning thirty-two
    report lines to the first delegate -- so a solution that followed the chain to
    its end failed those lines with nothing in the log to explain why.
    """
    _, _, lines, _ = _probe(
        [_booking("TR-1", rp="CP-A")],
        [_party("CP-A", delegated="CP-B"), _party("CP-B", delegated="CP-C"),
         _party("CP-C")])
    assert [l["filer_lei"] for l in lines] == ["LEI-CP-B"], (
        "the filer is the reporting party's own delegate; following the chain to "
        "CP-C is the reading #REG-7192 now rules out")

    # and the graded register really does contain such chains, so the rule is
    # load-bearing on the graded run rather than only in this crafted world
    register = {r["party_id"]: r for r in _load_json(DATA / "counterparty_register.json")}
    chained = [p for p, r in register.items()
               if r["delegated_to"] and register.get(r["delegated_to"], {}).get("delegated_to")]
    assert chained, "no party in the register delegates to a delegator"


def test_the_cap_queues_the_tail_in_deadline_order():
    """Submissions are taken earliest deadline first and the rest queued."""
    _, _, lines, queue = _probe(
        [_booking("TR-1", trade_day=20), _booking("TR-2", trade_day=10),
         _booking("TR-3", trade_day=15)],
        [_party("CP-A"), _party("CP-B")], max_submissions=2)
    assert [l["trade_id"] for l in lines] == ["TR-2", "TR-3"]
    assert [(r["trade_id"], r["reason"]) for r in queue] == [("TR-1", "over_cap")]


# --------------------------------------------------------------------------
# Contract, budget, determinism and isolation
# --------------------------------------------------------------------------
def test_policy_path_actually_influences_the_output():
    """The policy is resolved from its fixed path, not inlined as constants."""
    saved = (DATA / "reporting_policy.json").read_text(encoding="utf-8")
    try:
        _write_json(DATA / "reporting_policy.json", {"default": {
            "notional_floor_usd": 5_000_000, "deadline_business_days": 3,
            "max_submissions": 40, "late_grace_days": 2}})
        _, summary, _, _ = _run_pipeline()
        assert summary["effective_notional_floor"] == 5_000_000
        assert summary["effective_deadline_days"] == 3
        assert summary["effective_max_submissions"] == 40
        assert summary["effective_late_grace"] == 2
        assert summary != FIXTURE["primary"]["summary"]
    finally:
        (DATA / "reporting_policy.json").write_text(saved, encoding="utf-8")


def test_a_policy_that_omits_a_field_keeps_the_governed_baseline():
    """#REG-7210 fixes a baseline per field, and the shipped policy hides it.

    Every shipped value equals its own baseline, so dropping a field from the
    file that ships changes nothing and an engine that read the policy as
    all-or-nothing graded the same as one following the decision. Each field is
    therefore first set to something the baseline is not, then dropped on its
    own: the dropped one has to fall back while the others keep the staged
    figure, so a fallback that only fires on an empty file is not enough either.
    """
    path = DATA / "reporting_policy.json"
    saved = path.read_text(encoding="utf-8")
    baselines = {"notional_floor_usd": 1_000_000, "deadline_business_days": 1,
                 "max_submissions": 2500, "late_grace_days": 0}
    staged = {"notional_floor_usd": 4_000_000, "deadline_business_days": 3,
              "max_submissions": 60, "late_grace_days": 2}
    reported = {"notional_floor_usd": "effective_notional_floor",
                "deadline_business_days": "effective_deadline_days",
                "max_submissions": "effective_max_submissions",
                "late_grace_days": "effective_late_grace"}
    assert all(staged[f] != baselines[f] for f in baselines), (
        "a staged value equals its baseline, so dropping that field proves nothing")
    try:
        for field in baselines:
            trimmed = {k: v for k, v in staged.items() if k != field}
            _write_json(path, {"default": trimmed})
            _, summary, _, _ = _run_pipeline()
            assert summary[reported[field]] == baselines[field], (
                f"dropping {field} did not fall back to {baselines[field]}")
            for other in baselines:
                if other != field:
                    assert summary[reported[other]] == staged[other], (
                        f"dropping {field} disturbed {other}")
    finally:
        path.write_text(saved, encoding="utf-8")


def test_register_path_actually_influences_the_output():
    """The counterparty register is resolved from its fixed path too."""
    saved = (DATA / "counterparty_register.json").read_text(encoding="utf-8")
    try:
        register = _load_json(DATA / "counterparty_register.json")
        for p in register:
            p["in_scope"] = False
        _write_json(DATA / "counterparty_register.json", register)
        _, summary, lines, _ = _run_pipeline()
        assert summary["eligible_count"] == 0 and lines == []
    finally:
        (DATA / "counterparty_register.json").write_text(saved, encoding="utf-8")


def test_run_is_idempotent(primary_outputs):
    """Re-running over the same ledger reproduces the same artifacts."""
    _, summary, lines, queue = primary_outputs
    _, s2, l2, q2 = _run_pipeline()
    assert s2 == summary and _digest(l2) == _digest(lines) and _digest(q2) == _digest(queue)


def test_no_argument_run_writes_to_the_documented_defaults(primary_outputs):
    """With no flags at all the program reads and writes its documented defaults.

    The previous form still passed --output-dir, so it only exercised the --input
    default; a changed default output directory went unnoticed.
    """
    binary = _build(WORKFLOW_PATH)
    _publish_inputs()
    default_out = Path("/app/output")
    shutil.rmtree(default_out, ignore_errors=True)
    default_out.mkdir(parents=True, exist_ok=True)
    os.chmod(default_out, 0o777)
    result = _run_agent([binary], cwd=_candidate_dir())
    assert result.returncode == 0, result.stderr
    assert sorted(q.name for q in default_out.iterdir()) == ['exception_queue.jsonl', 'report_lines.json', 'summary.json']
    _, summary, doc, queue = primary_outputs
    assert _load_json(default_out / "summary.json") == summary
    assert _digest(_load_json(default_out / "report_lines.json")) == _digest(doc)
    assert _digest(_load_jsonl(default_out / "exception_queue.jsonl")) == _digest(queue)


def test_the_budget_is_enforced_by_killing_an_overrunning_run(primary_outputs):
    """The budget is enforced, and not by timing the grading machine.

    Every candidate run is executed with the contract's published budget as its
    hard timeout, so a run that overruns is killed and the suite fails. Nothing
    compares a measured elapsed time against a threshold.
    """
    assert HARD_TIMEOUT_SEC == int(RUNTIME_BUDGET_SEC)
    assert primary_outputs[1]["reported_count"] > 0, "the graded run did not complete"



def test_runtime_budget_is_stated_in_the_contract():
    """The budget enforced above is the one the contract publishes."""
    assert int(SPEC["runtime_budget_seconds"]) == int(RUNTIME_BUDGET_SEC)


def test_submitted_program_runs_unprivileged_and_cannot_write_reward(tmp_path):
    """The graded program runs as nobody and cannot touch the reward path."""
    probe = tmp_path / "main.go"
    probe.write_text(
        'package main\n\nimport ("fmt"; "os")\n\n'
        'func main() {\n\tfmt.Println(os.Getuid())\n'
        '\terr := os.WriteFile("/logs/verifier/reward.txt", []byte("1"), 0o644)\n'
        '\tfmt.Println(err != nil)\n}\n', encoding="utf-8")
    binary = _build(probe)
    result = _run_agent([binary], cwd=_candidate_dir())
    assert result.returncode == 0, result.stderr
    parts = result.stdout.split()
    assert parts[0] == str(CANDIDATE_UID) and parts[1] == "true"


def test_frozen_snapshot_preserved():
    """The migration's engine must still be on disk, unmodified."""
    assert ORIGINAL_WORKFLOW_PATH.exists()
    assert hashlib.sha256(ORIGINAL_WORKFLOW_PATH.read_bytes()).hexdigest() == \
        FIXTURE["broken_engine_sha256"]


def test_frozen_snapshot_is_wrong(primary_outputs):
    """The shipped engine does not already produce the governed return."""
    _, summary, _, _ = primary_outputs
    _, broken, _, _ = _run_pipeline(script_path=ORIGINAL_WORKFLOW_PATH)
    assert broken != summary


def test_governance_log_present():
    """The minute book the rules are reconstructed from is in the environment."""
    assert LOG_PATH.exists() and LOG_PATH.stat().st_size > 0


def test_calendar_actually_influences_the_output(primary_outputs):
    """The regulatory calendar is resolved from its fixed path, not inlined."""
    path = DATA / "reporting_calendar.json"
    saved = path.read_text(encoding="utf-8")
    try:
        cal = _load_json(path)
        closed = set(cal["non_business_days"])
        assert closed, "the shipped calendar closes no day, so this proves nothing"
        cal["non_business_days"] = []
        _write_json(path, cal)
        _, summary, lines, _ = _run_pipeline()
        assert lines, "opening the calendar must still produce a return"
        # with every day open, counting business days forward is plain calendar
        # arithmetic, so each deadline is exactly the trade day plus the policy's
        # span -- a run that merely noticed new bytes lands nowhere near this
        span = summary["effective_deadline_days"]
        by_trade = {row["trade_id"]: row for row in lines}
        for row in lines:
            assert row["deadline_day"] == row["trade_day"] + span, row["trade_id"]
        # and no deadline can be later than it was when days were closed
        base = {row["trade_id"]: row["deadline_day"] for row in primary_outputs[2]}
        assert any(base[r["trade_id"]] != r["deadline_day"]
                   for r in lines if r["trade_id"] in base), (
            "opening every closed day moved no deadline, so the calendar is unused")
        assert all(r["deadline_day"] <= base[r["trade_id"]]
                   for r in lines if r["trade_id"] in base), (
            "opening a closed day moved a deadline later")
        assert summary != FIXTURE["primary"]["summary"]
    finally:
        path.write_text(saved, encoding="utf-8")


def test_rate_table_actually_influences_the_output(primary_outputs):
    """The rate table is resolved from its fixed path; a currency it drops files nothing."""
    path = DATA / "fx_rates.json"
    saved = path.read_text(encoding="utf-8")
    try:
        fx = _load_json(path)
        dropped = sorted(fx["micro_usd_per_unit"])[0]
        del fx["micro_usd_per_unit"][dropped]
        _write_json(path, fx)
        _, summary, lines, _ = _run_pipeline()
        # the currency has no rate, so nothing denominated in it can be carried
        # into dollars and tested against the floor: those trades and only those
        # leave the return, and every other reported line is untouched
        # only the highest version of a trade is ever reported, so that is the
        # row whose currency decides whether the line can be priced
        ledger = {}
        for row in _load_json(LEDGER_PATH):
            live = ledger.get(row["trade_id"])
            if live is None or row["version"] > live["version"]:
                ledger[row["trade_id"]] = row
        for row in lines:
            assert ledger[row["trade_id"]]["currency"] != dropped, (
                f"{row['trade_id']} is priced in {dropped}, which now has no rate")
        before = {r["trade_id"] for r in primary_outputs[2]}
        gone = before - {r["trade_id"] for r in lines}
        assert gone, f"no reported trade was priced in {dropped}, so this proves nothing"
        assert all(ledger[t]["currency"] == dropped for t in gone), (
            "dropping one rate removed a trade priced in some other currency")
        assert summary["eligible_count"] < FIXTURE["primary"]["summary"]["eligible_count"]
    finally:
        path.write_text(saved, encoding="utf-8")


def test_shipped_contract_matches_the_golden_copy():
    """The output contract in the environment is unmodified.

    Field lists, container shapes and sort orders are golden metadata and are read
    from the verifier's own image; this proves the agent's copy still agrees with
    it, so the contract cannot be trimmed to weaken a schema check.
    """
    shipped = json.loads(SPEC_PATH.read_text(encoding="utf-8"))
    assert shipped == json.loads(GOLDEN_CONTRACT_PATH.read_text(encoding="utf-8"))
