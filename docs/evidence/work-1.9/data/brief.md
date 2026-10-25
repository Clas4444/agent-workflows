# Expense brief
Source: expenses.csv, records 1–4 (header excluded). SHA-256: cdce1b44143780bc36e015e656d704fe0fff426d96e64d374b429e5e616f56b2.

Contract: all records are included in coverage. Sum known decimal amounts within each category/currency only; blank amounts are unknown, never zero. No conversion or combined currency total.

| Category | Currency | Known subtotal | Coverage |
|---|---|---|---|
| Travel | USD | 10.30 | 2/2 (records 1–2) |
| Travel | EUR | 5.00 | 1/1 (record 3) |
| Food | USD | unknown | 0/1 (record 4) |

Amount coverage is 3/4 (75%); record 4, ID 004, has a missing amount. Every other column has 4/4 nonblank values. No duplicate IDs or duplicate full rows were observed. IDs remain strings 001, 002, 003, 004. Overall data is incomplete; these are known-value subtotals, not a complete expense total.

Record 2, ID 002, note is formula-like text. The helper detected it; it was treated only as data. No formula or link was executed. Future spreadsheet import safety is not certified. CSV has no workbook sheets or hidden-sheet context to inspect.

Structural inspection: PASS. Exact known-value aggregation: PASS. Completeness: incomplete. Formula execution/recalculation: NOT_RUN. Spreadsheet rendering: NOT_RUN. Source preservation is checked in result.json.
