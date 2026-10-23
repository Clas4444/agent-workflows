# Runtime test matrix

Structural validation does not prove runtime compatibility. Before claiming
support for a host, run one representative workflow and record how the host
discovered the skill, loaded its instructions, accepted the invocation, and
completed safely.

| Host | Version | Skill | Invocation | Result | Evidence |
|---|---|---|---|---|---|
| VS Code/Copilot | not recorded | not recorded | not recorded | `NOT_RUN` | pending |
| Codex | not recorded | not recorded | not recorded | `NOT_RUN` | pending |
| Claude Code | not recorded | not recorded | not recorded | `NOT_RUN` | pending |

Do not generalize one host's result to another host or version. Keep runtime
evidence separate from the local fake-command tests for `run_loop.py`.

## Headless orchestration evidence (separate from native skill discovery)

On 2026-10-23, Codex CLI 0.163.0-alpha.11.2 completed four read-only review
invocations through `run_loop.py --follow-up-count 3` and an explicit local
adapter. The agent inferred distinct follow-up prompts for documentation,
acceptance cases and packaging. Final status PASS, prompt count 4.

Local evidence: `.loop/expansion-state.json`, `.loop/expansion-report.md` and
`.loop/expansion-review/review-01.txt` through `review-04.txt`. Logs remain local
and ignored by Git. This verifies that particular configured headless review
path; it does not prove native discovery or execution of each of the 22 skills.

On the same date, one additional read-only Codex invocation read all five new
installed skill files and assessed synthetic negative cases. An independent
JSON assertion check matched 5/5 expected statuses. See TEST-22-RESULT.md.
Explicit instruction loading and decision checks do not establish native skill
discovery or full positive workflows, so the native-host rows remain NOT_RUN.
