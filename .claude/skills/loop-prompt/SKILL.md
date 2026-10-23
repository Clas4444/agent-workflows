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

## Workflow

Interpret `N` as follow-ups after the initial prompt. Use
`scripts/run_loop.py --follow-up-count N --self-prompt` with an explicit command.
After each invocation, accept exactly one non-empty, non-duplicate,
actionable `NEXT_PROMPT:` line and execute it. Every invocation must emit one
exact `LOOP_STATUS: PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN` marker.

## Boundaries and evidence

`PASS` is terminal for a normal run. Self-prompt mode continues only when a
valid new next prompt exists and the hard limit permits it. Stop early when no suitable work remains, or on
failure, block, timeout, startup failure, missing/duplicate/malformed marker,
repeated prompt or result, safety boundary, or user request. Write state and
report evidence for every invocation and review captured output for sensitive
data.

`/loop-prompt 5` permits six invocations: one initial prompt plus five
follow-ups. It is a maximum, not a guarantee. Never assume the chat host can
invoke itself or call a different agent without authorization. Fake-command
tests verify orchestration only, not host runtime compatibility or agent quality.
