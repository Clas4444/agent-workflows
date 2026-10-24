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

## Evidence and limitations

Each case keeps request.txt, execution.log, response.json, evidence.md and
verified.json when available. results.json records statuses incrementally.
Logs may contain private paths/output; publish only reviewed summaries and
sanitized evidence. Hashes refer to local raw bytes (including line endings),
not necessarily Git's normalized blobs.
All harness text I/O uses explicit UTF-8, including model-generated plans and
reports. This avoids Windows cp1252 failures for smart quotes or non-English text.
Independent verification directories are unique, so repeat grading preserves
previous challenge artifacts instead of colliding with or deleting them.

The current fixtures are synthetic and local. Dependency/advisory network
checks, production migrations, browser journeys and new model-quality grading
are outside scope. `loop-evaluate` scores supplied outputs; it does not launch
another model. The outer timeout terminates the direct CLI process, not every
possible descendant. A successful smoke case is not universal host support.
