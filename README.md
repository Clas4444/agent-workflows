# Portable Loop Skills

**22 bounded workflows for coding agents.** Review a change, investigate a bug,
write a fix, verify it and stop with evidence. Includes a Python continuation
runner, a synchronization tool and a validator with no third-party dependencies.

[Choose a skill](#skill-catalog) · [Get started](#quick-start) ·
[Run checks](#verification) · [Contribute](CONTRIBUTING.md)

> **Experimental · 1.1.0-experimental.** Shared instructions and matching files
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

| Workflow | Skill | Result to expect |
|---|---|---|
| Review | [loop-review](.github/skills/loop-review/SKILL.md) | Prioritized findings with evidence |
| Implement | [loop-code](.github/skills/loop-code/SKILL.md) | A scoped change and verified result |
| Debug | [loop-debug](.github/skills/loop-debug/SKILL.md) | Reproducer, repair and regression check |
| Diagnose | [loop-diagnose](.github/skills/loop-diagnose/SKILL.md) | Hypotheses and an isolated cause |
| Reproduce | [loop-diagnose-repro](.github/skills/loop-diagnose-repro/SKILL.md) | Minimal repeatable failure |
| Profile | [loop-diagnose-performance](.github/skills/loop-diagnose-performance/SKILL.md) | Comparable measurements and bottleneck evidence |
| Trace regression | [loop-diagnose-regression](.github/skills/loop-diagnose-regression/SKILL.md) | Known-good/failing comparison |
| Research | [loop-research](.github/skills/loop-research/SKILL.md) | Source-linked findings and recommendation |
| Compare repositories | [loop-research-repo](.github/skills/loop-research-repo/SKILL.md) | Adoption comparison and risks |
| Compare tools | [loop-research-tools](.github/skills/loop-research-tools/SKILL.md) | Capabilities, permissions and verification plan |
| Test | [loop-test](.github/skills/loop-test/SKILL.md) | Relevant checks and remaining gaps |
| Unit test | [loop-test-unit](.github/skills/loop-test-unit/SKILL.md) | Isolated behavior and assertions |
| Integration test | [loop-test-integration](.github/skills/loop-test-integration/SKILL.md) | Boundary contracts and cleanup evidence |
| Assess coverage | [loop-test-coverage](.github/skills/loop-test-coverage/SKILL.md) | Measured gaps and meaningful tests |
| Document | [loop-docs](.github/skills/loop-docs/SKILL.md) | Accurate instructions and examples |
| Create skills | [loop-skill-create](.github/skills/loop-skill-create/SKILL.md) | A scoped, synchronized skill contract |
| Review security | [loop-security](.github/skills/loop-security/SKILL.md) | Reachable risks and scoped remediation |
| Refactor | [loop-refactor](.github/skills/loop-refactor/SKILL.md) | Better structure with preserved behavior |
| Repair CI | [loop-ci](.github/skills/loop-ci/SKILL.md) | Job evidence and a verified correction |
| Prepare release | [loop-release](.github/skills/loop-release/SKILL.md) | Candidate readiness and unverified gates |
| Orchestrate | [loop-orchestrate](.github/skills/loop-orchestrate/SKILL.md) | Bounded headless invocations and state |
| Follow up | [loop-prompt](.github/skills/loop-prompt/SKILL.md) | Initial task plus limited inferred prompts |

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
manifest's 22 skills, preserving unrelated skills and backing up overwritten
files under `.loop/backups/`. Select a personal installation root only when
your host supports it and you intend to update it.

Preflight checks catch invalid names, missing source files, paths escaping the
selected root and existing backup conflicts. Backups are created before source
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
copies, stop instructions and bundled runners. It is not a general YAML parser
or proof of model behavior. Tests cover subprocess boundaries and failure paths;
synthetic model decision tests have a narrower scope than complete workflows.
The [CI workflow](.github/workflows/validate.yml) runs on Windows/Linux with
Python 3.11/3.12; consult the actual run before claiming CI success.

## Documentation

- [Usage and workflow selection](docs/SKILL-USAGE.md)
- [Positive and negative acceptance scenarios](docs/SKILL-SCENARIOS.md)
- [Validation commands and evidence](docs/VALIDATION.md)
- [Latest recorded test results](docs/TEST-22-RESULT.md)
- [Host compatibility and runtime evidence](docs/RUNTIME-TEST-MATRIX.md)
- [Writing conventions and reference projects](docs/AUTHORING.md)
- [Contributing](CONTRIBUTING.md) · [Security policy](SECURITY.md)

## License and ownership

An independent project maintained at
[Clas4444/loop-skills-repository](https://github.com/Clas4444/loop-skills-repository),
distributed under the [MIT license](LICENSE). This repository is not a fork of
the reference projects listed in the writing guide and is not affiliated with
OpenAI, Anthropic, GitHub or Microsoft. Reference projects inform presentation;
they do not imply copied implementations or verified host support.
