---
name: loop-prompt
description: "Run an initial user prompt, have the agent infer the next useful prompt, and execute a bounded number of follow-up prompts with evidence. Use when the user requests /loop-prompt N."
argument-hint: "[follow-up count and initial prompt]"
user-invocable: true
disable-model-invocation: true
---

# Loop Prompt

## Use when

The user explicitly requests `/loop-prompt N` and authorizes the configured
headless agent command.

## Runner location

Resolve scripts/run_loop.py relative to this SKILL.md directory, never the
working directory of the target project. The synchronized skill includes its
own runner. If that file is missing, report BLOCKED. Restore it only when writes
to an explicitly selected installation root are already authorized; otherwise
stop without modifying the installation. Authorization to invoke a runner does
not itself authorize synchronization or overwriting installed files.

## Inputs

Nonnegative follow-up count N, initial task, explicit command and evidence paths.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

Interpret `N` as follow-ups after the initial prompt. Use
`scripts/run_loop.py --follow-up-count N --self-prompt` with an explicit command.
After each invocation, accept exactly one non-empty, non-duplicate,
actionable `NEXT_PROMPT:` line and execute it. Every invocation must emit one
exact `LOOP_STATUS: PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN` marker.

## Output

At most N+1 invocations, distinct next prompts, stop reason and state/report evidence.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

`PASS` is terminal for a normal run. Self-prompt mode continues only when a
valid new next prompt exists and the hard limit permits it. Stop early when no suitable work remains, or on
failure, block, timeout, startup failure, missing/duplicate/malformed marker,
repeated prompt or result, safety boundary, or user request. Write state and
report evidence for every invocation and review captured output for sensitive
data.
Never sleep to consume time. The invocation count is a hard maximum, not a quota.

`/loop-prompt 5` permits six invocations: one initial prompt plus five
follow-ups. It is a maximum, not a guarantee. Never assume the chat host can
invoke itself or call a different agent without authorization. Fake-command
tests verify orchestration only, not host runtime compatibility or agent quality.

## Example

```text
/loop-prompt 3 review the supplied local change in bounded follow-ups
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
