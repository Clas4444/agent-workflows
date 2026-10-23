---
name: loop-diagnose-performance
description: "Run a bounded performance-diagnosis loop for slow, memory-heavy, or resource-intensive behavior. Establish a baseline, profile safely, isolate a bottleneck, and verify a targeted improvement."
argument-hint: "[duration, symptom, and performance target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Diagnose Performance

Define measurable latency, throughput, memory, CPU, or I/O criteria and capture
a baseline. Use bounded profiling with representative inputs and protect
credentials/private data. Compare one change at a time; do not claim improvement
without repeated comparable measurements. Record tool, metric, variance,
`PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`. Stop and consolidate when no new
measurement angle remains or results repeat more than three times; never sleep.
