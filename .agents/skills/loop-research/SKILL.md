---
name: loop-research
description: "Run a bounded evidence loop to research repositories, documentation, tools, extensions, plugins, skills, MCP servers, or implementation options. Use when the user asks to search, compare, or investigate repeatedly."
argument-hint: "[duration and research question]"
user-invocable: true
disable-model-invocation: false
---

# Loop Research

Define the question and criteria: relevance, maintenance, license, permissions,
security/privacy, compatibility, cost, and verification effort. Search official
documentation and primary repositories first. Record source, date/version,
evidence, confidence, and whether a claim is fact, inference, or recommendation.
Compare alternatives in a table and validate important claims independently.
Record each source check as `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`; an
unavailable search or source is not PASS.

Checkpoint each search angle. If no useful source or angle remains, or materially
identical results occur more than three consecutive times, write the consolidated
report and stop. Do not install, authenticate, clone private sources, or send
sensitive data without authorization. Never sleep to consume duration.
