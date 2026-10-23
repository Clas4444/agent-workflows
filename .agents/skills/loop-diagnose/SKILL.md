---
name: loop-diagnose
description: "Run a bounded diagnosis loop for a bug, crash, failing test, regression, or slow behavior: reproduce, isolate, test hypotheses, fix when authorized, and re-test. Use when the user asks to debug or diagnose repeatedly."
argument-hint: "[duration, symptom, and target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Diagnose

## Use when

Investigate a bug, crash, failing test, regression, or slow behavior that needs
reproduction and isolation.

## Workflow

Capture the exact symptom, environment, command, exit code, logs, and
reproduction. Maintain a hypothesis table and change one variable at a time.
Prefer the smallest reproducer and the most relevant regression test. Fix only
when authorized, then rerun the reproducer and regression checks.

## Boundaries and evidence

Keep failures visible. Each experiment records its hypothesis, evidence, action,
verification, and next test. Report `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.
Protect credentials and private data; do not install tools or change unrelated
files.

Stop when no suitable work remains, the deadline or user request ends the run,
a safety boundary is reached, or materially identical evidence recurs more than
three times. Never sleep to consume time. Write a consolidated report.
