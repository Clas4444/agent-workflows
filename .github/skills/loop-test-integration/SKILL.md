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

## Workflow

Map the boundary, required services, fixtures, environment, and cleanup. Run a
bounded smoke test first, then expand only when evidence requires it. Record
setup, command, exit code, logs, cleanup result, and reproducibility.

## Boundaries and evidence

Do not expose credentials or alter shared environments without authorization.
Report `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Stop when no suitable work remains, the deadline or user request ends the run, a
safety boundary is reached, or materially identical results recur more than
three times. Never sleep to consume time; write a consolidated report.
