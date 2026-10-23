---
name: loop-diagnose-regression
description: "Run a bounded regression-diagnosis loop: compare a known-good and failing state, bisect or narrow the change set, reproduce the regression, and verify the smallest authorized fix."
argument-hint: "[duration and regression target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Diagnose Regression

## Use when

Compare a known-good state with a failing state to isolate a regression and
verify the smallest authorized fix.

## Inputs

Known-good and failing revisions, expected behavior and reproduction command.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

Record both versions, the environment, reproduction command, and expected
behavior. Narrow the change set or bisect only when safe and authorized. Record
each candidate change, evidence, confidence, and verification.

## Output

Version comparison, narrowed change set, confidence and rerun evidence.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Preserve unrelated worktree changes and never use destructive history commands.
Report `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`. Do not claim a regression is
fixed without rerunning the reproducer.

Stop when no suitable work remains, the deadline or user request ends the run,
a safety boundary is reached, or materially identical evidence recurs more than
three times. Never sleep to consume time; write a consolidated report.

## Example

```text
/loop-diagnose-regression 15m isolate the regression between the supplied revisions
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
