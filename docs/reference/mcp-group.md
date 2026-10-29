# MCP integration and tool trust

Added 2026-10-24 as a new group with **three skills**. At its 1.4 introduction,
the catalog contained **32 skills in eight functional groups**. See the current
[taxonomy review](../testing/history/taxonomy-1.5.md) for later changes.

| Skill | Responsibility | Evidence required |
|---|---|---|
| loop-mcp-design | Pin the version/transport and design the interface before implementation | Schemas, errors, trust boundaries and a scoped acceptance matrix |
| loop-mcp-test | Exercise offline contracts or an authorized live interface | Fixed oracles, real commands, valid/invalid controls and side effects |
| loop-mcp-security | Review MCP-specific trust and authorization boundaries | Reachability, redacted evidence, enforced versus untested protections |

These workflows specialize general research, integration tests and defensive
review. They do not install a server, grant credentials or make this repository
an MCP implementation. Native skill folders remain flat and self-contained.

## Why this topic

This is a current engineering topic supported by primary sources, not a claim
that it ranks first in a popularity survey. The maintainers released a protocol
revision on July 28, 2026, with changes to lifecycle, routing and authorization.
Microsoft published a dedicated discussion of governance around MCP execution
on April 22, 2026. Those changes create practical needs for version-pinned
designs, contract tests and clear trust boundaries.

Sources reviewed on 2026-10-24:

- [MCP 2026-07-28 release](https://blog.modelcontextprotocol.io/posts/2026-07-28/)
- [Versioned tools specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)
- [Versioned security guidance](https://modelcontextprotocol.io/docs/2026-07-28/tutorials/security/security_best_practices)
- [Microsoft: a control plane for agent tool execution](https://developer.microsoft.com/blog/securing-mcp-a-control-plane-for-agent-tool-execution/)

The design skill explicitly avoids imposing old initialization/session behavior
on a version with a different lifecycle. The security skill distinguishes tool
annotations from actual authorization and treats descriptions/results as data.

## Actual new-skill exercise

One authorized Codex CLI invocation explicitly loaded all three new canonical
skills in a disposable offline fixture. It produced a design, a computed tool
acceptance checker and a security review of an intentionally deceptive catalog.
No network, server, credentials or destructive tool execution was used.

The fixed oracle has six cases: two valid sums and four invalid exchanges
(wrong ID, string operand, boolean operand, wrong sum). An independent parent
grader reran the checker from a fresh directory and changed IDs, operands and
formerly invalid inputs to reject hardcoded answers. All input hashes, including
the protected synthetic file, were unchanged. Scope statements in the reports
were reviewed by the parent; keyword checks alone do not assess report quality.

The initial unrelated README lookup inside the fixture failed and was retained
in local evidence. The workflow proceeded using explicitly provided source
paths. It is not hidden as a successful lookup or an MCP protocol defect.

Captured, reviewed artifacts are in [evidence/mcp-1.4](../evidence/mcp-1.4).
Public fixture inputs are under `tests/fixtures/mcp-offline/`. Tests replay the
captured checker without new model calls. Negative grader controls reject a
hardcoded nominal scorer, changed input sentinel and missing output.

Before the update, 119 tests passed in 17.661 seconds. After the update, **125
tests passed in 19.654 seconds** on Windows/Python 3.12.14. The complete suite
includes the old runner, adversarial, catalog, schema and synchronization tests.
Full/format validation, catalog checks, compilation and project-copy checks
are separate gates. CI must be checked on the pushed revision.

[The reviewed evidence index](../evidence/mcp-1.4.json) records instruction and
artifact identities, scope and independent grader results without raw private logs.

```text
python -m unittest discover -s tests -p test_mcp_smoke_grade.py -v
python scripts/mcp_smoke_grade.py --fixture PATH_TO_A_FRESH_PREPARED_FIXTURE
python -m unittest discover -s tests -v
python scripts/validate.py
python scripts/catalog.py
```

Prepare a replay fixture by copying the three public inputs and the three
captured artifacts into a new ignored directory and computing input-hashes.json
from the copied inputs' current bytes. Do not reuse raw Windows hashes across
Git line-ending normalization. The grader retains each independent attempt in
a new subdirectory; it never invokes a model itself.
Review a checker before replaying it: the grader executes local Python and is
not a sandbox for arbitrary downloaded or model-generated programs.

The hardened grader is specifically tied to the three public fixture inputs.
It derives their expected hashes from `tests/fixtures/mcp-offline`, requires the
fixture hash manifest to match that baseline exactly, and never reads arbitrary
paths from a supplied manifest. An empty map is not evidence of preservation.
It rechecks inputs, the manifest and checker bytes after verification. Prepare
a fresh copy of the current public fixture before replay; this does not silently
certify arbitrary custom corpora or retrofit old executions with stronger proof.
JSON input/output uses the shared duplicate-key/non-finite-literal policy.

## Limits and ownership

This is a **synthetic sum-tool acceptance subset**, not full MCP envelope,
metadata, transport, authentication, discovery or runtime enforcement validation.
Those checks remain **NOT_RUN**. CLI parsing and local artifact checks do not
prove production interoperability or injection resistance of a real deployment.
The shared three-skill exercise is not three independent server acceptance runs.

The MIT copyright notice now names the owner's GitHub identity:
`Copyright (c) 2026 Clas4444`. The permission and warranty paragraphs are unchanged.
