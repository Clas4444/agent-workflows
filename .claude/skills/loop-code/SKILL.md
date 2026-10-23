---
name: loop-code
description: "Run a bounded code implementation loop for a feature, refactor, bug fix, or configuration change: plan a small batch, edit, verify, inspect the diff, and repeat. Use when the user asks to implement code iteratively."
argument-hint: "[duration, target, and requested change]"
user-invocable: true
disable-model-invocation: false
---

# Loop Code

Parse duration, target, requested outcome, run ID, and authorization. Read project
instructions, status, patterns, tests, and acceptance criteria. Implement one
small reversible batch at a time, preserving unrelated changes. Ask before
behavior, dependency, permission, or data-scope changes. Inspect every diff and
run bounded relevant checks plus the standard gate when available. Record
`PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`; never weaken tests or install tools
without authorization.

Checkpoint each batch with evidence, files, verification, and next batch. If no
authorized work remains, or materially identical results occur more than three
times consecutively, write a consolidated report and stop. Never sleep to consume
the duration. Stop on deadline, user request, missing authorization/decision, or
a safety/privacy boundary.
