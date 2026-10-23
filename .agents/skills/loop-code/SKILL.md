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

## Workflow

1. Parse the positive duration, target, requested outcome, run ID, and
   authorization.
2. Read project instructions, worktree status, existing patterns, tests, and
   acceptance criteria.
3. Implement one small reversible batch while preserving unrelated changes.
4. Run the smallest relevant checks, then the project gate when needed.
5. Inspect the diff and record changed files, evidence, verification, and the
   next batch.

## Boundaries and evidence

Ask before changing behavior, dependencies, permissions, or data scope. Do not
install tools or weaken tests without authorization. Report `PASS`, `FAIL`,
`BLOCKED`, or `NOT_RUN`.

Stop when authorized work ends, the deadline or user request ends the run, a
safety boundary is reached, or materially identical results recur more than
three times. Never sleep to consume time. Write a consolidated report before
stopping.
