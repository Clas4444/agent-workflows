---
name: loop-diagnose-performance
description: "Run a bounded performance-diagnosis loop for slow, memory-heavy, or resource-intensive behavior. Establish a baseline, profile safely, isolate a bottleneck, and verify a targeted improvement."
argument-hint: "[duration, symptom, and performance target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Diagnose Performance

## Use when

Investigate slow, memory-heavy, CPU-heavy, or I/O-heavy behavior with measurable
evidence.

## Inputs

Representative workload, resource symptom and measurable performance objective.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

Define latency, throughput, memory, CPU, or I/O criteria and capture a baseline.
Use bounded profiling with representative inputs. Compare one change at a time,
recording the tool, metric, variance, and result. Do not claim improvement
without repeated comparable measurements.

## Output

Comparable baseline/profile measurements, variance, bottleneck evidence and verification gaps.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Protect credentials and private data. Report `PASS`, `FAIL`, `BLOCKED`, or
`NOT_RUN`; distinguish missing measurements from a failed measurement.

Stop when no suitable work remains, the deadline or user request ends
the run, a safety boundary is reached, or materially identical results recur
more than three times. Never sleep to consume time; write a consolidated report.

## Example

```text
/loop-diagnose-performance 15m profile local parser latency on the supplied fixture
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
