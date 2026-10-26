# Documentation review observations (2026-10-26)

These records were collected while reviewing the published 1.10 release and
improving its documentation. They are separate from the original discovery
campaign; no original runtime artifact or hash index was rewritten.

| Record | Scope |
|---|---|
| [release-ci.json](release-ci.json) | Read-only GitHub Actions API observation: exact release SHA, four completed successful jobs, public run/job links and observation time. |
| [release-claim-check.json](release-claim-check.json) | Compared both identical 718-file export pins with Git blobs at `c6255a1`; checked documented counts and JSON excerpts against the retained records/archive. Consistency check, not authenticated execution. |
| [quickstart-check.json](quickstart-check.json) | New disposable support installation in a path containing a space. The missing-install check exits 1 as expected; installation, post-check, doctor and installed lookup exit 0. Only selected folders are installed and the unrelated sentinel survives. No model or native host discovery. |
| [published-hashes.json](published-hashes.json) | SHA256 index of the reviewed records and this explanation; byte identity only. |

The quick-start commands use a sanitized `<fixture>` path. Actual stdout and
temporary files stay under ignored `.loop/`. The record identifies the tested
guide and relevant production source hashes. Existing global/personal installs
were not modified. API access was read-only; no new push or CI run was triggered.

Fresh repository gate results for the changed working tree are recorded in the
[documentation-review report](../../testing/DOCS-REVIEW-1.10-2026-10-26.md).
The release CI snapshot does not cover those later working-tree edits.
