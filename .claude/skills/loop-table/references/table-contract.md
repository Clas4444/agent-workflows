# CSV helper contract

The self-contained `scripts/table_check.py` supports UTF-8 CSV/TSV, including a
UTF-8 BOM, quoted fields and multiline fields. It does not open XLSX, run formulas,
write cleaned files or choose the meaning of columns. Use another suitable host
tool for those operations and verify its actual output separately.

```text
python scripts/table_check.py inspect "/input/expenses.csv"
python scripts/table_check.py aggregate "/input/expenses.csv" --value amount --group category --unit currency
python scripts/table_check.py aggregate "/input/counts.csv" --value count --unit-label items
```

Use `--delimiter "\t"` for TSV or another explicit single delimiter. The default
row cap is 100000; `--max-rows` changes it explicitly. Empty/duplicate or ambiguous
headers, ragged records and invalid decimal tokens fail. There is no locale,
thousands-separator or scientific-notation guessing. Identifiers remain strings.

Aggregation requires an explicit unit column or one declared unit label. Unit
labels are kept separate, without currency conversion. Decimal sums preserve
precision across integer/fractional scales. Missing numeric values fail by
default; `--allow-missing` reports incomplete known-value sums and record IDs.
It never silently substitutes zero. A header-only input gives no observations,
not evidence that a real-world total is zero.

The helper prints JSON to stdout and diagnostics to stderr. It leaves source
bytes unchanged. Structural PASS, numeric PASS, formula recalculation and visual
inspection are distinct. Formula-like text is identified for review and never
executed; inspection does not certify that a future spreadsheet application will
handle imported text safely.
