---
name: loop-test
description: "Run a bounded testing loop for a project or change: select tests, reproduce failures, improve coverage or fixtures when authorized, run checks, and report results. Use when the user asks to test repeatedly or improve verification."
argument-hint: "[duration and target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Test

## Use when

Select, run, or improve a bounded test strategy for a project or change.

## Inputs

Project or change, acceptance criteria, known test commands and permitted fixture edits.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

Identify the project test gate, baseline command, environment, and target risk.
Run the smallest relevant test first, then broaden only when evidence requires
it. Record the command, exit code, failure evidence, coverage gap, action, and
next test.

## Output

Test selection, commands, exit codes, failure evidence and unverified risks.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Change tests or fixtures only with authorization. Never weaken assertions or
accept a missing tool as `PASS`. Report `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Stop when no suitable work remains, the deadline or user request ends the run,
a safety boundary is reached, or materially identical results recur more than
three times. Never sleep to consume time; write a consolidated report.

## Example

```text
/loop-test 10m verify the current parser change
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
