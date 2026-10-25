---
name: loop-code
description: "Implement an authorized feature or configuration change in small verified batches. Prefer loop-debug when the main goal is repairing a reproducible bug and loop-refactor when the goal is restructuring without changing behavior."
argument-hint: "[duration, target, and requested change]"
user-invocable: true
disable-model-invocation: false
---

# Loop Code

## Use when

Implement an authorized feature, fix, refactor, or configuration change in
small verified batches.
For a dedicated reproducible repair or behavior-preserving restructuring,
prefer loop-debug or loop-refactor. An explicit invocation still keeps the
user's authorized implementation scope; routing does not grant extra actions.

## Inputs

Target, desired behavior, acceptance criteria and permitted implementation scope.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

1. Parse target, requested outcome, run ID, existing authorization and optional
   positive duration. Omitted duration means stop at scoped task completion.
2. Read project instructions, worktree status, existing patterns, tests, and
   acceptance criteria.
   Keep stable criterion IDs and distinguish user intent from design choices.
   Recheck the source ledger at handoff; changed context requires reassessment,
   not reuse of old PASS. Preserve TBD requirements instead of inventing them.
3. Implement one small reversible batch while preserving unrelated changes.
4. Run the smallest relevant checks, then the project gate when needed.
   Map results to the agreed criteria, including positive and negative controls.
   For executable contracts use the repository's `docs/ACCEPTANCE-GATE.md` when
   available. Do not change expected outcomes merely to match observed output.
5. Inspect the diff and record changed files, evidence, verification, and the
   next batch.

## Output

Small implementation diff, verification commands and results, remaining work.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Stay within authorized behavior, dependencies, permissions and data scope; ask
only when the next action would exceed that existing authorization. Do not
install tools or weaken tests without authorization. Report `PASS`, `FAIL`,
`BLOCKED`, or `NOT_RUN`.

Stop when authorized work ends, the deadline or user request ends the run, a
safety boundary is reached, or materially identical results recur more than
three times. Never sleep to consume time. Write a consolidated report before
stopping.

## Example

```text
/loop-code 15m add strict validation for parser input
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
