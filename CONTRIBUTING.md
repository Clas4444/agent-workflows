# Contributing

## Source of truth

Edit a skill in `.github/skills/<skill-name>/SKILL.md` first. Then copy the exact
file to the matching `.agents/skills/` and `.claude/skills/` directories.

## Required checks

For every skill:

1. The directory name matches the frontmatter `name`.
2. `description` is present and describes what and when to use.
3. The file has YAML frontmatter and remains below 500 lines.
4. The content records `PASS`, `FAIL`, `BLOCKED`, and `NOT_RUN`.
5. The loop has an explicit no-sleep rule and duplicate/no-work break condition.
6. All three copies have identical SHA-256 hashes.

Do not install packages, extensions, plugins, or MCP servers as part of a skill
change unless the user explicitly authorizes it.
