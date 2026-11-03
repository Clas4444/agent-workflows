# Workflow and attention coordination contracts v1

These contracts separate product behavior from experiment control. Neither
contract installs a peer repository, imports its code, grants external-action
authority or proves real-model adherence. Integration is explicit opt-in.

## Product: workflow-attention/v1

Agent Workflows owns the step sequence, condition facts, binding priority,
selected skills, result routes, mandatory criteria and ending conditions.
Agent Attention owns processing levels within the selected scope. It cannot
introduce a step, change a route/skill, expand permissions, remove criteria or
interpret a lower verification level as permission to omit mandatory checks.
Workflow Setup remains workflow design; Attention Setup is independent.
The helper's older `--layer attention/both` graph-scaffold options remain for
backward compatibility, with an explicit CLI note; they are not Attention Setup
entry points and do not replace its independent setup process.

The workflow graph remains `schema_version=1`. The preferred attachment is
a separate `contract_version=1` patch containing `attention` and/or binding-index
changes under `steps`. Axis values are integer1..5, with the five names accepted
by the helper. Unsupported versions, missing versioned profile data and unknown
fields are errors before mutation. Conditions, paths, criteria and routes cannot
be patched through this interface. A versionless attention/steps patch remains
the legacy v1 format; explicit empty profiles clear only that override layer.
This compatibility does not silently convert unsupported schemas.

`attach_attention` returns a new graph; its input is unchanged. Ordinary
`select` retains its legacy balanced-default metadata. Python callers choosing
`attention_scope(graph, cursor, current_profile)` explicitly overlay graph and
binding values on the supplied base; omitted base axes are balanced. The exact
original mapping is restored on normal exit, exception, nested exit or early
return. Re-enter after selecting the next step. This mutates only the caller's
in-memory mapping, never host settings or peer files. Without an attention
request it leaves the mapping unchanged. A STOP/DONE cursor cannot start a new
selection. Restoring a mapping is not proof that a model restored its behavior.

Maps are project-local design views. Graph sources remain portable relative
file pointers; export binds a map to an explicitly selected project. No fixed
machine path, external checkout or global installation is required. A map for
another root is stale; identity checking does not prove source freshness.

The self-contained fixture is
[workflow-attention-v1.json](../../tests/fixtures/workflow-attention-v1.json).
The workflow-side matrix exercises standalone, legacy/new attach, bad/missing
profiles, rejected intent edits, exceptions, early STOP, nested scope, mandatory
criteria, no cross-write and copied helper execution under isolated Python.
These are deterministic helper tests; combined live model behavior is NOT_RUN.

## Experiments: campaign-coordination/v1

This is an experiment harness facility, not a product instruction or attention
axis. Marker defaults are campaign-local. Optional peer sharing passes marker
artifacts explicitly; it never imports or executes a peer implementation.

Each marker has exactly `contract_version`, `scope`, `provider`,
`account_domain`, `campaign`, `reason`, `evidence`, `time`. Provider and campaign
are opaque IDs, and account_domain is an opaque non-secret quota-domain ID or
null. Do not put tokens, email addresses, machine paths or raw error bodies in
these fields. Evidence entries are relative identifiers. Times are timezone-aware
ISO8601. Unknown versions/fields and conflicting scope are diagnosed explicitly.
Provider identifies the authorized request/quota service, not merely a model
family. Different profile directories are not evidence of different accounts;
leave account_domain null until the quota identity is known.

- Campaign scope: cwd, process, parse, output, schema, fixture, auth_home,
  accounting and unknown_local faults. They do not stop another campaign.
- Provider/account scope: quota, rate_limit, capacity and auth_account. Confirmed
  different account domains do not block each other. If either domain is unknown,
  pause calls to the same provider until reviewed; do not assume distinct accounts.
- Different providers are unaffected. This is not permission to switch provider
  or account to evade quota; only a separately user-authorized campaign may do so.
- Stale/future markers affecting the requested domain require review, not deletion
  or automatic expiration. A stale local marker still cannot become a global one.
- Legacy unscoped stop files, when explicitly selected by an old CLI option,
  remain local prerequisites with a review diagnostic; no global domain is inferred.

Markers are append-only. `CampaignLedger` reserves a ticket before a request,
enforces an immutable provider/domain/campaign/cap configuration and serial
in-flight work by default. Unknown/crashed, cancelled and failed reservations
consume capacity; no automatic retry/refund occurs. An exclusive filesystem lock
protects concurrent reservation counts. A crash-held lock requires review and is
never deleted on a timestamp guess. A marker never clears another marker or
resumes a previous grid. The ledger/marker helper never calls a model.

Both harnesses use scoped stop-file decisions. The older per-harness reservation
formats remain compatible; the standalone ledger supplies the new contract for
coordinators and is regression-tested independently. No old campaign was migrated
or executed to test these changes. The canonical marker vector file is
[coordination-v1.json](../../tests/fixtures/coordination-v1.json). Parent review must
confirm the peer uses identical fixture content; this repository does not read
or write the peer checkout to manufacture that result.

## Skill applicability and measurement limits

`loop-work` coordinates a substantial non-coding package with deliverables,
dependencies, capacity and handoff. Its existing instructions explicitly say
not to turn a small request into a process. A small standalone JSON computation
can use a direct prompt; tabular reconciliation may warrant `loop-table`.
Code changes use the relevant coding workflow. Do not automatically append
`loop-work` to every task or treat a bundle as a mandatory sequence.

The existing two-case office pilot is an instruction-overhead experiment, not
proof that `loop-work` is the right router for tiny arithmetic or that it improves
real coordination work. Its original labels are retained. The versioned offline
regrade validates frozen roster, typed usage, final assistant evidence and
required checks; a separate read-only audit checks original traces and source
pins. Mock tests are not model runs. No new model call is authorized by COORD-02.
