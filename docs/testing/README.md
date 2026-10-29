# Testing and experiment index

Choose the evidence layer before interpreting a PASS. Deterministic repository
checks, model output checks, host discovery and remote CI establish different things.

## Run current checks

| Need | Entry point | Limit |
|---|---|---|
| Validate the repository and record a pinned session | [Testing procedure](procedure.md) | No model calls or native host discovery |
| Exercise installed skills with a model | [Runtime smoke harness](../reference/runtime-smoke.md) | Opt-in account usage; fixed synthetic fixtures |
| Plan, run or regrade the workflow cost experiment | [Advanced Codex workflow experiment](experiments/2026-10-30-workflow-advanced.md) | Explicit skill text and manual history replay; not a clean skill-free host |
| Check public evidence bytes | [Evidence map](evidence.md) | Hash identity is not proof of execution |

## Codex measurements

| Date | Record | Scope |
|---|---|---|
| 2026-10-30 | [Advanced workflow cases](experiments/2026-10-30-workflow-advanced.md) | Mixed-currency money, blocked dependency graphs, input revisions and source-text authority boundaries; reproducible public harness |
| 2026-10-29 | [Workflow batching pilot](experiments/2026-10-29-workflow-cost.md) | One-, three- and five-step arithmetic cases; includes a complete plain-prompt control |

The two campaigns retain their own source hashes, model/configuration and case
denominators. Do not pool their timings into a current average or relabel old
runs as new. Native conversation continuation is a separate unexecuted condition.

## Setup, compatibility and retained history

| Topic | Record |
|---|---|
| Independent setup responsibilities | [Setup separation](checks/setup-separation.md) |
| Original shared-graph setup checks | [Historical setup validation](history/1.11.0-workflow-setup.md) |
| Published 1.10 scope and results | [1.10 results](history/1.10-results.md) |
| Older releases | [1.9](history/1.9-results.md), [1.8](history/1.8-results.md), [1.7](history/1.7-results.md) |
| Retained failures and deleted-archive limits | [Archive reconciliation](history/2026-10-29-archive-reconciliation.md) |
| Documentation navigation performance correction | [CodeQL regex repair](checks/codeql-redos-repair.md) |

Store reports in `history/`, current configuration checks in `checks/`, and
model comparisons in `experiments/`. Byte-indexed packets remain in their
original `docs/evidence/` locations. Historical records retain their original
conditions; a file move is not a new execution.

Use PASS for a check that ran and met its criterion, FAIL for an observed
violation, BLOCKED for unavailable prerequisites, STALE for changed input pins,
and NOT_RUN for an unexecuted check. NOT_VERIFIED describes an attribution or
isolation claim that the captured evidence does not establish.
