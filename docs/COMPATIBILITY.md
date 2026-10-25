# Compatibility

This document records structural compatibility only. It does not prove that
all hosts interpret the skills or metadata in the same way. Runtime evidence is
tracked separately in [RUNTIME-TEST-MATRIX.md](./RUNTIME-TEST-MATRIX.md).

## Project layouts

| Host target | Project skill root | Status |
|---|---|---|
| VS Code with Copilot | `.github/skills/` | Structural checks pass |
| Codex | `.agents/skills/` | Files are synchronized; scoped runtime evidence is in the runtime matrix |
| Claude Code | `.claude/skills/` | Files are synchronized; runtime is `NOT_RUN` |

All 45 skills have valid frontmatter, matching lowercase hyphenated names,
descriptions, argument hints, and the existing invocation flags. Each copy is
byte-identical to the canonical `.github/skills/` file.
The historical 22-skill smoke report applies to its recorded revision, not
automatically to later instruction changes or the five 1.2 additions.

To claim runtime support for a host, record the host version, discovered skill,
invocation, result, and evidence in the runtime matrix. Do not generalize
evidence from one host or version to another.

The repository does not modify personal installations automatically. The
explicit `scripts/sync_skills.py --target ...` command can update an authorized
personal skill root with backups. See the README synchronization instructions.
Managed destinations reject hardlinks and symlink/reparse-point components
below the selected root, even aliases resolving within that root. This prevents
an internal alias from overwriting an unrelated skill. Windows junctions are
checked via reparse attributes on Python 3.11 as well. The explicitly selected
root itself is resolved first. Concurrent alias changes are not locked out.
