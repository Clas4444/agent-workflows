# Changelog

Repository updates are listed here; an entry does not imply a published package
or release tag.

## 1.2.0-experimental — 2026-10-24

- Expand from 22 to 27 skills with plan, dependency maintenance, migration,
  end-to-end acceptance and workflow evaluation contracts.
- Add public opt-in Codex fixtures and independent graders, with retained
  evidence and a usage-limit circuit breaker. CI never invokes models.
- Enforce ordered skill contracts, metadata uniqueness/types, bounded
  descriptions and no-sleep policy in the validator.
- Fix empty metadata parsing and optional-duration/authorization contradictions.
- Check scorer portability in a fresh directory and reject hardcoded metrics.
- Synchronize the manifest, catalog, scenarios, runtime guides and installation
  roots. Preserve revision-scoped historical 22-skill evidence.

## 1.1.0-experimental — 2026-10-23

- Add debug, security, refactor, CI and release workflows (22 skills total).
- Repair runner timeout, marker parsing, continuation and persistence evidence.
- Add synchronized runner bundles, backup-aware synchronization and Windows/Linux CI.
- Record real Codex smoke results separately on 2026-10-24.
