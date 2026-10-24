# Repository architecture

The skill catalog, runner and verification tooling have separate contracts.
This layout does not add an agent service or change the 27 skill instructions.

| Location | Responsibility |
|---|---|
| `.github/skills/` | Canonical skill instructions and bundled runner copies |
| `.agents/skills/`, `.claude/skills/` | Synchronized host layouts |
| `scripts/run_loop.py` | Standalone continuation runner; also distributed inside two skills |
| `scripts/validate.py` | Repository integrity checks, CLI and validation report |
| `scripts/validation/manifest.py` | Manifest model, names, version and safe native roots |
| `scripts/validation/skill_format.py` | Core metadata checks for the supported single-line subset |
| `scripts/validation/loop_policy.py` | Local headings, invocation flags, examples, statuses and stop conventions |
| `scripts/sync_skills.py` | Explicit-root synchronization, preflight and backups |
| `scripts/runtime_smoke.py`, `scripts/smoke_cases.py` | Opt-in model execution and independent artifact grading |
| `tests/` | Deterministic local tests; no model calls |
| `schemas/` | Versioned machine-readable descriptions of existing data contracts |
| `docs/evidence/` | Reviewed public execution summaries with provenance |
| `.loop/` | Ignored local attempts, sensitive raw logs and backups |

## Validation profiles

`python scripts/validate.py` remains the full gate and retains its public
Python imports, error messages, exit behavior and report format. It composes
manifest, metadata, Loop policy and synchronization checks.

`--profile format` omits the Loop policy layer while retaining manifest,
metadata, copy identity and bundled-runner integrity. It is a repository
diagnostic, not a validator for arbitrary third-party skill packages. It cannot
write the full-gate summary. Neither profile parses arbitrary YAML.

The six headings, four status words, literal invocation flags, slash example,
500-line limit and no-sleep rule are Loop project conventions. They are not
universal requirements of the Agent Skills specification. Host interpretation
of invocation metadata is distinct from either profile.

## Compatibility and scope

The refactor does not alter runner output or existing skill instructions.
Historical runtime evidence therefore retains its original scope; deterministic
regression tests characterize the verification changes separately. The runner
stays self-contained so copied skills do not depend on repository-only modules.

MCP/A2A/API adapters, OAuth flows, telemetry exporters and runtime policy
enforcement require separate scoped implementation and tests. Markdown guidance
does not enforce sandboxing, prevent prompt injection or provide authentication.
