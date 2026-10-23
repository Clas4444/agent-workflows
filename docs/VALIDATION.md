# Validation

The validator checks the manifest, skill metadata, three-root synchronization,
required safety/reporting rules, and the generated evidence fingerprint. It
uses only the Python standard library.

Run from the repository root:

```text
py -3 -m unittest discover -s tests -v
py -3 scripts\validate.py
py -3 -m py_compile scripts\run_loop.py scripts\validate.py tests\test_validate.py
git diff --check
```

On systems where `py -3` is unavailable, use the installed Python command
documented by that environment. A missing command is `NOT_RUN`, not `PASS`.

## Evidence

Generate the report after the tests and validator pass:

```text
py -3 scripts\validate.py --write-summary --tests-status PASS --ci-status NOT_RUN --runtime-status NOT_RUN
```

`docs/VALIDATION-RESULT.md` records structural status, test/CI/runtime status,
the clean commit or a working-tree fingerprint, and findings. `PASS`, `FAIL`,
`BLOCKED`, and `NOT_RUN` are distinct and must reflect actual evidence.

The generated report is excluded from the fingerprint to avoid self-reference.
Source, tests, skills, configuration, and other repository files remain
included. Reports about work outside this repository should use the configured
report directory or a workspace-relative `Markdown` directory instead.

## Skill checks

The expected skill count is 17. For each skill, the validator checks:

- `SKILL.md` exists in all three native roots;
- frontmatter `name` matches the directory and `description` is present;
- the file stays below 500 lines;
- all copies have identical SHA-256 hashes;
- instructions name all four statuses and define bounded stop conditions.

Host-runtime tests and CI remain `NOT_RUN` unless their evidence is recorded.
