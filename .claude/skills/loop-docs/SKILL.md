---
name: loop-docs
description: "Run a bounded documentation loop: audit README, guides, API references, examples, localization, and generated documentation; propose or make authorized updates; verify links and consistency. Use when the user asks to improve docs repeatedly."
argument-hint: "[duration and documentation target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Docs

Map the documentation surface and audience, then inspect one angle at a time:
accuracy, completeness, examples, links, terminology, localization, and
generated-output consistency. Trace claims to source code or authoritative
references. Make only scoped authorized edits and verify links, formatting, and
commands where possible.

Checkpoint evidence, changed files, verification, and next angle. If no useful
angle remains, or materially identical findings occur more than three consecutive
times, write the consolidated report and stop. Never sleep to consume duration.
Record documentation checks as `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`; missing
link or rendering tools are not PASS.
