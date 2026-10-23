---
name: loop-skill-create
description: "Create or maintain an agent skill through requirements, reusable-pattern inspection, synchronized editing, focused tests, documentation, and evidence review. Use when adding or changing a SKILL.md workflow."
argument-hint: "[duration, skill name, and requested behavior]"
user-invocable: true
disable-model-invocation: false
---

# Loop Skill Create

Extract the requested behavior, target hosts, scope, authorization, acceptance
criteria, and expected evidence before editing. Inspect the manifest,
`CONTRIBUTING.md`, validation docs, and existing skills for reusable patterns.
Treat `.github/skills/<skill-name>/SKILL.md` as the canonical source and do not
create a duplicate workflow when an existing skill can be improved.

Implement one small batch at a time. Validate lowercase hyphenated naming,
frontmatter boundaries, required fields, prerequisites, permitted actions,
constraints, outputs, bounded work, no idle sleeping, deadline/no-work/
repeated-result/blocked stop conditions, and explicit `PASS`, `FAIL`, `BLOCKED`,
and `NOT_RUN` reporting. Add a representative positive test and a focused
negative test using an isolated fixture when the workflow or validator supports
it. Diagnose failures, fix the root cause, and rerun the relevant checks.

Synchronize the canonical file exactly to every project skill root declared in
`skills-manifest.json`. Update documentation and reproducible evidence only
when the behavior or verification surface changes. Review the final diff for
unrelated edits, inspect generated reports, and record the command, result,
revision, limitations, and next action.

Stop and write a consolidated report when no authorized useful work remains,
the deadline is reached, work is blocked, a safety boundary is encountered, or
materially identical findings recur more than three consecutive times. Never
sleep to consume duration, and never claim host runtime compatibility without
host-specific evidence.
