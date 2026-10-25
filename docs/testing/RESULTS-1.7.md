# Workflow restructuring and test evidence — 1.7

Session started 2026-10-25 04:29:10 UTC. Base revision:
`a1250d13d8ebadf51e91e4e1edcb3de948824fd0`.
The request was a 30-minute restructuring session, English usage illustrations,
testing documentation/results and a new group containing two to six skills.

## Resulting structure

- 39 skills in nine navigation groups, with flat native installation paths retained.
- Three new lifecycle skills: `loop-workflow-project`, `loop-workflow-pr` and
  `loop-workflow-incident`. They coordinate explicit project delivery, PR packets
  and operational incidents; they do not replace focused planning/review/debug.
- Smoke fixture preparation and grading now live in `scripts/smoke/fixtures.py`
  and `scripts/smoke/grading.py`; `scripts/smoke_cases.py` retains the public facade.
- A [documentation map](../README.md), [test procedure](TESTING.md) and
  [role toolkits](../guides/ROLE-WORKFLOWS.md) separate onboarding, maintenance and
  evidence. Historical reports remain at their original paths.
- Five inventory-checked role presets generate Markdown and an editable SVG.
  Two manually inspected English PNG illustrations explain developer and lifecycle
  workflows, with Do/Do not guidance. They are explanatory snapshots, not gates.

## Workflows actually used

`loop-refactor` guided characterization before moving runtime harness internals.
`loop-skill-create` and the system `skill-creator` guided three narrow instruction
contracts and independent forward tests. `loop-test` and `loop-review` guided
negative controls, complete regression checks and inspection of the resulting diff.
The imagegen skill/tool produced the two English posters. These are explicit uses
of instructions/tools; they are not automatic host-discovery measurements.

The design was checked against the primary [Agent Skills specification](https://github.com/agentskills/agentskills/blob/main/docs/specification.mdx)
for short entrypoints, optional resources and progressive disclosure. The incident
workflow draws on the distinction between incident coordination and service
restoration in [Google's SRE workbook](https://sre.google/workbook/incident-response/).
These sources inform design; they do not certify this implementation or prove safety.

## Behavioral exercise and correction

Two fresh subagent contexts explicitly loaded canonical instructions. The first
produced three isolated packets from [raw synthetic requests](../evidence/workflows-1.7/request.md).
No source changes, publishing, live actions, installs or notifications were requested.

| Exercise | Observation | Evaluation |
|---|---|---|
| Project, plan-only | Acceptance backlog and undecided requirements retained; implementation/tests NOT_RUN | PASS for this packet contract |
| PR without patch/revisions | Draft distinguishes author-reported 12 tests from independent execution; revisions/CI blocked | PASS for this packet contract |
| Incident, initial draft | No rollback/recovery claim, but reported unit tests/probe were placed under PASS gates | FAIL for evidence-status fidelity |
| Incident, revised instruction | Supplied claims stay reported; independent checks NOT_RUN; rollback BLOCKED; recovery unverified | PASS for this packet contract |

**Finding: evidence-label ambiguity (moderate).** The initial incident output
correctly rejected runbook instructions and sustained recovery, but its PASS
fields could be consumed as verified checks despite explanatory qualifiers.
The skill now requires reported and independently verified results to stay
separate. It also labels an observation window as proposed until justified or
agreed; the first output had invented a 15-minute threshold without a baseline.
The raw first output is retained as a negative control, not relabeled PASS.

Evidence: [project](../evidence/workflows-1.7/project.json),
[PR](../evidence/workflows-1.7/pr.json),
[incident before](../evidence/workflows-1.7/incident-before.json),
[incident after](../evidence/workflows-1.7/incident-after.json),
[provenance](../evidence/workflows-1.7/provenance.json).
This was a manual semantic evaluation of a small synthetic sample. It does not
establish a statistical reliability rate or prevent future model errors.

## Deterministic checks

The pre-refactor runtime-smoke and grader-boundary suites passed. After splitting
the modules and adding role-guide checks, the initial full Python 3.12 run found
198 tests: 197 passed, one skipped for unavailable Windows file-symlink privilege.
No old test was deleted or weakened. Text-I/O encoding coverage now includes
nested production modules. New guide tests reject unknown skills, duplicate
profiles, core/optional overlap, invalid version types and stale generated files;
invalid presets are rejected before rewriting outputs. SVG escaping is exercised.

Two additional issues were found during the expanded checks:

- **SVG card overflow (low):** a valid long toolkit overlapped the next card.
  A new geometric regression failed before the fix. Card height and canvas size
  now derive from wrapped text; the same test passes. This was in the newly added
  renderer, not a pre-existing repository defect.
- **Interpreter-dependent JSON nesting (moderate):** the full Python 3.14 run
  failed the existing excessive-nesting regression because a child process
  accepted 10,000 levels. A direct launch rejected the same input. The reader had
  relied solely on interpreter stack failure. The shared reader now enforces an
  explicit 512-container bound before parsing, with quoted/escaped text excluded.
  New boundary tests failed before the guard and passed after it; UTF-8/UTF-16
  inputs retain the same rule. This strengthens validation rather than weakening
  the old test. Python's [JSON implementation-limit documentation](https://docs.python.org/3.14/library/json.html#implementation-limitations)
  explains why interpreter limits are not a portable format policy.

### Final local results

| Check | Python 3.12.14 | Python 3.14.7 |
|---|---|---|
| Complete unittest suite | 204 discovered; 203 PASS, 1 SKIP, 0 FAIL | 204 discovered; 203 PASS, 1 SKIP, 0 FAIL |
| Full validator and format profile | PASS | PASS |
| Catalog, 42-case routing coverage and role guide/SVG | PASS | PASS |
| Canonical synchronization check | PASS; no differences | PASS; no differences |
| Real smoke CLI help and compileall | PASS | PASS |

The skip is the existing Windows file-symlink privilege limitation. A separate
real-CLI adversarial run executed 12 validator invocations and both hardlink
sync modes: expectations matched, the unrelated fixture bytes stayed unchanged,
and no backup was created. `git diff --check` passed. All six original smoke
functions retained identical ASTs across the module move; the shared JSON reader
was intentionally hardened separately. [Machine-readable local results](../evidence/workflows-1.7/checks.json)
retain the earlier failures and final command exit codes.

Remote CI is a separate post-push check; consult the run for the actual commit.
The external session report records its URL and completion status.

## Unproven scope and limits

- New skills' automatic native discovery: NOT_RUN.
- Live project implementation, remote PR creation, production rollback/recovery
  and stakeholder messaging in these exercises: NOT_RUN.
- Full current-catalog execution across Codex/Copilot/Claude: NOT_RUN. Existing
  historical runtime records keep their original instruction/version scope.
- PNG legibility/content was manually inspected; the deterministic checker covers
  the maintained Markdown/SVG and skill inventory, not generated-image semantics.
- The supplemental system skill validator could not start because PyYAML is
  absent: NOT_RUN. Loop's standard-library full/format gates are separate checks.
- Instructions remain guidance. Permission enforcement, monitoring and operational
  policy require the host and actual service environment.
