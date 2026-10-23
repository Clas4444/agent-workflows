---
name: loop-orchestrate
description: "Run bounded follow-up prompts through a configured headless coding-agent command with state, timeout, stop markers, and evidence. Use when a loop must continue in a new agent invocation."
argument-hint: "[prompt, command adapter, limits, and report paths]"
user-invocable: true
disable-model-invocation: false
---

# Loop Orchestrate

## Use when

Run bounded process-level continuation through an explicitly configured
headless coding-agent command after the user authorizes that invocation.

## Workflow

Use `scripts/run_loop.py` with a positive timeout and finite limit. Configure
the installed host's command explicitly; do not assume Copilot, Codex, and
Claude Code share flags. Use `{prompt}` as an argument or omit it to send the
prompt on stdin. Each invocation must verify one useful batch and emit exactly
one `LOOP_STATUS: PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN` marker.

## Boundaries and evidence

Never use shell execution, hidden credentials, automatic permission escalation,
or this runner to bypass repository instructions or approval. The runner stops
on a terminal marker, timeout, startup failure, repeated prompt/result,
malformed marker, or iteration limit. It writes state and a report with prompt
count and stop reason; treat captured output as sensitive.

The runner streams both outputs in bounded chunks, keeps a bounded combined
tail, and hashes complete raw streams. Invalid UTF-8 is replaced in evidence.
Timeout cleanup guarantees the direct child only; Windows descendant cleanup is
host-specific. Record host, command/version, limits, evidence, and
`PASS`/`FAIL`/`BLOCKED`/`NOT_RUN`.

Stop when no suitable work remains, authorization is missing, the deadline ends,
a safety boundary is reached, or materially identical results recur more than
three times. Never sleep to consume time.
