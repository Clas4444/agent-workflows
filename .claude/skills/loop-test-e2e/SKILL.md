---
name: loop-test-e2e
description: "Verify a complete user-visible journey through its real entry point, including success, invalid input and observable side effects. Use for end-to-end acceptance, not isolated units or one integration boundary."
argument-hint: "[duration, target, and acceptance criteria]"
user-invocable: true
disable-model-invocation: false
---

# Loop Test E2E

## Use when

Test a complete CLI, API or UI journey against acceptance criteria. loop-test-unit isolates one unit; loop-test-integration checks a specific boundary rather than the whole entry-to-result journey.

## Inputs

User journey, real entry point, expected outputs/errors, disposable environment, fixture data and cleanup rules.
If duration is omitted, the authorized task scope is the bound. Reuse existing
authorization; clarify only prerequisites that prevent safe progress.

## Workflow

1. Map the journey from user input through the actual entry point to observable
   output and persistent side effects. Record environment and prerequisites.
2. Prepare disposable fixtures and the smallest success scenario. Exercise the
   real CLI/API/UI, rather than replacing the journey with internal mocks.
3. Verify an invalid-input or permission-denied journey and its exit/status,
   user-facing message and absence of unexpected writes or partial state.
4. Run authorized scenarios with bounded timeouts; keep deterministic assertions
   on outcomes instead of fragile timing. Record logs and cleanup results.
5. Report each scenario independently, including untested host/browser/backend
   variations and any environment-specific blockers.

## Output

Scenario matrix, real entry-point commands/actions, observable assertions, logs and cleanup evidence.
Report PASS for verified acceptance, FAIL for a failed check, BLOCKED for an
unavailable required prerequisite and NOT_RUN for checks not executed.

## Boundaries and evidence

Do not touch production accounts/data, send real messages or weaken authentication to make a test pass. Required unavailable services are BLOCKED. UI/browser checks not performed remain NOT_RUN.
Preserve unrelated work. Stop when no suitable work remains, the deadline or
user request ends the run, a safety boundary is reached, or materially identical
results recur more than three times. Never sleep to consume time. Write a
consolidated report with evidence, changes, limitations and next action.

## Example

```text
/loop-test-e2e 15m test the CLI sum journey and invalid-input behavior end to end
```

Adapt invocation syntax to the host; an example does not prove native discovery.
