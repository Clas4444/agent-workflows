# Expense briefing

The source contains 7 rows. Amounts are incomplete: source IDs 004 and 007 have blank amounts, which are unknown rather than zero.

| Category | Currency | Known subtotal | Source IDs with known amounts | Source IDs with missing amounts |
| --- | --- | --- | --- | --- |
| Food | EUR | 5.00 | 003 | None |
| Food | USD | 10.30 | 001, 002 | 004 |
| Other | JPY | Unknown (all amounts blank) | None | 007 |
| Travel | USD | 0.00 | 005, 006 | None |

Food USD's known subtotal excludes the unknown amount at ID 004. Other JPY has no known subtotal because ID 007 is blank. Travel USD totals -2.00 + 2.00 = 0.00, with no missing amounts.

Groups are sorted by category, then currency. Source IDs retain leading zeros. Currencies are kept separate; no conversion or grand total is included.
