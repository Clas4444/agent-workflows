# Runtime test matrix

Structural validation does not prove runtime compatibility. Before claiming
support for a host, run one representative workflow and record how the host
discovered the skill, loaded its instructions, accepted the invocation, and
completed safely.

| Host | Version | Skill | Invocation | Result | Evidence |
|---|---|---|---|---|---|
| Codex subagent / Windows, explicit canonical files | host version not recorded | loop-context + loop-handoff | Two independent synthetic preparation/cold-resume tasks | `PASS` for stated fixture scope only | [1.6 research/evidence](RESEARCH-1.6.md); no automatic discovery or product tests |
| Native automatic discovery / other hosts | not run | loop-context | New 1.6 contract | `NOT_RUN` | Explicit synthetic forward-test recorded separately |
| Native automatic discovery / other hosts | not run | loop-handoff | New 1.6 contract | `NOT_RUN` | Explicit synthetic cold-resume recorded separately |
| Revised 1.6 instruction contracts | not run | loop-evaluate / loop-skill-create | Research/repeated-trial upgrade | `NOT_RUN` | Historical instruction results invalidated |
| Acceptance/context instruction revision | not run | loop-plan / loop-research / loop-code / loop-test | Pinned sources and mapped acceptance controls | `NOT_RUN` | Local CLI tests are separate from native model execution; old instruction results invalidated |
| Revised 1.5 instruction contracts | not run | loop-review / loop-code / loop-diagnose / loop-test | Routing/workflow clarified | `NOT_RUN` | Historical evidence invalidated for current instruction text |
| Native host workflow | not run | loop-deploy | Structural contract only | `NOT_RUN` | No real deployment or rollback execution |
| Native host workflow | not run | loop-observe | Structural contract only | `NOT_RUN` | No live exporter/alert delivery or persistent monitor |
| Full MCP transport/auth/discovery | not run | loop-mcp-design | Offline skill exercise only | `NOT_RUN` | No server was installed or started |
| Full MCP transport/auth/discovery | not run | loop-mcp-test | Synthetic tool-acceptance subset only | `NOT_RUN` | Not an MCP conformance run |
| Full MCP transport/auth/discovery | not run | loop-mcp-security | Synthetic catalog review only | `NOT_RUN` | Runtime enforcement remains untested |
| Revised recovery contract | not run | loop-orchestrate / loop-prompt | Authorized-root recovery wording changed | `NOT_RUN` | Old 1.2 results remain historical; see runtime-invalidations-1.3.json |
| Native host workflow | not run | loop-test-compatibility | Structural/text contract only | `NOT_RUN` | New 1.3 skill; actual cross-host execution pending |
| Native host workflow | not run | loop-test-adversarial | Structural/text contract only | `NOT_RUN` | New 1.3 skill; adversarial CLI tests are not model runtime evidence |
| VS Code/Copilot | not recorded | not recorded | not recorded | `NOT_RUN` | pending |
| Codex CLI / Windows | 0.164.0-alpha.11.1 | Original 22 at recorded revision | Explicit skill request + installed instruction read | `PASS` for bounded smoke scope | [22-skill report](CODEX-SMOKE-2026-10-24.md) |
| Codex CLI / Windows, 1.2 | 0.164.0-alpha.11.1 | 5 new + 3 changed skills; 19 prior byte-identical cases retained separately | Explicit skill request + installed instruction read | `PASS` for recorded fixture scope; not a fresh 27-case run | [1.2 report](RUNTIME-1.2-RESULT.md) |
| Claude Code | not recorded | not recorded | not recorded | `NOT_RUN` | pending |

Do not generalize one host's result to another host or version. Keep runtime
evidence separate from the local fake-command tests for `run_loop.py`.

The Codex row records real local tool workflows, with 22 final passing cases
after two retests and one checker-path correction. Automatic skill discovery
without explicit name/path remains NOT_RUN. This row is not certification of
all possible tasks. See the report's failure history and scope restrictions.
Version 1.2 adds eight fresh case executions; evidence reuse for the other
nineteen is checked against instruction identity and labeled in the index.

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
discovery or full positive workflows. At that earlier point native-host
workflows were NOT_RUN; the 2026-10-24 Codex smoke campaign above adds scoped
workflow evidence while leaving other hosts and automatic discovery unverified.
