---
name: loop-test
description: "Select and execute a risk-based test strategy for a project or change when the required test layer is not yet known. Use focused unit, integration, E2E, coverage, adversarial or compatibility skills when that layer is already the main request."
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

1. Identify acceptance criteria, project gates, environment and the risk that
   each check must distinguish. Select the needed test layers before running.
2. Establish the smallest relevant baseline and include valid/invalid controls
   where applicable. Broaden when failures or untested boundaries justify it.
3. Inspect actual assertions and artifacts, not only the command's self-reported
   PASS. Keep unit, CLI, model/host and remote evidence separate.
4. Record commands, exit codes, failures, changed assertions and next action.
   Missing prerequisites are BLOCKED or NOT_RUN according to what was attempted;
   do not install or weaken gates merely to obtain a green report.
5. Trace results to stable acceptance IDs and the context revision/hash used.
   For executable contracts use the repository's `docs/ACCEPTANCE-GATE.md` when
   available. A zero exit alone, zero collected tests, an expected rejection
   caused by a missing executable, or a timeout cannot prove acceptance. Keep
   planned checks NOT_RUN and stale/missing context BLOCKED. After changing a
   checker, exercise a controlled failure to show it can reject bad behavior.

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
