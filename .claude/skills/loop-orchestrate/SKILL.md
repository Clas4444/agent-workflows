---
name: loop-orchestrate
description: "Run bounded follow-up prompts through a configured headless coding-agent command with state, timeout, stop markers, and evidence. Use when a loop must continue in a new agent invocation."
argument-hint: "[prompt, command adapter, limits, and report paths]"
user-invocable: true
disable-model-invocation: false
---

# Loop Orchestrate

Use `scripts/run_loop.py` only when the user authorizes external agent
invocations. Configure the host-specific headless command explicitly; do not
assume Copilot, Codex, and Claude Code share flags. Use `{prompt}` in the
command to pass the generated prompt as an argument, or omit it to send the
prompt on stdin. Never use shell execution, hidden credentials, or automatic
permission escalation.

Set a positive timeout and finite `--max-iterations`. Each invocation must
review the previous output, make one useful bounded batch, verify it, and end
with exactly one `LOOP_STATUS: PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN` marker.
The runner stops on that marker, a timeout, a start failure, or the iteration
limit. It writes state and a report; inspect both and treat captured output as
potentially sensitive. Do not use this runner to bypass user approval, safety
boundaries, tests, or repository instructions.

Example shape (adapt flags for the installed host):

```text
python scripts/run_loop.py --prompt "Review the target and continue safely" --max-iterations 3 --timeout-seconds 600 -- copilot -sp {prompt}
```

This harness provides process-level continuation, not universal runtime
compatibility. Record the host, command/version, limits, evidence, and
`PASS`/`FAIL`/`BLOCKED`/`NOT_RUN` result. Stop and report when no useful work
remains, results repeat materially more than three times, the deadline is
reached, or authorization is missing. Never sleep to consume duration.
