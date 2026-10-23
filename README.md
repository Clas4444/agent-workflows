# Portable Loop Skills

Cross-agent loop skills for VS Code/Copilot, Codex, and Claude Code.

> **Status: experimental.** The repository contains portable workflow
> instructions, not a guarantee that every host implements every field or
> behavior identically. Compatibility means the files follow supported skill
> layouts and metadata; host-level runtime behavior still needs testing.

This is an independent personal project and is not affiliated with GitHub,
Microsoft, OpenAI, Anthropic, or the maintainers of any referenced tool.

## Skill families

| Family | Purpose |
|---|---|
| `loop-review` | Review, evaluate, propose, verify, and report |
| `loop-code` | Implement code or configuration in verified batches |
| `loop-diagnose*` | Reproduce, isolate, and diagnose bugs, performance, and regressions |
| `loop-research*` | Research repositories, tools, extensions, plugins, skills, and MCP |
| `loop-test*` | Run unit, integration, coverage, or general testing loops |
| `loop-docs` | Audit and improve documentation |
| `loop-skill-create` | Create and maintain skills with synchronized evidence |
| `loop-orchestrate` | Continue bounded work through a configured headless agent command |
| `loop-prompt` | Infer and run a bounded number of follow-up prompts |

## Layout

- `.github/skills/` — VS Code/Copilot project skills
- `.agents/skills/` — Codex-compatible project skills
- `.claude/skills/` — Claude Code-compatible project skills
- `docs/` — compatibility and verification records

The same skill content is copied into each native project location. Personal
native installations are not moved or deleted by this repository.

## Verification status

- Structural validation: checked for 17 skills, valid metadata, matching names,
  and identical copies across the three project roots.
- Repeatable validation: run `python scripts/validate.py` and
  `python -m unittest discover -s tests -v`; the same checks run on pushes and
  pull requests through GitHub Actions.
- Host runtime validation: **not yet comprehensively tested** across all three
  agent products and versions.
- Treat each skill as a starting workflow. Review commands, permissions, data
  handling, and project-specific instructions before use.

## Scope and non-goals

These skills provide procedural guidance for coding-agent workflows. They do not
provide a security guarantee, replace project tests, authorize changes, or
install tools and integrations automatically.

## Safety and loop policy

- Duration is a work budget, never a reason to sleep.
- Stop and write a consolidated report when no suitable work remains or materially
  identical results occur more than three consecutive times.
- Preserve unrelated changes; do not stage, commit, push, install, or delete
  broadly without explicit authorization.
- Record `PASS`, `FAIL`, `BLOCKED`, and `NOT_RUN` distinctly.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for synchronization and validation.
See [SECURITY.md](./SECURITY.md) for responsible vulnerability reporting.
See [docs/VALIDATION.md](./docs/VALIDATION.md) for the reproducible validation
command and evidence format.
See [docs/SKILL-USAGE.md](./docs/SKILL-USAGE.md) for a skill selection guide,
command examples, sequencing, and `/loop-prompt` limits.
See [loop-orchestrate](./.github/skills/loop-orchestrate/SKILL.md) for the
optional headless continuation harness and its safety limits.
See [docs/ORCHESTRATION.md](./docs/ORCHESTRATION.md) for host command examples
and the exact continuation protocol.
