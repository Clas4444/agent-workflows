---
name: loop-diagnose
description: "Run a bounded diagnosis loop for a bug, crash, failing test, regression, or slow behavior: reproduce, isolate, test hypotheses, fix when authorized, and re-test. Use when the user asks to debug or diagnose repeatedly."
argument-hint: "[duration, symptom, and target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Diagnose

Capture the exact failure, environment, command, exit code, logs, and
reproduction. Maintain a hypothesis table and change one variable at a time.
Prefer the smallest reproducer and relevant regression test. Fix only with
authorization, then rerun the reproducer and regression checks. Keep failures
visible and record `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Checkpoint every experiment with evidence, hypothesis, action, verification, and
next test. If no new experiment remains, or materially identical evidence occurs
more than three consecutive times, write the consolidated report and stop. Never
sleep to consume duration; also stop on deadline, user request, missing
authorization/decision, or a safety/privacy boundary.
