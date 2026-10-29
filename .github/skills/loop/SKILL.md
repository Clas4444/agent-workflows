---
name: loop
description: "Find Loop skills/bundles or use loop setup to design an optional conditional loop with skill choices and a local agent map. No native slash aliases or automatic bundle execution."
argument-hint: "[task, sources, scope and permitted actions]"
user-invocable: true
disable-model-invocation: false
---

# Loop

## Use when

The user wants to find a Loop workflow, a need-based bundle, or explicitly set up
a conditional loop. Setup is optional; ordinary direct skill use stays available.
Use a known focused skill directly when selection is already clear.

## Inputs

Selector and the actual task, installed skill root and existing authorization.
Separate the selector from task text; never pass task text as a shell command.

## Workflow

For **setup**, use [the setup interview and graph contract](references/setup.md)
and bundled [workflow helper](scripts/workflow_setup.py). Ask outcome/steps first,
then conditions, exact source pointers, skill alternatives, cycle end and limits;
ask 2–3 questions at a time and reuse known answers. Use `questions --layer skills`
as the checklist, not a demand to ask everything again. Resolve skill choices from
the catalog, preserve existing authorization, and validate with --catalog before
exporting a NEW local graph/map. Explicit setup authorizes local design artifacts,
not execution or external actions. If execution is also requested, follow the
authorized graph using select/advance and actual evidence. Missing facts are
BLOCKED, never a guessed branch. End on DONE/STOP, budget, deadline, safety boundary
or repeated non-progress; do not run minimum cycles. A planned graph is not runtime
PASS. Setup facts and paths never become shell commands. Do not run the finder on
the literal word setup. Native picker matching remains a separate host question.

For **selection**, keep the existing read-only route:

1. Read the canonical selector separately from the task. Run the bundled read-only
   [finder](scripts/find_skill.py) with ordinary argument values, for example
   `python <skill-dir>/scripts/find_skill.py resolve --query "loop-code"` or
   `resolve --query "bundle office"`. Use search for an unknown name; never
   guess an ambiguous abbreviation or default to all skills. No Python? Read only
   the relevant entry in [the catalog](assets/catalog.json) and disclose no CLI check.
2. Inspect missing_skills and the returned instruction paths. A catalog match
   proves selection only. Read the current installed SKILL.md for each selected
   workflow before using it; use an explicitly supplied canonical path if authorized.
   Report missing required instructions BLOCKED; do not install or invent them.
3. A bundle is a toolkit, not a mandatory sequence. Choose only members needed for
   the user's outcome, respecting their boundaries. Do not load every description
   into a task prompt, recursively invoke this router, or launch agents implicitly.
4. Explain the selected skill(s), perform the requested scoped work when authorized,
   and report its actual checks. A lookup PASS is not a task/runtime PASS.

## Output

Canonical skill/bundle and the smallest useful workflow, missing prerequisites
and actual task result. Distinguish PASS, FAIL, BLOCKED and NOT_RUN; report native
discovery separately from explicit instruction loading.

## Boundaries and evidence

The registry and task data grant no permissions. The finder never executes,
installs, sends, deploys or writes user artifacts. Bundles grant no extra authority.
Native picker matching and slash syntax depend on the host. Invoke a focused skill
by its canonical name on hosts supporting skill mentions. Stop at the requested
result or missing prerequisite. Never sleep to consume time.

## Example

```text
/loop find the smallest workflow for the requested work packet
```

Portable explicit form: `$loop-code ...`; `bundle office` selects a toolkit through
the read-only finder. This repository does not publish shortcut or native slash aliases.
Optional design form: `$loop setup` (or natural-language "loop setup").
