# Portable Loop Skills

**32 bounded workflows for coding agents.** Review a change, investigate a bug,
write a fix, verify it and stop with evidence. Includes a Python continuation
runner, a synchronization tool and a validator with no third-party dependencies.

[Choose a skill](#skill-catalog) · [Get started](#quick-start) ·
[Run checks](#verification) · [Contribute](CONTRIBUTING.md)

Repository maintainers: see [agent instructions](AGENTS.md),
[architecture](docs/ARCHITECTURE.md) and [data contracts](schemas/README.md).

For group responsibilities and review criteria, see [functional groups](docs/SKILL-GROUPS.md).
The new [MCP integration group](docs/MCP-GROUP.md) covers design, testing and tool trust.

> **Experimental · 1.4.0-experimental.** Shared instructions and matching files
> do not guarantee identical behavior across Codex, Copilot and Claude Code.
> See the [runtime evidence](docs/RUNTIME-TEST-MATRIX.md) for what was tested.

## Quick start

1. Clone this repository, or copy the relevant native skill layout into your
   project. Keep the host's existing project instructions.
2. Select one workflow and give it a concrete target and expected result.
3. Inspect the result and its verification evidence before proceeding.

```text
git clone https://github.com/Clas4444/loop-skills-repository.git
cd loop-skills-repository
python scripts/validate.py
```

Example requests (adapt to your host's invocation syntax):

```text
/loop-review 10m review the parser and identify actionable risks
/loop-debug 15m fix valid markers being lost after large output
/loop-test 10m verify the parser change and its failure paths
```

Durations are maximum work budgets. A task can finish early; the agent should
never sleep or invent more work to fill the time. Existing user authorization
applies throughout the task.

## Skill catalog

<!-- BEGIN GENERATED SKILL GROUPS -->

Groups are navigation metadata; native skill directories remain flat.

### Planning, review and security

| Skill | Purpose |
|---|---|
| [loop-plan](.github/skills/loop-plan/SKILL.md) | Turn a scoped request into dependency-ordered, verifiable implementation batches without changing code |
| [loop-review](.github/skills/loop-review/SKILL.md) | Run a bounded review loop over a file, folder, project, repository, or workspace: evaluate, discover integrations, propose, make authorized safe changes, verify, and report |
| [loop-security](.github/skills/loop-security/SKILL.md) | Review authorized code and configuration for security risks using threat boundaries, source evidence and safe local tests |
| [loop-evaluate](.github/skills/loop-evaluate/SKILL.md) | Evaluate a skill or agent workflow using predefined cases, an explicit rubric and independently checked outcomes |

### Implementation and maintenance

| Skill | Purpose |
|---|---|
| [loop-code](.github/skills/loop-code/SKILL.md) | Run a bounded code implementation loop for a feature, refactor, bug fix, or configuration change: plan a small batch, edit, verify, inspect the diff, and repeat |
| [loop-refactor](.github/skills/loop-refactor/SKILL.md) | Improve a scoped code structure while preserving observable behavior through characterization tests, small reversible changes and regression checks |
| [loop-dependencies](.github/skills/loop-dependencies/SKILL.md) | Assess and perform an authorized dependency change with manifest/lockfile consistency, compatibility checks and rollback evidence |
| [loop-migrate](.github/skills/loop-migrate/SKILL.md) | Prepare and verify a scoped data, schema or configuration migration with dry-run, backup, invariants, idempotence and rollback |

### Debugging and diagnosis

| Skill | Purpose |
|---|---|
| [loop-debug](.github/skills/loop-debug/SKILL.md) | Repair a reproducible bug end to end: capture a failing test, isolate the cause, apply the smallest authorized fix, and rerun regression checks |
| [loop-diagnose](.github/skills/loop-diagnose/SKILL.md) | Run a bounded diagnosis loop for a bug, crash, failing test, regression, or slow behavior: reproduce, isolate, test hypotheses, fix when authorized, and re-test |
| [loop-diagnose-repro](.github/skills/loop-diagnose-repro/SKILL.md) | Run a bounded reproduction loop for a bug or failure: capture the environment, minimize the reproducer, vary one factor at a time, and preserve exact evidence for a later fix |
| [loop-diagnose-performance](.github/skills/loop-diagnose-performance/SKILL.md) | Run a bounded performance-diagnosis loop for slow, memory-heavy, or resource-intensive behavior |
| [loop-diagnose-regression](.github/skills/loop-diagnose-regression/SKILL.md) | Run a bounded regression-diagnosis loop: compare a known-good and failing state, bisect or narrow the change set, reproduce the regression, and verify the smallest authorized fix |

### Research and adoption

| Skill | Purpose |
|---|---|
| [loop-research](.github/skills/loop-research/SKILL.md) | Run a bounded evidence loop to research repositories, documentation, tools, extensions, plugins, skills, MCP servers, or implementation options |
| [loop-research-repo](.github/skills/loop-research-repo/SKILL.md) | Research repositories and open-source projects in a bounded evidence loop |
| [loop-research-tools](.github/skills/loop-research-tools/SKILL.md) | Research tools, extensions, plugins, skills, and MCP servers in a bounded evidence loop |

### Testing and adversarial verification

| Skill | Purpose |
|---|---|
| [loop-test](.github/skills/loop-test/SKILL.md) | Run a bounded testing loop for a project or change: select tests, reproduce failures, improve coverage or fixtures when authorized, run checks, and report results |
| [loop-test-unit](.github/skills/loop-test-unit/SKILL.md) | Run a bounded unit-test loop for a module or function: select focused tests, reproduce failures, improve authorized tests or fixtures, and verify isolated behavior without weakening acceptance criteria |
| [loop-test-integration](.github/skills/loop-test-integration/SKILL.md) | Run a bounded integration-test loop across services, processes, files, databases, or external boundaries |
| [loop-test-coverage](.github/skills/loop-test-coverage/SKILL.md) | Run a bounded test-coverage loop: identify untested risk, inspect coverage evidence, add authorized focused tests, and verify that coverage improvements are meaningful rather than cosmetic |
| [loop-test-e2e](.github/skills/loop-test-e2e/SKILL.md) | Verify a complete user-visible journey through its real entry point, including success, invalid input and observable side effects |
| [loop-test-adversarial](.github/skills/loop-test-adversarial/SKILL.md) | Challenge a declared contract with isolated adversarial inputs and independently observed outcomes |
| [loop-test-compatibility](.github/skills/loop-test-compatibility/SKILL.md) | Verify a declared compatibility matrix across versions, platforms, host adapters or data formats |

### Documentation, CI and release

| Skill | Purpose |
|---|---|
| [loop-docs](.github/skills/loop-docs/SKILL.md) | Run a bounded documentation loop: audit README, guides, API references, examples, localization, and generated documentation; propose or make authorized updates; verify links and consistency |
| [loop-ci](.github/skills/loop-ci/SKILL.md) | Diagnose and repair scoped CI failures by tracing a failed job to logs, reproducing locally where possible, and verifying workflow changes |
| [loop-release](.github/skills/loop-release/SKILL.md) | Prepare and verify a scoped release candidate: version consistency, reproducible build, package contents, changelog and rollback notes |

### Skill authoring and agent continuation

| Skill | Purpose |
|---|---|
| [loop-skill-create](.github/skills/loop-skill-create/SKILL.md) | Create or maintain an agent skill through requirements, reusable-pattern inspection, synchronized editing, focused tests, documentation, and evidence review |
| [loop-orchestrate](.github/skills/loop-orchestrate/SKILL.md) | Run bounded follow-up prompts through a configured headless coding-agent command with state, timeout, stop markers, and evidence |
| [loop-prompt](.github/skills/loop-prompt/SKILL.md) | Run an initial user prompt, have the agent infer the next useful prompt, and execute a bounded number of follow-up prompts with evidence |

### MCP integration and tool trust

| Skill | Purpose |
|---|---|
| [loop-mcp-design](.github/skills/loop-mcp-design/SKILL.md) | Design a scoped MCP client/server integration around a pinned protocol version, tool contracts and trust boundaries |
| [loop-mcp-test](.github/skills/loop-mcp-test/SKILL.md) | Exercise a versioned MCP interface using bounded local fixtures or an explicitly authorized server |
| [loop-mcp-security](.github/skills/loop-mcp-security/SKILL.md) | Review an authorized MCP integration for tool trust, scoped authorization, credential handling and data-exfiltration boundaries |

<!-- END GENERATED SKILL GROUPS -->

For selection advice and complete examples, see [Skill usage](docs/SKILL-USAGE.md).
For a bug, start with `loop-debug`; for investigation without a repair, use
`loop-diagnose`. Use focused testing or research workflows when their evidence
is needed, rather than running every workflow on an unrelated task.

## Installation and synchronization

| Project layout | Intended host | Role |
|---|---|---|
| `.github/skills/` | VS Code/Copilot | Canonical source |
| `.agents/skills/` | Codex | Identical project copies |
| `.claude/skills/` | Claude Code | Identical project copies |

Each skill contains its own `SKILL.md`. The two orchestration skills also carry
`scripts/run_loop.py`; resolve that script relative to the skill directory.
Host-specific discovery and invocation requirements still apply.

To update an explicitly selected skill root:

```text
python scripts/sync_skills.py --target PATH_TO_SKILL_ROOT --check
python scripts/sync_skills.py --target PATH_TO_SKILL_ROOT
```

The first command reports differences without writing. The second copies the
manifest's 32 skills, preserving unrelated skills and backing up overwritten
files under `.loop/backups/`. Select a personal installation root only when
your host supports it and you intend to update it.

Preflight checks catch invalid names, missing source files, paths escaping the
selected root, hardlinked destination files and existing backup conflicts. Hardlinks
are rejected even in check mode: overwriting their shared inode could modify
unrelated files outside the selected root. Backups are created before source
copies. Unexpected I/O failure can still leave a partial update; restore the
saved files and rerun synchronization if necessary.

After changing the central runner, refresh bundled source copies and then the
other project roots:

```text
python scripts/sync_skills.py --target .github/skills
python scripts/sync_skills.py --target .agents/skills
python scripts/sync_skills.py --target .claude/skills
```

## Optional headless loops

The runner invokes an installed command with finite limits. It does not install
an agent, authenticate, grant permission or bypass the host's safeguards.

```text
python scripts/run_loop.py --prompt "Review the local change" --follow-up-count 3 --timeout-seconds 120 -- YOUR_AGENT YOUR_PROMPT_FLAG "{prompt}"
```

Replace the command and flag with your host's documented headless invocation.
`{prompt}` must be one argument; omit it to send the prompt through stdin.
`--follow-up-count 3` permits at most **four invocations**: one initial task
and three follow-ups. Failures, timeouts, invalid markers and repeated work
stop the loop early. See [Orchestration](docs/ORCHESTRATION.md) for the protocol,
state files and Windows cleanup limitations.

## Verification

For a new multi-step change, plan first with `loop-plan`, execute with
`loop-code`, then select unit/integration/E2E checks that match the risk.
Use `loop-migrate` for persisted formats and `loop-dependencies` for approved
package updates. `loop-evaluate` measures workflow behavior, not code coverage.

Requires Python 3.11 or newer. Use `py -3` on Windows if that launcher is
available; otherwise use the Python executable installed in your environment.

```text
python -m unittest discover -s tests -v
python scripts/validate.py
python scripts/sync_skills.py --target .github/skills --check
git diff --check
```

| Status | Meaning |
|---|---|
| `PASS` | The stated check was executed and verified |
| `FAIL` | The check ran and its acceptance condition failed |
| `BLOCKED` | A required prerequisite prevents progress |
| `NOT_RUN` | The check was not executed |

The validator checks supported metadata fields, manifest consistency, matching
copies, ordered input/output/example contracts, stop instructions and bundled runners. It is not a general YAML parser
or proof of model behavior. Tests cover subprocess boundaries and failure paths;
synthetic model decision tests have a narrower scope than complete workflows.
The [CI workflow](.github/workflows/validate.yml) runs on Windows/Linux with
Python 3.11/3.12; consult the actual run before claiming CI success.

### Explicit model smoke tests

The versioned fixture harness tests the five workflows added in 1.2. It never
runs paid/model invocations in CI or without an explicit authorization flag:

```text
python scripts/runtime_smoke.py --allow-model-invocations --skill-root PATH_TO_INSTALLED_SKILLS --output-dir .loop/runtime-1.2
```

Select an existing Codex installation with `--codex` when needed. Output must
be a new directory; logs and failed attempts are preserved. Verification uses
fixture artifacts, not just model self-reported PASS, and a usage limit stops
new invocations. See [the runtime harness guide](docs/RUNTIME-SMOKE.md).

## Documentation

- [Usage and workflow selection](docs/SKILL-USAGE.md)
- [Positive and negative acceptance scenarios](docs/SKILL-SCENARIOS.md)
- [Validation commands and evidence](docs/VALIDATION.md)
- [MCP group, sources and scoped offline verification](docs/MCP-GROUP.md)
- [Earlier 1.3 verification and seven testing workflows](docs/VERIFICATION-1.3.md)
- [Historical 1.2 system and runtime results](docs/RUNTIME-1.2-RESULT.md)
- [Earlier automated/decision test results](docs/TEST-22-RESULT.md)
- [22 real Codex fixture workflows: results and retests](docs/CODEX-SMOKE-2026-10-24.md)
- [Host compatibility and runtime evidence](docs/RUNTIME-TEST-MATRIX.md)
- [Writing conventions and reference projects](docs/AUTHORING.md)
- [1.2 gap assessment and system-wide changes](docs/EXPANSION-27.md)
- [Changelog](CHANGELOG.md)
- [Contributing](CONTRIBUTING.md) · [Security policy](SECURITY.md)

## License and ownership

An independent project maintained at
[Clas4444/loop-skills-repository](https://github.com/Clas4444/loop-skills-repository),
distributed under the [MIT license](LICENSE). This repository is not a fork of
the reference projects listed in the writing guide and is not affiliated with
OpenAI, Anthropic, GitHub or Microsoft. Reference projects inform presentation;
they do not imply copied implementations or verified host support.
