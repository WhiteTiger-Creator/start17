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


_ABSENT = object()


def _writable_roots(work: Path) -> list:
    """Every directory the unprivileged run could drop a file into.

    Discovered rather than enumerated: the caller's work area and the HOME it is
    handed, the agent-visible tree under /app, every writable tmpfs the mount
    table names, and every world-writable directory within two levels of the
    root. /proc and /sys carry no candidate writes and are expensive to walk;
    /dev is world-writable in an ordinary container, so taking the whole device
    tree as one root would swallow /dev/shm into it and follow symlinks, and its
    tmpfs mounts are named here and by the mount table instead.
    """
    roots = {work, Path(CHILD_ENV["HOME"]), Path("/tmp"), Path("/var/tmp"),
             Path("/dev/shm"), Path("/run"), Path("/var/lock"), APP}
    try:
        for line in Path("/proc/mounts").read_text(encoding="utf-8").splitlines():
            parts = line.split()
            if len(parts) >= 3 and parts[2] in ("tmpfs", "ramfs"):
                roots.add(Path(parts[1]))
    except OSError:
        pass
    for depth_one in Path("/").iterdir():
        if str(depth_one) in ("/proc", "/sys", "/dev") or depth_one.is_symlink() \
                or not depth_one.is_dir():
            continue
        try:
            entries = [depth_one] + [q for q in depth_one.iterdir()
                                     if q.is_dir() and not q.is_symlink()]
        except OSError:
            continue
        for entry in entries:
            try:
                if entry.stat().st_mode & stat.S_IWOTH:
                    roots.add(entry)
            except OSError:
                continue
    ordered = sorted(roots, key=lambda q: len(str(q)))
    kept: list = []
    for root in ordered:
        if not any(str(root).startswith(str(k) + "/") for k in kept):
            kept.append(root)
    return kept


# Names an implementation could be handed off to. Only those the image actually
# carries are used; the point is not an exhaustive list of every interpreter that
# exists but that the ones a submission would reach for are shut for one run.
# `go` belongs on this list beside the script interpreters. The verifier image
# carries the toolchain so it can compile the submission, and `go run` will build
# and execute a second program from a source the engine writes at run time -- a
# hand-off with no helper file left behind for the file-stashing probe to take
# away, and no script interpreter involved for this list to close.
_INTERPRETER_NAMES = (
    "python3", "python3.13", "python3.12", "python", "perl", "ruby", "node",
    "sh", "bash", "dash", "busybox", "awk", "gawk", "mawk", "php", "tclsh", "lua",
    "go", "gofmt",
)
_INTERPRETER_DIRS = ("/usr/local/bin", "/usr/bin", "/bin", "/usr/local/sbin",
                     "/usr/sbin", "/sbin", "/usr/local/go/bin")


def _reachable_interpreters() -> list:
    """Interpreters on this image that the unprivileged run could execute."""
    found = {}
    for directory in _INTERPRETER_DIRS:
        for name in _INTERPRETER_NAMES:
            path = Path(directory) / name
            try:
                st = path.stat()
            except OSError:
                continue
            if not path.is_file() or not st.st_mode & stat.S_IXOTH:
                continue
            found[str(path.resolve())] = (path, st.st_mode)
    return sorted(found.values(), key=lambda pair: str(pair[0]))


def test_the_engine_refuses_the_directory_its_own_inputs_live_in():
    """instruction.md: /app/data is not a directory this run may empty and fill.

    --output-dir takes a directory, and nothing stopped one from naming the very
    directory the run reads: the three-files-and-nothing-else rule would then
    require clearing the snapshot, the journal, the register, the calendar, the
    rates and the policy, while the same contract requires every one of them
    back byte for byte. Those cannot both hold, so the contract settles it --
    the run says so and stops, having cleared nothing.

    What this confirms is the end state the contract now states, not which
    mechanism produced it: under the graded uid /app/data is root-owned, so a
    run that tried to clear it would fail on the removal and report that
    instead. Both readings leave the directory untouched and exit non-zero,
    which is the point -- there is no longer a reading of the contract on
    which a run quietly empties the directory its own inputs live in.
    """
    binary = _build(WORKFLOW_PATH)
    _publish_inputs()
    before = {q.name: hashlib.sha256(q.read_bytes()).hexdigest()
              for q in sorted(DATA.iterdir()) if q.is_file()}
    work = _candidate_dir()
    result = _run_agent([binary, "--output-dir", str(DATA)], cwd=work)
    assert result.returncode != 0, (
        "the run accepted /app/data as its output directory, where clearing the "
        "contents and returning the inputs unchanged cannot both be done")
    assert str(DATA) in result.stderr, (
        "the run refused the directory without naming it on standard error: "
        f"{result.stderr[-2000:]}")
    after = {q.name: hashlib.sha256(q.read_bytes()).hexdigest()
             for q in sorted(DATA.iterdir()) if q.is_file()}
    assert after == before, (
        "the refused run still changed /app/data: "
        f"{sorted(set(before) ^ set(after)) or [n for n in before if before[n] != after.get(n)]}")


def test_the_engine_starts_no_other_program():
    """instruction.md: the compiled program does the reporting itself.

    The two probes beside this one are run-time defences, and both were reasoned
    around: an engine can carry a helper as a byte constant, write it, run it
    and unlink it before the sweep looks, touching no interpreter on the image
    and leaving no file under /app to withhold. There is no way to start a
    process in Go that does not go through one of these, so this closes the
    route where it starts rather than chasing each way of reaching it.
    """
    source = WORKFLOW_PATH.read_text(encoding="utf-8")
    banned_imports = {"os/exec", "plugin", "C"}
    declared = set(_go_imports(source))
    assert not declared & banned_imports, (
        f"{WORKFLOW_PATH.name} imports {sorted(declared & banned_imports)}: the "
        "compiled program is meant to do the reporting itself rather than hand "
        "the run off to another program")
    payload = _go_source_payload(source)
    # Spelled against the name the FILE binds, not against the package name.
    # `import sc "syscall"` followed by `sc.Exec(...)` replaces the process with
    # an interpreter and writes the string "syscall.Exec" nowhere, so a scan for
    # that literal passed it straight through. The entry points are listed per
    # package and the local name is asked of Go's own parser.
    banned_entries = {
        "os": ("StartProcess",),
        # the process-starting entry points, and the process-creating NUMBERS a
        # raw syscall could carry. Banning `syscall.Syscall` outright was broader
        # than the rule it enforces: the same entry point carries SYS_FSYNC,
        # which flushes a file the run itself wrote and starts nothing. What
        # makes a raw syscall a hand-off is the number, so that is what is refused.
        "syscall": ("Exec", "ForkExec", "StartProcess", "SYS_EXECVE", "SYS_EXECVEAT",
                    "SYS_FORK", "SYS_VFORK", "SYS_CLONE", "SYS_CLONE3"),
    }
    local = _go_import_names(source)
    for path, entries in banned_entries.items():
        name = local.get(path)
        if name is None:
            continue
        assert name != ".", (
            f"{WORKFLOW_PATH.name} dot-imports {path}, which puts its "
            "process-starting entry points in scope under bare names")
        for entry in entries:
            assert f"{name}.{entry}" not in payload, (
                f"{WORKFLOW_PATH.name} reaches {path}.{entry} (written "
                f"{name}.{entry}), which starts another program or replaces this one")
    # a linker directive lives in a comment, where neither scan above looks
    assert "go:linkname" not in source, (
        f"{WORKFLOW_PATH.name} links to an unexported entry point")


def test_the_compiled_engine_does_the_reporting_itself():
    """instruction.md makes that one Go source the whole engine.

    Compiling the file on its own stops a sibling GO SOURCE joining the build,
    and nothing more. A single compilable `package main` whose only substantive
    act is to exec /usr/bin/python3 with the reporting implementation carried in
    a string constant beside it satisfies every other check here: it is one file,
    it compiles alone, it needs nothing else on disk, and it can be made to
    produce the sealed artifacts byte for byte. The Go engine the task asks for
    was never restored.

    The hand-off needs an interpreter it can reach. Every one this image carries
    is closed to the candidate uid for the length of one run -- root keeps them,
    so the suite itself is unaffected -- and the run has to produce the sealed
    artifacts anyway. A program that does the reporting in Go notices nothing; one
    that hands the work to an interpreter has nothing left to hand it to.
    """
    binary = _build(WORKFLOW_PATH)
    _publish_inputs()
    interpreters = _reachable_interpreters()
    assert interpreters, (
        "no interpreter on this image is executable by the candidate, so this "
        "probe is watching nothing -- check _INTERPRETER_DIRS")
    assert any(Path(path).name.startswith("python") for path, _ in interpreters), (
        "no python interpreter was found to close, though it is the one the "
        "hand-off reaches for first")
    assert any(Path(path).name == "go" for path, _ in interpreters), (
        "the Go toolchain was not among the interpreters closed, though this "
        "image carries it to compile the submission and `go run` will build and "
        "execute a second program from a source the engine writes at run time")

    work = _candidate_dir()
    out_dir = work / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o777)
    staged = work / "ledger.json"
    _stage_input(LEDGER_PATH, staged)

    try:
        for path, _mode in interpreters:
            # root-owned and root-executable still, so pytest and the Go
            # toolchain are untouched; unreachable to uid 65534
            os.chmod(path, 0o700)
        result = _run_agent(
            [binary, "--input", str(staged), "--output-dir", str(out_dir)], cwd=work)
    finally:
        for path, mode in interpreters:
            try:
                os.chmod(path, stat.S_IMODE(mode))
            except OSError:
                pass
    # The modes are captured once per RESOLVED path, so /bin/bash and
    # /usr/bin/bash -- the same file on this image -- are saved once rather than
    # twice, and the second save cannot record the mode the first chmod just
    # imposed. That is worth checking rather than assuming: leaving an
    # interpreter closed behind us breaks the harness for everything after.
    for path, mode in interpreters:
        assert path.stat().st_mode & stat.S_IXOTH, (
            f"{path} was left closed after the probe: the modes were not put "
            f"back, and everything that runs after this depends on them")

    named = [str(path) for path, _ in interpreters]
    assert result.returncode == 0, (
        f"the run exited {result.returncode} with these interpreters closed to "
        f"it: {named}\nstdout: {result.stdout[-2000:]}\n"
        f"stderr: {result.stderr[-2000:]}")
    assert _load_json(out_dir / "summary.json") == FIXTURE["primary"]["summary"], (
        f"the summary changed with these interpreters closed: {named}")
    assert _digest(_load_json(out_dir / "report_lines.json")) == \
        FIXTURE["primary"]["lines_digest"]
    assert _digest(_load_jsonl(out_dir / "exception_queue.jsonl")) == \
        FIXTURE["primary"]["queue_digest"]


def test_a_run_leaves_nothing_outside_its_output_directory():
    """instruction.md scopes a run to its --output-dir, and nothing checked it.

    Every other run here reads the three artifacts by name, so a run that also
    dropped a scratch file beside them, or in the directory it was started from,
    satisfied all of them. This walks the whole work area afterwards.

    What is graded is the state the run LEAVES, which is what the instruction
    asks for. Writing an artifact through a temporary file elsewhere and moving
    it into place is an ordinary way to write a file atomically, and a check that
    failed it would be failing correct work; a scratch file that outlives the run
    is a different thing, and so is one the run takes away that it did not put
    there. Both are caught below, in all three directions: added, changed, gone.
    """
    _publish_inputs()
    work = _candidate_dir()
    out_dir = work / "output"
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o777)
    staged = work / "ledger.json"
    _stage_input(LEDGER_PATH, staged)

    # Watching the per-run work area alone is not enough: the run is given
    # HOME=/candidate-work and that directory is world-writable, so a scratch
    # file dropped there -- or in /tmp -- left the output directory clean while
    # the run had still written outside it. Every place it can write is swept.
    # Compiled BEFORE the snapshot is taken. _build makes a temporary directory
    # under /tmp and fills the Go build cache there, so on a cold cache -- this
    # test run on its own, or first in a reordered run -- every one of those paths
    # landed in the difference and read as a write by the graded run.
    binary = _build(WORKFLOW_PATH)

    # Naming a few directories was not enough: an ordinary container mounts a
    # writable tmpfs at /dev/shm, which is under none of them, so a run that wrote
    # there was outside its output directory and outside the sweep. The watched set
    # is discovered instead -- the named directories, every writable tmpfs the
    # mount table carries, and every world-writable directory within two levels of
    # the root -- and each file is recorded with its size and modification time,
    # since a run that rewrites the SAME scratch path on every run has already
    # created it by the time this test snapshots and a set of paths differs by
    # nothing.
    watched = _writable_roots(work)
    if Path("/dev/shm").is_dir():
        assert any(Path("/dev/shm") == root or str(Path("/dev/shm")).startswith(
            str(root) + "/") for root in watched), (
            "the writable tmpfs at /dev/shm is watched by nothing here")

    def sweep():
        # Only what the CANDIDATE owns is recorded. The sweep reaches /tmp and the
        # tmpfs mounts, where the verifier's own machinery writes too -- pytest's
        # cache among them -- and a root-owned file appearing there while the run
        # was in flight is not this run leaving its output directory. The graded
        # binary runs as CANDIDATE_UID and everything it writes carries that
        # owner, so filtering on it keeps the check pointed at the run under test.
        seen = {}
        for root in watched:
            if not root.exists():
                continue
            for q in [root, *root.rglob("*")]:
                try:
                    # lstat, not stat: a candidate-owned symlink whose target
                    # is root-owned reported the TARGET's owner and was filtered
                    # out by the uid test below, so a link left behind in the
                    # work area counted as nothing at all.
                    st = q.lstat()
                except OSError:
                    continue
                if st.st_uid != CANDIDATE_UID:
                    continue
                # Mode travels with size and mtime, and a directory is recorded
                # by its mode rather than as None: a run that only widened the
                # permissions on something it left behind earlier, or that
                # rewrote a file to the same length and put the timestamp back,
                # changed something outside its output directory and the pair
                # alone could not see it. The content digest closes the rest of
                # that gap for a file small enough to read cheaply.
                if q.is_dir():
                    seen[str(q)] = ("dir", stat.S_IMODE(st.st_mode))
                    continue
                body = None
                if stat.S_ISREG(st.st_mode) and st.st_size <= 1_000_000:
                    try:
                        body = hashlib.sha256(q.read_bytes()).hexdigest()
                    except OSError:
                        body = "unreadable"
                seen[str(q)] = (st.st_mtime_ns, st.st_size,
                                stat.S_IMODE(st.st_mode), body)
        return seen

    before = sweep()
    result = _run_agent([binary, "--input", str(staged), "--output-dir", str(out_dir)], cwd=work)
    assert result.returncode == 0, (
        f"the run exited {result.returncode}\n"
        f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}")
    after = sweep()
    written = sorted(q for q, v in after.items() if before.get(q, _ABSENT) != v)
    expected = sorted(str(out_dir / n) for n in (
        "exception_queue.jsonl", "report_lines.json", "summary.json"))
    assert written == expected, (
        f"the run left something outside its output directory: "
        f"{[q for q in written if q not in expected]}")
    # and the other direction, which the difference above cannot see: a file the
    # sweep held before the run and no longer holds after it was taken away by
    # the run, which is as much a mark left outside as a file added
    gone = sorted(q for q in before if q not in after)
    assert not gone, f"the run removed files outside its output directory: {gone}"
    # A run that wrote nothing at all would also write nothing outside its output
    # directory, so the three artifacts are read back: the scope is only worth
    # measuring on a run that did the work.
    assert _load_json(out_dir / "summary.json") == FIXTURE["primary"]["summary"]
    assert _digest(_load_json(out_dir / "report_lines.json")) == \
        FIXTURE["primary"]["lines_digest"]
    assert _digest(_load_jsonl(out_dir / "exception_queue.jsonl")) == \
        FIXTURE["primary"]["queue_digest"]


def test_the_engine_is_one_file_with_no_sibling_source():
    """instruction.md names the case to reject: a helper split into a sibling source.

    _build compiles /app/workflow/build_report.go on its own, so a split
    submission fails to build and every artifact test collapses at once with a
    compiler error. Nothing said why. This checks the rule the instruction
    actually states, and reports the offending files by name.
    """
    engine = WORKFLOW_PATH.resolve()
    # the go tool ignores sources whose name starts with "." or "_", so the frozen
    # copy sitting beside the engine is not a sibling in the sense that matters
    siblings = sorted(q.name for q in WORKFLOW_PATH.parent.glob("*.go")
                      if q.resolve() != engine and not q.name.startswith((".", "_")))
    # A sibling is NOT itself a breach. instruction.md forbids a helper split into
    # a sibling source JOINING the build, and _build copies the engine to a
    # temporary directory and compiles it there, so nothing left in /app/workflow
    # can join it. An agent that wrote its recovery step in Go and left the file
    # behind has broken no stated rule, and failing it here would reject a correct
    # submission over something with no effect on anything graded. What is checked
    # is the rule itself: the engine compiles alone. The siblings are named in the
    # failure only so a split submission says why it failed rather than dying on
    # an undefined-symbol error that explains nothing.
    try:
        _build(WORKFLOW_PATH)
    except AssertionError as exc:
        raise AssertionError(
            f"{WORKFLOW_PATH.name} does not compile on its own, as instruction.md "
            f"requires. Other sources beside it, which never join this build: "
            f"{siblings}\n\n{exc}") from exc


# The files this task ships under /app. Anything else the submission leaves
# there is its own, and the engine must not need any of it at run time.
SHIPPED_UNDER_APP = frozenset({
    "data/counterparty_register.json", "data/fx_rates.json", "data/ledger_journal.json",
    "data/ledger_snapshot_pre_migration.json", "data/reporting_calendar.json",
    "data/reporting_policy.json", "data/transaction_ledger.json",
    "docs/reporting_contract.json", "incident/compliance_governance_log.md",
    "workflow/build_report.go", "workflow/.build_report.original.go",
})


def test_the_engine_does_the_work_itself_and_not_through_a_helper_it_left_behind():
    """The compiled program is the engine, not a launcher for something else.

    Compiling build_report.go alone proves only that it BUILDS alone. A small Go
    program that execs an interpreter over a script the submission left beside it
    -- /app/workflow/helper.py, say -- compiles alone perfectly well and then does
    none of the work itself. The whole submission arrives as /app, so any such
    helper has to be somewhere under /app to survive into this verifier: every
    file there that the task did not ship is moved out of the tree for the length
    of one run, and the run must still produce the graded artifacts. A submission
    that reads the shipped inputs and computes is untouched by this; one that
    hands the job to a file of its own has nothing left to hand it to.
    """
    binary = _build(WORKFLOW_PATH)
    stash = Path(tempfile.mkdtemp(prefix="not_shipped_"))
    moved = []
    for path in sorted(APP.rglob("*")):
        if path.is_dir() or APP / "output" in path.parents or path == APP / "output":
            continue
        rel = str(path.relative_to(APP))
        if rel in SHIPPED_UNDER_APP:
            continue
        target = stash / rel.replace("/", "__")
        shutil.move(str(path), str(target))
        moved.append((path, target))
    try:
        _publish_inputs()
        work = _candidate_dir()
        out_dir = work / "output"
        out_dir.mkdir(parents=True, exist_ok=True)
        os.chmod(out_dir, 0o777)
        result = _run_agent([binary, "--output-dir", str(out_dir)], cwd=work)
        assert result.returncode == 0, (
            "with every file the submission added under /app moved aside, the run "
            f"exited {result.returncode}; the engine is leaning on something it "
            f"left behind\nstdout: {result.stdout[-2000:]}\n"
            f"stderr: {result.stderr[-2000:]}")
        assert _load_json(out_dir / "summary.json") == FIXTURE["primary"]["summary"], (
            "the run produced a different report once its own files were moved "
            "aside, so the work was not being done by the compiled engine")
        assert _digest(_load_json(out_dir / "report_lines.json")) == \
            FIXTURE["primary"]["lines_digest"]
        assert _digest(_load_jsonl(out_dir / "exception_queue.jsonl")) == \
            FIXTURE["primary"]["queue_digest"]
    finally:
        for path, target in moved:
            path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(target), str(path))
        shutil.rmtree(stash, ignore_errors=True)


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
    # A fresh mkdtemp directory rather than /candidate-work/probe-N.json: that
    # name was predictable inside a 1777 directory, so an earlier graded run
    # could plant a symlink there and have root write the probe's bookings
    # through it. The directory is created here, owned by root and world-
    # readable so the run can still read the file it is handed.
    stage_dir = Path(tempfile.mkdtemp(prefix="probe_"))
    os.chmod(stage_dir, 0o755)
    staged = stage_dir / "ledger.json"
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
        shutil.rmtree(stage_dir, ignore_errors=True)


def test_an_empty_ledger_still_produces_the_three_artifacts():
    """The contract's ledger is an array with no minimum length.

    Every other run here hands the engine at least one booking, so an ordinary
    accumulator seeded from the first element -- best[ledger[0].TradeID] and then
    ledger[1:] -- passed the whole suite while panicking on the shortest
    conforming ledger there is. A run over [] owes the same three files: every
    count nought, an empty report array and an empty queue.
    """
    out_dir, summary, lines, queue = _probe([], [_party("CP-A"), _party("CP-B")])
    assert set(summary) == SUMMARY_KEYS
    for field in ("booking_count", "trade_count", "eligible_count",
                  "reported_count", "exception_count", "late_count",
                  "reported_usd_notional"):
        assert summary[field] == 0, f"{field} is {summary[field]} on an empty ledger"
    assert lines == [], "an empty ledger reported something"
    assert queue == [], "an empty ledger queued something"
    assert sorted(q.name for q in out_dir.iterdir()) == [
        "exception_queue.jsonl", "report_lines.json", "summary.json"]


def test_a_submission_cap_of_zero_files_nothing():
    """#REG-7196 takes submissions only until the cap is reached, nought included.

    The cap probes all use a positive limit and the fallback probe only asks that
    a zero-valued policy give a different summary from an omitted one, which an
    engine that echoes the nought into effective_max_submissions while quietly
    treating it as one satisfies. Here the only eligible confirmed booking has to
    go unfiled and be queued over the cap instead.
    """
    _, summary, lines, queue = _probe(
        [_booking("TR-1")], [_party("CP-A"), _party("CP-B")], max_submissions=0)
    assert summary["effective_max_submissions"] == 0
    assert summary["eligible_count"] == 1, (
        "the booking is not eligible, so the cap decides nothing here")
    assert lines == [], (
        "a cap of nought filed a report line, so the nought was read as no cap "
        "or clamped to one")
    assert [(r["trade_id"], r["reason"]) for r in queue] == [("TR-1", "over_cap")]
    assert summary["reported_count"] == 0 and summary["exception_count"] == 1


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


def test_a_trade_files_even_where_the_register_does_not_carry_the_other_side():
    """The other side's entry is never consulted, so its absence changes nothing.

    #REG-7186 has eligibility follow the REPORTING side alone, and the shipped
    engine reads the other party out of the register and drops the trade where it
    is missing. Every other_party in both ledgers sat in the register, so that
    lookup could be left in and nothing here noticed: the whole clause was dead.
    Here CP-B appears on the booking and nowhere in the register.
    """
    _, summary, lines, _ = _probe(
        [_booking("TR-1", rp="CP-A", op="CP-B")], [_party("CP-A", in_scope=True)])
    assert summary["eligible_count"] == 1, (
        "the trade was dropped because the register does not carry its other side")
    assert [l["trade_id"] for l in lines] == ["TR-1"]


def test_the_usd_conversion_is_exact_where_the_product_passes_sixty_four_bits():
    """#REG-7188 means the arithmetic value, not what a 64-bit register holds.

    Both bookings carry a notional whose product with the rate passes the int64
    ceiling while the dollar figure lands far inside it. A run that multiplies in
    64 bits and divides afterwards wraps and reports a number that is not the
    conversion at all -- negative, or small enough to fall under the floor and
    drop the trade from the report entirely. The graded book carries this case
    too, but a probe of its own says which rule broke.
    """
    ledger = [_booking("TR-BIG-1", notional=9_223_372_036_855),
              _booking("TR-BIG-2", notional=9_500_000_000_000)]
    _, summary, lines, queue = _probe(ledger, [_party("CP-A", in_scope=True),
                                               _party("CP-B", in_scope=True)])
    assert [(r["trade_id"], r["usd_notional"]) for r in lines] == [
        ("TR-BIG-1", 9_223_372_036_855), ("TR-BIG-2", 9_500_000_000_000)], (
        "a usd_notional was carried through a 64-bit multiply and wrapped; "
        "#REG-7188 asks for the arithmetic value of notional*rate/1e6")
    assert all(r["usd_notional"] > 0 for r in lines)
    assert summary["reported_usd_notional"] == 9_223_372_036_855 + 9_500_000_000_000
    assert queue == []
    # the probe stages a rate of a million micro-dollars to the unit, so each
    # product really does pass the ceiling and the case is not vacuous
    assert 9_223_372_036_855 * 1_000_000 > 2 ** 63 - 1
    assert 9_500_000_000_000 * 1_000_000 > 2 ** 63 - 1


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


def test_a_deadline_further_out_than_any_other_world_here_still_walks_every_day():
    """#REG-7190 counts business days forward, however many the policy names.

    Every world in this file uses nought, one or three business days, and the
    graded and held-out runs both carry one. An engine that walked correctly up
    to three and then stopped -- clamping, or unrolling the loop it was written
    with -- read the same as the governed rule on all of them. The contract lets
    the policy name any span up to the calendar's horizon, so this walks six
    over a week with two closures inside it: the sixth business day after day 40
    is day 48, not day 46 and not day 43.
    """
    trade_day = 40
    closed = (42, 45)
    ledger = [_booking("TR-1", trade_day=trade_day, submitted_day=trade_day)]
    _, summary, lines, _ = _probe(ledger, [_party("CP-A", in_scope=True),
                                           _party("CP-B", in_scope=True)],
                                  non_business=closed, deadline_days=6)
    assert summary["effective_deadline_days"] == 6
    assert [(r["trade_id"], r["deadline_day"]) for r in lines] == [("TR-1", 48)], (
        "six business days from day 40 over closures on 42 and 45 is day 48; a "
        "shorter answer means the walk stops counting or skips the closed days")


def test_a_deadline_of_zero_business_days_falls_on_the_trade_day():
    """#REG-7190 counts business days forward, and nought of them is a value.

    Every other world here uses one business day or three, and a deadline helper
    that quietly treats nought as a minimum of one reads the same as the
    governed rule on all of them: the graded and held-out runs both carry one,
    the ordinary probes default to one, and the policy mutation uses three. At
    nought the two part company -- the deadline is the trade day itself, so a
    booking submitted that same day is on time and one submitted the next day is
    late, where the minimum-of-one reading calls both of them on time.
    """
    trade_day = 40
    ledger = [_booking("TR-1", trade_day=trade_day, submitted_day=trade_day),
              _booking("TR-2", trade_day=trade_day, submitted_day=trade_day + 1)]
    _, summary, lines, _ = _probe(ledger, [_party("CP-A", in_scope=True),
                                           _party("CP-B", in_scope=True)],
                                  deadline_days=0)
    assert summary["effective_deadline_days"] == 0
    assert [(r["trade_id"], r["deadline_day"]) for r in lines] == [
        ("TR-1", trade_day), ("TR-2", trade_day)], (
        "a deadline of nought business days did not fall on the trade day, so "
        "the count is being floored at one")
    assert [(r["trade_id"], r["late"]) for r in lines] == [
        ("TR-1", False), ("TR-2", True)], (
        "the booking submitted the day after a same-day deadline was not late")
    assert summary["late_count"] == 1


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
def test_stale_contents_are_cleared_from_the_output_directory():
    """instruction.md says a run leaves the directory holding those three and nothing else.

    Nothing reached this: every other run here is handed a directory the suite
    has just created, so a run that wrote its three files over whatever it found
    satisfied all of them, and the reference never cleared either. The contents
    must go and the directory itself must stay -- the run does not own the path,
    and under the candidate uid removing it would be refused outright.
    """
    binary = _build(WORKFLOW_PATH)
    _publish_inputs()
    work = _candidate_dir()
    out_dir = work / "given-output"
    out_dir.mkdir(parents=True, exist_ok=True)
    os.chmod(out_dir, 0o777)
    stale = out_dir / "report_lines.json"
    stale.write_text("[]\n", encoding="utf-8")
    os.chmod(stale, 0o666)
    junk = out_dir / "left_behind.json"
    junk.write_text('{"stale": true}\n', encoding="utf-8")
    os.chmod(junk, 0o666)
    nested = out_dir / "scratch"
    nested.mkdir()
    (nested / "inner.json").write_text("{}\n", encoding="utf-8")
    os.chmod(nested / "inner.json", 0o666)
    os.chmod(nested, 0o777)
    before = out_dir.stat()

    result = _run_agent([binary, "--output-dir", str(out_dir)], cwd=work)
    assert result.returncode == 0, (
        f"the run exited {result.returncode}\n"
        f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}")
    assert sorted(q.name for q in out_dir.iterdir()) == [
        "exception_queue.jsonl", "report_lines.json", "summary.json"], (
        "a stale entry survived into the output directory")
    after = out_dir.stat()
    assert (after.st_ino, after.st_dev) == (before.st_ino, before.st_dev), (
        "the output directory was removed and recreated rather than emptied; the "
        "run does not own the path it writes into")
    # and the run is the graded one, not three empty files that happen to be named right
    assert _load_json(out_dir / "summary.json") == FIXTURE["primary"]["summary"]


def test_an_amendment_past_two_to_the_fifty_third_keeps_every_digit():
    """#REG-7170 has an amendment overwrite the named field, digits and all.

    A journal change carries its value as an untyped JSON member. A replay that
    decodes those through a float64 -- which is what a Go decoder does by
    default, and what most JSON readers do -- loses the low bits of any integer
    past 2^53: 9007199254740993 arrives as 9007199254740992 and the amendment
    writes a figure the journal never carried. The shipped journal now posts
    exactly that value, so the sealed ledger digest grades it, and this reads
    the booking back so a failure says which rule broke rather than only that a
    digest moved.
    """
    journal = _load_json(JOURNAL_PATH)
    posted = [c for c in journal
              if c.get("kind") == "amend" and c.get("field") == "notional"
              and isinstance(c.get("value"), int) and c["value"] > 2 ** 53]
    assert posted, "the journal no longer posts a notional past 2^53"
    ledger = {f'{r["trade_id"]}#{r["version"]}': r for r in _load_json(LEDGER_PATH)}
    for change in posted:
        booking = ledger.get(change["trade_key"])
        assert booking is not None, f'{change["trade_key"]} left the rebuilt ledger'
        assert booking["notional"] == change["value"], (
            f'{change["trade_key"]} carries {booking["notional"]}, not the '
            f'{change["value"]} the journal posted; the value was rounded on the '
            "way in rather than overwritten as it stood")
        # and it really is past what a float64 holds exactly
        assert int(float(change["value"])) != change["value"]


def test_a_change_naming_a_booking_the_snapshot_never_carried_is_ignored():
    """#REG-7170 says such a change is ignored, and no shipped data reached the rule.

    Every trade key the journal named was already in the snapshot, so a replay
    that INSERTED an unknown booking rebuilt the same ledger and matched the
    sealed digest. The journal now carries an amend, a withdraw and a reinstate
    against a booking the snapshot never held; all three must contribute nothing.
    """
    journal = _load_json(JOURNAL_PATH)
    snapshot = {(r["trade_id"], r["version"]) for r in _load_json(SNAPSHOT_PATH)}
    unknown = [c for c in journal
               if (c["trade_key"].split("#")[0],
                   int(c["trade_key"].split("#")[1])) not in snapshot]
    assert unknown, "the journal names no booking the snapshot lacks, so this proves nothing"
    assert {c["kind"] for c in unknown} == {"amend", "withdraw", "reinstate"}, (
        "the unknown booking is not exercised by all three change kinds")

    ghosts = {c["trade_key"].split("#")[0] for c in unknown}
    recovered = {(r["trade_id"], r["version"]) for r in _load_json(LEDGER_PATH)}
    for trade_id in sorted(ghosts):
        assert not any(t == trade_id for t, _ in recovered), (
            f"{trade_id} reached the rebuilt ledger, but the snapshot never "
            "carried it and #REG-7170 ignores a change that names it")


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
        # the grace term has to bite, not just be echoed back. #REG-7190 makes a
        # submission late only past the deadline PLUS late_grace_days, and the
        # shipped policy carries a grace of 0, so nothing else in this suite
        # reaches it: dropping the term entirely left every other test green.
        graced = summary["late_count"]
        assert summary != FIXTURE["primary"]["summary"]
    finally:
        (DATA / "reporting_policy.json").write_text(saved, encoding="utf-8")

    saved = (DATA / "reporting_policy.json").read_text(encoding="utf-8")
    try:
        # the same policy with the grace removed and nothing else changed
        _write_json(DATA / "reporting_policy.json", {"default": {
            "notional_floor_usd": 5_000_000, "deadline_business_days": 3,
            "max_submissions": 40, "late_grace_days": 0}})
        _, ungraced_summary, _, _ = _run_pipeline()
        assert ungraced_summary["effective_late_grace"] == 0
        assert ungraced_summary["late_count"] > graced, (
            "two days of grace excused no submission, so late_grace_days is not "
            f"reaching the lateness test: {graced} late with grace 2, "
            f"{ungraced_summary['late_count']} with grace 0")
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
            # The echoed effective_* value is not the thing being graded. An
            # engine can substitute the baseline for the four summary fields and
            # go on reading the raw map in its decisions, where a missing key is
            # nought in Go and nothing else here would notice. Each dropped run
            # is therefore compared with the same policy carrying that field at
            # its baseline, which must agree, and with the field at nought, which
            # must not -- except for late_grace_days, whose baseline IS nought,
            # so no behaviour can separate the two readings there.
            explicit = dict(staged)
            explicit[field] = baselines[field]
            _write_json(path, {"default": explicit})
            _, at_baseline, _, _ = _run_pipeline()
            assert summary == at_baseline, (
                f"dropping {field} did not behave as setting it to its baseline "
                f"of {baselines[field]}: the fallback reaches the summary field "
                "but not the run")
            if baselines[field] != 0:
                zeroed = dict(staged)
                zeroed[field] = 0
                _write_json(path, {"default": zeroed})
                _, at_zero, _, _ = _run_pipeline()
                assert summary != at_zero, (
                    f"dropping {field} produced the same run as setting it to "
                    "nought, which is what a missing Go map key reads as")
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
    """Re-running over the same ledger reproduces the same artifacts.

    Byte for byte, not merely value for value. Both comparisons below run on
    decoded documents and _digest sorts keys before hashing, so an engine that
    rendered summary.json with its fields in a different order on a later run
    satisfied them while its artifacts differed as files -- which is not what
    "identical across reruns" says.
    """
    first_dir, summary, lines, queue = primary_outputs
    second_dir, s2, l2, q2 = _run_pipeline()
    assert s2 == summary and _digest(l2) == _digest(lines) and _digest(q2) == _digest(queue)
    for name in ("summary.json", "report_lines.json", "exception_queue.jsonl"):
        assert (second_dir / name).read_bytes() == (first_dir / name).read_bytes(), (
            f"{name} came out with the same values but different bytes on a "
            "second run over the same ledger")


def test_the_default_output_path_is_a_directory_the_run_does_not_own():
    """instruction.md says the run writes into a path it does not own.

    Replacing /app/output with a link to somewhere else is not writing into it,
    and it aims every clearing step -- the engine's own and the verifier's --
    at whatever the link names. Checked before anything empties the path.
    """
    default_out = Path("/app/output")
    assert not default_out.is_symlink(), (
        f"/app/output is a symlink to {os.readlink(default_out)}")
    assert default_out.is_dir(), "/app/output is not a directory"
    assert _assert_agent_owned_dir(default_out) == default_out.resolve()
    for q in default_out.rglob("*"):
        assert not q.is_symlink(), f"{q} under /app/output is a symlink"


def test_no_argument_run_writes_to_the_documented_defaults(primary_outputs):
    """With no flags at all the program reads and writes its documented defaults.

    The previous form still passed --output-dir, so it only exercised the --input
    default; a changed default output directory went unnoticed.
    """
    binary = _build(WORKFLOW_PATH)
    _publish_inputs()
    default_out = Path("/app/output")
    # Root is about to empty this. It is an agent-writable path, so refuse it
    # outright unless it is a real directory inside /app: a symlink planted here
    # pointed the clearing step at /tests/fixtures and deleted the sealed goldens.
    _assert_agent_owned_dir(default_out)
    # the directory ships with the image; emptying it is what this test needs, but
    # its mode belongs to the environment and is put back either way
    mode = default_out.stat().st_mode & 0o7777 if default_out.exists() else 0o777
    try:
        for stale in sorted(default_out.rglob("*"), reverse=True):
            stale.unlink() if stale.is_file() or stale.is_symlink() else stale.rmdir()
        default_out.mkdir(parents=True, exist_ok=True)
        os.chmod(default_out, 0o777)
        result = _run_agent([binary], cwd=_candidate_dir())
        # the exit code is a precondition; the verdict is the three files and their content
        assert result.returncode == 0, (
            f"the run exited {result.returncode}\n"
            f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}")
        assert sorted(q.name for q in default_out.iterdir()) == [
            'exception_queue.jsonl', 'report_lines.json', 'summary.json']
        _, summary, doc, queue = primary_outputs
        assert _load_json(default_out / "summary.json") == summary
        assert _digest(_load_json(default_out / "report_lines.json")) == _digest(doc)
        assert _digest(_load_jsonl(default_out / "exception_queue.jsonl")) == _digest(queue)
    finally:
        if default_out.exists():
            os.chmod(default_out, mode)


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
    # the exit code is a precondition; the verdict is the two lines the probe printed
    assert result.returncode == 0, (
        f"the probe exited {result.returncode}\n"
        f"stdout: {result.stdout[-2000:]}\nstderr: {result.stderr[-2000:]}")
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


def test_the_engine_declares_no_option_beyond_the_two_it_documents():
    """instruction.md: it carries --input and --output-dir and declares no other option.

    The fixed-path rule was graded only in the direction that an ordinary run
    reads the fixed files, which an engine offering its own override passes
    without difficulty, since no run here ever supplies one. The declared set
    is read off the program itself rather than guessed at: the flag package
    prints every option it declares when it is asked for help, and that set has
    to be exactly the two the contract names.
    """
    binary = _build(WORKFLOW_PATH)
    _publish_inputs()
    usage = _run_agent([binary, "-h"], cwd=_candidate_dir())
    text = (usage.stdout or "") + (usage.stderr or "")
    assert text.strip(), (
        "the engine printed no usage, so the options it declares cannot be "
        "read off it")
    declared = {name for name in re.findall(r"-{1,2}([A-Za-z][A-Za-z0-9_.-]*)", text)
                if name not in {"h", "help"}}
    assert declared == {"input", "output-dir"}, (
        f"the engine declares {sorted(declared)}; the contract names --input "
        "and --output-dir and no other option")
