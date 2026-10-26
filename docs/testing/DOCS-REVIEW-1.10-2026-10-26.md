# 1.10 documentation review — 2026-10-26

Requested scope: review the repository's 1.10 documentation, correct misleading
content and add useful illustrations and inspectable evidence. Budget: up to
30 minutes, beginning 19:29 (Asia/Bangkok; 12:29 UTC). Base/release commit:
`c6255a192c56c633c21889886c6080230bb774aa`. No publication or personal/global
installation changes were requested in this session.

## Findings and changes

| Priority | Verified issue at the release revision | Correction and verification |
|---|---|---|
| P2 | README called the older 1.9 autonomous session “current” and did not surface the 1.10 results | Added a release-specific evidence table and linked current 1.10 records; earlier sessions are labeled historical |
| P2 | 1.10 report still declared no push and remote CI NOT_RUN after publication | Added a dated publication update; directly read GitHub API for exact SHA and four successful jobs; original local-campaign scope remains explicit |
| P2 | SKILL-GROUPS said 49 skills/13 groups; SKILL-USAGE said 8 groups; CONTRIBUTING said 39 skills | Compared manifest/group registry: 53 skills/15 groups; updated contributor payload sync and missing gate instructions |
| P2 | Manual `writing` bundle example omitted `loop`, although all bundles include it | Corrected the full-folder example against the bundle registry |
| P2 | Usage table presented slash examples without local host qualification; finder prose implied the helper reads instruction contents | Added explicit supported-host syntax and discovery limits; clarified that the helper checks paths/existence and the agent reads instructions |
| P3 | Architecture described the current campaign as eleven gates | Checked `verification_session.COMMANDS`: fourteen gates; whitespace check remains separate |
| P3 | Everyday guide still routed explicit filesystem work through the older organize selector | Updated files/work routes and added intake/support/knowledge outcomes |
| P3 | README contained `Â·`; earlier audit prose contained corrupted dash/multiplication characters | Corrected UTF-8 text only; historical outcomes and counts unchanged |
| P3 | Readers had to traverse long historical reports and raw archives to understand evidence | Added an evidence map with real JSON excerpts, a source-conflict example and the retained failed work trial; added two scoped SVG diagrams and a first-use guide |

No production code, skill instruction, alias registry or historical runtime
archive was changed. New evidence lives in a separate
[review observation directory](../evidence/docs-review-20261026/README.md).

## Checkpoints

| Elapsed / budget | Angle | Evidence, action and next step |
|---|---|---|
| 0–5 / 30 min | Release and navigation | Read instructions, README, reports and current metadata. Found stale release/navigation claims; read-only API confirmed published CI. Next: align guides and status. |
| 5–10 / 30 min | Onboarding and illustrations | Corrected counts, routes and manual-copy omission. Added first-use/evidence pages and two SVGs; rasterized and inspected text fit. Next: execute documented commands. |
| 10–15 / 30 min | Evidence and command checks | Support walkthrough passed in a disposable path with a space; all 718 release pins matched Git blobs; documented JSON excerpts matched archive. Local Markdown preview loaded images without page-width overflow at 1280px/390px. Next: final content/diff review and fixed gates. |
| 15–22 / 30 min | Contributor docs and verification | Fixed stale contributor count, incomplete payload-sync instructions and missing gates. First fresh campaign failed: README wording no longer matched the catalog contract; link/junction tests also hit sandbox permission limits. Restored required wording, preserved failed results and prepared a fresh campaign outside that boundary. |
| 22–29 / 30 min | Final bytes, export and closure | Working-tree and separate Git-byte export campaigns each passed 14 gates with unchanged pins. Verified final reports, checked links/diff and retained failed/superseded observations. Removed disposable export/install fixtures and temporary caches; retained logs and preview evidence. |

## Executed checks and limits

The initial archive regrade attempt discovered four tests but failed with eight
setup/cleanup errors because default sandbox TEMP denied extraction/removal
(`WinError 5`). A retry with session-local TEMP/TMP passed all four tests. No
assertion, expected outcome or production code was changed. This environment
failure is retained separately from the successful retry; it is not evidence of
a defect in the published release. The unavailable Windows Store `py` alias was
also bypassed with the configured Python 3.14.7 interpreter.

The first full campaign, `docs-review-20261026-314`, finished **FAIL** with
unchanged input pins: 10/14 gates PASS, 4/14 FAIL. Unit discovery reported 318
tests, 12 failures, 11 errors and one skip. A documentation edit replaced the
catalog checker's required `53 bounded workflows` phrase, breaking the catalog
and dependent validation checks. That phrase was restored without changing the
checker. Other failures/errors came from denied hardlink/junction creation in
the sandbox. The failed report/logs remain under
`.loop/docs-review-20261026/campaign-314/`; no result was relabeled PASS.

A pre-publication byte check also found CRLF in newly written JSON records, which
Git's input normalization would change. All new evidence was normalized to LF,
reindexed, and given an explicit `.gitattributes` rule matching the existing
evidence directories. This prevents the new index from passing locally but
failing after a Git checkout. Original evidence directories remain unchanged.
All five new evidence files, including their index, now have equal raw and
Git-filtered blob identities. An earlier PASS before the final JSON normalization
is retained as a superseded checkpoint, not verification of the final bytes.

A broader raw-versus-Git-filter comparison also flagged existing, untouched CRLF
files in this Windows checkout. It did not establish new source defects. Those
files were left unchanged. A separate export uses exact HEAD Git blobs plus
the 27 current text-only documentation/attribute additions normalized to LF;
its campaign is recorded separately from working-tree verification. No actual
Git index, commit or branch was changed to create that export.

Default-sandbox GitHub API access failed DNS resolution; read-only access outside
that network boundary succeeded. Public snapshots contain selected public API
fields, not credentials or private raw logs.

The documentation audit checks inline local Markdown file links and ATX/HTML
heading anchors outside fenced code. It does not parse every Markdown dialect or
verify external URLs. Local preview uses `marked` and headless Chrome with a
GitHub-like stylesheet; it is not the GitHub production renderer. Diagram
rasterization/inspection is documentation work, not the still-unrun office
artifact rendering described by the 1.10 runtime report.

## Final verification

Working-tree campaign **PASS**: Python 3.14.7, session
`docs-review-20261026-published-bytes-314`, **14/14 gates**, **318 discovered / 317
PASS / one Windows file-symlink privilege SKIP**. Its 727 declared verification
inputs remained unchanged. The [working-tree report](sessions/docs-review-20261026-published-bytes-314.json)
was independently rechecked with `verification_session.py --verify` after copying
it to the public session directory. It is a dirty working-tree record, not a new
published release. Original release CI remains tied to `c6255a1`.

Separate Git-byte export **PASS**: session `docs-review-20261026-export-314`,
Python 3.14.7, **14/14 gates**, **318 discovered / 317 PASS / one Windows
file-symlink privilege SKIP**, 727 unchanged declared inputs. The
[export report](sessions/docs-review-20261026-export-314.json) was independently
verified against that export before cleanup. Its Git HEAD is null because it is
an exported directory. The export method is described above; this is not a
commit or a claim that every raw Windows checkout byte equals a Git blob.

Documentation navigation audit: **PASS**, 91 Markdown files, 391 local inline
links (including 12 heading anchors); no unresolved local target was found.
The 69 external link occurrences were not exhaustively fetched; release CI was
verified separately through its actual public API. New evidence index, unchanged
historical evidence, raw/filtered identity for the five new evidence files and
`git diff --check`: **PASS**. No new implementation tests were added for prose.

Closure checkpoint: 19:58 Asia/Bangkok, approximately 29 minutes of the 30-minute
budget. Temporary export/install/cache directories were removed only inside this
session's `.loop` directory. Raw logs, the failed first campaign, superseded
checkpoint reports, render previews and the session-local audit scripts remain
there. Existing installation backups and tracked evidence were preserved.

Native discovery, new model trials, external service actions and a fresh A/B
comparison: **NOT_RUN**. This session improves documentation and evidence access;
it does not close those behavioral coverage gaps. Commit/push: **NOT_RUN**.
