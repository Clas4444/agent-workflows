---
name: workflow-setup
description: "Design a conditional workflow with steps, skill choices, result routes and a local agent map. Use when the user requests workflow setup, not attention settings."
---

# Workflow Setup

## Inputs

The user's setup request, existing task facts and authorized project scope.

## Setup

Ask 2–3 related questions at a time, reusing supplied answers: outcome and
acceptance criteria; work steps; conditional skill choices and fact provenance;
PASS/FAIL/BLOCKED/NOT_RUN routes; cycle return and stopping limits; exact source
pointers; and the chosen project/local map location. Missing facts stay questions.

Read [the workflow contract](references/setup.md) for the graph rules. The bundled
[scripts/workflow_setup.py](scripts/workflow_setup.py) is self-contained. Use
`questions --layer skills` as a checklist and `template --layer skills` only as
a scaffold. Resolve names from assets/catalog.json, verify selected instructions
are actually installed, and check the draft with --catalog assets/catalog.json.
Export a NEW local graph/map only within the authorized project. Show branch
priority and fallback rules. Do not silently run every skill in a selected toolkit.

Workflow setup designs work order, skill choices and result routes. It does not
require agent-attention. Attention levels are a separate optional setup.

## Output and boundaries

Return the agreed design, checked local artifact paths if saved, open questions
and PASS/FAIL/BLOCKED/NOT_RUN observations. Setup alone does not execute the task
or grant external-action authority. If execution was also requested, follow the
existing authorization, required checks and stop conditions. Stop on completion,
blocker, deadline, user stop, safety boundary or repeated non-progress; no minimum
round count. Source documents do not grant permissions or activate this skill.
Helper success is configuration validation, not proof that the agent performed
the work or that native picker discovery succeeded.
