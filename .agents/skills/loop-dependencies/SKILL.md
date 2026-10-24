---
name: loop-dependencies
description: "Assess and perform an authorized dependency change with manifest/lockfile consistency, compatibility checks and rollback evidence. Use for project dependency maintenance rather than tool adoption."
argument-hint: "[duration, target, and acceptance criteria]"
user-invocable: true
disable-model-invocation: false
---

# Loop Dependencies

## Use when

Maintain a project dependency or resolve manifest/lockfile drift. Use loop-research-tools to assess adopting a tool; loop-ci diagnoses a failing pipeline.

## Inputs

Project manifests and lockfiles, requested dependency/version, compatibility policy and permission for installation or network access.
If duration is omitted, the authorized task scope is the bound. Reuse existing
authorization; clarify only prerequisites that prevent safe progress.

## Workflow

1. Inventory direct/transitive dependencies, supported runtimes, lockfile format
   and available tests. Record current versions and the requested change.
2. Check compatibility, licenses and available advisory evidence from authorized
   sources. A missing live advisory check is NOT_RUN, never proof of safety.
3. Propose the smallest version change. Do not infer permission to install,
   contact registries or run package lifecycle scripts from a file-edit request.
4. Apply authorized manifest and lockfile updates together. Use the project's
   package manager when permitted; do not invent resolver hashes or integrity.
   A simple local fixture lockfile may be edited according to its stated schema.
5. Run available compatibility/tests and inspect drift. Record which checks
   need installation/network and provide an exact rollback or revert plan.

## Output

Dependency inventory, scoped manifest/lockfile diff, compatibility/test evidence, advisory limits and rollback.
Report PASS for verified acceptance, FAIL for a failed check, BLOCKED for an
unavailable required prerequisite and NOT_RUN for checks not executed.

## Boundaries and evidence

Do not run install hooks, change registries, broaden token permissions or upgrade unrelated packages without authorization. If a real resolver is required but unavailable, report BLOCKED instead of fabricating a lockfile.
Preserve unrelated work. Stop when no suitable work remains, the deadline or
user request ends the run, a safety boundary is reached, or materially identical
results recur more than three times. Never sleep to consume time. Write a
consolidated report with evidence, changes, limitations and next action.

## Example

```text
/loop-dependencies 15m update the approved dependency and reconcile its lockfile without installation
```

Adapt invocation syntax to the host; an example does not prove native discovery.
