# Validation

This repository is valid when metadata, synchronization, behavior contracts, and
documentation checks all pass.

Expected skill count: 14.

For each skill, verify:

- `SKILL.md` exists in all three native project trees.
- `name` matches the containing directory.
- `description` is present and the file is under 500 lines.
- All copies have identical SHA-256 hashes.
- Instructions distinguish `PASS`, `FAIL`, `BLOCKED`, and `NOT_RUN`.
- Instructions prohibit idle sleep and define the no-work/duplicate-result break.

The check result for the initial repository creation is recorded in the session
report under `C:\Code\Markdown`.
