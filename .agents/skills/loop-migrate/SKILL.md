---
name: loop-migrate
description: "Prepare and verify a scoped data, schema or configuration migration with dry-run, backup, invariants, idempotence and rollback. Use when stored state or format changes, not for behavior-preserving refactors."
argument-hint: "[duration, target, and acceptance criteria]"
user-invocable: true
disable-model-invocation: false
---

# Loop Migrate

## Use when

Change persisted state or its representation in a controlled migration. Use loop-refactor when external behavior and data formats must remain unchanged.

## Inputs

Source/target schema, representative fixtures, invariants, authorized write scope and rollback requirements.
If duration is omitted, the authorized task scope is the bound. Reuse existing
authorization; clarify only prerequisites that prevent safe progress.

## Workflow

1. Inventory source state and target schema. Define invariants such as record
   count, stable identifiers and value preservation; capture the baseline.
2. Prepare a dry-run that validates proposed changes without writing. Identify
   malformed/unsupported input and fail before touching original data.
3. Implement or inspect the smallest migration and backup strategy. Use copied
   local fixtures first; never treat a fixture success as production approval.
4. Verify dry-run leaves bytes unchanged, migration preserves invariants and a
   repeated run is idempotent. Retain a byte-identical original backup.
5. Exercise rollback on a disposable copy and verify restoration against the
   baseline. Report counts, commands, checksums, rejected inputs and limits.

## Output

Migration/dry-run results, invariants, before/after checksums, backup, idempotence and exercised rollback evidence.
Report PASS for verified acceptance, FAIL for a failed check, BLOCKED for an
unavailable required prerequisite and NOT_RUN for checks not executed.

## Boundaries and evidence

Do not migrate shared or production data, destroy backups or widen schema scope without authorization. Missing safe rollback or required access is BLOCKED; an unexercised rollback remains NOT_RUN.
Preserve unrelated work. Stop when no suitable work remains, the deadline or
user request ends the run, a safety boundary is reached, or materially identical
results recur more than three times. Never sleep to consume time. Write a
consolidated report with evidence, changes, limitations and next action.

## Example

```text
/loop-migrate 20m migrate local JSON fixtures from schema v1 to v2 with rollback
```

Adapt invocation syntax to the host; an example does not prove native discovery.
