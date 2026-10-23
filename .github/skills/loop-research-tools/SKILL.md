---
name: loop-research-tools
description: "Research tools, extensions, plugins, skills, and MCP servers in a bounded evidence loop. Evaluate capability, permissions, maintenance, compatibility, cost, and adoption risk before recommending or installing anything."
argument-hint: "[duration and capability gap]"
user-invocable: true
disable-model-invocation: false
---

# Loop Research Tools

## Use when

Evaluate a tool, extension, plugin, skill, or MCP server before recommending or
installing it.

## Workflow

State the capability gap and decision criteria. Inspect local tools and
configuration before checking official documentation and primary repositories.
Record capability, permissions, data flow, maintenance, compatibility, cost,
license, evidence, and a verification plan.

## Boundaries and evidence

Do not install or authenticate without explicit authorization. Mark every
candidate `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Stop when no suitable work remains, the deadline or user request
ends the run, a safety boundary is reached, or materially identical results
recur more than three times. Never sleep to consume time; write a consolidated
report.
