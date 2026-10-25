---
name: loop-workflow-project
description: "Turn an authorized small-project idea into an incremental delivery workflow with an MVP boundary, acceptance backlog, first verified slice and resumable state. Use for a new project lifecycle, not a single code change."
argument-hint: "[project goal, constraints, and permitted delivery scope]"
user-invocable: true
disable-model-invocation: false
---

# Loop Workflow Project

## Use when

Coordinate a small project's path from an idea to independently verified slices.
Use loop-plan when only a plan is wanted and loop-code for one implementation
batch. Do not expand a narrow feature request into a whole-project workflow.

## Inputs

Users/problem, desired outcome, existing repository, constraints and authorized
delivery scope. Missing product decisions remain TBD. If duration is omitted,
the scoped delivery is the bound; reuse authorization already given.

## Workflow

1. Establish the smallest useful outcome, explicit non-goals and observable
   acceptance IDs. Inspect existing code before assuming a greenfield project.
2. Create a dependency-ordered backlog of small end-to-end slices. Separate
   assumptions from approved decisions and record the source of critical context.
3. Select the next feasible slice and its verification gate. If implementation
   is authorized, implement and test that slice; otherwise deliver the backlog
   and mark execution NOT_RUN. Do not fabricate a baseline for an empty project.
4. Inspect the diff and actual user-visible behavior before marking a slice done.
   Reuse focused planning/code/test/review skills when available; the same gates
   still apply when those skills are not installed. Do not launch agents implicitly.
5. Leave a checkpoint with completed/remaining acceptance IDs, actual evidence,
   open decisions and one next bounded action. Publish/deploy only within existing
   authorization; a working prototype does not prove production readiness.

## Output

MVP boundary, acceptance backlog, one scoped result or plan-only handoff, tests,
risks and next action. Per gate distinguish PASS, FAIL, BLOCKED and NOT_RUN;
backlog completion is not inferred from code volume or a generated scaffold.

## Boundaries and evidence

Do not choose a paid service, install dependencies, create remote resources or
publish without the relevant authorization. Preserve unrelated work and failed
attempts. Stop when the agreed slice is complete, no useful work remains, the
user/deadline ends work or a safety boundary is reached. Never sleep to consume time.

## Example

```text
/loop-workflow-project scope a local inventory MVP and deliver one authorized, tested slice
```

Adapt invocation syntax to the host; this is a coordination workflow, not a service.
