---
name: loop-research-repo
description: "Research repositories and open-source projects in a bounded evidence loop. Compare relevance, activity, license, security, compatibility, and maintenance before recommending adoption."
argument-hint: "[duration and repository question]"
user-invocable: true
disable-model-invocation: false
---

# Loop Research Repo

## Use when

Evaluate repositories or open-source projects before recommending adoption.

## Workflow

Define the decision and criteria. Check official repository pages, documentation,
releases, issues, and license sources first. Record each URL, version/date,
evidence, confidence, and fact versus inference. Compare alternatives in a
table.

## Boundaries and evidence

Do not clone private sources, authenticate, install, or send sensitive data
without authorization. Mark each check `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Stop when no suitable work remains, the deadline or user request ends
the run, a safety boundary is reached, or materially identical results recur
more than three times. Never sleep to consume time; write a consolidated report.
