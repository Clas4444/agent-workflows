---
name: loop-test-unit
description: "Run a bounded unit-test loop for a module or function: select focused tests, reproduce failures, improve authorized tests or fixtures, and verify isolated behavior without weakening acceptance criteria."
argument-hint: "[duration and unit-test target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Test Unit

Identify the unit-test runner, baseline command, target unit, and test risk.
Run the smallest focused test with a bounded command. Record command, exit code,
failure evidence, and `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`. Change tests or
fixtures only with authorization and never weaken assertions. Checkpoint each
distinct hypothesis. If no new unit-test angle remains or results materially
repeat more than three times, write the consolidated report and stop; never sleep.
