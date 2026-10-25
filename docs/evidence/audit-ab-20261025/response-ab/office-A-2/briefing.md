# Expense briefing

The source contains 7 rows. The report is incomplete because IDs `004` and `007` have blank, unknown amounts.

| Category | Currency | Known subtotal | Source IDs with known amounts | Missing amount IDs |
| --- | --- | --- | --- | --- |
| Food | EUR | 5.00 | `003` | None |
| Food | USD | 10.30 | `001`, `002` | `004` |
| Other | JPY | Unknown (null) | None | `007` |
| Travel | USD | 0.00 | `005`, `006` | None |

Food USD's known subtotal excludes the unknown amount at ID `004`. Other JPY has no known amount, so its subtotal is null. Travel USD's known amounts, -2.00 and 2.00, sum to 0.00.

Groups are sorted by category, then currency. IDs retain their leading zeros, and missing IDs follow source order. No currency conversion or grand total is included.
