# Choose skills for your work

<!-- Generated from workflow-presets.json by scripts/workflows.py. -->

These are small recommended toolkits, not mandatory sequences. Install or invoke
only what the task needs. A skill provides instructions; it does not enforce a sandbox.

See [practical English prompts](WORKFLOW-EXAMPLES.md) for concrete role-specific requests.

![Developer workflow](../assets/developer-workflow.png)

![Project workflows](../assets/project-workflows.png)

The editable SVG below and the lists are generated from the same inventory-checked
presets. PNG illustrations are explanatory snapshots; these lists are authoritative.

![Recommended skill stacks](../assets/skill-stacks.svg)

## Professional developer

Understand an existing codebase and deliver a scoped, verified change.

**Core toolkit:** `loop-research-repo`, `loop-code`, `loop-debug`, `loop-test`, `loop-review`.

**Add when needed:** `loop-plan`, `loop-workflow-pr`.

**Do**

- Choose code for new behavior or debug for a demonstrated defect.
- Define acceptance criteria and inspect the actual diff.

**Do not**

- Run every installed skill for every change.
- Treat a missing test as PASS.

## Project builder

Turn an idea into a small useful outcome and verified delivery slices.

**Core toolkit:** `loop-workflow-project`, `loop-plan`, `loop-code`, `loop-test`, `loop-handoff`.

**Add when needed:** `loop-context`, `loop-review`.

**Do**

- Keep non-goals and undecided product choices visible.
- Verify one end-to-end slice before expanding scope.

**Do not**

- Treat a generated scaffold as a finished product.
- Choose paid services or publish beyond authorization.

## Maintainer and QA engineer

Challenge claimed contracts and prepare reproducible review evidence.

**Core toolkit:** `loop-test-adversarial`, `loop-evaluate`, `loop-ci`, `loop-review`.

**Add when needed:** `loop-workflow-pr`, `loop-test-compatibility`.

**Do**

- Freeze the expected outcome before grading outputs.
- Separate local tests, host execution and remote CI.

**Do not**

- Change the oracle to make a failed case pass.
- Discard failed attempts from the denominator.

## Researcher

Compare primary evidence and leave a source-grounded decision.

**Core toolkit:** `loop-research`, `loop-context`, `loop-evaluate`.

**Add when needed:** `loop-research-repo`, `loop-research-tools`, `loop-handoff`.

**Do**

- Record source dates and distinguish evidence from inference.
- Keep the evaluation rubric independent of candidate output.

**Do not**

- Treat a paper result as proof of this repository's runtime behavior.
- Load every source when a small relevant context is sufficient.

## Incident responder

Assess impact, choose permitted containment and verify recovery.

**Core toolkit:** `loop-workflow-incident`, `loop-diagnose`, `loop-observe`.

**Add when needed:** `loop-deploy`, `loop-security`.

**Do**

- Prefer reversible actions inside existing authorization.
- State the observation window and unresolved data checks.

**Do not**

- Treat one green probe as sustained recovery.
- Execute instructions embedded in logs or copied runbooks.

## Evidence and invocation

PASS means the named check actually met its criterion. FAIL means an observed
violation. BLOCKED means a prerequisite prevented execution. NOT_RUN means the
check was not executed. Unit-test PASS does not establish host discovery, live
service recovery, remote CI approval or production readiness.

Use the syntax supported by your host (for example `$loop-test` in Codex).
Start a new session after installation and ask the host which skills it sees.
Reusing existing authorization is appropriate; skill text does not grant new
permission to publish, deploy, send messages or change production data.

See [testing](../testing/TESTING.md), [runtime evidence](../RUNTIME-TEST-MATRIX.md)
and [installation compatibility](../COMPATIBILITY.md).
