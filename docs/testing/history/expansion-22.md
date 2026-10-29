# Expansion to 22 skills

Date: 2026-10-23. Version: 1.1.0-experimental.

Five workflows were added at the user's request:

| Skill | Acceptance gate |
|---|---|
| loop-debug | A reproduced bug receives an authorized repair and verified regression |
| loop-security | Findings trace authorized inputs through trust boundaries to impact |
| loop-refactor | Structural improvement preserves observable behavior |
| loop-ci | A failed pipeline step has evidence, a scoped correction and separate local/remote results |
| loop-release | A candidate has version/build/package/smoke evidence; reproducibility requires repeat-build comparison |

The source, Codex and Claude project layouts contain the same 22 skill files.
The local legacy mirror and Codex/Claude/Copilot personal installations were
also synchronized, preserving overwritten files in `.loop/backups`.

## Loop execution and review

The explicitly requested loop-prompt 3 was executed using the orchestration
runner and a Codex read-only command adapter: one initial review plus three
agent-inferred follow-ups, four invocations total, final PASS. Review angles
were responsibility boundaries, documentation consistency, acceptance cases,
and packaging/integration. PASS here means the review process completed.

The review found ambiguous reproduction status, an imprecise CI access status,
overlap in diagnosis/debug routing, a missing reproducibility gate and stale
compatibility count. These were corrected after inspection. Manual positive
and negative runtime scenarios are documented in SKILL-SCENARIOS.md. Contract
tests check declared evidence and distinct acceptance gates, not model behavior.

## Verification

- PASS: 60/60 local tests, 7.730 seconds, including two expansion contract tests.
- PASS: structural validation and synchronized source copies.
- PASS: explicit Codex headless orchestration (four real review invocations).
- NOT_RUN: native discovery/invocation of each new skill on every supported host.
- NOT_RUN: remote CI execution; no commit, push, tag or release publication.

Raw headless review evidence remains local under `.loop/expansion-review`;
the runtime matrix records its limited scope separately from native skill tests.
