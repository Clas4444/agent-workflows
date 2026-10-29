# Fourteen illustrated bundle workflows — 2026-10-26

User request: one image per bundle explaining iteration, why to use it, request
selection, recommendations and what to avoid; verify and push. Budget: up to
30 minutes from 20:02 Asia/Bangkok (13:02 UTC). Base commit `c6255a1`.
The earlier documentation corrections in this chat are included in publication.

## Delivered scope

- Fourteen separate editable SVGs in `docs/assets/bundles/`, with accessible
  titles/descriptions, four task-specific steps, a conditional feedback arrow,
  explicit exit/stop path, recommendations, avoid guidance and installed members.
- A [workflow atlas](../../guides/bundle-workflows.md) with selection links, text
  equivalents, alternatives and an example request per bundle. README, first-use,
  installation and documentation navigation link to it.
- Explanation source `docs/assets/bundles/workflows.json`; membership comes only
  from the existing bundle registry. No duplicate skill or membership change.
- A standard-library generator/checker and four focused regression tests. The
  regular workflow gate and an explicit CI step check missing/stale/extra SVGs,
  exact bundle coverage and skill references outside the installed bundle.

Each diagram is guidance, not a mandatory pipeline. A clear single-skill request
does not need all steps or members. Plan-only requests stop before execution.
The feedback arrow requires a useful next action, time and existing authority;
completion, a blocker, budget or boundary leaves a checkpoint. Files, incident,
learning and other specialized limits were checked against canonical text.

## Checkpoints and verification

| Elapsed / budget | Work and observation |
|---|---|
| 0–8 / 30 min | Read bundle membership and canonical responsibilities/boundaries; authored distinct selection, iteration and recommendations for all fourteen bundles. |
| 8–14 / 30 min | Generated and rendered all fourteen SVGs. Geometry checks found no canvas/card overflow or overlapping text. Inspected contact sheet and full-size examples. Four targeted regression tests passed. |
| 14–20 / 30 min | Reviewed staged scope, source/render hashes and exact Git-filtered bytes; exported the staged tree and passed all fourteen repository gates. Remote main still matched the base before publication. |

Rendering evidence: [reviewed record](../../evidence/bundle-atlas-20261026/README.md).
It measures actual SVG geometry in local Chrome, not host skill behavior or a
GitHub production rendering. Explanations and examples are not runtime evidence.

## Final checks and publication

**PASS** on Python 3.14.7 / Windows: fresh staged-Git export session
`bundle-atlas-20261026-export-314`, **14/14 gates**, **322 tests discovered / 321
PASS / one Windows file-symlink privilege SKIP**. All 748 declared input files
were unchanged. The [session report](../sessions/bundle-atlas-20261026-export-314.json)
was independently rechecked with `verification_session.py --verify` against its
export. Its Git HEAD is null because it ran from an exported Git tree, not a
checkout. Before commit, its inputs are compared against the actual staged blobs.
Older 318-test campaigns retain their original scope; they are not this run.

The atlas checker ran through the existing workflows gate; CI also has an
explicit atlas step. Four new deterministic tests cover accessible exact
coverage, stale/missing/extra SVG refusal, invalid-member and invalid-registry
write preflight, XML escaping and overflowing labels. Local Chrome geometry
checks passed for all fourteen diagrams. Rendered source identities were
rechecked before staging. No model calls or dependency installation occurred.

Documentation audit before publication: 94 Markdown files, 510 local inline
links including 40 heading anchors; no unresolved local target. External links
were not exhaustively fetched. Declared evidence indexes and whitespace checks
passed. Raw PNGs, contact sheet and gate logs stay under ignored `.loop/`.

Publication is authorized after these local checks. This report is captured
before the commit, so it cannot contain its own final commit SHA or predict CI.
Use the resulting commit's Actions run for actual remote status; no older CI
result is promoted to proof of this atlas change. The repository's version,
skill instructions, bundle membership and personal/global installations are
unchanged. Disposable export/temporary fixtures are removed after their reports
and staged-byte comparison are verified; logs and reviewed evidence are kept.

New native discovery, every-skill behavioral trials, office engines, external
service actions and broad reliability/A-B tests: **NOT_RUN**.
