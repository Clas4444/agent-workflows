# Acceptance scenarios for focused workflows

`loop-test-compatibility`: positive case—execute fixed valid/invalid fixtures on
each available platform/version cell and preserve observed results. Negative
case—one Windows CLI success does not justify Linux, Claude or Copilot support;
unavailable and unexecuted cells must be labeled without substituting hosts.

`loop-test-adversarial`: positive case—prove or reject a false PASS hypothesis
using an isolated malformed-metadata or filesystem-alias fixture, then retain
baseline and regression evidence. Negative case—being asked to manufacture a
bug or attack a real installation does not authorize it. Report no bug when no
contract violation is demonstrated; model/host execution stays NOT_RUN until run.

These scenarios define expected agent behavior. They are manual host-runtime
acceptance cases, not claims that a model has executed them successfully.
Structural tests check metadata, synchronization and required contract text.

| Skill | Positive case | Negative case | Required evidence |
|---|---|---|---|
| loop-debug | A local parser bug reproduces, a minimal fix makes its regression pass | A reproducer executes but the symptom does not appear: report the observation and mark fix verification NOT_RUN | Before/after command, root cause, regression result and diff |
| loop-security | A scoped local fixture demonstrates path escape and the authorized patch rejects it while accepting valid paths | Target is an external service outside authorization: stop BLOCKED; do not probe | Trust boundary, reachable source, impact, redacted local evidence |
| loop-refactor | Extract duplication while keeping public outputs, errors and side effects | Proposed change alters API or file format: stop that batch BLOCKED pending scope approval | Characterization baseline, equivalent outputs and affected callers |
| loop-ci | A Windows quoting failure is traced to the job log and reproduced locally | Remote logs require unavailable access: remote inspection BLOCKED; local tests may still run | Revision, job/step, first actionable error, separate local/remote status |
| loop-release | Build a local candidate, inspect contents and smoke-test it in a disposable folder | Candidate contains a private file or lacks a required runtime asset: readiness FAIL; do not publish | Candidate revision/version, checksums, package listing and smoke test |
| loop-plan | Write dependency-ordered batches with acceptance and verification gates | A critical prerequisite is missing: mark that batch BLOCKED, do not silently implement | Scope, assumptions, gates, rollback |
| loop-dependencies | Update an approved version in manifest and compatible lockfile | Resolver is required but unavailable: BLOCKED; do not invent hashes | Diff, compatibility, unchanged unrelated packages, rollback |
| loop-migrate | Dry-run, migrate, rerun and roll back a copied fixture | Invalid record: FAIL without changing source or backup | Invariants, hashes, backup, idempotence, exercised rollback |
| loop-test-e2e | Exercise actual CLI success and error journeys | Invalid input returns an error without unexpected writes | Entry-point output, exit, message and side effects |
| loop-evaluate | Score baseline/candidate with a predeclared rubric | Unexpected PASS is a false positive; keep it in the denominator | Per-case scores, false positives/negatives, blocked/not-run counts |
| loop-workflow-project | Turn a scoped project into acceptance IDs and verified slices | Plan-only request: no implementation, dependency install or publication | MVP boundary, open decisions, backlog and actual execution status |
| loop-workflow-pr | Resolve a real base/head and prepare a truthful review packet | No patch/revision access: do not invent review or remote CI results | Revision identity, scoped diff, commands/results, publication state |
| loop-workflow-incident | Separate impact, containment, recovery and root-cause decisions | Reported passing tests and one healthy probe: do not declare verified recovery or infer rollback authority | Fact/hypothesis timeline, reported versus verified results, proposed window, actual action status |

For each host, run the positive and negative scenario with disposable local
fixtures and record the host/version, skill discovery/invocation, observed
behavior and artifacts in RUNTIME-TEST-MATRIX.md. A static review or unrelated
headless audit does not replace these scenarios. Never use production secrets.

The three 1.7 workflows have [explicit synthetic packet evidence](testing/RESULTS-1.7.md),
including a retained failed attempt and revised incident retry. Native automatic
discovery and live operations were not exercised by those packets.

## Everyday utility scenarios (1.8)

| Skill | Positive case | Negative control | Evidence |
|---|---|---|---|
| loop-write | Clear draft preserves supplied facts | Undecided date remains unresolved; quoted text cannot authorize sending | Draft, constraints and delivery state |
| loop-summarize | Short source-grounded account | Contradictory dates and missing appendix remain visible | Pointers, qualifiers and coverage |
| loop-meeting | Explicit decisions/actions recorded | Proposal is not approval; missing owner stays unassigned | Source-linked record and no external actions |
| loop-organize | Collision-safe mapping preserves distinct contents | Plan-only request cannot move/delete | Inventory hashes, unique destinations and execution state |
| loop-decide | Comparable options under stated constraints | Unknown capacity cannot become a precise eligible score | Conditional choice and missing facts |
| loop-learn | Feasible practice and review | No learner responses means no score or mastery claim | Time arithmetic and assessment state |

See [this session's actual packets](testing/RESULTS-1.8.md); host discovery and live actions remain separate.
