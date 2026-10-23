---
name: loop-ci
description: "Diagnose and repair scoped CI failures by tracing a failed job to logs, reproducing locally where possible, and verifying workflow changes. Use for CI pipelines rather than general application debugging."
argument-hint: "[duration, workflow or run, and failing job]"
user-invocable: true
disable-model-invocation: false
---

# Loop CI

## Use when

A pipeline fails or needs an authorized reliability correction. Use loop-test
for local test strategy and loop-debug for an application defect independent
of its CI environment.

## Inputs

Workflow/run identity, revision, failed job/step and accessible logs.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

1. Record repository, revision, run/job identity, platform, tool versions,
   failing step, command, exit code and first actionable log evidence.
2. Distinguish application failure from runner, dependency, permission, cache,
   quoting or environment issues. Reproduce with the closest local environment.
3. If required remote logs are inaccessible, mark remote inspection BLOCKED
   and explain the missing access. If remote inspection is outside the selected
   scope and was not attempted, mark it NOT_RUN. Do not invent a successful run
   from a valid workflow file.
4. Make a scoped authorized correction. Preserve assertions, required checks
   and least-privilege permissions; avoid unrelated workflow rewrites.
5. Run local checks and available workflow validation, then inspect the diff.
   Report local and remote results separately with run links when available.

## Output

Actionable cause, scoped fix, local checks and separately evidenced remote status.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Do not expose CI secrets, install tools, grant broader tokens, disable gates or
trigger costly/deploying workflows without authorization. Publishing a workflow
or rerunning external jobs must stay within the user's authorized scope.
Report PASS, FAIL, BLOCKED or NOT_RUN with logs, changed files and next action.

Stop when no suitable work remains, the deadline or user request ends the run,
a safety boundary is reached, or materially identical results recur more than
three times. Never sleep to consume time; write a consolidated report.

## Example

```text
/loop-ci 15m investigate the supplied failed Windows test-job log
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
