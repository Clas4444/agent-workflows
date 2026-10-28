# Bundle starting points

A bundle installs a toolkit. Start with one focused skill below; add another only
when its output is needed. These are defaults for the stated request, not an
execution order for every member. If the outcome is unclear, use `loop` to select.

| Bundle | Typical request / minimum input | Start with | Expected first output |
|---|---|---|---|
| writing | Draft a message: audience, facts, tone | `loop-write` | draft with missing facts marked |
| office | Prepare a packet: sources, deliverables, deadline | `loop-work` | feasible deliverables and checkpoint |
| learning | Study a topic: goal, level, available time | `loop-learn` | study plan and understanding checks |
| decisions | Compare options: choices, hard constraints, priorities | `loop-decide` | criteria and evidence-backed comparison |
| developer | Implement a change: repository, expected behavior | `loop-code` | small implementation and relevant checks; use `loop-debug` for a reproducible bug |
| project | Deliver a project slice: goal, constraints, current state | `loop-workflow-project` | scoped slice and acceptance criteria |
| qa | Challenge a contract: target, declared invariant | `loop-test-adversarial` | isolated positive/negative controls |
| incident | Assess an incident: symptoms, impact, timestamps | `loop-workflow-incident` | impact and next safe investigation |
| work | Complete a task: desired artifact, constraints, sources | `loop-work` | feasible checkpoint and required inputs |
| files | Organize files: exact root, desired arrangement | `loop-files` | inventory and reviewable move plan |
| documents | Produce a file: format, audience, supplied content | `loop-document` | document artifact and format checks |
| data | Analyze a table: input, column meaning, question | `loop-table` | validated table assessment and totals |
| support | Triage tickets: ticket text, supplied policies | `loop-support` | provisional categories and draft replies; use `loop-intake` if scope is unclear |
| knowledge | Maintain FAQ: sources, revisions, intended readers | `loop-knowledge` | source-linked entries and unresolved conflicts |

## Four worked request examples

These are illustrative expected outputs, not additional recorded model trials.
For actual executions see [the evidence map](../EVIDENCE.md#behavioral-evidence).

### Developer: add JSON export

Request: `$loop-code add JSON export to the existing CSV CLI, preserving IDs as
strings; leave CSV behavior unchanged.` Supply the repository and sample input
`id,amount` / `001,3.50`. Start with `loop-code`; use `loop-test` only if the test
strategy is unclear. Expected JSON includes `"id": "001"`; amount representation
must follow an explicit agreed schema. Check the actual CLI output, invalid input,
and existing CSV behavior. A passing helper test alone is insufficient.

### Office: prepare an event packet

Request: `$loop-work prepare a briefing and checklist from this event brief;
the budget is 200 EUR and the venue is pending. Save drafts locally.` Start with
`loop-work`, then `loop-document` if a document file is required. Expected packet
contains the budget, a pending venue decision and feasible next tasks. Compare
every date/cost/owner with sources and open the produced artifact. Do not invent
bookings or mark invitations sent. Missing event date remains unknown.

### Support: unknown cause and refund authority

Request: `$loop-support triage these tickets and draft replies: T1 export failed
once; T2 requests a refund. No SLA or refund approval was supplied.` Expected
output keeps T1's cause provisional and T2's approval unknown, with two unsent
drafts. Check IDs, source references, absence of invented owner/ETA and no claim
of resolution or sending. The [historical support trial](../EVIDENCE.md#behavioral-evidence)
provides a separately retained execution of a related fixture.

### Knowledge: contradictory policies

Request: `$loop-knowledge build a FAQ draft: policy A says refunds within 14 days,
policy B says 30 days; revision dates are unknown.` Expected draft cites both,
flags the conflict and requests authoritative revision information. Check both
periods survive and no policy is silently selected or publication claimed. Compare
the [retained conflicting-policy output](../EVIDENCE.md#readable-example-conflicting-policies).
