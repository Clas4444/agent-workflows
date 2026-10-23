# Compatibility

## Classification

All 14 loop skills are VS Code/Copilot-compatible. Each has:

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

No skill was classified as VS Code-incompatible. Existing personal copies under
`C:\Users\tranh` remain untouched.
