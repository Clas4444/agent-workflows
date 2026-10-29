# 1.2 gap assessment and expansion to 27 skills

Date: 2026-10-24. Version: 1.2.0-experimental.

## Assessment of the 22-skill system

The existing set covers implementation, diagnosis, research, tests, security,
refactoring, CI and release, and has scoped 22-case Codex smoke evidence.
Its main gaps were lifecycle coverage and reproducibility of the evaluation
process, rather than a need for more near-identical debugging names.

| Gap | Addition | Distinct acceptance gate |
|---|---|---|
| Multi-step work starts without a dependency-aware plan | loop-plan | Verifiable batches before implementation |
| No dedicated manifest/lockfile maintenance workflow | loop-dependencies | Approved compatible versions, consistent lockfile and rollback |
| Persisted data changes lack an explicit migration protocol | loop-migrate | Dry-run, invariants, backup, idempotence and exercised rollback |
| Existing tests stop at unit/integration boundaries | loop-test-e2e | Real user entry point through output, errors and side effects |
| Skill quality relies on ad hoc/local evaluation | loop-evaluate | Fixed rubric, denominators, false-positive/negative evidence |

## System-wide corrections

- Added five full contracts, examples and distinct routing guidance, not aliases.
- Updated manifest, README catalog, usage guide, compatibility, scenarios,
  authoring expectations and project/personal installation copies together.
- Fixed optional-duration contradictions in loop-review/loop-code and clarified
  that existing authorization should not trigger repeated permission questions.
- Strengthened the validator: ordered contract sections, examples, duplicate
  metadata, literal booleans, bounded descriptions and explicit no-sleep rule.
- Fixed empty metadata values accidentally consuming the next line; reject an
  invalid manifest before using its paths.
- Added mutation tests that change every copy together so hash synchronization
  alone cannot mask a broken contract.
- Added a public opt-in runtime harness with versioned fixtures, independent
  graders, a quota circuit breaker and retained per-attempt evidence.
- Added negative grader checks, including dependency drift and a hardcoded
  evaluation scorer that passes nominal inputs but fails perturbed inputs.
- Fixed Windows cp1252 failures by declaring UTF-8 at production/test text-I/O
  boundaries, with a smart-quote regression and a guard against new implicit I/O.
- Corrected overly literal plan-heading grading while preserving tests for truly
  missing scope. A fresh-directory evaluation check exposed and fixed an
  undocumented report-file prerequisite in a model-generated scorer.

Historical 22-skill reports retain their source revisions and results. They
are not rewritten as tests of 27 skills. New runtime results and remaining
gaps are recorded separately after executing the current fixtures.

## Remaining boundaries

Automatic discovery without explicit skill names, Copilot/Claude runtime,
production migrations, live advisory integration, UI-specific E2E and exhaustive
model evaluation remain separate work. Neither a new skill nor a source match
proves those behaviors. No new third-party dependency is required by this expansion.
