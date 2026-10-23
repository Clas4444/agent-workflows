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

## Inputs

Capability gap, current tool environment and permission/cost constraints.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

State the capability gap and decision criteria. Inspect local tools and
configuration before checking official documentation and primary repositories.
Record capability, permissions, data flow, maintenance, compatibility, cost,
license, evidence, and a verification plan.

## Output

Capability and permission comparison, data flows, evidence and an adoption verification plan.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Do not install or authenticate without explicit authorization. Mark every
candidate `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Stop when no suitable work remains, the deadline or user request
ends the run, a safety boundary is reached, or materially identical results
recur more than three times. Never sleep to consume time; write a consolidated
report.

## Example

```text
/loop-research-tools 10m assess tools for local workflow validation without installing
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
