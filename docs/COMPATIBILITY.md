# Compatibility

Compatibility claims in this document are structural, not a guarantee of
identical runtime behavior. See [the runtime matrix](./RUNTIME-TEST-MATRIX.md).

## Classification

All 15 loop skills are structurally VS Code/Copilot-compatible. Each has:

- valid YAML frontmatter;
- a matching lowercase hyphenated `name`;
- `description`;
- `argument-hint`;
- `user-invocable: true`;
- `disable-model-invocation: false`.

The same portable `SKILL.md` content is also copied to Codex and Claude Code
project-native locations.

## Native locations

| Agent | Project skill directory |
|---|---|
| VS Code/Copilot | `.github/skills/` |
| Codex | `.agents/skills/` |
| Claude Code | `.claude/skills/` |

No skill was classified as structurally VS Code-incompatible. Comprehensive
runtime testing across all hosts and versions remains `NOT_RUN`. Existing
personal copies under `C:\Users\tranh` remain untouched.
