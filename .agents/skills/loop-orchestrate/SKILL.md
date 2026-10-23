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

## Runner location

Resolve scripts/run_loop.py relative to this SKILL.md directory, never the
working directory of the target project. The synchronized skill includes its
own runner. If that file is missing, report BLOCKED and synchronize the skill
from its source repository before running it.

## Inputs

Explicit installed command adapter, prompt, positive timeout, finite limit and evidence paths.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

Use `scripts/run_loop.py` with a positive timeout and finite limit. Configure
the installed host's command explicitly; do not assume Copilot, Codex, and
Claude Code share flags. Use `{prompt}` as an argument or omit it to send the
prompt on stdin. Each invocation must verify one useful batch and emit exactly
one `LOOP_STATUS: PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN` marker.

## Output

Invocation count, stop reason, per-step status and local state/report paths.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

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

## Example

```text
/loop-orchestrate run the supplied headless command with a 120-second timeout and two-invocation limit
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
