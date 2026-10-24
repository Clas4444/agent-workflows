# Validation

The validator checks the manifest, skill metadata, three-root synchronization,
named statuses, and recognizable stop instructions. It uses only the Python
standard library. Metadata extraction uses regular expressions for the supported
fields; it is not a general YAML parser or a semantic safety-policy checker.
Report generation computes a fingerprint; validation does not compare a saved
report's fingerprint with the current source.

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

The expected skill count is 27. For each skill, the validator checks:

- `SKILL.md` exists in all three native roots;
- frontmatter `name` matches the directory and `description` is present;
- supported metadata keys are not duplicated, descriptions fit 1024 characters,
  and invocation flags are literal true/false;
- the six input/workflow/output/boundary/example contract sections occur once
  in order and the skill includes its own invocation example;
- the file stays below 500 lines;
- all copies have identical SHA-256 hashes;
- instructions name all four statuses, contain an explicit stop instruction,
  match at least one recognized break-condition pattern and explicitly prohibit
  sleeping to consume time. This does not
  prove every stop policy is present or that a host will follow it.

Host-runtime tests and CI remain `NOT_RUN` unless their evidence is recorded.

`tests/test_contract_validation.py` mutates all copies together to verify the
validator catches broken contracts even when their hashes still match.
`tests/test_runtime_smoke.py` checks fixture graders and quota classification
without invoking a model. Opt-in execution is documented in RUNTIME-SMOKE.md.
