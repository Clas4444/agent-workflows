# From a request to a verified result

Choose by outcome, not by installing or invoking every skill.

| Need | Start with | Useful additions | What done means |
|---|---|---|---|
| A multi-step office/personal assignment | `loop-work` | write, meeting, document | Requested artifacts exist, criteria are checked and remaining commitments are explicit |
| Local file organization | `loop-files` | organize for an ambiguous/mixed request | Only authorized moves occurred; path/content/count and protected files are checked |
| Table analysis | `loop-table` | decide, document | Explicit types/units/missing rules, reconciled numbers and source-preserving output |
| A document file | `loop-document` | write, summarize, table | The requested saved file is reopened; content, layout and export checks are reported separately |
| Software implementation | `loop-code` | plan, debug, test, review | Requested behavior works at the real source/installed entry point with relevant regressions |

`loop-organize` remains a compatibility selector for existing users. Explicit file
requests should use files; work priorities/deliverables should use work. The
software-project workflow remains software-specific, rather than becoming a
catch-all for every personal project.

## Example: an office work package

```text
Use $loop-work to create an event brief, agenda and task checkpoint from these
notes. Budget is USD 150; date/approval are undecided. Available effort is 120
minutes. Fit proposed work to capacity, preserve unknown owners/dates, and create
the requested local Markdown files. Do not book, send or schedule anything.
```

A realistic result includes actual files and source-linked checks. Drafts may
be complete while approval, outreach and bookings remain BLOCKED/NOT_RUN.
Estimated effort is not claimed elapsed time or a calendar reservation.

## Example: files with an occupied destination

```text
Use $loop-files on this selected folder. Preserve the existing receipt and both
same-named but different source files. Produce a pinned mapping, perform only
the authorized moves, verify moved/protected contents, and leave recovery steps.
```

The installed `scripts/file_plan.py` can inventory, plan, preflight and verify.
It never moves anything. Keep plan/results outside the selected root. Actual
native moves and rollback require scope authorization; a passing plan is not an
executed reorganization. No multi-file atomicity or concurrency lock is promised.

## Example: expenses with mixed units and missing data

```text
Use $loop-table to summarize the supplied CSV by category and currency. Preserve
leading-zero IDs, flag missing amounts, treat formula-like text as data and
produce a source-grounded report without changing the input.
```

The installed CSV helper uses exact decimals and separate unit labels. Missing
values fail unless partial known-value reporting is explicitly selected. It
does not open Excel workbooks or certify future spreadsheet-import safety.

## Install the relevant payload

```text
python scripts/install_skills.py --bundle work --bundle documents --target "/my/project/.agents/skills"
python scripts/install_skills.py --bundle files --bundle data --target "/my/project/.agents/skills"
```

Replace the example target. Every selected skill includes its declared supporting
scripts/references/assets. For manual installation, copy the full folder. Start a
fresh host session in the selected project and verify actual discovery; matching
files alone do not prove activation. See [install by need](INSTALL-BY-NEED.md).
