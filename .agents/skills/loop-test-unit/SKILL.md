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

## Inputs

Target unit, test runner, expected behavior and isolation requirements.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

Identify the unit-test runner, baseline command, target unit, and test risk.
Run the smallest bounded test. Record the command, exit code, failure evidence,
assertions changed, and next hypothesis.

## Output

Focused assertions and commands covering the behavior and relevant failure cases.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Change tests or fixtures only when authorized and never weaken assertions.
Report `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Stop when no suitable work remains, the deadline or user request ends the
run, a safety boundary is reached, or materially identical results recur more
than three times. Never sleep to consume time; write a consolidated report.

## Example

```text
/loop-test-unit 10m test parser marker handling in isolation
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
