---
name: loop-diagnose-regression
description: "Run a bounded regression-diagnosis loop: compare a known-good and failing state, bisect or narrow the change set, reproduce the regression, and verify the smallest authorized fix."
argument-hint: "[duration and regression target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Diagnose Regression

Record known-good and failing versions, environment, reproduction command, and
expected behavior. Compare changes or bisect only when safe and authorized.
Preserve unrelated worktree changes and avoid destructive history operations.
Record candidate change, evidence, confidence, and `PASS`, `FAIL`, `BLOCKED`, or
`NOT_RUN`. Consolidate and stop when no new comparison remains or materially
identical evidence repeats more than three times; never sleep.
