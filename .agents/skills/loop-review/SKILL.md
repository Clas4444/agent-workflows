---
name: loop-review
description: "Inspect a scoped change or repository and report prioritized findings with source evidence. Use for review; use loop-plan for planning, loop-evaluate for fixed-rubric scoring and loop-research workflows for adoption decisions."
argument-hint: "[duration and target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Review

## Use when

Evaluate a file, folder, project, repository, or workspace and report verified
findings. This workflow may make only explicitly authorized safe edits.

## Inputs

Target path or revision, review criteria and authorized changes.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

1. Parse the review target and optional positive duration; create a run ID.
   Set a deadline only when a duration was supplied; otherwise use task completion.
2. Read repository instructions, status, prior checkpoints, and relevant tests.
3. Review one distinct angle at a time: correctness, tests, docs/config,
   build/release, integrations, security/privacy, usability, or hygiene.
4. Record evidence, risk, priority (`P0`–`P3`), authorization, action, and
   verification. Inspect every diff.
5. Separate observed defects, design tradeoffs and untested hypotheses. Give
   each actionable finding a source location and a verification path; do not
   invent findings to fill a quota. Route implementation or research only when
   the user's scope calls for it, and preserve read-only review requests.

## Output

Prioritized findings with source locations, risk, checked evidence and unresolved gaps.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Do not invent support, install tools, expose private data, or change files
outside the requested scope. Each checkpoint records elapsed/requested time,
angle, evidence, finding, action, verification, and next angle. Report
`PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Stop when no suitable work remains, the deadline or user request ends the run, a
safety boundary is reached, or materially identical results recur more than
three times. Never sleep to consume time. Write the consolidated report under
the configured report directory, or `<workspace>/Markdown` when none exists.

## Example

```text
/loop-review 10m review this repository before adoption
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
