---
name: loop-test-integration
description: "Run a bounded integration-test loop across services, processes, files, databases, or external boundaries. Verify setup, contracts, failure paths, cleanup, and reproducibility."
argument-hint: "[duration and integration target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Test Integration

## Use when

Verify a contract across processes, files, services, databases, or other
external boundaries.

## Inputs

Boundary contract, local services/processes, fixtures and cleanup constraints.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

Map the boundary, required services, fixtures, environment, and cleanup. Run a
bounded smoke test first, then expand only when evidence requires it. Record
setup, command, exit code, logs, cleanup result, and reproducibility.

## Output

Setup, contract checks, logs, exit codes, cleanup and reproducibility evidence.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Do not expose credentials or alter shared environments without authorization.
Report `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Stop when no suitable work remains, the deadline or user request ends the run, a
safety boundary is reached, or materially identical results recur more than
three times. Never sleep to consume time; write a consolidated report.

## Example

```text
/loop-test-integration 15m test the runner-to-child-process contract locally
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
