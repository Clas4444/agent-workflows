# Research ledger: audit and paired evaluation, 2026-10-25

Session: `audit-ab-20261025T083146Z`. Repository base:
`393104e50f1007b30d04638259db72c6c19f011b`. Research was performed during this
session, rather than relabeling the 1.9 research as new. `PASS` below means the
named source was actually retrieved and read. It does not mean an external
benchmark, host integration, or standard conformance suite was executed.

## Decision and method

The immediate priority is evidence quality: isolate the no-Loop condition,
freeze an independent acceptance checker, and distinguish completed tasks from
tested skill obligations. More skill names or a wholesale directory rewrite
would not establish effectiveness. Use a small paired experiment as a pilot;
publish every trial and all infrastructure failures. Do not transfer an outside
paper's performance numbers to this repository.

The research used `loop-research`: primary documentation, original author
papers and public upstream repositories. Web reads were supplemented by
read-only `git ls-remote <public-url> HEAD`. The first unprivileged Git attempt
failed DNS resolution; the subsequent network-enabled read succeeded. No
external code, document skill, dataset, or license was copied into this repo.

## Source ledger

All sources were checked on **2026-10-25 UTC**. A live documentation page has a
retrieval date, not an invented immutable version. Git pins identify observed
upstream HEAD; they do not identify the installed alpha CLI build.

| ID | Source and observed version | What was actually inspected | Status and limit |
|---|---|---|---|
| S1 | [Agent Skills specification](https://agentskills.io/specification), live page | Required frontmatter, portable folder structure, resources, progressive disclosure and validation sections | PASS source read; reference validator NOT_RUN |
| S2 | [OpenAI Build skills](https://developers.openai.com/codex/skills/), redirected to [current page](https://learn.chatgpt.com/docs/build-skills) | Activation, discovery locations, context budget, optional metadata and authoring guidance | PASS source read; exact local-host agreement NOT_VERIFIED |
| S3 | [openai/skills](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431), `49f948faa9258a0c61caceaf225e179651397431` | Current README and directory-level licensing notice | PASS source read and HEAD resolved; individual skill licenses not exhaustively audited |
| S4 | [openai/plugins](https://github.com/openai/plugins/tree/0722921d5542fc593105c27bd52630babd8b8c2a), `0722921d5542fc593105c27bd52630babd8b8c2a` | README, plugin manifest and companion-surface description | PASS source read and HEAD resolved; plugin installation NOT_RUN |
| S5 | [anthropics/skills](https://github.com/anthropics/skills/tree/dbd4588f9e1033efb41dad4bef2f7947c8993d44), `dbd4588f9e1033efb41dad4bef2f7947c8993d44` | README, self-contained skills, demonstration disclaimer and document-skill license distinction | PASS source read and HEAD resolved; examples not executed |
| S6 | [Codex feature registry](https://github.com/openai/codex/blob/970111f6cb62cc02fe36a82ea7d71b37a2889c97/codex-rs/features/src/lib.rs) and [session startup](https://github.com/openai/codex/blob/970111f6cb62cc02fe36a82ea7d71b37a2889c97/codex-rs/core/src/session/session.rs), `970111f6cb62cc02fe36a82ea7d71b37a2889c97` | `SkipHostSkillDiscovery` description and startup condition; current skill source paths located through GitHub tree API | PASS pinned snippets read; installed binary equivalence NOT_VERIFIED |
| S7 | [SkillsBench paper](https://arxiv.org/html/2602.12670v1), v1, 2026-02-13; [author repo](https://github.com/benchflow-ai/skillsbench/tree/f860ecf02ef53412a030f8661c83d644b739ff01), `f860ecf02ef53412a030f8661c83d644b739ff01` | Task specification, skill conditions, verification, leakage prevention, repeated trials, limitations; current repo quick start | PASS paper/repo read and HEAD resolved; benchmark NOT_RUN |
| S8 | [SWE-Skills-Bench](https://arxiv.org/html/2603.15401v1), v1, 2026-03-16 | Requirement-driven paired design, pinned projects, execution-based verification, preliminary-results warning | PASS paper read; paper-linked repository returned 404; reproduction NOT_RUN |
| S9 | [Skill Coverage](https://arxiv.org/html/2606.20659v1), v1, 2026-06-09 | Observable skill behavior constraints, source grounding, binary coverage and measurement limitations | PASS paper read; automated extraction/judging NOT_RUN |
| S10 | [WorkBench](https://arxiv.org/html/2405.00823v2), v2, 2024-08-03 | Sandbox, task/outcome pairs, outcome-centric evaluation and template dependence | PASS paper read; benchmark NOT_RUN |
| S11 | [Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents), 2026-01-09 | Trials, graders, transcripts, outcomes and harness distinction | PASS engineering article read; recommendations are not a formal standard |
| S12 | [Effective harnesses for long-running agents](https://www.anthropic.com/research/effective-harnesses-for-long-running-agents), 2025-11-26 | Initializer/incremental work, persistent progress, feature checks and premature-completion failure modes | PASS engineering article read; examples NOT_RUN |
| S13 | [AGENTS.md](https://agents.md/), live page | Purpose, setup/test instructions and nested scope | PASS source read; cross-host discovery NOT_RUN |
| S14 | [JSON Schema Core 2020-12](https://json-schema.org/draft/2020-12/json-schema-core), published 2022-06-16 | Vocabulary, dialect, assertions, annotations and validation scope | PASS source read; full dialect conformance NOT_RUN |

Some guessed historical Codex paths (`core/src/skills/loader.rs`,
`core-skills/src/loader.rs`, `skills/src/loader.rs`) returned 404. They are not
evidence that skill discovery is absent. The current pinned tree places loader
modules under `codex-rs/ext/skills/src/loader/`. Failed lookups are retained here
to distinguish source navigation failures from product behavior.

## Findings, applicability and decisions

### Portable packaging is a format contract, not a behavioral guarantee

S1 defines a skill directory with required `SKILL.md`, required name and
description, optional code/resources and naming constraints. It recommends
progressive disclosure and relative references. This supports the repo's
canonical skill folders and declared resource inventory. It does not establish
that a model follows instructions or that every host supports extension fields.
Keep Loop policy checks separate from portable-format checks. Do not describe a
local metadata subset as complete YAML or universal host conformance.

S2 describes metadata-first activation and separate local discovery roots,
including repository `.agents/skills`, user `$HOME/.agents/skills`, admin and
system skills. It also documents a bounded initial skill list that can shorten
descriptions or omit skills. Concise triggers and small selected installations
remain appropriate. Directory byte equality cannot demonstrate native discovery
or implicit routing. Actual discovery must be checked in the chosen host.

### The upstream distribution recommendation changed

S3's current README marks `openai/skills` deprecated and points to S4. This is a
dated documentation finding, not a reason to invalidate older pinned research.
S4 presents plugins containing a manifest plus optional skills/connectors and
other surfaces. A future optional plugin package is worth a separately tested
distribution proposal; replacing all portable native layouts during this audit
would increase scope without measured user benefit. S3 explicitly puts licenses
inside individual skill directories; there is no assumed blanket license.

S5 distinguishes example skills from actual production behavior and separates
many Apache-licensed examples from source-available document skills. Learn from
self-contained packaging and artifact verification patterns. Do not copy those
document implementations or assume that source availability grants an open
source redistribution license. The read-only inspection granted no credentials,
network integration, or external action authority.

### Baseline isolation requires evidence, not a prompt promising to ignore skills

S6 marks `skip_host_skill_discovery` under development. Its startup fast path
requires both the feature and no extension requiring host discovery. The pinned
[skills extension](https://github.com/openai/codex/blob/970111f6cb62cc02fe36a82ea7d71b37a2889c97/codex-rs/ext/skills/src/extension.rs)
reports that requirement when a host provider exists; its default installer adds
one. This conditional path does not prove that the locally installed
`0.164.0-alpha.11.1` executable suppresses every skill surface. S2's discovery
roots make a new `CODEX_HOME` alone insufficient evidence of a clean baseline.

For the pilot, use separate processes, empty instruction roots, fresh histories
and per-arm task copies; inspect the actual startup trace or a discovery canary.
Keep provider/model/tool/authority settings equal. If those conditions cannot be
demonstrated, label isolation NOT_VERIFIED and do not publish a causal comparison.
A source flag is not a filesystem sandbox: it does not prevent a model from
explicitly reading another readable directory.

### Measure requirement satisfaction and preserve negative results

S7 uses skill/no-skill conditions, deterministic verification and leakage checks.
Its methodology supports frozen task inputs, hidden independent oracles and
retained trajectories. Its task/model distribution does not support adopting a
universal optimum skill count or claiming Loop improvements from its results.
The v1 text contains differing task counts across sections; this audit does not
silently resolve that discrepancy or import its headline scores. Paper license
is CC BY 4.0; the inspected code repo identifies Apache-2.0. No material copied.

S8 anchors tasks to pinned repositories and explicit requirements, with paired
execution-based checks. Its findings are explicitly preliminary. Apply the
design principle, including reporting overhead and losses, rather than its
numerical results. The linked author repository returned 404 in this check;
independent reproduction is therefore unverified. No repository license was
inferred from the paper's availability.

S10 evaluates actual sandbox state changes, rather than an agent's statement
that an email or meeting action succeeded. Apply the same principle locally:
reopen delivered artifacts, check their contents, and inspect unintended state
changes. Its simulated workplace tools and templates do not validate this repo's
real office connectors. This audit neither executed its tasks nor authorized real
email/calendar writes. The inspected paper is CC BY 4.0.

S11 distinguishes individual trials from tasks, final environment outcomes from
transcripts, and evaluation infrastructure from the agent harness. Report raw
per-trial outcomes and distinguish any-success from all-success. A small pilot
cannot support a broad superiority claim. The article is practitioner guidance,
not an independently replicated guarantee or a replacement for negative controls.

### Loaded instructions are not tested obligations

S9 treats observable behavior constraints as a coverage denominator and requires
scenario-specific trajectory evidence. This supports a ledger separating
static review, instruction loading, task success and exercised obligations.
Coverage and correctness must remain separate. Its model-assisted extraction and
judging have measurement assumptions; importing that system in this short audit
would require independent calibration. Use explicit source-linked obligations for
the pilot and mark the rest NOT_RUN. The inspected paper is CC BY 4.0; no outside
coverage percentages are assigned to Loop.

S12 describes persistent progress and incremental verification across context
windows. Keep session ID, exact source pins, failed attempts and handoff state.
The article's initializer/coding split is useful inspiration, not evidence that
Loop's runner reliably cancels descendants or that a Markdown checkpoint
enforces permissions. Those properties require their own runtime tests.

S13 supports a predictable repository instruction file with actual commands and
scope. Audit inherited instructions when isolating experiments. It has no
required schema and does not promise identical implementation by every host.
S14 supplies structural schema semantics, not authenticity of a test report or
truth of an agent's claim. A structurally valid report still needs source/session
identity, fresh execution and meaningful checker controls. No new general JSON
Schema engine is justified solely by this research.

## Rejected changes and remaining research

| Proposal | Decision and reason |
|---|---|
| Invoke all 49 skills in every task | Reject: context/routing cost and no evidence this improves an outcome. Test suitable skills for each task. |
| Add skills to demonstrate progress | Reject: this audit first needs evidence of an unmet distinct workflow. |
| Replace portable installs with plugins immediately | Defer: optional distribution needs native install, dependency and discovery tests. |
| Treat a successful unit suite as model/runtime success | Reject: different objects and acceptance criteria. |
| Automatically claim clean baseline from a new configuration directory | Reject: discovery has other roots and the current feature is conditional. |
| Import published benchmark gains or optimize to one pilot result | Reject: different tasks/models, uncertainty and selection bias. |
| Add MCP/A2A conformance work to this audit | Out of scope: the repository declares skills and a local runner, not a protocol service. Existing MCP instruction quality can be reviewed without claiming server compliance. |
| Automate every skill-obligation coverage judgment now | Defer: extraction/judge calibration would be a separate measured intervention. |

Unproven areas include cross-host native activation, distribution through plugins,
multi-platform model behavior, prolonged/cold handoff effectiveness, real office
connectors, model-independent effects and full external benchmark reproduction.
Read status in this ledger must not be substituted for execution evidence in the
session's testing report.
