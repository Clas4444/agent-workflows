---
name: loop-diagnose
description: "Investigate an unexplained symptom using competing hypotheses and discriminating experiments. Use for diagnosis without an assumed repair; prefer loop-debug for a requested fix, loop-diagnose-repro for minimization and the focused performance/regression routes when those are the goal."
argument-hint: "[duration, symptom, and target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Diagnose

## Use when

Investigate a bug, crash, failing test, regression, or slow behavior that needs
reproduction and isolation.
For an explicit end-to-end bug-fix request, prefer loop-debug, which requires
a failing baseline, an authorized repair and a verified regression test.

## Inputs

Symptom, target, expected behavior and available reproduction details.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

1. Capture the symptom, environment, exact command, exit code and logs. Record
   reproduction frequency; an executed attempt without the symptom is not the
   same as a command that was NOT_RUN.
2. Maintain competing hypotheses with supporting/contradicting evidence and
   choose the smallest experiment that distinguishes them. Change one variable
   at a time and avoid prematurely treating correlation as cause.
3. Stop with an isolated cause or the next useful experiment. If an authorized
   repair becomes the goal, carry the failing baseline into loop-debug rather
   than silently turning a read-only investigation into implementation.

## Output

Hypothesis table, exact reproducer, isolated cause or next discriminating experiment.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Keep failures visible. Each experiment records its hypothesis, evidence, action,
verification, and next test. Report `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.
Protect credentials and private data; do not install tools or change unrelated
files.

Stop when no suitable work remains, the deadline or user request ends the run,
a safety boundary is reached, or materially identical evidence recurs more than
three times. Never sleep to consume time. Write a consolidated report.

## Example

```text
/loop-diagnose 10m investigate intermittent parser failure without editing code
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
