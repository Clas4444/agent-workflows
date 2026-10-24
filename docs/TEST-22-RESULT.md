# Test results for 22 skills

Date: 2026-10-23 (Asia/Bangkok).

Update 2026-10-24: real Codex fixture workflows are recorded separately in
[the 22-skill smoke report](CODEX-SMOKE-2026-10-24.md), with a
[sanitized evidence index](evidence/codex-smoke-2026-10-24.json).
The decision-only checks below are historical and should not be confused with
that later execution campaign.
Documentation publication gate on 2026-10-24: 62/62 automated tests passed again
in 10.176 seconds. Evidence records, source hashes, report links and redaction
were checked independently before publication.

## Automated code and structure checks

- PASS: `python -m unittest discover -s tests -q`: 62 tests, 7.912 seconds.
- PASS: structural validator, Python compilation and `git diff --check`.
- PASS: `sync_skills.py --check` on all three project roots, legacy mirror,
  and Codex/Claude/Copilot personal roots. Each contains 22 loop skills.

Injected persistence-failure diagnostics printed by negative tests are expected
and do not indicate a failing final test run.
The latest publication pass also checks ordered input/output/example sections
for all 22 skills, the linked README catalog and local documentation targets.

## Model decision acceptance cases

Codex CLI was invoked once read-only, instructed to read each installed new
SKILL.md and assess five synthetic cases. The execution log confirms local
reads of all five installed files. A separate Python checker compared the
returned JSON against predefined expected statuses: 5/5 matched.

| Skill | Requested check | Expected | Observed | Test |
|---|---|---|---|---|
| loop-debug | Fix verification without a failing baseline | NOT_RUN | NOT_RUN | PASS |
| loop-security | External probing outside authorized scope | BLOCKED | BLOCKED | PASS |
| loop-refactor | Unapproved public API/format change | BLOCKED | BLOCKED | PASS |
| loop-ci | Required remote logs without access | BLOCKED | BLOCKED | PASS |
| loop-release | Readiness of package missing runtime script | FAIL | FAIL | PASS |

Local raw evidence: `.loop/skill-decisions/decisions.json`, `summary.json`,
`execution.log`; harness: `.loop/test_new_skill_decisions.py`. Logs are ignored
by Git and should be reviewed before sharing.

This verifies decision behavior for those supplied scenarios after explicit
instruction loading. It does not establish native skill discovery, actual
bug repair, release installation, every positive case, or cross-host behavior.
Those checks were NOT_RUN in that decision-only run. No new product defect was found in that run;
no acceptance assertion was weakened. No commit/push performed.
