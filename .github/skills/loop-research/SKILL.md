---
name: loop-research
description: "Run a bounded evidence loop to research repositories, documentation, tools, extensions, plugins, skills, MCP servers, or implementation options. Use when the user asks to search, compare, or investigate repeatedly."
argument-hint: "[duration and research question]"
user-invocable: true
disable-model-invocation: false
---

# Loop Research

## Use when

Answer a technical question or compare implementation options with evidence
before recommending or adopting anything.

## Inputs

Research question, decision criteria, scope and available primary sources.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

Define the question and criteria: relevance, maintenance, license, permissions,
security/privacy, compatibility, cost, and verification effort. Check official
documentation and primary repositories first. Record the source, date/version,
evidence, confidence, and whether each statement is fact, inference, or
recommendation. Compare alternatives and verify important claims independently.

## Output

Source-linked comparison distinguishing facts, inferences, confidence and recommendation.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Do not install, authenticate, clone private sources, or send sensitive data
without authorization. Mark each source check `PASS`, `FAIL`, `BLOCKED`, or
`NOT_RUN`; an unavailable source is not `PASS`.

Stop when no suitable work remains, the deadline or user request ends
the run, a safety boundary is reached, or materially identical results recur
more than three times. Never sleep to consume time; write a consolidated report.

## Example

```text
/loop-research 10m compare validation approaches using official sources
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
