# New Codex office evidence

12 new CLI invocations, separate from Copilot. Original checker labels are all
FAIL; diagnostic-corrected strict acceptance is 11/12, required-fields semantics
12/12. See the [report](../../testing/experiments/2026-11-03-codex-office.md).

From the repository root, reproduce without raw traces or model access:

```text
python scripts/codex_office_analysis.py --packet docs/evidence/codex-office-20261103 --output .loop/codex-office-recomputed
node scripts/empirical_render.cjs .loop/codex-office-recomputed
```

Python uses its standard library. PNG rendering needs Node with sharp available.
JSON/CSV and SVG output should reproduce exactly. PNG bytes can vary with font/
renderer versions; published hashes identify this capture.

protocol.json and seal.json retain the pre-call pin. measured-controller.py is
an exact-byte archive, not a standalone executable entry point in this location.
Its hash matches the protocol's codex_office_pilot.py source pin. Other measured
helpers were unchanged from public source commit
f9262dafc05d2e682d315e0eac800f0885e69618. Current canonical controller/classifier
includes the post-campaign diagnostic fix and must not be claimed as the original
measured source. No calls were rerun after that fix; the 12-call budget is spent.

The observations retain original status/candidate/usage/checks and raw-file hashes.
Item classifications omit diagnostic machine paths. The analysis adds separate
regrade fields; it does not edit original status. The model identity is requested,
not independently resolved by CLI telemetry; backend request counts are unknown.
Matching hashes establish byte identity, not independent execution attestation.
