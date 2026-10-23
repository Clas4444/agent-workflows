---
name: loop-prompt
description: "Run an initial user prompt, have the agent infer the next useful prompt, and execute a bounded number of follow-up prompts with evidence. Use when the user requests /loop-prompt N."
argument-hint: "[follow-up count and initial prompt]"
user-invocable: true
disable-model-invocation: true
---

# Loop Prompt

Interpret `/loop-prompt N` as one initial user prompt followed by at most `N`
agent-generated follow-up prompts. Use `scripts/run_loop.py --follow-up-count
N --self-prompt` with an explicitly configured headless agent command. Never
assume the current chat host can invoke itself, and never call a different
agent without authorization.

After each invocation, derive exactly one non-empty, non-duplicate, actionable
`NEXT_PROMPT:` from the previous result and execute it. Every invocation must
end with exactly one `LOOP_STATUS: PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.
`PASS` is terminal for a normal run; a self-prompt run may continue only when a
valid new `NEXT_PROMPT:` explicitly supplies the next invocation. Stop early on
failure, blocking, timeout, startup failure, missing/duplicate/malformed
markers, repeated prompts or results, safety boundary, or user request. Keep
the requested count as a hard upper bound, never sleep to consume it, and write
state/report evidence for every prompt. Review captured output for sensitive
data before sharing.

The count means follow-up prompts after the initial prompt, not total prompts.
For example, `/loop-prompt 5` permits six invocations: the user's prompt plus
five inferred prompts. A fake-command test only verifies orchestration, not
runtime compatibility or agent quality.
