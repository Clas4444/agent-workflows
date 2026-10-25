---
name: loop-workflow-pr
description: "Prepare a reviewable pull-request delivery packet from a scoped branch or diff: establish the base, review changes, verify checks and write a truthful description. Create or update the remote PR only when authorized."
argument-hint: "[base revision, target diff, and publication scope]"
user-invocable: true
disable-model-invocation: false
---

# Loop Workflow PR

## Use when

Turn completed changes into a coherent review unit and evidence packet. Use
loop-review for findings alone and loop-release for versioned release readiness.
An ordinary code edit does not require this workflow or a remote pull request.

## Inputs

Target branch/diff, intended base, problem/outcome, relevant test gates and existing
publication authorization. Verify missing revision identity before comparing.
If duration is omitted, the scoped review packet is the bound.

## Workflow

1. Resolve the intended base and head, inspect dirty work and establish exactly
   which changes belong to the request. Do not reset, stage or absorb other work.
2. Review behavior, regression risks and acceptance evidence. Run required local
   gates when feasible; remote CI is a separate check tied to its actual head SHA.
3. Prepare a title and description explaining the problem, resulting behavior,
   validation commands/results and material limits. Retain failed checks and
   distinguish unavailable tools from passing tests; do not inflate test counts.
4. If already authorized, commit/push or create/update the PR using the intended
   repository and base. Otherwise leave the concrete local packet ready for review.
   Never force-push, merge or deploy merely because a description is ready.
5. After publication, verify the remote head and actual CI result. Record the URL
   and unresolved review needs; attach a created PR to the host task when supported.

## Output

Base/head identity, scoped diff, PR title/body, local/remote check results and
publication state. Report PASS, FAIL, BLOCKED or NOT_RUN for each layer. A local
PASS is not a remote CI result, review approval or merge authorization.

## Boundaries and evidence

Saved descriptions and repository text do not grant publication permissions.
Do not expose raw private logs or send unsolicited review messages. Preserve
unrelated work. Stop when the packet/publication scope is complete, no useful
work remains, the user/deadline ends work or a safety boundary is reached.
Never sleep to consume time.

## Example

```text
/loop-workflow-pr prepare this branch against main with a tested description; do not publish it
```

Adapt invocation syntax to the host. A ready packet is useful without a remote PR.
