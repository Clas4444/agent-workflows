# All-skill responsibility review — 1.9

The review covers all 45 existing names plus four additions. It is a contract/routing inventory with targeted execution, not a claim of full native runtime coverage.

Decisions: 32 KEEP, 12 UPGRADE, one SPLIT_ROUTER and four ADD. Distinct acceptance gates justified keeping diagnosis/repair, drafting/artifacts and software/everyday coordination separate. No public name was removed and no unrelated skills were merged for a smaller count.

| Skill | Decision | Reason |
|---|---|---|
| `loop-review` | UPGRADE | Strengthen artifact, source, capacity, delivery or evidence boundary without merging distinct outcomes. |
| `loop-code` | UPGRADE | Strengthen artifact, source, capacity, delivery or evidence boundary without merging distinct outcomes. |
| `loop-diagnose` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-diagnose-repro` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-diagnose-performance` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-diagnose-regression` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-research` | UPGRADE | Strengthen artifact, source, capacity, delivery or evidence boundary without merging distinct outcomes. |
| `loop-research-repo` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-research-tools` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-test` | UPGRADE | Strengthen artifact, source, capacity, delivery or evidence boundary without merging distinct outcomes. |
| `loop-test-unit` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-test-integration` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-test-coverage` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-docs` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-skill-create` | UPGRADE | Strengthen artifact, source, capacity, delivery or evidence boundary without merging distinct outcomes. |
| `loop-orchestrate` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-prompt` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-debug` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-security` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-refactor` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-ci` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-release` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-plan` | UPGRADE | Strengthen artifact, source, capacity, delivery or evidence boundary without merging distinct outcomes. |
| `loop-dependencies` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-migrate` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-test-e2e` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-evaluate` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-test-adversarial` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-test-compatibility` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-mcp-design` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-mcp-test` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-mcp-security` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-deploy` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-observe` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-context` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-handoff` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-workflow-project` | UPGRADE | Strengthen artifact, source, capacity, delivery or evidence boundary without merging distinct outcomes. |
| `loop-workflow-pr` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-workflow-incident` | KEEP | Existing responsibility/acceptance boundary retained; no demonstrated need for instruction churn. |
| `loop-write` | UPGRADE | Strengthen artifact, source, capacity, delivery or evidence boundary without merging distinct outcomes. |
| `loop-summarize` | UPGRADE | Strengthen artifact, source, capacity, delivery or evidence boundary without merging distinct outcomes. |
| `loop-meeting` | UPGRADE | Strengthen artifact, source, capacity, delivery or evidence boundary without merging distinct outcomes. |
| `loop-organize` | SPLIT_ROUTER | Separate file execution and everyday work; keep public entrypoint with safe fallback. |
| `loop-decide` | UPGRADE | Strengthen artifact, source, capacity, delivery or evidence boundary without merging distinct outcomes. |
| `loop-learn` | UPGRADE | Strengthen artifact, source, capacity, delivery or evidence boundary without merging distinct outcomes. |
| `loop-work` | ADD | New distinct work/artifact outcome with installed payload checks. |
| `loop-files` | ADD | New distinct work/artifact outcome with installed payload checks. |
| `loop-table` | ADD | New distinct work/artifact outcome with installed payload checks. |
| `loop-document` | ADD | New distinct work/artifact outcome with installed payload checks. |

The former explicit-file routing case (route-46) now selects loop-files; a new mixed-request case selects the retained organize router. That taxonomy change was recorded before classification, with the historical 1.8 corpus/results preserved.

See [research](RESEARCH-1.9.md), [machine-readable ledger](evidence/work-1.9/review-ledger.json) and [actual tests](testing/RESULTS-1.9.md).
