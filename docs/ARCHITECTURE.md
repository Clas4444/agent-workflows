# Repository architecture

The skill catalog, runner and verification tooling have separate contracts. Native
skill directories remain flat; historical evidence is versioned independently.

| Location | Responsibility |
|---|---|
| `.github/skills/` | Canonical skill instructions and bundled runner copies |
| `.agents/skills/`, `.claude/skills/` | Synchronized host layouts |
| `scripts/run_loop.py` | Standalone continuation runner; also distributed inside two skills |
| `scripts/validate.py` | Repository integrity checks, CLI and validation report |
| `scripts/acceptance_gate.py` | Opt-in acceptance/source identity contract and local subprocess evidence |
| `scripts/catalog.py`, `skill-groups.json` | Functional group coverage and generated README catalog |
| `scripts/discovery.py`, `.github/skills/loop/` | Generated canonical-name/bundle catalog and Codex UI metadata; portable read-only lookup, not a host command registrar |
| `scripts/routing_check.py`, `skill-routing.json` | Per-skill decisions, overlap review and fixed primary-route cases |
| `scripts/validation/manifest.py` | Manifest model, names, version and safe native roots |
| `scripts/validation/json_data.py` | Shared strict JSON input: reject duplicate decoded keys and NaN/Infinity literals |
| `scripts/validation/skill_format.py` | Core metadata checks for the supported single-line subset |
| `scripts/validation/loop_policy.py` | Local headings, invocation flags, examples, statuses and stop conventions |
| `scripts/sync_skills.py` | Explicit-root synchronization, preflight and backups |
| `scripts/runtime_smoke.py` | Opt-in host execution and evidence collection |
| `scripts/smoke_cases.py` | Compatibility facade retaining the existing fixture/grader imports |
| `scripts/smoke/fixtures.py` | Synthetic task inputs, preparation and source snapshots |
| `scripts/smoke/grading.py` | Artifact grading and bounded verification subprocesses |
| `scripts/workflows.py`, `workflow-presets.json` | Inventory-checked role guidance and editable SVG |
| `scripts/docs_check.py` | Read-only local Markdown file/image and heading navigation checks; no URL fetching or renderer claim |
| `scripts/install_skills.py`, `scripts/skill_bundles.py`, `skill-bundles.json` | Explicit need-based selection using the existing sync engine |
| `scripts/doctor_skills.py` | Read-only selected-install diagnosis with observed before/after reference pins; no host discovery or writes |
| `scripts/verification_session.py` | Fixed gate campaign with session identity and before/after verification-input hashes |
| `scripts/evidence_indexes.py` | Declared published-byte index integrity; strict relative paths and aliases, no artifact execution or attestation |
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

## Navigation without installation churn (1.7)

The new project-workflows group coordinates explicit project, PR and incident
lifecycles. It does not replace focused code, plan, review or debug skills.
Role presets recommend a small toolkit; neither presets nor groups are runtime
dispatchers. Generated Markdown/SVG are checked in CI against the manifest.
PNG illustrations are explanatory snapshots, not executable configuration.

The smoke module split retains both `scripts.smoke_cases` package imports and
the direct `python scripts/runtime_smoke.py` entry point. Fixture preparation
does not execute submissions; grading owns subprocess verification. The retained
23 runtime-smoke characterization tests and boundary tests exercise both sides.
See [test procedure](testing/TESTING.md) and [1.7 results](testing/RESULTS-1.7.md).

## Everyday needs and session identity (1.8)

Three new groups cover communication, organization and decision/learning tasks.
They provide agent instructions, not mail/calendar/file-service integrations.
Need bundles are overlapping installation selections; groups remain a disjoint
navigation partition. Neither structure is a mandatory runtime dispatcher.

The existing `sync(target, backup, check=False)` API retains full-catalog behavior.
Its optional keyword-only `selected` list restricts the same preflight, backup and
copy engine. Empty/unknown selections fail rather than silently selecting all.
The need-based CLI resolves bundle unions before invoking that engine.

Session verification pins production code, tests, schemas, host copies, CI,
catalog/installation metadata, README and declared guide/evidence inputs.
The exact scope is recorded in each report. Raw logs and session-report prose
under `docs/testing/` are excluded to avoid a report hashing itself. A source
change during the campaign yields STALE, and verification rejects another
session ID, changed inputs or missing gate results. This is provenance checking,
not cryptographic attestation of an untrusted report's execution.

## Complete payloads and historical identity (1.9)

`skill-resources.json` declares supporting files; `scripts/skill_resources.py` is shared by validation and sync. Repository-native inventories are exact; selected external installs preserve unmanaged extras. Source/destination aliases and resource case collisions fail preflight. Both validation profiles retain resource integrity. Helpers are self-contained and live inside their owning canonical skill, not duplicated root implementations.

`instruction_history.py` verifies archived 1.7/1.8 bytes plus explicit current-hash
invalidations. It does not turn historical runtime PASS into new execution. The
generated install table uses the same registry as the CLI. The 1.10 session runner
has fourteen gates, defined by `COMMANDS` in `scripts/verification_session.py`;
old records retain their original recipe. `git diff --check` is a separate check.

## Selection and delivery (1.10)

![Request, selection, installation and verified output](assets/loop-workflow.svg)

The `loop` gateway resolves a selector to canonical skills or a need bundle.
Its bundled catalog supports lookup even outside this repository. It reports
missing installed instructions; it does not install them or execute task text.
`agents/openai.yaml` supplies display metadata for supporting hosts. A metadata
file or successful CLI lookup cannot establish native discovery.

Groups partition the 53 skills into fifteen navigation categories. Fourteen
bundles are overlapping installation selections. Role presets are task guidance.
None requires running every listed member. See [start here](guides/START-HERE.md)
for an installation-to-use example and [evidence](EVIDENCE.md) for tested scope.
