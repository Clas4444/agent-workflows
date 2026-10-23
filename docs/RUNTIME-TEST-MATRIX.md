# Runtime test matrix

Structural validation does not prove runtime compatibility. Before claiming
support for a host, run one representative workflow and record how the host
discovered the skill, loaded its instructions, accepted the invocation, and
completed safely.

| Host | Version | Skill | Invocation | Result | Evidence |
|---|---|---|---|---|---|
| VS Code/Copilot | not recorded | not recorded | not recorded | `NOT_RUN` | pending |
| Codex | not recorded | not recorded | not recorded | `NOT_RUN` | pending |
| Claude Code | not recorded | not recorded | not recorded | `NOT_RUN` | pending |

Do not generalize one host's result to another host or version. Keep runtime
evidence separate from the local fake-command tests for `run_loop.py`.
