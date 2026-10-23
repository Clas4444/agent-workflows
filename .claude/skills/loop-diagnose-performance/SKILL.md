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

## Workflow

Define latency, throughput, memory, CPU, or I/O criteria and capture a baseline.
Use bounded profiling with representative inputs. Compare one change at a time,
recording the tool, metric, variance, and result. Do not claim improvement
without repeated comparable measurements.

## Boundaries and evidence

Protect credentials and private data. Report `PASS`, `FAIL`, `BLOCKED`, or
`NOT_RUN`; distinguish missing measurements from a failed measurement.

Stop when no suitable work remains, the deadline or user request ends
the run, a safety boundary is reached, or materially identical results recur
more than three times. Never sleep to consume time; write a consolidated report.
