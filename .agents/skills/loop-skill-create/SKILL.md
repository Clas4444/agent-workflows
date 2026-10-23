---
name: loop-skill-create
description: "Create or maintain an agent skill through requirements, reusable-pattern inspection, synchronized editing, focused tests, documentation, and evidence review. Use when adding or changing a SKILL.md workflow."
argument-hint: "[duration, skill name, and requested behavior]"
user-invocable: true
disable-model-invocation: false
---

# Loop Skill Create

## Use when

Create or maintain a synchronized `SKILL.md` workflow without duplicating an
existing responsibility.

## Workflow

Extract behavior, target hosts, scope, authorization, acceptance criteria, and
expected evidence. Inspect the manifest, `CONTRIBUTING.md`, validation docs,
and related skills. Edit `.github/skills/<skill-name>/SKILL.md`, then copy it
exactly to `.agents/skills/` and `.claude/skills/`.

Validate metadata, prerequisites, permitted actions, constraints, outputs,
bounded work, verification, stop conditions, and all four statuses. Add focused
positive and negative tests when the validator supports them. Update
documentation and generated evidence only when the verification surface changes.

## Boundaries and evidence

Do not add a duplicate workflow, dependency, host-compatibility claim, or
permission without authorization and evidence. Review the final diff for
unrelated edits. Record command, result, revision, limitations, and next action
as `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Stop when no suitable work remains, the deadline or user request ends the run,
a safety boundary is reached, or materially identical findings recur more than
three times. Never sleep to consume time or sleep to consume duration; write a
consolidated report.
