---
name: loop-refactor
description: "Improve a scoped code structure while preserving observable behavior through characterization tests, small reversible changes and regression checks. Use for maintainability work without a feature or bug-fix behavior change."
argument-hint: "[duration, target, and maintainability objective]"
user-invocable: true
disable-model-invocation: false
---

# Loop Refactor

## Use when

The user wants clearer structure, reduced duplication or simpler dependencies
without changing observable behavior. Use loop-code for requested new behavior
and loop-debug for an existing incorrect behavior.

## Inputs

Target structure, maintainability objective and observable behavior to preserve.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

1. Define the maintainability objective and behavior to preserve: public API,
   errors, side effects, formats, ordering and relevant performance constraints.
2. Inspect callers, project patterns, worktree changes and existing tests. Capture
   a baseline and add authorized characterization tests for important gaps.
3. Make one small reversible structural change. Avoid mixing behavior changes,
   dependency upgrades and unrelated formatting into the same batch.
4. Rerun characterization tests and relevant project gates. Compare outputs and
   side effects against the baseline; inspect the diff and affected callers.
5. Report the structural benefit, preserved contracts, commands and results.
   Missing behavior evidence is NOT_RUN, not proof of equivalence.

## Output

Characterization baseline, structural diff and equivalent behavior checks.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Preserve unrelated work. Do not change public behavior, dependencies or data
formats without authorization. Keep meaningful assertions. Report PASS, FAIL,
BLOCKED or NOT_RUN and identify any unverified behavior or performance claim.

Stop when no suitable work remains, the deadline or user request ends the run,
a safety boundary is reached, or materially identical results recur more than
three times. Never sleep to consume time; write a consolidated report.

## Example

```text
/loop-refactor 15m simplify the parser while preserving its public behavior
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
