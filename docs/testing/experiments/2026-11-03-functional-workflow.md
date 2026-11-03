# Functional workflow checks — FUNCTION-03

For one clear stateless step, a direct prompt or focused skill avoids setup
bookkeeping. Conditional multi-step work with bounded repair and checkpoints
can justify a graph. Workflow Setup determines WHAT/NEXT/STOP; optional Agent
Attention only adjusts processing inside a selected step. There is no default
promise of lower token cost.

## User-visible checkpoint behavior

`start --project` opts into tracking v1. After actually doing/checking a selected
step, `record --project` pins its exact source files with the caller observation.
Before reuse, `resume --project` retains unaffected completed work and invalidates
the earliest changed PASS and its downstream suffix. Pre-step facts are restored;
consumed steps/cycles remain spent. STOP stays stopped. Missing/aliased files,
changed graphs, unsupported versions, unknown tracking fields and inconsistent
budgets produce diagnostics. Legacy start/advance remains compatible, without a
source-freshness claim. select alone does not check recorded evidence freshness.
See [the guide](../../guides/workflow-setup.md) and
[contract](../../reference/coordination-contract.md).

| Acceptance | Before | Verified after repair |
|---|---|---|
| Failing code check → repair → verify → stop | Graph cursor alone routes caller status | Real fixture subprocess fails, corrected code passes, tracked route reaches DONE within budget |
| Requirement changes during checkpoint | Graph unchanged; legacy cursor cannot detect source change | Only affected suffix rewinds; intake retained and counters unchanged |
| Authority conflict | Must not invent permission | CLI BLOCKED route stops and code bytes remain unchanged |
| Malformed/refunded history | Invalidated observations were not checked against counters | Invalidated and retained records both validate consumed budget; malformed tracking rejected |
| Current cursor mutation | Current facts/last aliased the retained observation | Independent snapshot preserves recorded history |

Before implementation, five new-feature CLI controls failed because record/resume
did not exist. These are missing-capability controls, not five independent defects.
Seven initial CLI journeys passed after implementation. Delivery review reproduced
two additional failures (observation aliasing and invalidated-budget validation),
then all nine CLI/helper journeys passed. Five controller/oracle controls cover
wrong code with valid JSON, boolean-input defects, unauthorized writes, telemetry
types, local policy pause and a runtime quota item that previously allowed false
PASS despite a valid handoff. The repaired path stops with the proper scoped
marker; this is a deterministic transport control, not another model attempt.
Public-input reproduction tests reject changed
counters and source snapshots in a fresh directory. These are deterministic
checks with real files/subprocesses, not model calls or native picker tests.

## New Codex attempts

Six slots were frozen before calls: three realistic repair/resume/authority cases
× baseline/workflow, one repetition per cell. Both arms received identical files,
tools and authority. Baseline received a complete, useful task prompt; workflow
added explicit setup/map/route instructions. The independent oracle stayed outside
the project; requirements and visible starting checks were available to both arms.
Requested model: gpt-6.1-sol, low effort. Actual model/internal request count:
NOT_REPORTED. Requested isolation flags alone do not establish clean A/B isolation.

| Slot | Original status | Separate prerequisite-v2 | Wall seconds | Input | Cached input | Output | Total |
|---|---|---|---:|---:|---:|---:|---:|
| repair / workflow | FAIL | BLOCKED_ENVIRONMENT | 15.909 | 59930 | 54144 | 273 | 60203 |
| repair / baseline | FAIL | BLOCKED_ENVIRONMENT | 17.416 | 67166 | 57856 | 259 | 67425 |
| resume / baseline | CANCELLED_UNKNOWN | CANCELLED_UNKNOWN | unknown | unknown | unknown | unknown | unknown |
| remaining three planned slots | NOT_RUN | NOT_RUN | — | — | — | — | — |

The two completed sessions reported policy/read-only restrictions. Traces contain
zero command_execution events and no requested artifacts; independent checks
confirm no repair was delivered. The messages do not independently prove an OS
cause. Original FAIL rows remain unchanged; prerequisite-v2 is a separate layer.
The initial controller treated the report as an artifact failure and continued;
manual stop left the third reservation uncertain. A later controller fix pauses
conservatively on this report without command events and rereads shared marker
artifacts before each reservation. That fix was not model-tested.

Budget: **3/12 consumed**, including one cancelled/unknown attempt. Remaining
ceiling9 is paused, not permission to bypass the unresolved prerequisite. The
local process marker does not block a peer campaign. No auth/quota retry, Copilot
call, provider/account switch or new model call occurred during delivery review.
Whole-campaign token usage is unknown because the third attempt has no completed
usage. Completed cache-write counts are0; reasoning outputs23 and15 are subsets
of output. Cached input is already part of input. No efficacy/cost comparison or
comparative chart is eligible with failed prerequisites and no executed work.
No general savings or live combined behavior is established.

## Public evidence and limits

The [packet](../../evidence/coordination-function-20261103/README.md) contains
[source metrics](../../evidence/coordination-function-20261103/function03-model.csv),
original/regrade labels, all recorded event types after identifier/path removal,
reservation history, frozen protocol and measured source snapshots. Raw traces
and machine-specific logs remain private and unavailable for public replay;
hashes are not independent attestation. The measured helper/controller differ
from final source after the later repairs; blocked attempts do not verify those
repairs. The independent consistency command uses only published inputs:

```text
python scripts/coordination_evidence.py
python scripts/evidence_indexes.py
```

Final gate results and input pin are in the
[local delivery receipt](../sessions/coordination-function-local-20261103.json).
Old receipts remain historical and are stale for this final source. Source-tracked
observations are caller data, not authenticated execution. Only exact listed
dependencies can be invalidated. Live model setup/map/skill adherence, live resume,
native discovery and combined integration remain BLOCKED/NOT_VERIFIED. Common-v1
local fixtures are unchanged; parent-reported peer hash equality is separate from
live integration. Illustrations are unchanged. No global skills or peer files were
modified. Delivery uses patch1.11.5; no release/tag is created.

## Delivery verification

Source/evidence commit [`cf3cff1`](https://github.com/Clas4444/agent-workflows/commit/cf3cff1070d60efc31f6ee8068da5b8fa98b76f2) passed the exact-SHA Windows/Linux Python3.11/3.12 matrix and CodeQL Python/JavaScript/Actions. All61 changed public file bytes match GitHub downloads. [Remote receipt](../sessions/coordination-function-remote-20261103.json) separates this source SHA from its documentation-only follow-up. No additional model call or broader effectiveness claim follows from CI.
