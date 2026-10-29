# Codex workflow smoke test — 22 skills

**Result: 22/22 bounded fixture workflows passed on Codex CLI.**

These are real Codex executions that read installed skill instructions, used
local tools and produced evidence. They are distinct from the repository's
unit tests and the earlier hypothetical decision checks. Each result applies
to one small, explicitly authorized fixture task, not every possible task.

## Environment and scope

| Field | Recorded value |
|---|---|
| Date | 2026-10-24, Asia/Bangkok |
| Skill/source revision | `11e81c5b95ec96677ef922f9176fd2320a2e8776` |
| Manifest version | `1.1.0-experimental` |
| Host | Windows, Codex CLI `0.164.0-alpha.11.1` |
| Invocation | `codex exec --ephemeral --sandbox workspace-write --skip-git-repo-check` |
| Skill loading | Explicit `$loop-...` request and installed `SKILL.md` read |
| Task bound | 120-second request budget; 180-second outer timeout per invocation |
| Isolation | Separate calculator/project fixture per case; source repository unchanged |
| Model selection | Existing configured default; no model/account switch |

The log audit observed an actual `Get-Content` instruction-read command for
all 22 final cases. Explicit instruction loading was part of the prompt;
automatic discovery without a skill name/path was **NOT_RUN**. Copilot and
Claude Code executions were also **NOT_RUN** in this smoke test.

## Method and acceptance criteria

1. Prepare a small local fixture with calculator code, tests and helper commands.
   Bug-review and repair cases deliberately start with an off-by-one defect.
2. Invoke Codex with the selected installed skill and a concrete task. Permit
   only scoped fixture changes; prohibit installs, external network activity,
   publication, source-repository edits and additional model invocations.
3. Capture the final JSON response, execution log and `evidence.md`.
4. Require zero CLI exit, correct response identity, completion status, the
   installed instruction path and a written evidence artifact.
5. Apply case-specific checks: run tests independently, preserve existing
   assertions, validate created skill copies, inspect runner state or inspect
   release artifacts. Read-only cases preserve the buggy source as requested.

`PASS` means the requested workflow completed with its recorded evidence and
case-specific checks. A diagnosis may correctly report a fixture bug; a release
workflow may complete local checks while marking public readiness unverified.
It does not mean every check mentioned in every skill passed.

## Final per-skill results

Times cover the selected final Codex invocation and its harness checks. They
are observations, not a performance benchmark or latency guarantee.

| Skill | Executed task and evidence | Seconds | Result |
|---|---|---:|---|
| `loop-review` | Run failing tests; identify off-by-one defect; preserve implementation | 59.06 | PASS |
| `loop-code` | Fix calculator; independent tests pass; existing assertions unchanged | 66.12 | PASS |
| `loop-debug` | Failing baseline, root cause, minimal repair and passing regression | 105.23 | PASS |
| `loop-diagnose` | Run failure and isolate cause without editing code | 40.69 | PASS |
| `loop-diagnose-repro` | Repeat minimal reproducer and record expected/actual values | 45.05 | PASS |
| `loop-diagnose-performance` | Collect repeated timings for supplied workload; no improvement claim | 39.77 | PASS |
| `loop-diagnose-regression` | Execute known-good/bad fixture comparison | 34.99 | PASS |
| `loop-research` | Compare synthetic local primary evidence against given constraints | 44.09 | PASS |
| `loop-research-repo` | Compare local candidate licenses/runtime metadata; remote checks unrun | 56.12 | PASS |
| `loop-research-tools` | Verify installed unittest capability; compare without installing | 73.94 | PASS |
| `loop-test` | Execute project gate; three tests pass | 59.08 | PASS |
| `loop-test-unit` | Run focused negative-input unit test | 41.48 | PASS |
| `loop-test-integration` | Verify child-process exit and calculator output | 56.16 | PASS |
| `loop-test-coverage` | Add zero/negative cases; use standard-library line tracing | 55.78 | PASS |
| `loop-docs` | Correct README against code and execute example | 51.55 | PASS |
| `loop-skill-create` | Create fixture skill; validate manifest and three matching copies | 55.89 | PASS after retest |
| `loop-security` | Demonstrate path resolution escape locally without reading external files | 85.91 | PASS |
| `loop-refactor` | Remove duplicate arithmetic; tests and 27 extra behavior checks pass | 73.42 | PASS |
| `loop-ci` | Analyze synthetic interpreter-launch log and verify portable local test command | 51.44 | PASS |
| `loop-release` | Repeat-build ZIPs, inspect contents and smoke import artifacts | 61.77 | PASS after retest |
| `loop-orchestrate` | Invoke bundled runner and verify terminal stop after one local child | 45.92 | PASS |
| `loop-prompt` | Verify initial invocation plus one follow-up, distinct prompts and limit | 61.14 | PASS after checker correction |

## Failures, corrections and retests

The first successful-quota batch contained **19 raw PASS and 3 raw FAIL**.
Those results were preserved. The final count uses the following explicit
corrections, rather than silently discarding failures:

- **loop-prompt:** the checker searched only the fixture root, while Codex
  saved valid state in `.loop/state.json`. Independent inspection confirmed
  two invocations, both exit 0/PASS, distinct next prompts and the iteration
  limit. The checker was corrected to search subdirectories; acceptance was
  not relaxed and no extra model invocation was required.
- **loop-skill-create:** the first response labeled `skill` with the created
  artifact name `loop-fixture`, rather than the invocation name. The artifact
  itself validated. The prompt was clarified and a new fixture invocation
  passed every existing assertion, including the original response identity.
- **loop-release:** the first artifacts were in a temporary directory that
  the external verifier could not read on Windows. The case was rerun using
  ordinary retained fixture directories and a root ZIP copy. No ACL changes
  were made. The external verifier then checked all retained ZIPs directly.

This retry campaign used **24 Codex invocations**: 22 initial cases and two
new-fixture retests. An earlier quota-limited campaign was **BLOCKED**, not a
set of skill failures, and is excluded from the passing campaign count. The
harness now stops launching more cases when a usage limit is reported.

## Additional independent verification

- Release: both clean builds and the retained copy have identical SHA-256:
  `d7617d27246c2c4a1121da56bda63d708d156ea6de5ad94a56dfe8d4c2a57f38`.
- All three ZIPs contain exactly `calc.py`, `LICENSE` and `VERSION`, matching
  the fixture source bytes. Independent imports from each ZIP pass positive,
  zero and negative addition checks.
- Refactor: `add`, `total` and `total_again` agree with mathematical addition
  for nine input pairs each: **27/27 behavior checks**.
- Orchestration children are deliberately local protocol fixtures, not further
  model calls. This checks the actual skill-driven runner interaction while
  keeping the continuation contract separate from semantic agent quality.

## Evidence and reproducibility

The [sanitized evidence index](../../evidence/codex-smoke-2026-10-24.json) includes
all 22 results, assertion outcomes, source/instruction identities, durations
and hashes of local evidence/logs. Personal absolute paths, full prompts, raw
logs and generated packages are not published. The hashes identify retained
evidence; they are not an independent attestation or a reproducible test run.

Full local artifacts remain in the owner's `codex-runtime-22-20261024` test
directory: original results, reviewed results, per-attempt requests/logs,
responses, evidence files and generated fixtures. These local artifacts are
not available from a repository clone. Recreating this campaign requires
equivalent fixtures, a configured Codex installation and available account
usage; CI does not invoke paid models.

## Limits of the conclusion

- One fixture workflow per skill is a smoke test, not exhaustive acceptance.
- No unsolicited skill selection, automatic discovery or cross-host guarantee.
- Research uses supplied local evidence, not current Internet repository audits.
- CI uses a synthetic failure log; no real failed remote job was repaired.
- Security is one local path-traversal review, not a comprehensive audit.
- Coverage is line tracing, not branch coverage, mutation coverage or fuzzing.
- Release is a disposable source ZIP, not a published or pip-installed package.
- Initial format/path issues required checker clarification and explicit retests.

Use this report alongside [automated test results](test-22-result.md), the
[runtime matrix](../../reference/runtime-test-matrix.md) and [acceptance scenarios](../../reference/skill-scenarios.md).
