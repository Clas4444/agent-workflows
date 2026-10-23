---
name: loop-review
description: "Run a bounded review loop over a file, folder, project, repository, or workspace: evaluate, discover integrations, propose, make authorized safe changes, verify, and report. Use when the user asks for repeated review or evaluation."
argument-hint: "[duration and target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Review

Parse one positive duration and target, create a run ID/deadline, read applicable
instructions and prior checkpoints, then review one angle per iteration:
correctness, tests, docs/config, build/release, integrations, security/privacy,
usability, and hygiene. Discover existing tools before proposing additions.
Rank findings P0-P3, record evidence/risk/authorization/verification, edit only
authorized files, inspect diffs, and record `PASS`, `FAIL`, `BLOCKED`, or
`NOT_RUN`.

Each iteration checkpoint includes run ID, status, elapsed/requested, angle,
evidence, finding, action, verification, and next angle. Do not repeat an angle
without new evidence. If no suitable work remains, or materially identical
findings occur more than three consecutive times, write the consolidated report
and stop. Never sleep just to consume duration. Stop also on user request,
missing authorization/decision, or a safety/privacy boundary.

Write primary reports under a configured report directory when one is
available; otherwise use `<workspace>/Markdown`. On the original Windows
workspace, `C:\Code\Markdown` remains the default for targets under `C:\Code`.
