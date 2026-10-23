# Runtime Test Matrix

Structural compatibility is not the same as runtime compatibility. Before
claiming host support, run at least one representative invocation in the target
host and record:

| Host | Version | Skill | Invocation | Result | Evidence |
|---|---|---|---|---|---|
| VS Code/Copilot | not recorded | not recorded | not recorded | NOT_RUN | pending |
| Codex | not recorded | not recorded | not recorded | NOT_RUN | pending |
| Claude Code | not recorded | not recorded | not recorded | NOT_RUN | pending |

A `PASS` requires evidence that the host discovered the skill, loaded its
instructions, accepted the arguments, and completed a safe representative
workflow. Do not generalize one host's result to another host or version.
