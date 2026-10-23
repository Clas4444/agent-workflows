# Headless loop orchestration

`scripts/run_loop.py` is an optional process-level harness. It invokes a
configured command repeatedly; it does not install an agent, authenticate a
host, grant permissions, or make the current chat host invoke itself.

## Basic contract

Provide a prompt, a finite limit, a positive timeout, and a command after `--`.
Use `{prompt}` as one command argument when the host accepts the prompt as an
argument. If the token is absent, the runner writes the prompt to stdin.
Commands are passed without shell interpolation.

```text
py -3 scripts/run_loop.py --prompt "Review this change" --max-iterations 3 --timeout-seconds 600 -- copilot -p "{prompt}"
```

Check the installed host's own flags before adapting the examples for Codex or
Claude Code. The runner does not define a shared host CLI.

## Follow-ups and batches

`--follow-up-count N --self-prompt` permits one initial invocation and at most
`N` inferred follow-ups. The next result must contain exactly one non-empty,
non-duplicate `NEXT_PROMPT:` line. A failure, block, timeout, startup error,
malformed or duplicate marker, repeated prompt/result, safety boundary, or
missing evidence stops the run before another invocation.

```text
py -3 scripts/run_loop.py --prompt "Review and test this change" --follow-up-count 3 --timeout-seconds 600 --self-prompt -- copilot -p "{prompt}"
```

For independent prompts, use a UTF-8 file with one non-empty prompt per line.
Lines beginning with `#` are ignored:

```text
py -3 scripts/run_loop.py --prompt-file prompts.txt --batch-dir .loop/demo --max-iterations 3 --timeout-seconds 600 -- copilot -p "{prompt}"
```

The batch writes one JSON/Markdown pair per prompt and `summary.json` and
`summary.md`. The batch is `PASS` only when every prompt is `PASS`.

## Markers and evidence

Each invocation must emit exactly one complete status marker:

```text
LOOP_STATUS: PASS
LOOP_STATUS: FAIL
LOOP_STATUS: BLOCKED
LOOP_STATUS: NOT_RUN
```

In a normal run, `PASS`, `FAIL`, and `BLOCKED` are terminal. In self-prompt
mode, `PASS` or `NOT_RUN` may continue only when a valid next prompt exists and
the limit permits it. State JSON records every invocation, prompt count,
status, and stop reason. The Markdown report is a short index; state and
captured output may contain sensitive data.

The runner reads stdout and stderr concurrently in bounded chunks, retains
only a combined 100,000-character decoded tail, and parses markers while
reading. It hashes complete raw streams without retaining them. Stdout is
placed before stderr in retained evidence; cross-stream timing is not
preserved. Invalid UTF-8 is replaced in retained text.

Timeout handling terminates and waits for the direct child. Descendant cleanup
on Windows is host-specific and is not guaranteed by this project.
