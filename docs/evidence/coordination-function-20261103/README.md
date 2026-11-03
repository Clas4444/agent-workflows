# Coordination and functional delivery evidence — 2026-11-03

This packet separates deterministic helper behavior, a historical read-only audit,
and new blocked Codex attempts. It is not proof of live combined product behavior.

- `coord02-audit.json` reconciles the existing12 office traces against their
  frozen source/usage pins; `coord02-regrade-v2.json` is a separate versioned layer.
  Original labels remain in [the original packet](../codex-office-20261103/README.md).
- `function03-protocol.json` froze six planned coding/resume/authority slots.
  `function03-model.json` and CSV retain original and separate prerequisite-v2
  labels. Three attempts consume budget: two completed and one cancelled/unknown.
- `function03-events-sanitized.json` retains all recorded event types, assistant
  messages and counters; removes thread/item identifiers and the local config path.
  Zero command events were recorded. Model-reported restriction does not prove
  an OS cause. Original private traces are not publicly available for replay;
  their SHA256 values identify retained bytes, not independent attestation.
- Measured controller/helper archives match the frozen source pins. They are
  source snapshots, not current entry points. The controller pause fix and final
  helper corrections were made later and were not exercised by these sessions.
- `function03-budget.json` preserves reservations and uncertain cancellation.
  No remaining slot is permission to bypass the unresolved prerequisite.
- Common-v1 fixtures retain their original hashes; local helper tests do not
  establish live peer/model integration. `review-controls.json` records failures
  and repairs without publishing machine-specific logs.

Reproduce public consistency checks from the repository root:

```text
python scripts/coordination_evidence.py
python scripts/evidence_indexes.py
```

The first regenerates the historical v2 analysis and checks new model counters,
statuses, budget and source archive hashes using only published inputs. It does
not reconstruct missing private traces, execute model output or call a model.
The final local gate receipt is published separately under testing sessions to
avoid a verification-input self-reference. No general cost comparison is eligible
for the blocked FUNCTION-03 slots; no comparative chart is warranted.
