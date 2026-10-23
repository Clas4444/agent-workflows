# Skill Usage Guide

These skills are workflows for coding agents, not autonomous permissions. Invoke
one explicitly, describe the target and desired outcome, and let the host apply
the repository's normal approval rules.

## Choose a skill

| Skill | Use it when you need to | Typical invocation |
|---|---|---|
| `loop-review` | inspect a repository, change, or design and report findings | `/loop-review 10m repository` |
| `loop-code` | implement a feature, fix, refactor, or configuration change | `/loop-code 15m fix the failing parser tests` |
| `loop-test` | select, run, or improve a bounded test strategy | `/loop-test 10m validate the API change` |
| `loop-test-unit` | isolate behavior in one module or function | `/loop-test-unit 10m parser module` |
| `loop-test-integration` | verify boundaries between processes, files, services, or databases | `/loop-test-integration 15m upload flow` |
| `loop-test-coverage` | identify meaningful untested risk and add focused coverage | `/loop-test-coverage 15m authentication` |
| `loop-diagnose` | reproduce and isolate an unexpected failure | `/loop-diagnose 15m failing command` |
| `loop-diagnose-repro` | minimize a bug to a repeatable reproducer | `/loop-diagnose-repro 15m crash on import` |
| `loop-diagnose-regression` | compare a known-good and failing revision | `/loop-diagnose-regression 20m recent regression` |
| `loop-diagnose-performance` | measure and isolate a slow or resource-heavy path | `/loop-diagnose-performance 20m slow endpoint` |
| `loop-research` | research a technical question or implementation option | `/loop-research 10m compare validation libraries` |
| `loop-research-repo` | evaluate repositories before adopting code or tools | `/loop-research-repo 15m candidate repositories` |
| `loop-research-tools` | evaluate extensions, skills, MCP servers, or agent tools | `/loop-research-tools 15m testing tools` |
| `loop-docs` | audit, update, and verify project documentation | `/loop-docs 10m usage documentation` |
| `loop-skill-create` | create or maintain a synchronized `SKILL.md` workflow | `/loop-skill-create 20m new release workflow` |
| `loop-orchestrate` | run bounded prompts through an explicitly configured headless CLI | `py -3 scripts/run_loop.py ...` |
| `loop-prompt` | run one prompt followed by agent-generated follow-ups | `/loop-prompt 3 review and test this change` |

Durations are work budgets, not sleep timers. The exact syntax for slash
commands can vary by host; the intent, target, and requested count are the
important inputs.

## A practical sequence

For a code change, use:

1. `loop-review` to establish scope, risks, and acceptance criteria.
2. `loop-code` to implement one small batch at a time.
3. `loop-test` or a focused `loop-test-*` skill to verify behavior.
4. `loop-docs` when user-facing behavior or commands changed.
5. `loop-review` again to inspect the final diff and evidence.

For a repository or tool evaluation, use `loop-research-repo` or
`loop-research-tools`, then `loop-review`; do not install or adopt anything
without explicit authorization.

## Required reporting

Every loop must distinguish `PASS`, `FAIL`, `BLOCKED`, and `NOT_RUN`. Report the
commands or evidence used, files changed, remaining gaps, and the next bounded
action. Stop when there is no authorized useful work, a safety boundary is
reached, or materially identical findings recur more than three times.

## `/loop-prompt` and headless orchestration

`/loop-prompt 3 task` means one initial invocation plus at most three
agent-generated follow-ups. It does not guarantee four invocations: a timeout,
failure, block, missing `NEXT_PROMPT:`, or safety boundary stops the run.

For direct process-level orchestration, use an explicit command and quote the
placeholder as one argument on Windows:

```text
py -3 scripts/run_loop.py --prompt "Review and test this change" --follow-up-count 3 --timeout-seconds 600 -- copilot -p "{prompt}"
```

The runner writes JSON state and a Markdown report. Review captured output for
secrets before sharing it. Fake-agent tests prove only the runner protocol;
they do not prove that a particular Copilot, Codex, or Claude Code version is
runtime-compatible.
