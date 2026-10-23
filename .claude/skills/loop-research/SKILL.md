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

## Workflow

Define the question and criteria: relevance, maintenance, license, permissions,
security/privacy, compatibility, cost, and verification effort. Check official
documentation and primary repositories first. Record the source, date/version,
evidence, confidence, and whether each statement is fact, inference, or
recommendation. Compare alternatives and verify important claims independently.

## Boundaries and evidence

Do not install, authenticate, clone private sources, or send sensitive data
without authorization. Mark each source check `PASS`, `FAIL`, `BLOCKED`, or
`NOT_RUN`; an unavailable source is not `PASS`.

Stop when no suitable work remains, the deadline or user request ends
the run, a safety boundary is reached, or materially identical results recur
more than three times. Never sleep to consume time; write a consolidated report.
