---
name: loop-docs
description: "Run a bounded documentation loop: audit README, guides, API references, examples, localization, and generated documentation; propose or make authorized updates; verify links and consistency. Use when the user asks to improve docs repeatedly."
argument-hint: "[duration and documentation target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Docs

## Use when

Audit or improve a README, guide, API reference, example, localization, or
generated document.

## Workflow

Map the audience and documentation surface. Check accuracy, completeness,
examples, links, terminology, localization, and generated-output consistency.
Trace claims to source code or authoritative references. Make only scoped
authorized edits and verify commands, links, and formatting where possible.

## Boundaries and evidence

Preserve uncertainty and distinguish `PASS`, `FAIL`, `BLOCKED`, and `NOT_RUN`.
Record evidence, changed files, verification, and the next angle.

Stop when no useful angle remains, the deadline or user request ends the run, a
safety boundary is reached, or materially identical findings recur more than
three times. Never sleep to consume time; write a consolidated report.
