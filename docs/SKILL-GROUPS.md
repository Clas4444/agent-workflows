# Functional skill groups

The catalog has **49 skills in thirteen groups**. `skill-groups.json` defines
navigation membership; `skills-manifest.json` remains the installation inventory.
Every manifest skill must occur in exactly one group. README tables are generated
from this mapping and canonical descriptions.

| Group | Reviewer checks |
|---|---|
| Discovery and scoped planning | Primary sources, adoption constraints, acceptance criteria and non-implementation planning |
| Implementation and maintenance | Authorized edits, preserved behavior, dependency/data rollback |
| Debugging and diagnosis | Failing baseline, discriminating experiments, cause and regression evidence |
| Testing and evidence evaluation | Real entry points, fixed rubrics, independent oracles and negative controls |
| Review and security assurance | Located findings, reachable risks and preserved review scope |
| Delivery and operational verification | Readiness, authorized rollout, health/rollback gates and observable failure signals |
| Skill authoring and agent continuation | Distinct workflow, synchronized assets, limits and preserved task scope |
| End-to-end project workflows | MVP delivery slices, truthful PR evidence and authorized incident containment/recovery |
| Everyday writing and source summaries | Audience, preserved facts, source coverage and draft/delivery separation |
| Work delivery, meetings and file organization | Decision/action provenance, unassigned owners, collision-safe mapping and explicit move scope |
| Everyday decisions and learning | Hard constraints, conditional choices, realistic time budgets and actual learner assessment |
| Tables and document artifacts | Explicit units, source preservation, complete payloads and separate format/layout checks |
| MCP integration and tool trust | Pinned interface versions, tool acceptance contracts and scoped authorization boundaries |

## Check or update the catalog

```text
python scripts/catalog.py
python scripts/catalog.py --write
python scripts/validate.py
```

The first command is read-only. The second updates only the marked README
catalog block. Validation checks coverage, duplicate/unknown entries and stale
tables when group metadata is present. CI checks the catalog explicitly so
removing that file cannot silently skip the gate.

Native roots `.github/skills`, `.agents/skills` and `.claude/skills` remain flat.
Moving skills into group subdirectories would change discovery and installation
paths. Change navigation membership rather than moving native skill folders.

## Adversarial workflow boundary

`loop-test-adversarial` challenges declared contracts with isolated fixtures,
independent oracles, valid controls and retained failures. `loop-security` covers
broader threat review; `loop-debug` starts from a demonstrated bug;
`loop-evaluate` measures quality against a fixed rubric.

Native host behavior and implicit discovery remain **NOT_RUN** for the two new
1.3 adversarial/compatibility skills. The 1.2 runtime campaign stays tied to its frozen 27-skill manifest and
must not be presented as a fresh execution of all current skills.

The three new MCP workflows and their current offline exercise are described in
[MCP integration and tool trust](MCP-GROUP.md). Complete protocol/host support is
not inferred from that fixture.

For the current cross-group decisions, four upgrades and the deployment and
observability additions, see [taxonomy review 1.5](TAXONOMY-1.5.md).
For context preparation, handoff and research-backed evaluation upgrades, see
[research update 1.6](RESEARCH-1.6.md).

## Verification of this update

On 2026-10-24, Windows/Python 3.12.14: **115 deterministic tests passed** in
15.150 seconds. Full and format validation, catalog rendering/coverage, Python
compilation, project-copy synchronization and whitespace checks passed.
The suite retains the demonstrated adversarial fixes for metadata, version
digits and hardlinked sync destinations; see [the adversarial report](ADVERSARIAL-2026-10-24.md).

The historical evidence test now reads its frozen 1.2 manifest rather than
silently assigning old PASS results to a larger catalog. Additional tests
check the historical manifest separately from additions and their explicit NOT_RUN status.
No old runtime results were rewritten. Grouping tests reject missing/duplicate
membership even when the skill files themselves are valid.

That 115-test result records the earlier grouping step. The subsequent 29-skill
review and final test scope are documented in [1.3 verification](VERIFICATION-1.3.md).
Only the three project layouts were synchronized; personal installations were
not modified. Host runtime claims and remote CI remain separate evidence.
