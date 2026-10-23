---
name: loop-test-coverage
description: "Run a bounded test-coverage loop: identify untested risk, inspect coverage evidence, add authorized focused tests, and verify that coverage improvements are meaningful rather than cosmetic."
argument-hint: "[duration and coverage target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Test Coverage

Identify the coverage tool, baseline, critical paths, and measurable threshold
from project evidence. Separate line, branch, path, and mutation evidence.
Add only authorized tests; do not change thresholds or exclude code to create a
false PASS. Record command, metric, exit code, and `PASS`, `FAIL`, `BLOCKED`, or
`NOT_RUN`. Stop and consolidate when no new risk remains or results repeat more
than three times; never sleep.
