# Skill usage

These skills guide bounded everyday work and software development in an agent
host. They do not grant permissions or replace project-specific instructions.
Invoke one skill with a
clear target and desired outcome; let the host apply its normal approval rules.

## Select a skill

Use `loop-deploy` for an authorized rollout or local rehearsal after a candidate
is prepared; use `loop-observe` to verify signal correlation and detection.
`loop-release` remains readiness preparation, and profiling remains
`loop-diagnose-performance`. See [cross-group decisions](TAXONOMY-1.5.md).

The **MCP integration and tool trust** group adds `loop-mcp-design` for a pinned
interface design, `loop-mcp-test` for offline or authorized live contract checks,
and `loop-mcp-security` for MCP-specific trust/authorization review. A local
fixture PASS does not establish MCP transport or authentication conformance.

Browse the fifteen functional groups in [the grouped catalog](SKILL-GROUPS.md)
or the README for all 53 skills. The table below is a selection of common
workflows; installation paths remain unchanged. Examples use Codex dollar skill
mentions after discovery. Other hosts may use different invocation syntax;
native slash aliases are not registered by this repository. See the
[finder guide](guides/SKILL-FINDER.md).

| Skill | Use it for | Typical invocation |
|---|---|---|
| `loop-review` | Scope, evaluate, and report on a change or repository | `$loop-review 10m repository` |
| `loop-code` | Implement an authorized feature or configuration change | `$loop-code 15m add the requested JSON export` |
| `loop-diagnose` | Investigate an unexplained symptom with competing hypotheses | `$loop-diagnose 15m failing command` |
| `loop-diagnose-repro` | Minimize a repeatable reproducer | `$loop-diagnose-repro 15m import crash` |
| `loop-diagnose-performance` | Measure a slow or resource-heavy path | `$loop-diagnose-performance 20m slow endpoint` |
| `loop-diagnose-regression` | Compare known-good and failing states | `$loop-diagnose-regression 20m recent regression` |
| `loop-research` | Investigate a scoped everyday or technical question | `$loop-research 10m validation options` |
| `loop-research-repo` | Evaluate repositories before adoption | `$loop-research-repo 15m candidate repositories` |
| `loop-research-tools` | Evaluate tools, extensions, skills, or MCP servers | `$loop-research-tools 15m testing tools` |
| `loop-test` | Select and run a bounded project test strategy | `$loop-test 10m API change` |
| `loop-test-unit` | Test one module or function | `$loop-test-unit 10m parser module` |
| `loop-test-integration` | Test process, file, service, or database boundaries | `$loop-test-integration 15m upload flow` |
| `loop-test-coverage` | Improve meaningful coverage | `$loop-test-coverage 15m authentication` |
| `loop-docs` | Audit and update documentation | `$loop-docs 10m usage guide` |
| `loop-skill-create` | Create or maintain a synchronized skill | `$loop-skill-create 20m release workflow` |
| `loop-orchestrate` | Run an explicitly configured headless command | `py -3 scripts/run_loop.py ...` |
| `loop-prompt` | Run an initial prompt and bounded follow-ups | `$loop-prompt 3 review this change` |
| `loop-debug` | Reproduce, repair and regression-test a specific bug | `$loop-debug 15m fix parser rejecting valid input` |
| `loop-security` | Review trust boundaries and verify scoped defensive fixes | `$loop-security 20m local file upload handler` |
| `loop-refactor` | Improve structure while preserving behavior | `$loop-refactor 15m simplify parser without API changes` |
| `loop-ci` | Trace and repair a failed CI job | `$loop-ci 15m failed Windows test job` |
| `loop-release` | Prepare and smoke-test a release candidate | `$loop-release 20m verify candidate version 1.10.2-experimental` |
| `loop-plan` | Break a scoped request into verifiable dependent batches | `$loop-plan 10m plan a JSON export command` |
| `loop-dependencies` | Maintain approved versions and lockfile consistency | `$loop-dependencies 15m update the approved package` |
| `loop-migrate` | Change persisted formats with dry-run and rollback | `$loop-migrate 20m upgrade local JSON fixtures to schema v2` |
| `loop-test-e2e` | Exercise a complete real entry-point journey | `$loop-test-e2e 15m test CLI success and invalid input` |
| `loop-evaluate` | Score versioned workflows against a fixed rubric | `$loop-evaluate 15m compare supplied baseline and candidate outputs` |
| `loop-test-adversarial` | Challenge declared invariants and prove false PASS results in isolated fixtures | `$loop-test-adversarial test metadata and synchronization boundaries without touching real installations` |
| `loop-test-compatibility` | Check a declared platform/version/adapter matrix without inventing support | `$loop-test-compatibility compare available CLI entry points and mark unavailable hosts NOT_RUN` |

## Recommended sequences

`loop-debug` closes a bug with a verified repair; `loop-diagnose` may finish with
an isolated cause and no code change. `loop-security`, `loop-refactor`, `loop-ci`
and `loop-release` each target a different acceptance gate rather than repeating
a general implementation loop. None grants permission to publish or deploy.
See [SKILL-SCENARIOS.md](./SKILL-SCENARIOS.md) for positive and negative manual
acceptance cases. Contract-text tests do not prove an agent follows a skill.

For a code change:

1. Establish scope and acceptance criteria; use `loop-plan` when planning is needed.
2. `loop-code` — implement one small authorized batch.
3. `loop-test` or a focused testing skill — verify behavior.
4. `loop-docs` — update commands or user-facing behavior.
5. `loop-review` — inspect the final diff and evidence.

For a larger change, precede this sequence with `loop-plan`. Choose
`loop-migrate` when persisted state changes and `loop-dependencies` when a
package/lockfile update is the target. `loop-test-e2e` checks the actual user
journey; it is broader than an isolated integration boundary. `loop-evaluate`
uses a fixed rubric and preserves failures, rather than measuring code lines.

For a diagnosis, use the narrowest diagnosis skill that fits. For adoption
decisions, use `loop-research-repo` or `loop-research-tools` before
`loop-review`. Do not install or authenticate anything without authorization.

Every loop reports `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`, plus commands or
evidence, changed files, remaining gaps, and the next action. Stop when useful
authorized work ends, a safety boundary is reached, the deadline expires, or
materially identical results repeat more than three times.

## `$loop-prompt`

`$loop-prompt 3 task` means one initial invocation followed by at most three
agent-generated follow-ups. It does not guarantee four invocations. A timeout,
failure, block, startup error, missing or malformed marker, duplicate prompt or
result, safety boundary, or missing evidence stops the run.

For direct orchestration, quote `{prompt}` as one argument on Windows:

```text
py -3 scripts/run_loop.py --prompt "Review and test this change" --follow-up-count 3 --timeout-seconds 600 --self-prompt -- copilot -p "{prompt}"
```

Inspect local JSON state and Markdown reports before sharing captured output.
Fake-agent tests verify the runner protocol only; they do not prove runtime
compatibility with a particular host or host version.

## Context and session transfer (1.6)

- `loop-context`: select relevant existing sources, preserve critical constraints and record conflicts/identities.
- `loop-handoff`: checkpoint unfinished work or validate a saved checkpoint before resuming. It does not launch another process.

See [research and verification](RESEARCH-1.6.md).

## Project workflows (1.7)

Use `loop-workflow-project` for MVP-to-slice delivery, `loop-workflow-pr` for a review packet, and `loop-workflow-incident` for incident impact and recovery decisions. Do not invoke a whole lifecycle for a narrow code edit. See [role workflows](guides/ROLE-WORKFLOWS.md).

## Everyday utility skills (1.8)

- `loop-write`: Everyday drafts; delivery is separate.
- `loop-summarize`: Source-grounded summaries and coverage limits.
- `loop-meeting`: Meeting decisions/actions without invented ownership.
- `loop-organize`: select files or work for an ambiguous organization request; it does not perform moves.
- `loop-decide`: Conditional choices under stated priorities.
- `loop-learn`: Feasible practice and learning plans without invented assessment.

See [install by need](guides/INSTALL-BY-NEED.md) and [non-coding examples](guides/EVERYDAY-WORK.md).

## Work and artifact delivery (1.9)

- `loop-work`: coordinate and complete bounded everyday deliverables.
- `loop-files`: file inventories, pinned mappings, authorized native moves and recovery checks.
- `loop-table`: source-preserving table analysis with explicit units and missing-value rules.
- `loop-document`: actual document artifacts and separate content/layout/export gates.

`loop-organize` remains a compatibility selector; explicit filesystem requests now route to loop-files. Supporting resources are declared, synchronized and tested from fresh installations.

## Selection and incoming knowledge work (1.10)

- `loop`: portable canonical-name/bundle lookup; see [finder](guides/SKILL-FINDER.md).
- `loop-intake`: source-backed brief for an unclear request, before delivery.
- `loop-support`: ticket impact/category and response draft, without inventing SLA.
- `loop-knowledge`: maintain multi-source claims, conflicts and source revisions.

Use `$loop bundle support` or `$loop bundle knowledge` to select a toolkit.
Use only necessary members and read their current installed instructions. Native
slash discovery is separate from deterministic lookup and remains host-dependent.
