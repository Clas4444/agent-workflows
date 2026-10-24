---
name: loop-code
description: "Run a bounded code implementation loop for a feature, refactor, bug fix, or configuration change: plan a small batch, edit, verify, inspect the diff, and repeat. Use when the user asks to implement code iteratively."
argument-hint: "[duration, target, and requested change]"
user-invocable: true
disable-model-invocation: false
---

# Loop Code

## Use when

Implement an authorized feature, fix, refactor, or configuration change in
small verified batches.

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
3. Implement one small reversible batch while preserving unrelated changes.
4. Run the smallest relevant checks, then the project gate when needed.
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
