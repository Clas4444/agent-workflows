# Validation

This repository is valid when metadata, synchronization, behavior contracts, and
documentation checks all pass. Run the dependency-free validator from the
repository root:

```text
python scripts/validate.py
```

Use `python scripts/validate.py --write-summary` to generate
`docs/VALIDATION-RESULT.md` for a local evidence snapshot. The GitHub Actions
workflow runs the validator on pushes and pull requests.

Expected skill count: 14.

For each skill, verify:

- `SKILL.md` exists in all three native project trees.
- `name` matches the containing directory.
- `description` is present and the file is under 500 lines.
- All copies have identical SHA-256 hashes.
- Instructions distinguish `PASS`, `FAIL`, `BLOCKED`, and `NOT_RUN`.
- Instructions prohibit idle sleep and define the no-work/duplicate-result break.

Generated validation results belong in this repository when they are intended
to be shared. Reports about work performed outside this repository may use a
configured report directory or a workspace-relative `Markdown` directory.
