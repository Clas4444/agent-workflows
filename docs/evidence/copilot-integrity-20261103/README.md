# Copilot integrity evidence

Historical cohorts: workflow-only 20 packages/35 CLI and combined 60 packages/90
CLI. New pilot: 12 planned packages, all NOT_RUN, zero CLI. See the
[report](../../testing/experiments/2026-11-03-copilot-integrity.md) for grading layers,
denominators, failures and limits. Parsed synthetic answers are sanitized data;
raw traces, local workspaces and source PDF are excluded. Saved cents functional
acceptance is a historical flag, not a new independently executed checker.

From the repository root, create the ignored `.loop` output directory if absent,
then reproduce offline without the original machine:

```text
python scripts/empirical_audit.py --saved docs/evidence/copilot-integrity-20261103/historical.json --fixture docs/evidence/copilot-integrity-20261103/historical-fixture.json --output .loop/copilot-recomputed-summary.json
python scripts/empirical_figures.py --historical docs/evidence/copilot-integrity-20261103/historical.json --pilot docs/evidence/copilot-integrity-20261103/pilot-observations.json --output .loop/copilot-recomputed-figures
node scripts/empirical_render.cjs .loop/copilot-recomputed-figures
```

Python requires only the standard library. PNG rendering requires Node with
`sharp` available; SVG and chart-data reproduction does not. The aggregate
should equal historical-summary.json. Chart data and SVGs should equal the
published figures. PNG bytes may vary with `sharp`/font/platform versions; the
published byte index identifies this capture, not a universal rendering hash.

The protocol/seal are immutable. The pilot runner requires an explicitly supplied
local stop-marker path and `--execute`; these offline reproduction commands never
call a model. Do not remove a marker to force execution or resume the old grid.
Source hashes are identity records, not execution attestation.
