---
name: loop-review
description: "Run a bounded review loop over a file, folder, project, repository, or workspace: evaluate, discover integrations, propose, make authorized safe changes, verify, and report. Use when the user asks for repeated review or evaluation."
argument-hint: "[duration and target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Review

## Use when

Evaluate a file, folder, project, repository, or workspace and report verified
findings. This workflow may make only explicitly authorized safe edits.

## Workflow

1. Parse one positive duration and the review target; create a run ID and
   deadline.
2. Read repository instructions, status, prior checkpoints, and relevant tests.
3. Review one distinct angle at a time: correctness, tests, docs/config,
   build/release, integrations, security/privacy, usability, or hygiene.
4. Record evidence, risk, priority (`P0`–`P3`), authorization, action, and
   verification. Inspect every diff.

## Boundaries and evidence

Do not invent support, install tools, expose private data, or change files
outside the requested scope. Each checkpoint records elapsed/requested time,
angle, evidence, finding, action, verification, and next angle. Report
`PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Stop when no suitable work remains, the deadline or user request ends the run, a
safety boundary is reached, or materially identical results recur more than
three times. Never sleep to consume time. Write the consolidated report under
the configured report directory, or `<workspace>/Markdown` when none exists.
