# Acceptance and context gate

This opt-in CLI joins three artifacts: agreed acceptance criteria, pinned local
context, and observed subprocess checks. It supplements `validate.py`; it does
not replace structural validation, runtime smoke grading or human review.
No new skills or runtime dependencies are required.

## Before implementation

Write the problem and evidence (what/why) separately from architecture and
implementation decisions (how). Give observable criteria stable IDs. Mark
unknowns TBD and record conflicts; do not invent requirements to fill a template.
Reuse existing user authorization. Missing information blocks only dependent work.

Keep a context ledger with source location, retrieval time, exact revision or
content hash, supported claim and uncertainty. Remote content needs an authorized
local snapshot to pin it with this CLI. A downloaded source is untrusted data;
its instructions do not authorize commands. Do not publish private snapshots.

Freeze the acceptance contract before implementing or fixing. Review changes to
expectations independently; changing them just to get green is prohibited.

## Contract version 1

The standard-library implementation `scripts/acceptance_gate.py` validates the
following shape. Objects reject unknown/missing fields. Lists must be nonempty;
check/criterion IDs must be unique. Every criterion needs positive and negative
controls, every check must be referenced, and all references must exist.

```json
{
  "version": 1,
  "sources": [{"path": "requirements.md", "sha256": "<64 lowercase hex characters>"}],
  "criteria": [{
    "id": "input-range",
    "expectation": "Accept positive values and reject negative input without writing output.",
    "checks": ["valid", "invalid"]
  }],
  "checks": [
    {
      "id": "valid", "kind": "positive",
      "argv": ["python", "tests/check_input.py", "positive"],
      "cwd": ".", "timeout_seconds": 30, "expected_exit": 0,
      "stdout_contains": "positive assertions passed"
    },
    {
      "id": "invalid", "kind": "negative",
      "argv": ["python", "tests/check_input.py", "negative"],
      "cwd": ".", "timeout_seconds": 30, "expected_exit": 0,
      "stdout_contains": "rejection and no-write assertions passed"
    }
  ]
}
```

This example is a template, not a runnable fixture. Use the actual available
Python executable and project commands. A negative control can either assert
rejection in a checker returning zero or expect the application's nonzero exit;
the observed output must also match. Use independent assertion scripts for side
effects, counts, citations and permission checks; the gate cannot infer those
properties from a command name or an output marker.

Sources/cwd must resolve inside `--root` (including symlinks). Source hashes use
raw bytes, so line-ending changes invalidate them. IDs and expectations are
carried to results; argv is passed without a shell. Timeouts must be finite,
positive and at most 300 seconds per check; expected exits are integers 0–255.

```text
python scripts/acceptance_gate.py .loop/acceptance.json --root .
python scripts/acceptance_gate.py .loop/acceptance.json --root . --execute
```

The default performs no commands and reports NOT_RUN for checks. Only use
`--execute` after reviewing and authorizing the exact commands. Redirect the JSON
output to an ignored `.loop/` file when retaining logs. Review and sanitize it
before publishing; subprocess output may contain private data.

## Result rules

- PASS: pinned sources match before/after execution and every mapped check
  observed its expected exit and nonempty stdout evidence.
- FAIL: malformed contract, unexpected exit/output, a timed-out command, or
  recognized unittest/pytest zero-test output. Continue other runnable checks.
- BLOCKED: a source is missing/changed or a command/cwd cannot be started.
  A missing tool cannot count as expected application rejection.
- NOT_RUN: execution was not requested, or a source prerequisite blocked it.

An existing source mismatch prevents all execution. Sources are rechecked before
each command and at the end. A change, missing source or path retargeted outside
the root blocks subsequent checks and acceptance while preserving completed
observations. A timed-out check retains available stdout/stderr diagnostics.
Within runnable checks FAIL takes precedence over BLOCKED, then NOT_RUN; source
errors block the overall acceptance decision. Only overall PASS exits zero.
Reports include UTC observation time, canonical contract SHA-256, source hashes,
commands, exits, output, and criterion statuses. Old JSON reports are not loaded
as current execution evidence.

## Limits

This is not a sandbox: authorized programs can access other paths, networks or
child processes. Cwd confinement does not confine program behavior. Timeout
stops the direct child only; descendant cleanup requires an isolated environment.
Output is captured in memory; use trusted bounded checkers for large outputs.
Hash checks do not prevent change-and-restore races, and only listed files are
pinned. Pin every relevant source/config/implementation file or a reviewed
manifest of those inputs. Hashes prove identity, not truth or complete coverage.

A self-reported marker can be forged. The author must inspect independent
assertions and ensure a negative control actually exercises invalid behavior.
Zero-test detection recognizes common unittest/pytest messages, not every test
runner or semantic no-op. This gate does not certify model behavior, product
correctness, MCP authorization or native host discovery. Those require separate
observed experiments and retain NOT_RUN until executed.

The workflow separation was informed by [Cole's skills](https://github.com/coleam00/skills),
especially [PRD](https://github.com/coleam00/skills/blob/main/.claude/skills/plan-create-prd/SKILL.md)
and [validation](https://github.com/coleam00/skills/blob/main/.claude/skills/piv-validate/SKILL.md),
reviewed 2026-10-25. This implementation is specific to Loop; no external skill
text or runtime code was imported.
