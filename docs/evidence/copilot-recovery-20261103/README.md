# Copilot recovery and requested line charts

The historical combined/cents line charts contain all six arms and five independent repetitions per arm (30 packages). They are not a learning curve. Input table: ../copilot-integrity-20261103/figures/historical-runs.csv. Token totals are input + output; cache is not added again.

Reproduce from the repository root:

```text
python scripts/empirical_lines.py --source-table docs/evidence/copilot-integrity-20261103/figures/historical-runs.csv --output .loop/combined-cents-lines
node scripts/empirical_render.cjs .loop/combined-cents-lines
```

Python needs only its standard library. PNG rendering optionally requires Node and sharp. Source-table hash and all 30 numeric chart points are in figures/line-data.json and figures/line-data.csv. The historical source packet remains unchanged. Recovery model observations will be reported separately, never joined to historical repetitions.
