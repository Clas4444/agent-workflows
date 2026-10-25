# Headless loop orchestration

`scripts/run_loop.py` is an optional process-level harness. It invokes a
configured command repeatedly; it does not install an agent, authenticate a
host, grant permissions, or make the current chat host invoke itself.

## Basic contract

Provide a prompt, a finite limit, a positive timeout, and a command after `--`.
Use `{prompt}` as one command argument when the host accepts the prompt as an
argument. If the token is absent, the runner writes the prompt to stdin.
Commands are passed without shell interpolation.
Every invocation, including the first, receives instructions for the status
marker protocol. `--follow-up-count 0` explicitly permits only one invocation.
When `{prompt}` is supplied, stdin is closed without sending a second copy.
In normal mode, later invocations receive the original request and the bounded
previous output so a fresh process can continue from the last result.

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
An evidence persistence failure makes the batch fail. Failed invocations do not
reuse state from an earlier run at the same path; their summary records zero
verified iterations when fresh state cannot be trusted.
When evidence is saved successfully, per-prompt summaries preserve `BLOCKED`
and `NOT_RUN` with their actual invocation counts. The overall batch still
fails unless every invocation succeeds.

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
State records `started_at` before the first invocation and `finished_at` after
the last invocation, both in UTC.
`invocation_status` records the child workflow result; `final_status` becomes
`FAIL` if evidence persistence fails. `persistence_errors` records diagnostics
in any state file that can still be saved. If storage remains unavailable,
stderr and the nonzero exit code are authoritative; an older file may remain.
Each iteration saves `output_fingerprint`: concatenated SHA-256 digests of
the complete stdout and stderr streams. Timeout/startup errors instead hash
the recorded diagnostic message; their partial child streams are unavailable.
The state and report paths must differ; the runner rejects a collision before
starting the command. Existing hardlinked evidence destinations are rejected as
well, including links to unrelated files. The pair is checked again after the
child exits and before either write. This is preflight protection, not a lock
against a concurrent alias change between checking and writing. If an unsafe
alias appears during the child run, the runner exits nonzero without overwriting
either destination; any old evidence is stale and stderr is authoritative.
Self-prompt follow-ups retain the original scope and the
bounded previous output, labeled as reference rather than new authorization.

The runner reads stdout and stderr concurrently in bounded chunks, retains
only a combined 100,000-character decoded tail, and parses markers while
reading. It hashes complete raw streams without retaining them. Stdout is
placed before stderr in retained evidence; cross-stream timing is not
preserved. Invalid UTF-8 is replaced in retained text.
UTF-8 characters split between reads are decoded incrementally. Complete lines
are parsed before limiting unfinished lines to 8,192 characters. Oversized
marker lines are rejected, and an oversized ordinary line cannot turn its
suffix into a marker. Missing or malformed status markers stop both modes.

Timeout handling terminates and waits for the direct child. The deadline also
covers waiting for a child that has already closed its output. Descendant
cleanup on Windows is host-specific and is not guaranteed by this project.
