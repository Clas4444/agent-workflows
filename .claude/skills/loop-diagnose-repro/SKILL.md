---
name: loop-diagnose-repro
description: "Run a bounded reproduction loop for a bug or failure: capture the environment, minimize the reproducer, vary one factor at a time, and preserve exact evidence for a later fix."
argument-hint: "[duration, symptom, and reproducer target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Diagnose Repro

## Use when

Turn a bug or failure into a small, repeatable reproducer for later diagnosis
or repair.

## Workflow

Record the symptom, environment, exact command, expected and actual results,
logs, and reproduction rate. Minimize the case without hiding the failure and
vary one factor at a time. Record each hypothesis, evidence, and confidence.

## Boundaries and evidence

Do not fix target code unless authorized. Protect sensitive logs and preserve
the exact reproducer. Report `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Stop when no suitable work remains, the deadline or user request ends the run,
a safety boundary is reached, or materially identical results recur more than
three times. Never sleep to consume time; write a consolidated report.
