# Opt-in runtime smoke harness

`scripts/runtime_smoke.py` provides reusable local cases for the five 1.2
workflows. `scripts/smoke_cases.py` owns fixture preparation and independent
artifact grading. Both use only Python's standard library.

## Before running

Use an existing configured Codex CLI, available account usage and the intended
installed skill root. Model calls may consume account quota. The harness
requires `--allow-model-invocations`, does not install/authenticate anything,
does not bypass sandboxing, and is never called by CI.

```text
python scripts/runtime_smoke.py --allow-model-invocations --skill-root PATH_TO_SKILLS --output-dir .loop/runtime-1.2
```

Optional flags: `--codex PATH`, `--timeout 180`, and `--skills loop-migrate
loop-evaluate`. The output directory must not exist. Keep each attempt rather
than overwriting old logs. Each CLI invocation runs `workspace-write` scoped to
its fixture, with explicit user authorization in the task prompt.
Three regression fixtures are also available for the existing contracts changed
in 1.2: `--skills loop-review loop-code loop-prompt`. Defaults run only the five
new workflows. Unsupported skill names are rejected rather than silently skipped.

## What is graded

| Skill | Independent checks |
|---|---|
| loop-plan | Plan gates and scope; calculator unchanged; no unsolicited implementation |
| loop-dependencies | Approved version in both files, preserved unrelated package, exact original backup |
| loop-migrate | No-write dry-run, schema/value invariants, byte backup, idempotence, rollback, malformed-input preservation |
| loop-test-e2e | Real CLI output/exit/error for success/zero/negative/invalid cases; sentinel unchanged |
| loop-evaluate | Fixed-rubric counts, original inputs unchanged, perturbed-output challenge to detect hardcoded totals |

Missing artifacts, failing assertions, nonzero CLI exits and invalid response
identity cannot be PASS. An account usage limit is BLOCKED and stops new calls;
remaining cases are NOT_RUN. A missing required instruction or executable is
reported as unavailable rather than silently using another account/model.

Dependency grading independently reads the actual JSON versions against the
original approval metadata and requires the original checker bytes. A replaced
checker is not executed as an oracle. E2E grading requires a nonempty passing
unittest suite, then runs that suite in fresh directories against wrong-sum and
invalid-input-acceptance mutants. Both must be rejected by assertions. Keep the
suite self-contained in `test_e2e.py`, using its own directory for fixture paths;
the original application and sentinel remain untouched. These two mutations do
not prove complete coverage.

## Evidence and limitations

Each case keeps request.txt, execution.log, response.json, evidence.md and
verified.json when available. results.json records statuses incrementally.
Logs may contain private paths/output; publish only reviewed summaries and
sanitized evidence. Hashes refer to local raw bytes (including line endings),
not necessarily Git's normalized blobs.
The instruction hash is captured before execution and compared after the host
returns. Drift or disappearance prevents a PASS; both hashes and the original
response are retained. Historical records with only a post-run hash do not gain
this guarantee retrospectively. This check does not defeat change-and-restore
races or prove that the host actually read the instruction.
The grader also rechecks immutable fixture inputs after executing submissions.
The implementation/scorer/test artifacts themselves must stay byte-identical
during verification. Allowed implementation/dependency edits are distinguished
from files declared immutable by the task. Missing artifacts become failed
checks; completed observations are retained. Metric counts must be actual Python
integers (excluding bool/float), and the full expected metric maps are checked
for both nominal and perturbed inputs.

Response JSON may be bare or enclosed in a complete JSON code fence; an
arbitrary final line is not treated as a closing fence. Duplicate keys and
nonstandard non-finite literals are rejected before reading a claimed PASS.
All harness text I/O uses explicit UTF-8, including model-generated plans and
reports. This avoids Windows cp1252 failures for smart quotes or non-English text.
Independent verification directories are unique, so repeat grading preserves
previous challenge artifacts instead of colliding with or deleting them.

Python verification starts with `-I -S -B -X utf8`: inherited Python import settings and
site hooks cannot replace the grader's startup modules. The standard-library
unittest framework is imported before the fixture directory is exposed to test
discovery. Code/review grading selects the preserved `test_calc.py`, not arbitrary
extra test modules. A code grade requires a nonempty observed suite and a separate
arithmetic probe whose typed outputs are compared by the trusted parent. Merely
printing an OK line, exiting zero during import, or replacing child assertions
does not establish that behavior. This does not sandbox arbitrary submitted code
or make a finite functional probe exhaustive; the remaining process/network/file
permissions are still the caller's responsibility. No historical PASS is promoted
to this new oracle guarantee.

The current fixtures are synthetic and local. Dependency/advisory network
checks, production migrations, browser journeys and new model-quality grading
are outside scope. `loop-evaluate` scores supplied outputs; it does not launch
another model. The outer timeout terminates the direct CLI process, not every
possible descendant. A successful smoke case is not universal host support.
