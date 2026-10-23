# Headless Loop Orchestration

The repository can continue a loop in a new process through
`scripts/run_loop.py`. This is process-level orchestration, not a guarantee
that an agent host will automatically invoke itself.

The runner requires an explicit headless command, a finite iteration limit, and
a timeout. Use `{prompt}` when the agent accepts the prompt as an argument; if
the token is absent, the prompt is sent on standard input.

For multiple independent prompts, put one prompt per non-empty line in a UTF-8
file. Lines beginning with `#` are ignored:

```text
python scripts/run_loop.py --prompt-file prompts.txt --batch-dir .loop/demo --max-iterations 3 --timeout-seconds 600 -- copilot -sp {prompt}
```

The batch writes one JSON/Markdown pair per prompt plus `summary.json` and
`summary.md`. A batch passes only when every prompt finishes with `PASS`.

To derive follow-up prompts automatically from the initial prompt:

```text
python scripts/run_loop.py --prompt "Develop a safe validation improvement" --follow-up-count 5 --timeout-seconds 600 -- copilot -sp {prompt}
```

This permits one initial invocation plus five inferred follow-up invocations.
Each result must contain `NEXT_PROMPT:`. The count is an upper bound, not a
guarantee: failures, timeouts, missing next prompts, and safety boundaries stop
the run early.

Examples (verify flags against the installed version before use):

```text
python scripts/run_loop.py --prompt "Review and continue one bounded batch" --max-iterations 3 --timeout-seconds 600 -- copilot -sp {prompt}
python scripts/run_loop.py --prompt "Review and continue one bounded batch" --max-iterations 3 --timeout-seconds 600 -- codex exec {prompt}
python scripts/run_loop.py --prompt "Review and continue one bounded batch" --max-iterations 3 --timeout-seconds 600 -- claude -p {prompt}
```

Each invocation must end with one exact marker:

```text
LOOP_STATUS: PASS
LOOP_STATUS: FAIL
LOOP_STATUS: BLOCKED
LOOP_STATUS: NOT_RUN
```

The runner stops on `PASS`, `FAIL`, or `BLOCKED`; a `NOT_RUN` result continues
until the limit. It also stops on timeout, process-start failure, or the
iteration limit. State is written as JSON and a short report is written to the
configured paths. Captured output may contain sensitive data; inspect it
before sharing. The runner does not install tools, authenticate, grant
permissions, or use shell execution.

Runtime compatibility remains host-specific. A successful fake-command test
only proves the runner's continuation protocol, not that Copilot, Codex, or
Claude Code works in a particular environment.
