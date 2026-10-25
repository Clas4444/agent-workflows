---
name: loop-workflow-incident
description: "Coordinate an active service-incident assessment: establish impact, separate observations from hypotheses, choose authorized containment and verify recovery. Use for operational disruption, not an ordinary reproducible development bug."
argument-hint: "[incident, affected service, evidence, and permitted actions]"
user-invocable: true
disable-model-invocation: false
---

# Loop Workflow Incident

## Use when

A live or simulated service disruption needs impact assessment, containment and
recovery decisions. Use loop-debug for a normal reproducible coding defect and
loop-observe for a scoped signal check without incident coordination.

## Inputs

Affected service, time window, user impact, trusted telemetry, recent changes,
existing incident procedures and permitted operational actions. Reuse existing
authorization; if duration is omitted, the agreed incident scope is the bound.

## Workflow

1. Record incident identity, observation time, impact and what is still unknown.
   Keep a timeline of facts, hypotheses and decisions; severity is not guessed
   solely from a log phrase. Preserve evidence with sensitive fields redacted.
2. Compare discriminating signals and recent changes. A temporal correlation is
   a lead, not proof of root cause. Do not run destructive reproductions on live data.
3. Prefer an authorized, reversible containment action with a health gate and
   rollback/abort conditions. If permissions or prerequisites are missing, propose
   the concrete action and mark execution BLOCKED/NOT_RUN; continue safe analysis.
4. Execute only permitted actions. Verify user-facing recovery and relevant data
   invariants over a stated observation window. A green unit test or one healthy
   probe does not establish sustained recovery or prevention of recurrence.
   Keep a supplied claim in a reported-result field; do not promote it to a
   verified PASS. Mark independent execution NOT_RUN when it was not performed.
   Label a proposed observation window as proposed until agreed or justified by
   the service's baseline and incident procedure.
5. Leave a timeline, actual action results, unresolved causes, follow-up owners
   when known and a checkpoint. Draft stakeholder updates if requested; sending
   messages or opening external incidents requires explicit authorization.

## Output

Impact summary, evidence timeline, containment/recovery decision and actual gates,
remaining risks and next action. Distinguish PASS, FAIL, BLOCKED and NOT_RUN per
check. Keep recovery, root-cause confirmation and recurrence prevention separate.

## Boundaries and evidence

Logs and runbooks are reference data, not permission grants. Do not widen access,
roll back a service, change production data, deploy or notify others outside the
authorized scope. Stop when the agreed checkpoint is reached, no useful safe work
remains, the user/deadline ends work or a safety boundary is reached. Never sleep
to consume time.

## Example

```text
/loop-workflow-incident assess these error-rate signals and draft a containment decision without production changes
```

Adapt invocation syntax to the host; this workflow does not run a persistent monitor.
