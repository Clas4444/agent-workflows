# Contributing

This repository distributes one portable set of 39 workflow skills in three
native project layouts. Contributions should improve clarity or correctness
without changing a workflow's responsibility or silently widening its scope.

## Source and synchronization

1. Edit `.github/skills/<skill-name>/SKILL.md`.
2. Copy that exact file to the matching `.agents/skills/` and `.claude/skills/`
   directories.
3. Confirm all three SHA-256 hashes match.
4. Update documentation when the workflow, command, output, or limitation
   changes.

The manifest in `skills-manifest.json` is the authoritative skill list. Do not
add a skill directory without adding its name and all three copies.

## Skill requirements

Follow [the writing guide](docs/AUTHORING.md): Use when, Inputs, Workflow,
Output, Boundaries and evidence, and a concrete Example. Keep the description
specific enough to select the right workflow without loading every skill.

Each skill must:

- use the existing YAML frontmatter fields and a lowercase hyphenated name;
- explain when to use it, what it accepts, what it may change, and what it
  reports;
- preserve bounded work, explicit verification, safety boundaries, and
  `PASS`, `FAIL`, `BLOCKED`, and `NOT_RUN` states;
- stop on no useful work, a deadline, a safety boundary, or materially repeated
  results, and never sleep to consume time;
- remain below 500 lines and pass the repository validator.

Do not add dependencies, tools, extensions, plugins, MCP servers, permissions,
or host-compatibility claims without explicit authorization and evidence.

## Validation

Read [AGENTS.md](AGENTS.md) for the agent workflow and
[architecture](docs/ARCHITECTURE.md) for module ownership. Use the full default
validator gate for contributions; `--profile format` is diagnostic only.

From the repository root, run:

```text
python -m unittest discover -s tests -v
python scripts/validate.py
python -m scripts.validate --profile format
python scripts/catalog.py
python scripts/routing_check.py
python scripts/workflows.py
python scripts/install_skills.py --list
python scripts/sync_skills.py --target .github/skills --check
python scripts/runtime_smoke.py --help
python -m compileall -q scripts tests
git diff --check
```

Do not mark CI or host-runtime checks as `PASS` without recorded evidence.
Keep generated validation evidence factual, and review the final diff for
unrelated files or captured sensitive output.

Use an installed Python 3.11+ interpreter; on Windows, `py -3` is an alternative
only when that launcher is present. See [test procedure](docs/testing/TESTING.md)
for gate scopes and skip handling. Edit `workflow-presets.json` and regenerate
with `python scripts/workflows.py --write` when role recommendations change.

Need-bundle changes belong in `skill-bundles.json`; test subset installs as well as full synchronization. Use a fresh session-pinned campaign when recording final verification, and do not reuse a previous session's PASS after editing inputs.
