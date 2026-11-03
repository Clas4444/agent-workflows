# Task status

- State: OFFLINE_VERIFIED_PILOT_STOPPED_PUBLICATION_PENDING
- Started: 2026-11-03.
- WF-01: PASS offline re-aggregation of 80 historical packages / 125 CLI; 367 internal model requests. All saved usage counters and usage hashes match. Original statuses unchanged; revision order and wrapper sensitivity scored separately. Saved cents regrade remains a historical layer, not independently re-executed.
- WF-02: Harness/oracles implemented; 13 focused deterministic tests PASS, including isolated fresh-directory reproduction and extra-file/tool controls; all 14 publication gates PASS (405 tests, 403 PASS, two platform skips). New control bug (null-owner mutation changed nothing) detected and corrected before freeze/calls.
- WF-03: Single-shot three-arm protocol, equal task data, no expected answers; host-isolation acceptance gate required.
- WF-04: Shared sibling stop marker observed (USAGE_UNAVAILABLE). Workflow experimental CLI attempts: 0/12; all 12 planned slots NOT_RUN. No model calls permitted while marker remains.
- WF-05: No product routing/graph change justified by this audit; no version bump.
- WF-06: Public reproducible tables, source/usage pins, four SVG/PNG figures, CSV/JSON chart data and report complete; all 14 local gates PASS with unchanged input pin. Commit/push and exact-SHA remote CI pending at this snapshot.

Next: push the complete reviewed package, then verify Actions and CodeQL on that exact SHA. Local gate summary: docs/testing/sessions/copilot-integrity-20261103.json. Do not resume the old grid or clear the shared stop marker.
