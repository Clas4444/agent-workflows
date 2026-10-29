# 1.3 catalog verification

Date: 2026-10-24. Current catalog: **29 skills, seven functional groups**.
Source baseline before the pending updates: `216cd47561b005e73b59be73c7e899fc359b908e`.

## What changed

- Added `loop-test-adversarial` and `loop-test-compatibility`, with distinct
  oracles for contract violations and declared support matrices.
- Grouped the complete README catalog from `skill-groups.json`; the gate checks
  exact membership, stale tables and the advertised introductory skill count.
- Retained the demonstrated metadata, Unicode-version and hardlink fixes from
  [the adversarial campaign](2026-10-24-adversarial.md).
- Clarified both continuation skills: missing-runner recovery requires writes
  already authorized for an explicitly selected installation root. Invocation
  alone does not authorize overwriting an installation.
- Preserved historical evidence against its frozen manifest. The two changed
  instruction contracts invalidate direct reuse of their old runtime PASS;
  [the invalidation registry](../../evidence/runtime-invalidations-1.3.json) records
  old/new hashes and current NOT_RUN status.

## All seven testing workflows used

| Workflow | Actual activity | Evidence scope |
|---|---|---|
| loop-test | Select relevant gates, then execute the complete deterministic suite | Local Python tests, not 29 fresh host workflows |
| loop-test-unit | Contract/metadata, manifest/schema and parser tests | Positive, malformed, duplicate and bounded-input assertions |
| loop-test-integration | Synchronization, backups, hardlinks, child status and persistence | Disposable files and real child processes where specified |
| loop-test-coverage | stdlib trace line counts with missing-line reporting | Parent-process line coverage only; no branch coverage claim |
| loop-test-e2e | Real catalog edit → stale rejection → regenerate → validate journey | Actual CLI entry points; original skill bytes retained |
| loop-test-adversarial | Repeat malformed-data and hardlink reproductions, valid controls and regressions | Demonstrated old false PASS results and corrected side effects |
| loop-test-compatibility | Valid/invalid script versus module entry-point matrix | Available Windows/Python cells; CI cells checked separately |

These workflows were applied to the repository and its complete catalog. They
are not a claim that every skill was autonomously selected or independently
executed against every host and every task.

## Codex review and corrections

One explicitly authorized Codex CLI audit read all 29 canonical instructions,
applied all seven testing workflows and executed contract, sync, real CLI,
adversarial and full-suite commands. The audit's full suite passed **118 tests**
before the final corrections. Its report and tool log remain under ignored
`.loop/native-review-1.3/`.

The review identified missing-runner authorization ambiguity, a stale README
introduction (27 instead of 29) and stale 27-to-28 prose. The first is an
instruction ambiguity, not a demonstrated unauthorized host write. The README
count issue had a new real-CLI regression that failed before the gate was fixed.
Both were repaired. The final deterministic suite includes that regression.

The Codex audit read coverage evidence whose first measurement omitted
`trace --missing`; that display can misleadingly show 100% of observed lines.
The parent reran with missing-line accounting and retained both outputs.
Only the corrected measurement is used for coverage statements. Subprocess
execution is not automatically included, so low parent-process coverage of CLI
or model orchestration does not mean those subprocess journeys were absent.
Conversely, passing a subprocess does not establish complete branch coverage.

See [the machine-readable current index](../../evidence/verification-1.3.json) for
final counts, normalized instruction identities and per-skill evidence status.
Raw execution reports are retained locally, not published with private paths.

## Reproduce locally

```text
python -m unittest discover -s tests -v
python scripts/validate.py
python -m scripts.validate --profile format
python scripts/catalog.py
python scripts/sync_skills.py --target .github/skills --check
python scripts/adversarial_repro.py --output-dir .loop/repro-fresh --expect fixed
python -m compileall -q scripts tests
git diff --check
```

For parent-process line measurement, use Python's `trace --count --missing
--summary --coverdir` around the unittest command. Keep outputs under `.loop/`
and do not exclude production code to inflate coverage. There is no repository
coverage threshold; branch/path coverage and exhaustive mutation scoring remain
NOT_RUN. Contract mutation tests are distinct from a mutation score.

## Remaining limitations

- Native discovery and positive acceptance workflows for each of all 29 skills
  were not rerun. Twenty-five instruction identities still match the historical
  1.2 evidence; two new and two revised contracts have current host runtime
  **NOT_RUN**. The Codex catalog audit is separate evidence, not a replacement.
- Claude/Copilot runtime, production data, live dependency advisories and UI
  journeys remain NOT_RUN. Python/OS CI success does not prove those hosts.
- Metadata parsing is a documented subset, not arbitrary YAML conformance.
  Preflight does not prevent concurrent filesystem substitution; process
  timeout only guarantees direct-child termination.
- Personal installations were not modified by this repository update. Project
  copies are synchronized; remote CI must be checked on the pushed commit.
