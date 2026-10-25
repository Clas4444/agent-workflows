# Work ledger

Use a small ledger when the task spans multiple deliverables or sessions. Keep it
in the requested format; the JSON asset is a starting structure, not a required
service or proof of completion.

- Outcome and done criteria: observable artifacts/decisions, not activity counts.
- Scope: permitted files/actions, exclusions and existing authority.
- Sources: location/date or hash, relevant fact and uncertainty.
- Work items: ID, dependency, estimated effort, hard deadline/time zone when known,
  owner when explicit, state and acceptance evidence.
- Capacity: available time, assumptions and overloads; estimated effort is not a
  calendar reservation. Do not fill unknown availability with invented free slots.
- Checkpoint: completed/remaining criteria, source/artifact identities, actual
  checks and one next permitted action. Preserve failed attempts and blockers.

Useful work states are proposed, ready, in progress, blocked and done. These are
not interchangeable with check outcomes PASS/FAIL/BLOCKED/NOT_RUN. A blocked task
may have a PASS prerequisite check; a completed draft may have delivery NOT_RUN.

Only classify an item done when its defined outcome is observed. If asked for a
plan only, return a concrete plan and mark production/external actions NOT_RUN.
If an authorized document is requested, create and inspect the actual file rather
than replacing it with a suggestion to create one later.

Keep dependency IDs stable across updates. A missing dependency or cycle blocks
readiness; it is not proof of completion. Record which source IDs a done criterion
depends on so an observed source revision change can trigger targeted revalidation.
Do not infer that every old criterion failed just because one input changed.
