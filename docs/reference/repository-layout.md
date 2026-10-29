# Repository layout and naming

Agent Workflows separates maintained instructions, implementation, user guidance
and execution records. Directory placement communicates which source to edit.

| Location | Content and editing rule |
|---|---|
| Repository root | Project identity, license, contribution/security policy and catalog registries consumed by public tools |
| `.github/skills/` | Canonical source of the 53 bounded workflows |
| `.agents/skills/`, `.claude/skills/` | Generated host copies; synchronize from canonical sources |
| `skills/workflow-setup/` | Independent, self-contained Workflow Setup package, separate from the 53-workflow catalog |
| `scripts/` | Repository tools and canonical helper implementations; stable command entry points |
| `tests/` | Deterministic regression tests; no model calls |
| `schemas/` | Versioned data contracts |
| `docs/guides/` | Instructions for a user completing a task or installing a selection |
| `docs/reference/` | Architecture, authoring, compatibility and technical contracts |
| `docs/testing/` | Testing procedure, evidence index and navigation |
| `docs/testing/checks/` | Configuration checks and validation records, each limited to its recorded scope |
| `docs/testing/experiments/` | Dated model experiments with explicit denominators and limitations |
| `docs/testing/history/` | Earlier release reports, audits and development records |
| `docs/testing/sessions/` | Original session captures; do not rewrite recorded pins or outcomes |
| `docs/evidence/` | Immutable published packets and byte indexes; preserve original names and bytes |
| `docs/assets/` | Shared diagrams and visual assets |
| `.loop/` | Ignored local maps, raw traces, attempts and backups; never force-add |

## Names

- Maintained document names use lowercase words separated by hyphens:
  `workflow-setup.md`, `runtime-smoke.md`.
- Dated reports put the date first: `2026-10-30-workflow-advanced.md`. Older
  release reports may use a version prefix: `1.10-results.md`. Do not invent a
  date for an undated historical record.
- A readable check and its JSON observation use the same stem where applicable:
  `setup-separation.md` and `setup-separation.json`.
- Python modules and tests use `snake_case.py`; skill directories and registry
  JSON files use `kebab-case`. Names follow the owning ecosystem rather than
  forcing one spelling convention onto every file type.
- Keep conventional names such as `README.md`, `SKILL.md`, `AGENTS.md`,
  `CHANGELOG.md` and `LICENSE`. Existing immutable captures are naming exceptions.

## Content and evidence

A current guide explains what to do; a technical reference defines a contract;
an experiment identifies source/model/configuration, fixtures, measurements and
limits. Historical PASS, FAIL, BLOCKED, STALE and NOT_RUN observations stay
historical. Moving a report does not rerun it or certify current code.

During this reorganization, historical Markdown changes are limited to local
link destinations needed for navigation. Historical JSON captures retain their
original Git bytes, including old path labels. Their old input scopes must not
be rewritten to imply they tested the new directory layout. All indexed packets
under `docs/evidence/` remain unchanged.

## Compatibility entry points

Four old Markdown paths remain as short links to maintained locations:

- `docs/ACCEPTANCE-GATE.md`: referenced by installed workflow instructions.
- `docs/EVIDENCE.md`: established evidence-index entry point.
- `docs/testing/BUNDLE-ATLAS-2026-10-26.md` and
  `docs/testing/DOCS-REVIEW-1.10-2026-10-26.md`: referenced by immutable packets.

Other old paths remain available at their original Git revisions. New links
use the canonical locations in this layout. Existing CLI names and root
registries are retained; users do not need to change their tool commands.

See [all documentation](../README.md), [testing](../testing/README.md) and
[standalone skills](../../skills/README.md).
