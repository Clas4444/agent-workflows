# Validation

This repository is valid when metadata, synchronization, behavior contracts, and
documentation checks all pass. Run the dependency-free validator from the
repository root:

```text
python scripts/validate.py
```

Use `python scripts/validate.py --write-summary --tests-status PASS` to generate
`docs/VALIDATION-RESULT.md` after the validator tests pass. The GitHub Actions
workflow runs the validator and tests on pushes and pull requests. Do not mark
CI or runtime checks as `PASS` unless their actual evidence exists.

Run the focused validator tests as well:

```text
python -m unittest discover -s tests -v
```

On Windows where `python` is not on `PATH`, use `py -3` instead. The validator
report records the exact clean commit or a working-tree fingerprint, and keeps
structural validation, validator tests, CI, and agent runtime checks separate.
`NOT_RUN`, `BLOCKED`, `FAIL`, and `PASS` are not interchangeable.
The generated `docs/VALIDATION-RESULT.md` is excluded from the working-tree
fingerprint so rewriting evidence does not change the source fingerprint it
records. Skills, source, tests, configuration, and other repository files
remain included.

Expected skill count: 17.

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
