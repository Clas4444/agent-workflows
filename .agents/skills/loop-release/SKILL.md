---
name: loop-release
description: "Prepare and verify a scoped release candidate: version consistency, reproducible build, package contents, changelog and rollback notes. Use for release readiness; publishing remains a separately authorized action."
argument-hint: "[duration, release target, and requested version]"
user-invocable: true
disable-model-invocation: false
---

# Loop Release

## Use when

Prepare an authorized release candidate and assess readiness. Use loop-ci for
pipeline failures and loop-docs for documentation-only maintenance.

## Inputs

Candidate revision/version, release gates, supported environments and publication scope.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

1. Read release instructions and record target revision, requested version,
   supported environments, acceptance gates and publication authorization.
2. Check manifest/version consistency, changelog, license notices, migration
   requirements and rollback instructions. Do not invent a version or support.
3. Run the documented build and tests using existing tools. Inspect package
   contents for missing runtime assets, development-only files and private data.
   To claim reproducibility, rebuild the same revision with the same recorded
   inputs in clean disposable directories and compare artifact checksums. Explain
   any project-documented normalization; do not ignore unexplained differences.
   Without that comparison, mark build reproducibility NOT_RUN.
4. Verify an install or smoke test in a disposable local location where possible;
   record artifact identity, checksums, commands, exit codes and platform.
5. Report release readiness, exact candidate, passed/failed gates and unresolved
   risks. A successful build alone does not prove successful installation.

## Output

Readiness checklist, artifact checksums, package/smoke evidence and unresolved gates.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Do not tag, push, publish, deploy, sign with private keys or change credentials
without authorization. Keep preparation reversible and preserve unrelated work.
Report PASS, FAIL, BLOCKED or NOT_RUN; untested platforms stay NOT_RUN.

Stop when no suitable work remains, the deadline or user request ends the run,
a safety boundary is reached, or materially identical results recur more than
three times. Never sleep to consume time; write a consolidated report.

## Example

```text
/loop-release 15m check release readiness for the current candidate without publishing
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
