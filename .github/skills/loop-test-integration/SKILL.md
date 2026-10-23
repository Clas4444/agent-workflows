---
name: loop-test-integration
description: "Run a bounded integration-test loop across services, processes, files, databases, or external boundaries. Verify setup, contracts, failure paths, cleanup, and reproducibility."
argument-hint: "[duration and integration target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Test Integration

Map the integration boundary, required services, fixtures, environment, and
cleanup. Run a bounded smoke test first, then expand only when evidence requires
it. Record setup, command, exit code, logs, cleanup result, and
`PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`. Do not expose credentials or alter
shared environments without authorization. Stop with a consolidated report when
no new angle remains or materially identical results repeat more than three times
consecutively; never sleep.
