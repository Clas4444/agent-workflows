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

## Inputs

Candidate repositories, adoption question and required license/runtime constraints.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

Define the decision and criteria. Check official repository pages, documentation,
releases, issues, and license sources first. Record each URL, version/date,
evidence, confidence, and fact versus inference. Compare alternatives in a
table.

## Output

Repository comparison with URLs, dates/revisions, maintenance and adoption risks.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Do not clone private sources, authenticate, install, or send sensitive data
without authorization. Mark each check `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`.

Stop when no suitable work remains, the deadline or user request ends
the run, a safety boundary is reached, or materially identical results recur
more than three times. Never sleep to consume time; write a consolidated report.

## Example

```text
/loop-research-repo 15m compare the supplied parser repositories for adoption
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
