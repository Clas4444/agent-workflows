---
name: loop-diagnose-repro
description: "Run a bounded reproduction loop for a bug or failure: capture the environment, minimize the reproducer, vary one factor at a time, and preserve exact evidence for a later fix."
argument-hint: "[duration, symptom, and reproducer target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Diagnose Repro

Capture symptom, environment, exact command, expected/actual result, logs, and
reproduction rate. Minimize the reproducer without hiding the failure and vary
one factor at a time. Record hypothesis, evidence, confidence, and
`PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`. Do not fix target code unless
authorized. Consolidate and stop when no new experiment remains or materially
identical evidence repeats more than three times; never sleep.
