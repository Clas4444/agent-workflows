# Validation

For executable acceptance criteria and context freshness, see the separate
[acceptance gate](ACCEPTANCE-GATE.md). Structural PASS here does not execute that
contract or imply its checks passed. The gate is opt-in, dry-run by default and
does not change existing runner protocols or `validate.py` CLI behavior.

The validator checks the manifest, skill metadata, three-root synchronization,
named statuses, and recognizable stop instructions. It uses only the Python
standard library. Metadata extraction uses regular expressions for the supported
fields; it is not a general YAML parser or a semantic safety-policy checker.
Required name/description values must decode to non-empty strings in the
supported subset: plain strings, YAML single quotes with doubled apostrophes,
or double quotes with JSON-compatible escapes. Collections, typed scalars,
unclosed quotes and unsupported YAML constructs are rejected instead of being
coerced into text. Duplicate supported keys include whitespace before `:`.
Report generation computes a fingerprint; validation does not compare a saved
report's fingerprint with the current source.
Unreadable or invalid UTF-8 skill files produce per-file FAIL findings rather
than an uncaught decoder traceback; later copies are still checked.

Control-plane JSON readers share a duplicate-key policy: decoded keys must be
unique at every object depth, including escape-equivalent spellings. The
nonstandard NaN/Infinity literals are rejected. Quoted strings with those names
remain ordinary strings. This is input-policy hardening, not a general JSON
Schema engine or a cryptographic canonicalization format.

Plain `-`/`?` indicators followed by separation are rejected; quoted literals and
safe prefixes such as `-item` remain valid. The manifest version follows
[SemVer 2.0 syntax](https://semver.org/), including nonempty prerelease/build
identifiers and numeric leading-zero restrictions. The metadata subset follows
the [YAML plain-scalar restrictions](https://yaml.org/spec/1.2.2/#733-plain-style);
this is still not a general YAML parser.

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
Fingerprint encoding v2 uses framed filename/content-hash records and POSIX
relative path spelling. This removes filename/content boundary ambiguity;
historical fingerprints use their historical encoding and are not rewritten.
Source, tests, skills, configuration, and other repository files remain
included. Reports about work outside this repository should use the configured
report directory or a workspace-relative `Markdown` directory instead.

## Skill checks

The default `loop` profile remains the full project gate. For metadata and
repository-integrity diagnosis only, run `python scripts/validate.py --profile
format`. This keeps manifest, copy and bundled-runner checks but omits local
Loop conventions. It cannot generate the full validation summary.

The implementation separates manifest parsing, supported metadata checks and
Loop policy under `scripts/validation/`; see [architecture](ARCHITECTURE.md).
The six headings, four statuses, invocation flags, slash example, size limit
and no-sleep rule below are project conventions, not universal Agent Skills
format requirements. The [manifest schema](../schemas/README.md) documents
the existing data shape without changing existing files.

The expected skill set comes from `skills-manifest.json`; it is not a fixed
historical count. For each declared skill, the validator checks:

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

## Adversarial reproduction

Cross-group selection cases and per-skill decisions are checked independently
with `python scripts/routing_check.py`. The full validator also checks this
metadata when skill-routing.json is present; CI invokes the checker explicitly
so a missing file cannot silently skip the repository gate. Prediction grading
requires all fixed IDs and includes no-skill controls. These checks do not prove
automatic host discovery or runtime skill behavior.
Each skill must also have a single-answer primary case, and NONE needs a
dedicated single-answer control. Broadening every answer set cannot manufacture
coverage. Additional explicitly ambiguous cases remain permitted.

```text
python -m unittest discover -s tests -p test_adversarial.py -v
python scripts/adversarial_repro.py --output-dir .loop/adversarial-fresh --expect fixed
```

The output directory must be new. The reproducer runs real local validator and
sync CLIs on disposable fixtures, including a hardlink to another fixture file
outside the selected installation root. It does not touch personal skills,
invoke a model or access a network. `--repo` can point to a disposable snapshot
of an older revision; `--expect vulnerable` tests the recorded old behavior.
A matching expectation is not a claim that an invalid fixture passed validation
correctly. Read the per-invocation exit codes and side effects in results.json.

## Portable JSON depth bound (1.7)

Shared control-plane JSON readers reject nesting deeper than 512 containers
before parsing. This is a Loop limit, not a JSON standard restriction. Brackets
inside quoted strings do not count; strings, UTF-8 bytes and UTF-16 bytearrays
share the same rule. Duplicate decoded keys and non-finite constants remain
rejected. Interpreter recursion failures are still converted to controlled errors.
The explicit bound avoids launch-mode-dependent acceptance on Python 3.14.
