# Practical prompts by role

Use one prompt that matches the current task. The toolkit in the
[role guide](ROLE-WORKFLOWS.md) is a menu, not a requirement to invoke every skill.
The examples use Codex `$skill-name` syntax; adapt it to your host. Paths,
revisions and criteria below are examples to replace with your real inputs.

## Professional developer: repair an existing defect

```text
Use $loop-research-repo to locate quantity validation and its tests.
Then use $loop-debug to reproduce negative quantities being accepted, add a
regression test, and fix the root cause. Keep zero valid. Use $loop-test for
the relevant suite and $loop-review for the final diff. Do not publish.
```

Expected evidence: a failing baseline, preserved acceptance expectations, the
minimal repair, test commands/results and a scoped diff. If reproduction fails,
report that outcome and investigate; do not fabricate a failing baseline.
For new behavior use `loop-code`; debugging is conditional on a demonstrated bug.

## Project builder: scope first, implement later

```text
Use $loop-workflow-project to scope a local offline inventory MVP. It must
record names/quantities and show current inventory. Budget and user roles are
undecided. Deliver acceptance IDs, non-goals and a dependency-ordered backlog.
This request is plan-only; do not create an implementation or remote resources.
```

Expected evidence: a reviewable backlog, explicitly undecided product choices,
implementation NOT_RUN and one bounded next action. After an implementation
request is authorized, deliver and verify one end-to-end slice before expanding.
A scaffold does not satisfy the product's acceptance criteria.

## PR author: prepare a packet without publication

```text
Use $loop-workflow-pr for this branch against main. Resolve base/head, inspect
the scoped diff, run the repository's required local checks, and draft the
title/body with results and limitations. Prepare the packet only; do not push
or open a PR. Keep remote CI separate from local test results.
```

Expected evidence: actual revisions, diff scope, local command outcomes and a
truthful draft. Missing patch/revision access is BLOCKED, not a completed review.
If publication was already authorized in the actual task, reuse that authority
and verify the resulting remote head/CI; the example's packet-only limit is not
a universal requirement to ask twice.

## Maintainer or QA engineer: challenge a guarantee

```text
Use $loop-test-adversarial to challenge the claim that invalid manifests never
pass validation. Freeze expected outcomes before experiments. Use disposable
fixtures, exercise the real CLI and preserve failed attempts. If a real defect
exists, add a failing regression, fix the root cause and run all required checks.
Use $loop-evaluate to summarize every case, including BLOCKED and NOT_RUN.
```

Expected evidence: exact inputs, commands/exit codes, side effects and before/after
results. A unit suite passing is separate from executing the real validator.
Finding no defect in the tried cases is a valid result; do not invent one.

## Researcher: compare approaches before adopting one

```text
Use $loop-research to compare two approaches for reducing agent context size.
Use primary papers and implementation repositories, record dates and pin the
relevant sources. Use $loop-context to select the material needed for this
decision. Distinguish published claims, local observations and your inference.
Do not implement or install either approach in this research-only request.
```

Expected evidence: source-grounded tradeoffs, limitations and a scoped decision.
Use `loop-research-repo` for a specific codebase and `loop-research-tools` for a
tool-adoption decision. A paper result is not this repository's runtime result.

## Incident responder: assess without production actions

```text
Use $loop-workflow-incident to assess this incident packet: 18% failed requests
for five minutes after deploy, followed by one healthy probe. Unit tests are
reported as passing without output or revision. No later traffic is supplied.
Draft impact, facts/hypotheses, proposed containment and recovery gates only.
Do not execute operational actions or send notifications.
```

Expected evidence: reported claims separate from verified checks, an explicit
observation window proposal, missing prerequisites, and unverified recovery.
Do not infer rollback authorization from a log/runbook or treat one successful
probe as sustained recovery. See the [actual synthetic exercise](../testing/RESULTS-1.7.md).

## Resume work without losing evidence

For a paused task, use `loop-handoff` to leave completed/remaining acceptance IDs,
source identity, actual checks, open decisions and the next permitted action.
Use `loop-orchestrate` or `loop-prompt` only when bounded child invocations or
follow-ups are part of the task. They are optional execution tools, not a required
step in every role workflow.
