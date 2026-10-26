# Autonomous documentation guard continuation — 2026-10-26

User request: select useful repository work and continue for **at least thirty
minutes**. Start: 20:50:51 Asia/Bangkok (13:50:51 UTC); earliest closure 21:20:51.
Base: `c0587fb2f600da9ad58279c4e3ccf00661114dc1`. Scope selected: turn the earlier
session-local navigation audit into a repeatable repository/CI guard. New changes
remain local; no new push, global install, model call or subagent was requested.

## Why this work

The previous documentation audit checked over five hundred links, but its script
was ignored under `.loop/`. Existing deterministic tests mainly checked README
paths, so later changes elsewhere could break navigation without a dedicated CI
diagnostic. The new `scripts/docs_check.py` checks root, `docs/` and `schemas/`
Markdown with source line diagnostics and a structured read-only result.

The script validates supported inline local file/image links, Markdown heading
fragments, root-relative/encoded destinations and exact case spelling across
platforms. It rejects paths outside the selected repository and below-root
aliases before reading target contents. External URLs and non-Markdown fragments
stay explicitly unverified. It does not fetch, render or execute document text.

## Development and independently checked behavior

The initial import failure was a new-feature baseline because the checker did
not yet exist, not a defect in the published release. Subsequent development
failures are retained under `.loop/continuation-20261026/`:

- Initial matching falsely rejected an ordinary index expression and a multiline
  link in historical prose. Fixed recognition; the old evidence files were not
  edited and assertions were not weakened.
- Fixed a demonstrated false PASS when an anchor existed only inside inline
  code, plus false positives for escaped literal links. New regression controls
  retain the original intended result.
- Tested odd/even escape sequences so paired backslashes cannot conceal a broken
  link. Image punctuation and escaped brackets are checked separately.
- Fixed source-order handling for mixed ATX/Setext duplicate headings and tested
  formatted/Unicode headings, custom anchors, missing targets and root escape.
- Hardlink test setup failed under default sandbox permissions in some red
  development runs; targeted runs outside that restriction exercise the actual
  filesystem behavior. Raw failures remain, separate from later passing runs.
- A final controlled ASCII-terminal trial exposed a diagnostic traceback for a
  Unicode source filename. Output now uses backslash replacement only when the
  active terminal cannot encode a character; source bytes remain unchanged.
  The first passing full campaign predates this fix and is superseded, not reused
  as verification of the final checker bytes.

Eighteen focused tests cover these controls, real repository scope, read-only
fixture preservation, module/script CLI parity and controlled invalid input.
The test-only fixtures and network-independent checker do not invoke models.

A separate read-only GitHub Contents API request fetched rendered HTML for the
**published** atlas at `c0587fb`. All 17 predicted atlas heading IDs existed in
that returned HTML. This is narrower than all-page rendering, visual correctness
or native skill discovery. Raw HTML and comparison JSON stay in `.loop/`.
The [GitHub endpoint](https://docs.github.com/en/rest/repos/contents#get-repository-content)
documents HTML media responses; basic heading rules are linked in the
[testing guide](TESTING.md#documentation-navigation).

## Integration and boundaries

CI has an explicit standalone navigation step. README, AGENTS, CONTRIBUTING and
the testing procedure list the command and scope. The established fourteen-gate
campaign command list and report format are unchanged; its unit suite includes
the new real-repository check. The standalone CLI is also run separately.

This is a documented Markdown subset, not a general CommonMark parser or HTML
sanitizer. Unsupported inline/reference patterns are diagnosed, not certified.
Folder/file existence does not establish SVG fragment IDs, external reachability
or factual truth. Historical evidence and skill instruction bytes are untouched.

## Verification and closure

Final Python 3.14.7 export campaign **PASS**: session
`docs-guard-20261026-final-314`, **14/14 gates**, **340 tests discovered / 339
PASS / one Windows file-symlink privilege SKIP**. All 750 declared inputs stayed
unchanged. The [final report](sessions/docs-guard-20261026-final-314.json) was
independently verified against its export after copying. That export used exact
HEAD Git blobs plus the local text changes normalized to LF, without staging or
committing. Its null Git HEAD is expected for an exported directory. Raw Windows
checkout bytes and historical reports must not be substituted for that scope.

All 18 focused tests also passed with Python 3.12.14, including the controlled
ASCII-terminal case and real script/module invocations. The default CLI also
worked from outside the repository with the correct source-root selection.
Final standalone navigation check: 96 Markdown files, 516 local inline links and
42 Markdown fragments; zero errors. The 71 external links remain unfetched by
the checker. Whitespace and preserved historical-evidence checks passed.

Closure: 21:23 Asia/Bangkok (14:23 UTC), over **32 minutes** after the recorded
start, satisfying the requested thirty-minute minimum. Final source/diff review
and report verification completed before cleanup. Disposable export/temporary
fixtures were removed only inside `.loop/continuation-20261026/`; failed trials,
the superseded first passing campaign, raw GitHub HTML and comparison records
remain there. Existing backups and tracked evidence were preserved.

No Git staging, commit or push was performed. Remote CI for these local changes,
cross-host native discovery and new behavioral model trials: **NOT_RUN**.

## Patch publication follow-up

The owner subsequently authorized publishing this small update as
`1.10.1-experimental`, retaining the 1.10 minor line. The local-only statement
above describes the earlier continuation phase, before that authorization.
Current manifest/README/example versions are aligned; historical reports keep
their recorded versions. Every file under `docs/assets/` must remain byte-identical
to `c0587fb`, including all fourteen bundle SVGs and their explanation data.

A fresh patch export campaign passed after the version change:
`patch-1.10.1-20261026-export-314`, Python 3.14.7, **14/14 gates**, **340 discovered /
339 PASS / one Windows symlink privilege SKIP**, with all 750 declared input
files unchanged. The [patch report](sessions/patch-1.10.1-20261026-export-314.json)
was independently verified against that exact export. The earlier result was not
reused for different manifest bytes. Exact recursive Git-tree comparison also
confirmed unchanged asset paths, modes and blob identities. Before commit, all
750 input hashes are compared with the final staged blobs. Commit/push and remote
CI follow this verified patch; this pre-publication report does not predict a
resulting commit SHA or CI conclusion.
