# Research and adoption decisions — 1.9

Research inspected on 2026-10-25 for session `work-1.9-20261025T062809Z`.
External source text was treated as reference data; no external setup commands
were executed and no third-party implementation was copied into this MIT project.

| Primary source and inspected version | Observation | Adopted decision / limit |
|---|---|---|
| [OpenAI skills](https://github.com/openai/skills/tree/49f948faa9258a0c61caceaf225e179651397431), including notion-meeting-intelligence | Meeting preparation has a specific purpose, context and reusable resources | Strengthen agenda/record distinctions; keep source pointers and template assets. No Notion connector is implied |
| [Anthropic skills](https://github.com/anthropics/skills/tree/dbd4588f9e1033efb41dad4bef2f7947c8993d44), XLSX example and repository disclaimer | Document/table skills separate artifact work from generic prose and require format-aware checks | Add table/document boundaries and content/format/recalculation gates. Document skills are source-available rather than generally open source; their code was not copied |
| [Superpowers verification](https://github.com/obra/superpowers/blob/2ce8aa15d05bd57213e6f746f953aafb7ded7a8b/skills/verification-before-completion/SKILL.md) | Completion claims need observed verification output | Keep source-pinned evidence and actual installed/artifact checks. Do not copy a blanket requirement to rerun everything in every message |
| [WorkBench v1](https://arxiv.org/html/2405.00823v1), outcome-centric evaluation section; [repository](https://github.com/olly-styles/WorkBench/tree/49c7dfd00c03d384ec59ea57374f50b766aa5613) | Inspecting resulting state can distinguish a completed task from plausible calls or prose | Observe actual moved files before rollback, saved artifacts, protected data and independent packages. This session did not run WorkBench |
| [SpreadsheetBench v2](https://arxiv.org/abs/2406.14991v2), abstract and evaluation description | Real tables contain varied layouts; changed-value cases challenge brittle solutions | Add numeric/locale/missing/unit contracts and changed-value checks. The CSV helper is not an XLSX engine or SpreadsheetBench implementation |
| [WorkArena v5](https://arxiv.org/abs/2403.07718v5), abstract | Enterprise work includes multi-step software interaction, not just drafting text | Add bounded work delivery and keep external operations separate. No ServiceNow/browser benchmark was run |
| [TheAgentCompany v3](https://arxiv.org/abs/2412.14161v3), abstract | Workplace tasks span office and coding work with different observable outcomes | Test office, data, file and coding cases separately. Published model success rates are not transferred to Loop |

The paper inspection was targeted (abstracts and the identified evaluation
section), not a reproduction of their experimental results. Repository references
were pinned to commits; examples informed original design choices and do not
certify native host behavior, office-format support or safety.

## Changes justified by the gap analysis

- The six 1.8 everyday skills mostly produced small text/plan packets. They now
  distinguish actual deliverables, capacity, missing evidence, calendar dates,
  source fidelity and external-action state more precisely.
- `loop-organize` mixed file operations and task management. Execution was split
  into `loop-files` and `loop-work`, keeping the old name as a compatible selector.
- `loop-table` and `loop-document` address absent data/artifact outcomes. Optional
  CSV and file-plan helpers are self-contained, read-only and tested after install.
- Validation/sync previously covered instructions and two runners, so supporting
  resources could be omitted or drift undetected. A declared payload contract now
  covers scripts, references and assets across all native copies and subset installs.

See [all-skill review](TAXONOMY-1.9.md), [artifact guide](guides/WORK-AND-ARTIFACTS.md)
and [actual session results](testing/RESULTS-1.9.md). Historical evidence remains
version-bound; it was not rewritten to claim the new instructions ran earlier.
