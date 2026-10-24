# Minimal read-only sum design

Reference: MCP 2026-07-28, https://modelcontextprotocol.io/specification/2026-07-28.
Version facts are supplied by the parent review; no network verification performed.
The reference uses stateless core; no legacy initialization/session prerequisite.
Transport selection: offline files only. Client/server/SDK: none instantiated.
These supplied examples cover only a synthetic tool acceptance subset, not full
MCP envelopes or conformance. Required protocol metadata, transport,
authentication and discovery remain NOT_RUN.

## Contract

Tool name: sum. Pure integer addition, no filesystem, network or credential access.
Input schema: {"type":"object","properties":{"a":{"type":"integer"},"b":{"type":"integer"}},"required":["a","b"],"additionalProperties":false}.
Output structuredContent schema: {"type":"object","properties":{"sum":{"type":"integer"}},"required":["sum"]}.
Booleans are excluded from all integers. No numeric magnitude bound is claimed;
the offline computation uses Python arbitrary precision subject to local resources.
A production size limit must be specified and tested before deployment.

The local oracle requires both jsonrpc fields to be the string 2.0, method
tools/call, name sum, exactly a/b arguments, non-null IDs equal in value and
Python JSON-decoded type, and an integer structuredContent.sum equal to a+b.
It does not validate all legal JSON-RPC ID types or complete response envelopes.
Missing/wrong required fields yield FAIL. Case identities and totals are not
used in arithmetic or acceptance logic.

## Errors and timeout

Offline FAIL means a failed acceptance assertion, not an emitted protocol error.
A future server should distinguish malformed envelopes/unknown methods (protocol
errors) from execution failures (tool error result), validating inputs before
execution. Wire error codes and required version metadata need real-spec/runtime
verification: NOT_RUN. Proposed caller deadline: 1 second, cancellation on expiry,
no automatic retry; neither timeout nor cancellation executed here. Addition is
idempotent and has no intended side effects. Pagination is inapplicable.
Version upgrades require a new reference review and rerun; no universal support.

## Acceptance matrix

| Assertion | Expected | Evidence |
|---|---|---|
| Positive and negative valid sums | PASS | results.json |
| Unequal IDs | FAIL | results.json |
| String or boolean operand | FAIL | results.json |
| Incorrect sum | FAIL | results.json |
| Missing fields, typed IDs, boolean output, wrong version/method/name, extra argument | FAIL | verify_checks.py local assertions |
| Transport, metadata, authentication, discovery | NOT_RUN | Outside offline scope |
| Real errors, cancellation, timeout, host compatibility | NOT_RUN | No server |

Tool readOnlyHint may communicate intent only. The eventual host/server must
enforce an allowlist and filesystem/network boundaries independently of catalog
text. No credentials are needed or supplied. Design review is not conformance.
