# Testing and experiment index

Choose the evidence layer before interpreting a PASS. Deterministic repository
checks, model output checks, host discovery and remote CI establish different things.

## Run current checks

| Need | Entry point | Limit |
|---|---|---|
| Validate the repository and record a pinned session | [Testing procedure](TESTING.md) | No model calls or native host discovery |
| Exercise installed skills with a model | [Runtime smoke harness](../RUNTIME-SMOKE.md) | Opt-in account usage; fixed synthetic fixtures |
| Plan, run or regrade the workflow cost experiment | [Advanced Codex workflow experiment](CODEX-WORKFLOW-ADVANCED.md) | Explicit skill text and manual history replay; not a clean skill-free host |
| Check public evidence bytes | [Evidence map](../EVIDENCE.md) | Hash identity is not proof of execution |

## Codex measurements

| Date | Record | Scope |
|---|---|---|
| 2026-10-30 | [Advanced workflow cases](CODEX-WORKFLOW-ADVANCED.md) | Mixed-currency money, blocked dependency graphs, input revisions and source-text authority boundaries; reproducible public harness |
| 2026-10-29 | [Workflow batching pilot](CODEX-WORKFLOW-COST.md) | One-, three- and five-step arithmetic cases; includes a complete plain-prompt control |

The two campaigns retain their own source hashes, model/configuration and case
denominators. Do not pool their timings into a current average or relabel old
runs as new. Native conversation continuation is a separate unexecuted condition.

## Setup, compatibility and retained history

| Topic | Record |
|---|---|
| Independent setup responsibilities | [Setup separation](SETUP-SEPARATION.md) |
| Original shared-graph setup checks | [Historical setup validation](WORKFLOW-SETUP.md) |
| Published 1.10 scope and results | [1.10 results](RESULTS-1.10.md) |
| Older releases | [1.9](RESULTS-1.9.md), [1.8](RESULTS-1.8.md), [1.7](RESULTS-1.7.md) |
| Retained failures and deleted-archive limits | [Archive reconciliation](ARCHIVE-RECONCILIATION.md) |
| Documentation navigation performance correction | [CodeQL regex repair](CODEQL-REDOS-REPAIR.md) |

Keep existing report paths and byte-indexed packets in place. New navigation
belongs here; historical reports are records of their original conditions.

Use PASS for a check that ran and met its criterion, FAIL for an observed
violation, BLOCKED for unavailable prerequisites, STALE for changed input pins,
and NOT_RUN for an unexecuted check. NOT_VERIFIED describes an attribution or
isolation claim that the captured evidence does not establish.
