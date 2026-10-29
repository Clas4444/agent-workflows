# Documentation map

The [repository layout](reference/repository-layout.md) defines file placement,
names and the boundary between maintained guidance and historical evidence.

Start with the task you actually have. Groups describe responsibilities;
role toolkits recommend a small subset, not a requirement to run all skills.

## Current release routes

| Need | Read |
|---|---|
| Design a conditional loop | [Workflow setup](guides/workflow-setup.md) |
| Check current expectations and gaps | [Setup separation and expectations](testing/checks/setup-separation.md) |
| Inspect setup integration | [Setup evidence](testing/history/1.11.0-workflow-setup.md) |
| Upgrade or roll back | [Release compatibility](reference/release.md) |
| Find current tests, Codex experiments and retained history | [Testing and experiment index](testing/README.md) |

## Existing topic routes

| Need | Start here |
|---|---|
| Understand Loop and try the first workflow | [Start here: installation to checked output](guides/start-here.md) |
| Choose a bundle and understand its iteration, recommendations and limits | [14 illustrated bundle workflows](guides/bundle-workflows.md) |
| Inspect the published 1.10 release and its evidence | [Evidence map](testing/evidence.md), [1.10 scope and tests](testing/history/1.10-results.md) |
| Choose skills for a developer, builder, researcher, QA or incident responder | [Role workflows and English illustrations](guides/role-workflows.md) |
| Try a concrete request without widening scope | [Practical English prompts](guides/workflow-examples.md), [work/artifact guide](guides/work-and-artifacts.md) |
| Write, summarize, organize, decide or study without coding | [Everyday work](guides/everyday-work.md) |
| Install a small selection for your needs | [Install by need](guides/install-by-need.md) |
| Install skills and understand host differences | [Compatibility](reference/compatibility.md) |
| Inspect functional boundaries | [Skill groups](reference/skill-groups.md), [usage](reference/skill-usage.md) |
| Understand implementation and data contracts | [Architecture](reference/architecture.md), [schemas](../schemas/README.md) |
| Author or update instructions | [Authoring](reference/authoring.md), [contributing](../CONTRIBUTING.md) |
| Run checks and interpret their limits | [Test procedure](testing/procedure.md), [validation](reference/validation.md) |
| Understand process cleanup and the earlier autonomous session | [Lifecycle contract](reference/process-lifecycle.md), [historical three-hour ledger](testing/history/2026-10-25-autonomous-3h.md) |
| Inspect the earlier audit and paired pilot | [1.9.1 audit](testing/history/2026-10-25-audit-ab.md), [research ledger](testing/history/2026-10-25-research-audit.md) |
| Inspect the previous restructuring session | [1.9 tests and research update](testing/history/1.9-results.md) |
| Find short names or call a bundle | [Skill finder](guides/skill-finder.md) |
| Check actual host evidence | [Runtime matrix](reference/runtime-test-matrix.md), [runtime smoke](reference/runtime-smoke.md) |

Historical reports are grouped under `testing/history/`; their outcomes and
recorded commands retain their original meaning. Immutable evidence packets
stay at their original paths and bytes. Compatibility pages retain links from
installed instructions and frozen evidence. A historical PASS applies to its
recorded scope, not every current skill or host.

## Archived experiment reconciliation

[Published findings and retained failures](testing/history/2026-10-29-archive-reconciliation.md) · [Audit data](testing/history/2026-10-29-archive-reconciliation.json)
