# Current all-skill inventory audit

Session: `audit-ab-20261025T083146Z`. Base: `393104e50f1007b30d04638259db72c6c19f011b`.

Fresh static reads covered **49/49 canonical instruction files**, all **13 groups**, routing cases and all declared helper/reference assets. The machine-readable [ledger](skills-audit.json) retains exact byte identities and per-skill reasons. This review does **not** reuse historical runtime PASS.

## Decisions

**46 KEEP, 3 IMPROVE; 0 SPLIT, MERGE, DEPRECATE or NEW_NEEDED.** KEEP means retain the present responsibility, not universal runtime approval. IMPROVE is a design recommendation, not a confirmed behavioral defect.

| Skill | Decision | Reason |
|---|---|---|
| [loop-review](../../../.github/skills/loop-review/SKILL.md) | KEEP | Prioritized source-backed findings remain distinct from planning, grading and adoption; installed delivery surfaces are explicitly included. |
| [loop-code](../../../.github/skills/loop-code/SKILL.md) | KEEP | Small authorized implementation batches retain acceptance IDs, source identity, negative controls and installed-artifact verification. |
| [loop-diagnose](../../../.github/skills/loop-diagnose/SKILL.md) | KEEP | Competing hypotheses and reproduction frequency preserve the distinction between investigation and repair. |
| [loop-diagnose-repro](../../../.github/skills/loop-diagnose-repro/SKILL.md) | KEEP | Minimization preserves the failing observation and explicitly avoids an unsupported fix claim. |
| [loop-diagnose-performance](../../../.github/skills/loop-diagnose-performance/SKILL.md) | KEEP | Repeated comparable measurements and variance are required before an improvement claim. |
| [loop-diagnose-regression](../../../.github/skills/loop-diagnose-regression/SKILL.md) | KEEP | Known-good/failing revisions and rerun evidence define a distinct historical-isolation workflow. |
| [loop-research](../../../.github/skills/loop-research/SKILL.md) | KEEP | Dated primary sources, exact revision/content identity, untrusted-source treatment and benchmark applicability are explicit. |
| [loop-research-repo](../../../.github/skills/loop-research-repo/SKILL.md) | IMPROVE | Repository adoption criteria are useful, but the leaf workflow does not inherit the current general-research source-snapshot/recheck and embedded-instruction rules when installed alone. |
| [loop-research-tools](../../../.github/skills/loop-research-tools/SKILL.md) | IMPROVE | Capability/permission/data-flow adoption review is useful, but standalone instructions omit the general-research exact source identity/recheck and explicit embedded-instruction rule. |
| [loop-test](../../../.github/skills/loop-test/SKILL.md) | KEEP | Risk-based layer selection, frozen criteria, controlled failures and end-state checks are more useful than indiscriminate test volume. |
| [loop-test-unit](../../../.github/skills/loop-test-unit/SKILL.md) | KEEP | Isolated function/module assertions and preservation of acceptance criteria remain a distinct focused route. |
| [loop-test-integration](../../../.github/skills/loop-test-integration/SKILL.md) | KEEP | Boundary setup, cleanup and reproducibility are explicit; real service availability remains an execution prerequisite. |
| [loop-test-coverage](../../../.github/skills/loop-test-coverage/SKILL.md) | KEEP | Line, branch, path and mutation evidence are separated and thresholds cannot be weakened for a green result. |
| [loop-docs](../../../.github/skills/loop-docs/SKILL.md) | KEEP | Documentation claims are traced to source; command/link verification is scoped and unavailable checks remain visible. |
| [loop-skill-create](../../../.github/skills/loop-skill-create/SKILL.md) | KEEP | Responsibility comparison, frozen realistic tasks, artifact checks, resource declaration and instruction-history invalidation cover authoring lifecycle. |
| [loop-orchestrate](../../../.github/skills/loop-orchestrate/SKILL.md) | KEEP | Explicit host adapter, finite limits and terminal markers separate process continuation from native host compatibility; descendant cleanup limitation is disclosed. |
| [loop-prompt](../../../.github/skills/loop-prompt/SKILL.md) | KEEP | Explicit invocation only, N+1 hard ceiling, early stops and retained state distinguish bounded follow-ups from unrestricted autonomy. |
| [loop-debug](../../../.github/skills/loop-debug/SKILL.md) | KEEP | A demonstrated failing baseline precedes repair and rerun; failure to reproduce is not promoted to a verified fix. |
| [loop-security](../../../.github/skills/loop-security/SKILL.md) | KEEP | Authorized assets, reachability, impact and safe local probes prevent a generic scan result becoming a security guarantee. |
| [loop-refactor](../../../.github/skills/loop-refactor/SKILL.md) | KEEP | Observable behavior and characterization baseline distinguish restructuring from requested feature changes. |
| [loop-ci](../../../.github/skills/loop-ci/SKILL.md) | KEEP | Run/job/revision identity and local versus remote results address a genuine pipeline-specific boundary. |
| [loop-release](../../../.github/skills/loop-release/SKILL.md) | KEEP | Rebuild checksum comparison is required for reproducibility and install success is separated from build success. |
| [loop-plan](../../../.github/skills/loop-plan/SKILL.md) | KEEP | Stable criteria, context identities and positive/negative controls are explicit; planning does not authorize implementation. |
| [loop-dependencies](../../../.github/skills/loop-dependencies/SKILL.md) | KEEP | Manifest/lockfile consistency, advisory uncertainty and lifecycle-script authorization are explicit. |
| [loop-migrate](../../../.github/skills/loop-migrate/SKILL.md) | KEEP | Dry-run, invariant preservation, idempotence and actually exercised rollback define persisted-state transformation. |
| [loop-test-e2e](../../../.github/skills/loop-test-e2e/SKILL.md) | KEEP | Real entry point, invalid-input journey and absence of unwanted side effects distinguish E2E from unit mocks. |
| [loop-evaluate](../../../.github/skills/loop-evaluate/SKILL.md) | IMPROVE | Frozen oracles, denominators, all-attempt retention and pass@k/pass^k are sound; comparable baseline guidance should explicitly name instruction/history/global-skill leakage. |
| [loop-test-adversarial](../../../.github/skills/loop-test-adversarial/SKILL.md) | KEEP | Independent invariants, untouched baseline and failing regression before root repair support falsifiable false-PASS testing. |
| [loop-test-compatibility](../../../.github/skills/loop-test-compatibility/SKILL.md) | KEEP | Per-cell real execution, unsupported controls and separation of synchronized bytes from host discovery constrain compatibility claims. |
| [loop-mcp-design](../../../.github/skills/loop-mcp-design/SKILL.md) | KEEP | Versioned protocol/transport and tool trust boundaries prevent skill text being mistaken for a running server. |
| [loop-mcp-test](../../../.github/skills/loop-mcp-test/SKILL.md) | KEEP | Offline envelope, live transport, authentication and host interoperability are separately labeled. |
| [loop-mcp-security](../../../.github/skills/loop-mcp-security/SKILL.md) | KEEP | Tool annotations are hints rather than enforcement; synthetic credentials and absent forbidden side effects are explicit. |
| [loop-deploy](../../../.github/skills/loop-deploy/SKILL.md) | KEEP | Known artifact, authorized environment, health gate and observed rollback remain distinct from release readiness. |
| [loop-observe](../../../.github/skills/loop-observe/SKILL.md) | KEEP | Signal provenance, absent data versus zero, noise and actual alert delivery are explicit without implicit persistent monitoring. |
| [loop-context](../../../.github/skills/loop-context/SKILL.md) | KEEP | Task-relevant source selection preserves critical constraints and distinguishes matching hashes from faithful summary meaning. |
| [loop-handoff](../../../.github/skills/loop-handoff/SKILL.md) | KEEP | Resume rechecks source/artifact drift and retained failures; saved commands are not grants of authority. |
| [loop-workflow-project](../../../.github/skills/loop-workflow-project/SKILL.md) | KEEP | Software MVP slices and actual user-visible gates remain separate from non-software work and narrow edits. |
| [loop-workflow-pr](../../../.github/skills/loop-workflow-pr/SKILL.md) | KEEP | Base/head identity and exact remote-head CI follow publication; a local PASS is not review or merge authorization. |
| [loop-workflow-incident](../../../.github/skills/loop-workflow-incident/SKILL.md) | KEEP | Operational impact, hypotheses, containment, observation windows and user-facing recovery are separate claims. |
| [loop-write](../../../.github/skills/loop-write/SKILL.md) | KEEP | Consequential facts, unknown commitments and actual requested-file delivery are checked separately from sending. |
| [loop-summarize](../../../.github/skills/loop-summarize/SKILL.md) | KEEP | Read coverage, source qualifiers, contradictions and material omissions constrain faithful compression. |
| [loop-meeting](../../../.github/skills/loop-meeting/SKILL.md) | KEEP | Proposal, decision, ownership, due date and completion are independently supported rather than inferred from a transcript. |
| [loop-organize](../../../.github/skills/loop-organize/SKILL.md) | KEEP | Existing compatibility selector has explicit file/work branches and a safe standalone fallback; deleting it would break established invocation. |
| [loop-decide](../../../.github/skills/loop-decide/SKILL.md) | KEEP | Hard constraints, unknown feasibility, compatible units and sensitivity prevent fabricated precise recommendations. |
| [loop-learn](../../../.github/skills/loop-learn/SKILL.md) | KEEP | Observable learning outcomes, time arithmetic and actual learner responses distinguish planning from demonstrated mastery. |
| [loop-work](../../../.github/skills/loop-work/SKILL.md) | KEEP | Done criteria, actual deliverables, capacity and task-state/check-state separation cover office packages without imposing software planning. |
| [loop-files](../../../.github/skills/loop-files/SKILL.md) | KEEP | Pinned regular-file inventory, separate native moves, protected identities and nontransactional concurrency limits define a bounded helper contract. |
| [loop-table](../../../.github/skills/loop-table/SKILL.md) | KEEP | Explicit types/units/missing policy, exact arithmetic and formula/layout separation constrain table claims. |
| [loop-document](../../../.github/skills/loop-document/SKILL.md) | KEEP | Requested format, reopened final artifact and distinct content/container/layout/export checks prevent file-extension-only acceptance. |

## Actionable observations

- **DOCUMENTATION_GAP INV-DOC-01:** `docs/VALIDATION.md` still states an expected count of 34; the parsed manifest has 49. Prefer manifest-driven wording.
- **DESIGN_RISK INV-DESIGN-01:** `loop-evaluate` should explicitly define baseline isolation from global/project skills and previous attempts before claiming a no-skill comparison. Its existing comparable-conditions rule does not spell out that operational hazard.
- **DESIGN_RISK INV-DESIGN-02:** `loop-research-repo` and `loop-research-tools` can be installed alone but omit the source-snapshot/recheck and untrusted embedded-instruction rules found in current `loop-research`. A small aligned clarification is preferable to forcing all research skills to be installed.

## Changes rejected

The focused test layers remain distinct; merging them would erase useful prerequisites. `loop-organize` remains a compatibility selector after the existing split into files/work. No additional generic automation or protocol-service skill is justified by this static review. Do not add names to increase the catalog count.

## Verification and limits

Static inspection: **49/49 reviewed**. Every listed skill has a primary curated route case; this is a corpus-coverage observation, not a measured routing run. All per-skill **runtime validation: NOT_RUN; native discovery: NOT_RUN** for this inventory activity. Helper/reference text was read; both bundled runner copies were checked for byte identity with the root runner, without claiming a new runner behavior audit. No behavioral bug is proven by these recommendations. Separately executed benchmark and platform tests must retain their own IDs and limits.
