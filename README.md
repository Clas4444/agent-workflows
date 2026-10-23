# Portable Loop Skills

Cross-agent loop skills for VS Code/Copilot, Codex, and Claude Code.

## Skill families

| Family | Purpose |
|---|---|
| `loop-review` | Review, evaluate, propose, verify, and report |
| `loop-code` | Implement code or configuration in verified batches |
| `loop-diagnose*` | Reproduce, isolate, and diagnose bugs, performance, and regressions |
| `loop-research*` | Research repositories, tools, extensions, plugins, skills, and MCP |
| `loop-test*` | Run unit, integration, coverage, or general testing loops |
| `loop-docs` | Audit and improve documentation |

## Layout

- `.github/skills/` — VS Code/Copilot project skills
- `.agents/skills/` — Codex-compatible project skills
- `.claude/skills/` — Claude Code-compatible project skills
- `docs/` — compatibility and verification records

The same skill content is copied into each native project location. Personal
native installations are not moved or deleted by this repository.

## Safety and loop policy

- Duration is a work budget, never a reason to sleep.
- Stop and write a consolidated report when no suitable work remains or materially
  identical results occur more than three consecutive times.
- Preserve unrelated changes; do not stage, commit, push, install, or delete
  broadly without explicit authorization.
- Record `PASS`, `FAIL`, `BLOCKED`, and `NOT_RUN` distinctly.

See [CONTRIBUTING.md](./CONTRIBUTING.md) for synchronization and validation.
