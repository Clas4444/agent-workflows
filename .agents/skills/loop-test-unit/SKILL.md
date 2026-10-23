---
name: loop-test-unit
description: "Run a bounded unit-test loop for a module or function: select focused tests, reproduce failures, improve authorized tests or fixtures, and verify isolated behavior without weakening acceptance criteria."
argument-hint: "[duration and unit-test target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Test Unit

## Use when

Verify one module or function in isolation with focused unit tests.

## Workflow

Identify the unit-test runner, baseline command, target unit, and test risk.
Run the smallest bounded test. Record the command, exit code, failure evidence,
assertions changed, and next hypothesis.

## Boundaries and evidence

Change tests or fixtures only when authorized and never weaken assertions.
Report `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Stop when no suitable work remains, the deadline or user request ends the
run, a safety boundary is reached, or materially identical results recur more
than three times. Never sleep to consume time; write a consolidated report.
