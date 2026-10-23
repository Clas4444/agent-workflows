# Skill usage

These skills provide bounded workflows for coding agents. They do not grant
permissions or replace project-specific instructions. Invoke one skill with a
clear target and desired outcome; let the host apply its normal approval rules.

## Select a skill

| Skill | Use it for | Typical invocation |
|---|---|---|
| `loop-review` | Scope, evaluate, and report on a change or repository | `/loop-review 10m repository` |
| `loop-code` | Implement an authorized feature, fix, refactor, or configuration change | `/loop-code 15m fix the parser tests` |
| `loop-diagnose` | Reproduce and isolate an unexpected failure | `/loop-diagnose 15m failing command` |
| `loop-diagnose-repro` | Minimize a repeatable reproducer | `/loop-diagnose-repro 15m import crash` |
| `loop-diagnose-performance` | Measure a slow or resource-heavy path | `/loop-diagnose-performance 20m slow endpoint` |
| `loop-diagnose-regression` | Compare known-good and failing states | `/loop-diagnose-regression 20m recent regression` |
| `loop-research` | Investigate a technical question | `/loop-research 10m validation options` |
| `loop-research-repo` | Evaluate repositories before adoption | `/loop-research-repo 15m candidate repositories` |
| `loop-research-tools` | Evaluate tools, extensions, skills, or MCP servers | `/loop-research-tools 15m testing tools` |
| `loop-test` | Select and run a bounded project test strategy | `/loop-test 10m API change` |
| `loop-test-unit` | Test one module or function | `/loop-test-unit 10m parser module` |
| `loop-test-integration` | Test process, file, service, or database boundaries | `/loop-test-integration 15m upload flow` |
| `loop-test-coverage` | Improve meaningful coverage | `/loop-test-coverage 15m authentication` |
| `loop-docs` | Audit and update documentation | `/loop-docs 10m usage guide` |
| `loop-skill-create` | Create or maintain a synchronized skill | `/loop-skill-create 20m release workflow` |
| `loop-orchestrate` | Run an explicitly configured headless command | `py -3 scripts/run_loop.py ...` |
| `loop-prompt` | Run an initial prompt and bounded follow-ups | `/loop-prompt 3 review this change` |

## Recommended sequences

For a code change:

1. `loop-review` — define scope, risks, and acceptance criteria.
2. `loop-code` — implement one small authorized batch.
3. `loop-test` or a focused testing skill — verify behavior.
4. `loop-docs` — update commands or user-facing behavior.
5. `loop-review` — inspect the final diff and evidence.

For a diagnosis, use the narrowest diagnosis skill that fits. For adoption
decisions, use `loop-research-repo` or `loop-research-tools` before
`loop-review`. Do not install or authenticate anything without authorization.

Every loop reports `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`, plus commands or
evidence, changed files, remaining gaps, and the next action. Stop when useful
authorized work ends, a safety boundary is reached, the deadline expires, or
materially identical results repeat more than three times.

## `/loop-prompt`

`/loop-prompt 3 task` means one initial invocation followed by at most three
agent-generated follow-ups. It does not guarantee four invocations. A timeout,
failure, block, startup error, missing or malformed marker, duplicate prompt or
result, safety boundary, or missing evidence stops the run.

For direct orchestration, quote `{prompt}` as one argument on Windows:

```text
py -3 scripts/run_loop.py --prompt "Review and test this change" --follow-up-count 3 --timeout-seconds 600 --self-prompt -- copilot -p "{prompt}"
```

Inspect local JSON state and Markdown reports before sharing captured output.
Fake-agent tests verify the runner protocol only; they do not prove runtime
compatibility with a particular host or host version.
