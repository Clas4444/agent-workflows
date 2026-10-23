---
name: loop-test-coverage
description: "Run a bounded test-coverage loop: identify untested risk, inspect coverage evidence, add authorized focused tests, and verify that coverage improvements are meaningful rather than cosmetic."
argument-hint: "[duration and coverage target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Test Coverage

## Use when

Find and reduce important untested risk with meaningful focused tests.

## Inputs

Critical behavior, existing coverage tool and any project-defined thresholds.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

Identify the coverage tool, baseline, critical paths, and measurable threshold
from project evidence. Separate line, branch, path, and mutation evidence.
Add only authorized tests and record the command, metric, exit code, and result.

## Output

Measured coverage type and baseline, risk-based gaps and verified focused additions.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Do not change thresholds or exclude code to create a false `PASS`. Report
`PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Stop when no suitable work remains, the deadline or user request ends the run, a
safety boundary is reached, or materially identical results recur more than
three times. Never sleep to consume time; write a consolidated report.

## Example

```text
/loop-test-coverage 15m inspect untested timeout and persistence paths
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
