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

## Inputs

Requested workflow, target hosts, responsibility boundary and acceptance criteria.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

Extract behavior, target hosts, scope, authorization, acceptance criteria, and
expected evidence. Inspect the manifest, `CONTRIBUTING.md`, validation docs,
and related skills. Edit `.github/skills/<skill-name>/SKILL.md`, then copy it
exactly to `.agents/skills/` and `.claude/skills/`.

When research informs a change, keep primary-source links, inspected revision
and the specific design decision they support. Separate reported experimental
results from applicability to this repository; do not copy benchmark claims into
runtime support claims. Compare nearby skill responsibilities before adding one.

Validate metadata, prerequisites, permitted actions, constraints, outputs,
bounded work, verification, stop conditions, and all four statuses. Add focused
positive and negative tests when the validator supports them. Update
documentation and generated evidence only when the verification surface changes.
For substantial behavior changes, freeze realistic tasks and acceptance oracles
before forward-testing. Include an off-target case and a cold/stale-context case
when relevant. Judge produced artifacts and side effects, not wording alone;
retain failures and distinguish explicit instruction loading from native discovery.

## Output

Canonical skill, synchronized copies, focused checks and documented runtime limitations.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Do not add a duplicate workflow, dependency, host-compatibility claim, or
permission without authorization and evidence. Review the final diff for
unrelated edits. Record command, result, revision, limitations, and next action
as `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Stop when no suitable work remains, the deadline or user request ends the run,
a safety boundary is reached, or materially identical findings recur more than
three times. Never sleep to consume time or sleep to consume duration; write a
consolidated report.

## Example

```text
/loop-skill-create 15m improve the release skill evidence contract
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
