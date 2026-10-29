# Releases and compatibility

Version **1.11.3** publishes `skills/workflow-setup` as an independent skill.
Copy the complete package and invoke `$workflow-setup`; the gateway request
`$loop setup` remains available. Ordinary direct workflows remain available
without graph files or cursors. See the [setup guide](../guides/workflow-setup.md).

Workflow Setup works with Agent Workflows alone. Independent attention setup
belongs to Agent Attention; its graph bridge is an optional explicit integration.
See [setup separation checks](../testing/checks/setup-separation.md).

## Compatibility and migration

The 53 skill names, 14 bundles and runner state format remain unchanged.
The separate setup package is not silently added to that catalog or its installer.
Copying SKILL.md alone omits the helper, references, example and catalog. Existing
installation plan IDs must be reviewed again after source/version changes.

Graph contract v1 is shared with the companion repo through vendored helpers;
neither installation imports the other repo. Changed graphs invalidate existing
cursors: review the graph and explicitly restart rather than editing its hash.
Python 3.11+ is required for local helpers. Native slash aliases and an enforced
scheduler are not supplied. Setup alone does not authorize or start execution.

Documentation now follows the [repository layout](repository-layout.md): guides,
references, checks, experiments and history have distinct folders. Use lowercase
canonical paths for new links. Four compatibility pages retain references from
installed instructions and immutable evidence; other old document paths remain
available at their original Git revisions. CLI entry points and root registries
keep their existing names.

## Verification scope

The copied setup helper is tested under isolated Python with its bundled catalog.
These are package/configuration checks, not native picker verification. See
the historical [setup checks](../testing/history/1.11.0-workflow-setup.md) and
[expectation audit](../testing/history/expectation-audit.md). Local deterministic checks,
model measurements and remote CI have separate evidence. Candidate capture JSON
records conditions at capture time; committed=false/pushed=false there describes
the pre-publication measurement, not a live repository status. Historical results
are preserved. Real-model setup interviews and reproducible archives are NOT_RUN.

## Rollback

Stop active work and retain local graphs, cursors and customized instructions.
Restore the previous installed skill payload from its backup or the prior Git
revision. Do not delete the entire host skill directory. Use ordinary direct
workflows or reinstall a compatible graph-v1 helper before continuing a saved
design. Documentation-only moves do not change graph hashes.
