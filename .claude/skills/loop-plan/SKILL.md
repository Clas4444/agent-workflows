---
name: loop-plan
description: "Turn a scoped request into dependency-ordered, verifiable implementation batches without changing code. Use before multi-step work when acceptance criteria, risks or sequencing need definition."
argument-hint: "[duration, target, and acceptance criteria]"
user-invocable: true
disable-model-invocation: false
---

# Loop Plan

## Use when

Plan a multi-step change before implementation. Use loop-code to execute an agreed batch; loop-review evaluates an existing target rather than decomposing a new request.

## Inputs

Requested outcome, target, existing constraints, user authorization and any deadline.
If duration is omitted, the authorized task scope is the bound. Reuse existing
authorization; clarify only prerequisites that prevent safe progress.

## Workflow

1. Inspect the target and project instructions; distinguish stated requirements
   from assumptions. Reuse existing authorization rather than asking again.
2. Define observable acceptance criteria and explicit out-of-scope behavior.
   Give criteria stable IDs; separate the problem, supporting evidence and
   falsifiable outcome (what/why) from architecture and implementation (how).
   Keep unknown requirements as TBD; conflicting requirements stay unresolved
   until the user or authoritative evidence resolves them. Never invent answers.
3. Break work into small dependency-ordered batches. For each batch name files
   or components, expected behavior, verification command and completion gate.
4. Identify uncertain prerequisites, risky state changes, rollback points and
   the smallest experiment needed before dependent work can begin.
5. Write a plan with priorities and next action. Do not silently implement it.
   Mark assumptions and prerequisites separately from executed verification.
6. Map each criterion to positive and negative controls before implementation.
   Record context paths, revisions and hashes; recheck them at handoff. For
   executable contracts use the repository's `docs/ACCEPTANCE-GATE.md` when
   available; planned checks remain NOT_RUN, not evidence of working behavior.

## Output

A dependency-ordered plan with acceptance criteria, verification gates, risks, rollback and scope.
Report PASS for verified acceptance, FAIL for a failed check, BLOCKED for an
unavailable required prerequisite and NOT_RUN for checks not executed.

## Boundaries and evidence

Planning does not authorize implementation, installation, deployment or wider data access. Missing critical requirements are BLOCKED; planned tests remain NOT_RUN until executed.
Preserve unrelated work. Stop when no suitable work remains, the deadline or
user request ends the run, a safety boundary is reached, or materially identical
results recur more than three times. Never sleep to consume time. Write a
consolidated report with evidence, changes, limitations and next action.

## Example

```text
/loop-plan 10m plan a validated JSON export command without implementing it
```

Adapt invocation syntax to the host; an example does not prove native discovery.
