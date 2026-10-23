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

## Workflow

Record both versions, the environment, reproduction command, and expected
behavior. Narrow the change set or bisect only when safe and authorized. Record
each candidate change, evidence, confidence, and verification.

## Boundaries and evidence

Preserve unrelated worktree changes and never use destructive history commands.
Report `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`. Do not claim a regression is
fixed without rerunning the reproducer.

Stop when no suitable work remains, the deadline or user request ends the run,
a safety boundary is reached, or materially identical evidence recurs more than
three times. Never sleep to consume time; write a consolidated report.
