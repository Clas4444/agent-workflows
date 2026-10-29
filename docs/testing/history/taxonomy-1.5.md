# Cross-group skill review and taxonomy 1.5

The review started from all **32 workflows** at revision
`014fbc8991d0c8912fb0cd9c0882e148fb710e0e`, inspecting their actual workflow,
outputs and boundaries. The resulting catalog has **34 skills in eight groups**.
This is a repository-specific design assessment, not a popularity ranking.

## Reorganized around the requested outcome

| Group | Primary question | Main boundary |
|---|---|---|
| Discovery and scoped planning | What should we adopt or do next? | Evidence or plan; no implicit implementation |
| Implementation and maintenance | What authorized behavior/state should change? | Features, preserved behavior, package/data contracts |
| Debugging and diagnosis | What caused this failure? | Investigation, minimization, regression and repair are distinct |
| Testing and evidence evaluation | What can we demonstrate? | Test layers and fixed-rubric scoring are separate gates |
| Review and security assurance | What findings deserve action? | Source-backed review rather than implementation or scoring |
| Delivery and operational verification | Is this artifact ready, rolled out and observable? | Readiness, rollout and signals must not collapse into one PASS |
| Skill authoring and agent continuation | How is a workflow packaged or continued? | Explicit adapters, finite limits and retained scope |
| MCP integration and tool trust | How does the MCP boundary behave? | Domain-specific contracts, not generic server support |

Planning now sits next to research; general review and security form assurance;
fixed-rubric evaluation moves into verification. Delivery includes the missing
rollout and signal-verification stages. Native folders and public invocation
names remain unchanged, so reorganization does not break installation paths.

## Upgrade, split and merge decisions

| Overlap | Decision and implementation |
|---|---|
| review / plan / evaluate | Keep distinct outputs; upgrade review metadata and require located, evidence-backed findings without inventing a quota |
| code / debug / refactor | Keep feature, demonstrated repair and unchanged-behavior restructuring; upgrade code metadata to prefer specialists when appropriate |
| diagnose / debug / repro | Keep investigation, repair and minimization; upgrade diagnose to competing hypotheses and discriminating experiments |
| generic test / focused layers | Upgrade generic test to choose an unknown strategy; keep known layers explicit and prevent automatic execution of every test type |
| research / repo / tools | Merge navigation with planning, retain target-specific checks and names; no demonstrated reason to remove existing entry points |
| orchestrate / prompt | Already share one runner implementation; normal continuation and inferred follow-ups have different protocols, so do not merge public commands |
| release / deployment | Split responsibilities by adding loop-deploy; readiness must not silently become environment mutation |
| profiling / observability | Add loop-observe; request correlation and detection are different from measuring a performance bottleneck |
| security / adversarial / MCP security | Keep threat review, false-PASS experiments and MCP-specific credential/tool trust distinct |

No skill was deleted or renamed merely to reduce the count. Shared safety
paragraphs alone are insufficient evidence that acceptance contracts are the
same. Detailed per-skill actions and reasons are machine-readable in
`skill-routing.json`, covering every current skill exactly once.

## Cross-group gaps

| Gap | Disposition | Concrete acceptance |
|---|---|---|
| Release candidate → selected environment | Add loop-deploy | Known artifact, authorized target, health/abort gates, exercised local rollback |
| Changed system → detectable/explainable failure | Add loop-observe | Signal provenance, request correlation, detection fixture and privacy/cardinality limits |
| Full incident command and notification handling | Deferred | No incident-specific runbook or authority model supplied; existing diagnosis/deploy/observe can support a scoped response |
| Persistent agent memory and lifecycle | Deferred | No storage/trust model supplied; a generic memory skill would invent requirements |
| General API contract specialization beyond integration tests | Deferred | Need a concrete unsupported contract before duplicating the integration workflow |

The two new workflows have explicit no-production/default-no-background-work
boundaries. Rehearsal and offline signal checks do not establish production
deployment, live alert delivery or runtime enforcement.

## Cross-checking routes

`skill-routing.json` contains one primary-route example for each of 34 skills
and three no-skill controls: **37 fixed cases**. Expected outcomes were written
before the model classification. Cases and decision coverage are checked by:

```text
python scripts/routing_check.py
python scripts/routing_check.py --predictions PATH_TO_PREDICTIONS_JSON
```

The checker requires all case IDs, reports the full denominator and rejects
missing/unknown routes. It does not call a model, dispatch work or demonstrate
automatic host discovery. Several workflows may legitimately collaborate on a
real request; these deliberately scoped examples test the requested primary goal.

Controlled Codex experiments receive only catalog metadata and the request
texts, without expected routes. Its supplied output is graded independently.
The measured result and final suite count are in
[the evidence index](../../evidence/taxonomy-1.5.json); raw logs remain local under
`.loop/taxonomy-routing-1.5/`. This small curated experiment is not a general
routing benchmark and does not prove every workflow was executed.

Observed result: **37/37 accepted routes in each of two invocations**, with the
expected routes withheld. The second independently shuffled catalog and request
order (seeds 1505/1506) to reduce positional matching. The same 37 cases were
used, not 74 unique cases. There was no before/after model-routing baseline, so
this does not quantify an improvement over the old catalog. The untouched test
baseline passed **125 tests in 18.800 seconds**; the final suite passed **130
tests in 19.182 seconds**, Windows/Python 3.12.14. Full/format validation,
catalog/routing gates, compilation and three project-root checks also passed.

## Evidence integrity and compatibility

The four upgraded instructions invalidate direct reuse of their old host
results. The existing invalidation registry records old/current hashes, reasons
and NOT_RUN; historical campaigns remain unchanged. Group moves alone do not
invalidate identical instruction content. The two additions begin with native
host/runtime NOT_RUN. No production deployment, real alerting or background
monitoring was performed by this update.
