# Version 1.2 system verification

Date: 2026-10-24. Manifest: **1.2.0-experimental, 27 skills**.

## Outcome and evidence scope

- **Five new skill fixtures passed** after preserving and diagnosing failures.
- **Three changed existing contracts passed fresh Codex regression fixtures**:
  loop-review, loop-code and loop-prompt.
- **Nineteen unchanged instruction files match the earlier 22-skill campaign
  byte for byte**. Their earlier results are reused with explicit provenance.
- This is **8 current executions plus 19 unchanged historical cases**, not a
  fresh run of every skill in one campaign. Explicit skill/path loading was
  used; spontaneous discovery, other hosts and production workloads remain untested.

The [evidence index](evidence/runtime-1.2-2026-10-24.json) covers each manifest
entry and records this distinction. Its normalized instruction hashes are
checked against current source in CI, preventing silent evidence drift.
Raw local evidence and failed attempts remain under `.loop/runtime-1.2-*`.

## Current Codex cases

Codex CLI **0.164.0-alpha.11.1**, Windows, workspace-write sandbox, existing
configured model. Local fixture tools only: no installations, live registries,
production migration, remote publication or further model calls inside a case.

| Skill | Independent outcome |
|---|---|
| loop-plan | Scope, acceptance gates, ordered batches, verification and rollback recorded; source unchanged |
| loop-dependencies | Approved dependency updated consistently; unrelated package unchanged; backup exact |
| loop-migrate | No-write dry-run, value/ID invariants, exact backup, repeat idempotence, exercised rollback; invalid input preserves source/backup |
| loop-test-e2e | Real CLI success, negative, zero, bad integer and missing-argument journeys; tests pass; sentinel unchanged |
| loop-evaluate | Six-case denominator and exact baseline/candidate counts; perturbed-output challenge; unchanged grading inputs |
| loop-review | Actual failing baseline and source finding; source/tests preserved |
| loop-code | Authorized one-line repair; original tests unchanged and passing |
| loop-prompt | Two local child invocations, distinct next prompts, terminal iteration bound |

Every selected final case completed with exit 0, a correctly identified
installed skill, `evidence.md` and passing artifact checks. Execution logs
record explicit instruction reads for all eight cases.

## Failure history and repairs

The first new-skill batch had **3 raw PASS and 2 raw FAIL**. A new-fixture
retest had evaluation PASS but another plan-check failure; raw results were
not overwritten or removed.

1. **Plan heading false negative:** the first grader accepted only literal
   `out-of-scope`, rejecting an equivalent `Out of scope` heading. The grader
   now accepts whitespace/hyphen variants while still rejecting a missing
   scope section. A negative test preserves that requirement.
2. **Windows text encoding:** the retest plan contained UTF-8 smart quotes,
   but implicit locale reads used cp1252 and raised UnicodeDecodeError.
   Production/test text I/O now declares UTF-8, with a smart-quote regression
   and an AST guard against reintroducing implicit production text I/O.
   Retained plan artifacts were independently regraded; the original source
   baseline hash and failed result were preserved.
3. **Scorer report dependency:** a model-generated scorer produced correct
   nominal metrics but required a pre-existing human report, failing in the
   independent fresh directory. The skill/task contract now requires a scorer
   to work from only documented input files. A new fixture passed, including
   changed candidate/baseline outputs. The old failed scorer remains local.
4. **Repeated verification:** independent grader directories now use retained
   unique names, so a later verification does not collide with prior artifacts.

These corrections changed real I/O and artifact checks, not the expected
mathematical results or rubric labels. Missing files, dependency drift,
hardcoded metrics and unsupported prerequisites still cannot be PASS.

## System-wide integration checks

- Local deterministic suite: **89 tests passed** in 9.884 seconds with Python
  3.12.14 on Windows. Structural validation, source compilation, runtime harness
  help, whitespace checks and all seven synchronization checks passed.
- Manifest, README catalog, usage, authoring, scenarios, compatibility and
  changelog updated for 27 skills.
- Canonical and project/personal copies synchronized across seven roots.
- Validator now checks ordered contracts, duplicate metadata, literal boolean
  flags, bounded/empty descriptions, invocation example and no-sleep policy.
- Contract mutation, UTF-8, fixture/grader, quota and evidence-integrity tests
  supplement the original runner regressions. No acceptance assertions were weakened.
- CI runs only deterministic local tests, help and compilation. The runtime
  harness requires an explicit model-call authorization flag.

See [the gap assessment](EXPANSION-27.md), [harness instructions](RUNTIME-SMOKE.md)
and [historical 22-skill report](CODEX-SMOKE-2026-10-24.md).
