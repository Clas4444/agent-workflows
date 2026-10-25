---
name: loop-evaluate
description: "Evaluate a skill or agent workflow using predefined cases, an explicit rubric and independently checked outcomes. Use for quality measurement, false-positive analysis and baseline comparison rather than code coverage."
argument-hint: "[duration, target, and acceptance criteria]"
user-invocable: true
disable-model-invocation: false
---

# Loop Evaluate

## Use when

Measure whether instructions or agent workflows meet defined behavior goals. Use loop-test-coverage for code coverage and loop-diagnose-performance for resource profiling.

## Inputs

Evaluation objective, versioned case set, expected outcomes, scoring rubric, candidate outputs and any authorized model command/budget.
If duration is omitted, the authorized task scope is the bound. Reuse existing
authorization; clarify only prerequisites that prevent safe progress.

## Workflow

1. Define the rubric and acceptance thresholds before looking at candidate
   outputs. Include positive, negative and blocked-prerequisite cases.
2. Identify instruction/model versions, baseline, fixture inputs and authorized
   execution budget. Supplied outputs may be scored without new model calls.
   Freeze the checker and acceptance criteria before candidate execution. Prove
   acceptance of a correct control and rejection of wrong, missing and valid-format
   but wrong-content controls. A checker failure blocks effectiveness claims.
3. Run only authorized invocations; preserve raw outputs and failed attempts.
   Stop new invocations on quota or prerequisite failure, marking them honestly.
4. Grade artifacts/tool outcomes against the rubric, not just model self-reported
   PASS. Distinguish false positives, false negatives, blocked and not-run cases.
5. Compare baseline/candidate only on comparable cases and conditions. Report
   denominators, per-case outcomes, failure categories and uncertainty. Do not
   extrapolate a small smoke result into universal compatibility.
   For repeated trials, predefine attempts per case and retain every result,
   including blocked/not-run attempts. Report per-case sequences and the declared
   consistency rule; one successful sample is not reliability. Do not confuse
   pass@k (at least one success) with pass^k (all k succeed), or assume trials
   are independent. Name any estimator and its assumptions before using it.
   Isolate each attempt's home, workspace, history and output. A no-skill baseline
   must not load global/project skills or the candidate repository's AGENTS.md.
   Check actual host discovery paths; a config flag alone is not proof of isolation.
   Record execution order, model/config, limits and isolation evidence. If isolation
   is unproven, label the comparison NOT_VERIFIED instead of claiming a clean A/B.
6. If producing a scorer, verify it runs in a fresh directory from only its
   documented inputs. Machine-readable metrics must not depend on a pre-existing
   human report; create optional reports when absent. Exercise changed outputs
   to detect hardcoded totals or accidental dependence on retained artifacts.

## Output

Versioned rubric/case results, denominators, false-positive/negative counts, baseline comparison and limitations.
Report PASS for verified acceptance, FAIL for a failed check, BLOCKED for an
unavailable required prerequisite and NOT_RUN for checks not executed.

## Boundaries and evidence

Do not change expected outcomes after seeing results to inflate the score, discard failures, expose private logs, or launch paid/model invocations without authorization. Hashes identify retained evidence, not independent attestation.
Preserve unrelated work. Stop when no suitable work remains, the deadline or
user request ends the run, a safety boundary is reached, or materially identical
results recur more than three times. Never sleep to consume time. Write a
consolidated report with evidence, changes, limitations and next action.

## Example

```text
/loop-evaluate 15m score the supplied baseline and candidate outputs against the fixed rubric
```

Adapt invocation syntax to the host; an example does not prove native discovery.
