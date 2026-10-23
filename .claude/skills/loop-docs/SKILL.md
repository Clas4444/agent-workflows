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

## Inputs

Audience, documentation paths, desired correction and source-of-truth files.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

Map the audience and documentation surface. Check accuracy, completeness,
examples, links, terminology, localization, and generated-output consistency.
Trace claims to source code or authoritative references. Make only scoped
authorized edits and verify commands, links, and formatting where possible.

## Output

Accurate scoped documentation diff, checked commands/links and remaining uncertainty.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Preserve uncertainty and distinguish `PASS`, `FAIL`, `BLOCKED`, and `NOT_RUN`.
Record evidence, changed files, verification, and the next angle.

Stop when no useful angle remains, the deadline or user request ends the run, a
safety boundary is reached, or materially identical findings recur more than
three times. Never sleep to consume time; write a consolidated report.

## Example

```text
/loop-docs 10m align the usage guide with the current manifest
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
