# Portable Loop Skills

Portable, bounded workflows for coding agents, plus a small Python runner for
process-level continuation and a dependency-free validator.

The repository is intended for projects that use agent instructions in VS Code
with Copilot, Codex, or Claude Code. It standardizes how an agent plans a small
batch, changes only authorized files, verifies the result, records evidence,
and stops instead of looping indefinitely.

> **Experimental.** The files are portable instructions, not a promise that
> every host interprets them or their metadata identically. Host-runtime
> compatibility remains unverified unless the runtime matrix records evidence.

## What is included

The 17 skills are grouped by responsibility:

| Family | Skills | Use for |
|---|---|---|
| Review and implementation | `loop-review`, `loop-code` | Scope a change, implement it, inspect the diff, and verify it |
| Diagnosis | `loop-diagnose`, `loop-diagnose-repro`, `loop-diagnose-performance`, `loop-diagnose-regression` | Reproduce failures, isolate causes, measure regressions, and verify fixes |
| Research | `loop-research`, `loop-research-repo`, `loop-research-tools` | Compare sources, repositories, tools, and adoption risks before acting |
| Testing | `loop-test`, `loop-test-unit`, `loop-test-integration`, `loop-test-coverage` | Select and run bounded tests or improve meaningful coverage |
| Documentation and skills | `loop-docs`, `loop-skill-create` | Maintain project documentation or synchronized agent workflows |
| Orchestration | `loop-orchestrate`, `loop-prompt` | Run explicitly configured headless invocations with hard limits |

Every workflow distinguishes `PASS`, `FAIL`, `BLOCKED`, and `NOT_RUN`. A
duration is a work budget, never a reason to wait or invent work.

## Repository layout

- `.github/skills/` — canonical source and VS Code/Copilot project skills
- `.agents/skills/` — byte-identical Codex project copies
- `.claude/skills/` — byte-identical Claude Code project copies
- `docs/` — usage, compatibility, orchestration, validation, and runtime evidence
- `scripts/run_loop.py` — optional process-level orchestration runner
- `scripts/validate.py` — dependency-free structure and synchronization validator
- `tests/` — deterministic validator and runner tests

Edit `.github/skills/` first, then synchronize the exact file to the other two
skill roots. The manifest declares the 17 skills and the three supported
project-root layouts.

## Installation and use

Clone or copy the repository into a project that supports one of the native
skill layouts. Do not copy these files into a personal global installation
unless the host's own documentation says to do so. The repository does not
install tools, authenticate hosts, grant permissions, or move personal files.

Start with [the skill usage guide](./docs/SKILL-USAGE.md). A common code-change
sequence is:

1. `loop-review` — establish scope, risks, and acceptance criteria.
2. `loop-code` — make one authorized implementation batch.
3. `loop-test` or a focused testing skill — verify the behavior.
4. `loop-docs` — update user-facing instructions when behavior or commands changed.
5. `loop-review` — inspect the final diff and evidence.

Use the diagnosis or research families when the task needs them; do not invoke
multiple overlapping loops merely to consume a budget.

## Optional headless orchestration

`loop-orchestrate` and `loop-prompt` wrap an explicitly configured command;
they do not make a host self-invoking. For the runner contract and quoting
examples, see [docs/ORCHESTRATION.md](./docs/ORCHESTRATION.md).

`/loop-prompt 3 task` means one initial invocation and at most three
agent-generated follow-ups. Failures, timeouts, malformed markers, repeated
prompts or results, safety boundaries, and missing evidence stop the run early.
Captured output can contain secrets; inspect local state and reports before
sharing them.

## Verification and limits

Run the checks from the repository root:

```text
py -3 -m unittest discover -s tests -v
py -3 scripts\validate.py
py -3 -m py_compile scripts\run_loop.py scripts\validate.py tests\test_validate.py
```

The validator checks metadata, the manifest, all three skill roots, required
stop/reporting rules, and the generated evidence fingerprint. The current
validation report records structural tests as `PASS`, while CI and agent
runtime tests remain `NOT_RUN` unless separately evidenced. See
[docs/VALIDATION.md](./docs/VALIDATION.md) and
[docs/RUNTIME-TEST-MATRIX.md](./docs/RUNTIME-TEST-MATRIX.md).

The runner's tests use local fake commands. They verify the continuation
protocol, bounded capture, marker handling, and persistence failures; they do
not prove that a particular Copilot, Codex, or Claude Code version works.
Timeout handling guarantees termination of the direct child only. Descendant
cleanup on Windows is host-specific.

## Safety and contribution

Review commands, permissions, data handling, and project instructions before
using a workflow. Preserve unrelated changes. Do not expose credentials or
captured private output in issues or reports.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for the synchronization contract and
[SECURITY.md](./SECURITY.md) for responsible reporting. This independent
project is not affiliated with GitHub, Microsoft, OpenAI, or Anthropic.
