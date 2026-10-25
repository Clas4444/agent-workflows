# Acceptance and context upgrade — 2026-10-25

## Scope and workflows

Applied three recommendations from the Cole Medin research: acceptance before
implementation, context provenance/freshness, and execution results that cannot
turn missing work into PASS. Kept all 34 skills and existing runner interfaces.
Used loop-code for implementation, loop-test for isolated controls and project
checks, and loop-review for diff/evidence review. No external implementation was
imported, no skill was installed globally, and no remote push was performed.

## Changes

- Added `scripts/acceptance_gate.py`, an opt-in standard-library CLI. Its
  reviewed JSON contract maps stable criterion IDs to positive/negative checks
  and pinned local sources. Default execution status is NOT_RUN; only overall
  PASS exits zero. See [the contract and limitations](ACCEPTANCE-GATE.md).
- Upgraded loop-plan, loop-research, loop-code and loop-test. Synchronized all
  three native project layouts. Updated routing review decisions without
  changing the 37 fixed routing prompts or expected routes.
- Updated current instruction hashes and invalidated historical runtime claims
  for changed text. Historical executions remain intact. The revised four
  native workflows are NOT_RUN.
- Fixed a separately discovered existing fingerprint bug in `validate.py`.

## Existing bug: parent directory excluded the whole repository

Severity: P2, source-evidence integrity. The fingerprint excluded a path if any
absolute component was `.loop`, `.git` or `__pycache__`. A repository nested
under one of those directory names produced the SHA-256 of empty content:

```text
e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855
```

Changing source then left the fingerprint identical. This did not demonstrate
an arbitrary invalid skill passing structural validation; it demonstrated a
report identity failing to identify changed source.

Added `test_fingerprint_ignores_only_repo_relative_exclusions` before fixing:
all three parent-name subcases FAILED. Fixed exclusions to inspect paths
relative to the repository being fingerprinted. The new regression now passes,
and ignored directories inside the repository remain ignored. The existing
generated-report exclusion test also passes unchanged.

Reproduce the regression with an available Python 3.11+ executable:

```text
python -m unittest discover -s tests -p test_validate.py -k fingerprint -v
```

## Execution evidence

15 new acceptance-gate tests exercise real subprocesses, default no-execution,
source changes before/during execution, missing source/tool/cwd, empty test
suites, timeout, malformed contracts, duplicate JSON keys, stable criterion
mapping and a real toy CLI with deliberately broken rejection behavior.

The initial new-feature test failed to import the not-yet-implemented gate;
that is a development red test, not proof of a pre-existing feature bug. The
fingerprint regression above is the independently reproduced existing bug.

Four additional CLI scenarios were executed outside unittest in isolated
`.loop/acceptance-20261025/` fixtures. No real repository data was mutated by
their application commands. Sanitized results:
[acceptance-20261025.json](evidence/acceptance-20261025.json).

| Scenario | Expected / observed | Gate exit | Observation |
|---|---|---|---|
| Working application | PASS / PASS | 0 | Positive input doubled; negative input rejected with exit 2 |
| Deliberately broken rejection | FAIL / FAIL | 1 | Same acceptance expectations; negative input incorrectly exited 0 |
| Source changed after pinning | BLOCKED / BLOCKED | 1 | Both application checks NOT_RUN |
| Default, no execute flag | NOT_RUN / NOT_RUN | 1 | Both application checks NOT_RUN |

The CLI scenarios can be recreated through the checked-in subprocess
integration tests and the documented contract:

```text
python -m unittest discover -s tests -p test_acceptance_gate.py -v
```

## Final verification

| Check | Result |
|---|---|
| `python -m unittest discover -s tests -v` | PASS — 146 tests, including original tests |
| `python scripts/validate.py` | PASS — structural validation only |
| `python -m scripts.validate --profile format` | PASS — reduced metadata/integrity profile only |
| `python scripts/catalog.py` | PASS |
| `python scripts/routing_check.py` | PASS — static curated coverage, no model classification rerun |
| `python scripts/sync_skills.py --target .github/skills --check` | PASS — no runner/source differences |
| `python -m compileall -q scripts tests` | PASS |
| `git diff --check` | PASS |
| Native runtime of revised four skills | NOT_RUN |
| Other host/platform execution and remote CI | NOT_RUN |

Environment: Windows, bundled Python 3.12.14; working tree based on commit
`9ff1fe7035081f1235934cf7fe494877089b42e8`. The WindowsApps `python` and
`py` aliases could not execute; an existing bundled interpreter was used without
installing dependencies. The restricted temporary directory could not hold
fixtures, so TEMP/TMP were pointed to the repository's ignored `.loop/tmp`.
This exposed the fingerprint defect. Sandbox hardlink restrictions initially
prevented two existing tests; the complete suite was rerun with the necessary
execution permission and passed. An intermediate routing test also required its
explicit upgraded-skill inventory to include plan/research; counts, fixed case
expectations and negative assertions were preserved.

Local raw test logs remain ignored under `.loop/acceptance-full-tests-final.log`;
subprocess JSON retains outputs under each scenario directory. Published results
omit private executable paths and raw logs.

## Remaining limits

Pinned source hashes prove identity, not source truth, citation entailment or
complete context. Before/after checks do not defeat change-and-restore races.
All relevant inputs must be listed. The gate is not a sandbox, signatures or
tamper-proof storage; subprocess output can lie and must be backed by independent
assertions. Its zero-test detection covers common messages, not every runner.
Timeout only terminates the direct child; output is captured in memory.

No production deployment, real MCP multi-user authorization, persistent memory,
external benchmark, automatic host discovery or revised-skill model campaign
was executed. This change does not certify those behaviors.
