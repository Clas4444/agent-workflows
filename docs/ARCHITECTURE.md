# Repository architecture

The skill catalog, runner and verification tooling have separate contracts.
This layout keeps the catalog, runner and verification tools separate. Native
skill directories remain flat; historical evidence is versioned independently.

| Location | Responsibility |
|---|---|
| `.github/skills/` | Canonical skill instructions and bundled runner copies |
| `.agents/skills/`, `.claude/skills/` | Synchronized host layouts |
| `scripts/run_loop.py` | Standalone continuation runner; also distributed inside two skills |
| `scripts/validate.py` | Repository integrity checks, CLI and validation report |
| `scripts/acceptance_gate.py` | Opt-in acceptance/source identity contract and local subprocess evidence |
| `scripts/catalog.py`, `skill-groups.json` | Functional group coverage and generated README catalog |
| `scripts/routing_check.py`, `skill-routing.json` | Per-skill decisions, overlap review and fixed primary-route cases |
| `scripts/validation/manifest.py` | Manifest model, names, version and safe native roots |
| `scripts/validation/json_data.py` | Shared strict JSON input: reject duplicate decoded keys and NaN/Infinity literals |
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

Historical refactors and runtime campaigns retain their recorded scope; later
instruction changes are tracked in the invalidation index. The 2026-10-25
hardening rejects unsafe evidence aliases and strengthens graders without
changing marker names or existing CLI flags. Deterministic regression tests
characterize those changes separately from model runtime. The runner stays
self-contained so copied skills do not depend on repository-only modules.

MCP/A2A/API adapters, OAuth flows, telemetry exporters and runtime policy
enforcement require separate scoped implementation and tests. Markdown guidance
does not enforce sandboxing, prevent prompt injection or provide authentication.
