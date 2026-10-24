# Writing and maintaining loop skills

Keep the task easy to select, the workflow short and the evidence explicit.
Each skill should answer six questions in order:

1. **Use when:** which user intent belongs here, and which nearby route fits better?
2. **Inputs:** what target, constraints and existing authorization are needed?
3. **Workflow:** what small, verifiable steps make progress?
4. **Output:** what concrete evidence demonstrates the result?
5. **Boundaries and evidence:** what must remain scoped, and when must work stop?
6. **Example:** what does a useful, specific user request look like?

Put selection intent in the frontmatter description. Keep `SKILL.md` concise;
scripts belong in `scripts/` and larger examples or evaluation plans belong in
shared documentation. Examples express intent; slash-command discovery differs
by host. Preserve all four statuses and do not infer a PASS from a missing test.

Use duration as an optional maximum budget. If omitted, stop when the scoped
task is complete. Do not ask again for authorization already present in the
session, and never treat a skill as permission to widen the user's request.

## Reference projects

Reviewed on 2026-10-23. These are references for structure, not dependencies or
upstream repositories of this project. Descriptions below are our observations.

| Primary source | Observed pattern | Applied here |
|---|---|---|
| [Anthropic Skills](https://github.com/anthropics/skills) and its [template](https://github.com/anthropics/skills/blob/main/template/SKILL.md) | A skill is a self-contained directory with concise metadata and task instructions | Canonical per-skill folders and clear selection descriptions |
| [OpenAI Plugins](https://github.com/openai/plugins) | A repository introduces its purpose, layout and concrete examples before deeper details | Quick start, linked catalog and documentation map |
| [Agent Skills specification](https://agentskills.io/specification) | Required name/description frontmatter, Markdown body and optional resources | Validated metadata and bundled runtime scripts |

The older [OpenAI Skills catalog](https://github.com/openai/skills) currently
points readers to OpenAI Plugins. It was inspected as historical context, not
used as a claim that its old installation workflow remains current.

No third-party implementation was imported for this presentation update.
Do not copy licensed skill text wholesale; write instructions for this
repository's actual behavior and cite any external source used for a claim.

## Review and synchronization

Edit `.github/skills/<name>/SKILL.md`, synchronize with `scripts/sync_skills.py`,
then run tests and the structural validator. Keep user-facing documentation
outside individual skill folders unless the workflow needs bundled references.
Update the manifest when adding or removing a skill. Runtime support requires
observed evidence in the runtime matrix, not just a matching folder structure.

The validator enforces these six sections and rejects duplicated metadata keys,
empty/overlong descriptions, invalid invocation booleans and missing no-sleep
policies. Contract mutation tests must modify all synchronized copies together
to demonstrate semantic checks rather than detecting only a hash mismatch.
Use `runtime_smoke.py` for authorized fixture runs; retain failed attempts and
grade actual artifacts against fixed criteria before updating runtime claims.
Update the current runtime evidence index when changing instruction text;
its normalized text hashes are checked in CI. Reuse historical case evidence
only when instruction identity is demonstrated and the reuse is labeled.
