# Release 1.11.0 — 2026-10-29

This release adds optional conditional workflow design through the existing skill.
Install first, verify host discovery, then request setup when a reusable graph is
useful. Ordinary direct work remains available without graph files or cursors.

## Compatibility and migration

The 53 skill names, 14 bundles and runner state format remain unchanged.
Reinstall the selected Loop gateway payload to receive its new helper, reference
and example; copying SKILL.md alone omits required setup resources. Existing
installation plan IDs must be reviewed again after source/version changes.

Graph contract v1 is shared with the companion repo through vendored helpers;
neither installation imports the other repo. Changed graphs invalidate existing
cursors: review the graph and explicitly restart rather than editing its hash.
Python 3.11+ is required for local helpers. Native slash aliases and an enforced
scheduler are not supplied. Setup alone does not authorize or start execution.

## Verification scope

See [setup checks](testing/WORKFLOW-SETUP.md) and the
[expectation audit](testing/EXPECTATION-AUDIT.md). Local deterministic checks,
model measurements and remote CI have separate evidence. Candidate capture JSON
records conditions at capture time; committed=false/pushed=false there describes
the pre-publication measurement, not a live repository status. Historical results
are preserved. Real-model setup interviews and reproducible archives are NOT_RUN.

## Rollback

Stop active work and retain local graphs, cursors and customized instructions.
Restore the previous installed skill payload from its backup or the prior Git
revision. Do not delete the entire host skill directory. Older helpers do not
understand this new setup feature; resume ordinary direct use or reinstall a
compatible graph-v1 helper before continuing a saved design.
