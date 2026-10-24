# Functional skill groups

The catalog has **32 skills in eight groups**. `skill-groups.json` defines
navigation membership; `skills-manifest.json` remains the installation inventory.
Every manifest skill must occur in exactly one group. README tables are generated
from this mapping and canonical descriptions.

| Group | Reviewer checks |
|---|---|
| Planning, review and security | Scope, acceptance criteria, priorities, trust boundaries and evaluation rubric |
| Implementation and maintenance | Authorized edits, preserved behavior, dependency/data rollback |
| Debugging and diagnosis | Failing baseline, discriminating experiments, cause and regression evidence |
| Research and adoption | Primary sources, capability gaps, permissions and compatibility |
| Testing and adversarial verification | Real entry points, independent oracles, negative controls and false PASS evidence |
| Documentation, CI and release | Accurate commands, supported environments and publication authorization |
| Skill authoring and agent continuation | Distinct workflow, synchronized assets, limits and preserved task scope |
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
skills. The 1.2 runtime campaign stays tied to its frozen 27-skill manifest and
must not be presented as a fresh execution of all current skills.

The three new MCP workflows and their current offline exercise are described in
[MCP integration and tool trust](MCP-GROUP.md). Complete protocol/host support is
not inferred from that fixture.

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
