# COORD-02 and FUNCTION-03 chart sources

The historical office12 calls and FUNCTION-03 six planned slots are separate.
No model call or old-record edit was needed to create these figures. Graph style
matches the existing report figures. All four SVGs were rendered to PNG and viewed.

| Figure | Scope | Sources |
|---|---|---|
| [Historical quality PNG](historical-quality.png) / [SVG](historical-quality.svg) | Strict diagnostic-corrected acceptance, derived recursive key/type schema, required-field semantics; n4/arm | [historical-quality.csv](historical-quality.csv), [runs](historical-runs.csv) |
| [Historical costs PNG](historical-cost.png) / [SVG](historical-cost.svg) | Individual token/time observations; two repeats/case/arm, no fitted line | [historical-runs.csv](historical-runs.csv) |
| [FUNCTION-03 states PNG](function03-status.png) / [SVG](function03-status.svg) | Two prerequisite-v2 BLOCKED, one cancelled/unknown, three NOT_RUN; original FAIL labels retained | [function03-slots.csv](function03-slots.csv) |
| [FUNCTION-03 observed costs PNG](function03-observed-cost.png) / [SVG](function03-observed-cost.svg) | Only two attempts have measured input/output/cache/time; missing values are crosses, never zero | [function03-slots.csv](function03-slots.csv) |

[chart-data.json](chart-data.json) contains every chart row and SHA256 pins for
the [published source packet](../coordination-function-20261103/README.md).
Structural schema is a derived key/type-only layer, not a new model run, value
check or replacement for the preserved original rubric. No eligible FUNCTION-03
efficacy/cost A/B comparison follows from failed prerequisites. Its cancelled
attempt usage is unknown; total campaign usage cannot be reconstructed.

Reproduce tables/SVG from repository root using only the published inputs:

```text
python scripts/coordination_charts.py --write
python scripts/coordination_charts.py
```

Optional PNG rendering requires Node.js and the standard sharp package available
on the module path:

```text
node scripts/empirical_render.cjs docs/evidence/coordination-function-charts-20261103
```

The default Python check compares regenerated table/SVG bytes. PNG bytes are
indexed, and their dimensions/signatures are tested; rasterization may vary with
renderer/font versions. The committed PNGs were visually reviewed. Their hashes
are recorded in [published-hashes.json](published-hashes.json). Negative controls
remain a qualitative before/after evidence table in the report; heterogeneous
controls do not provide an independent paired model-score series to plot.
