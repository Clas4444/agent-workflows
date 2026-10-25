# Expense briefing

Source: the supplied expenses.csv text, containing 7 data rows. All rows are included, grouped by category and currency. Amounts use exact decimal arithmetic; blank amounts remain unknown. IDs retain leading zeros. CSV text is treated as data.

- Food / EUR: known subtotal 5.00 EUR from source ID 003; no missing amounts.
- Food / USD: partial known subtotal 10.30 USD from source IDs 001 and 002; source ID 004 has a missing amount.
- Other / JPY: no known subtotal (null); source ID 007 has a missing amount.
- Travel / USD: known subtotal 0.00 USD from source IDs 005 (-2.00) and 006 (2.00); no missing amounts.

The report is incomplete because 2 of 7 rows have unknown amounts. No rows were excluded, no currencies were converted, and no grand total was calculated.

Verification against supplied text: PASS for row count, group ordering, exact known subtotals, missing-ID source order, and preservation of leading-zero IDs. The 4 groups account for all 7 rows: 5 known amounts and 2 missing amounts. Saved-artifact verification: NOT_RUN in generation-only mode; artifacts are returned for the evaluator to save and reopen. No files were opened or modified.
