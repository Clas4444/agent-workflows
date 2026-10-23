---
name: loop-debug
description: "Repair a reproducible bug end to end: capture a failing test, isolate the cause, apply the smallest authorized fix, and rerun regression checks. Use when the user wants a bug fixed, rather than diagnosis alone."
argument-hint: "[duration, symptom, target, and expected behavior]"
user-invocable: true
disable-model-invocation: false
---

# Loop Debug

## Use when

The user requests a fix for a specific bug. Use loop-diagnose for investigation
without repair, or loop-diagnose-repro when only a minimal reproducer is needed.

## Inputs

Bug symptom, target, expected behavior, available failing case and repair authorization.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

1. Read repository instructions, worktree status, symptom and expected behavior.
   Record the environment, exact failing command, exit code and relevant logs.
2. Reproduce the failure before editing; add a focused regression test when
   authorized. Distinguish a command not executed (NOT_RUN) from an executed
   attempt where the symptom did not appear. Record the observed result and
   reproduction rate; fix verification remains NOT_RUN without a demonstrated
   failing baseline. Investigate one variable at a time rather than claiming a fix.
3. Keep a hypothesis table with evidence and confidence. Isolate the cause and
   apply one small reversible fix within the user's scope.
4. Run the original reproducer and the focused test, then relevant project gates.
   Inspect the diff and verify the fix did not merely hide the symptom.
5. Report root cause, changed files, before/after commands, results, remaining
   risks and next action. A patch without verification is not PASS.

## Output

Failing baseline, root cause, minimal fix, regression results and remaining risk.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Do not weaken assertions, swallow unexpected errors, expose sensitive logs,
install dependencies, or change unrelated behavior without authorization.
Preserve unrelated work. Report PASS, FAIL, BLOCKED or NOT_RUN per check.

Stop when no suitable work remains, the deadline or user request ends the run,
a safety boundary is reached, or materially identical results recur more than
three times. Never sleep to consume time; write a consolidated report.

## Example

```text
/loop-debug 15m fix valid markers being lost after large output
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
