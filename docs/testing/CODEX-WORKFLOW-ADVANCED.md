# Codex workflow experiment: harder office cases

Recorded 2026-10-30. Requested Codex CLI model `gpt-6.1-sol`, reasoning `low`, CLI 0.165.0-alpha.1.2 on Windows. Agent Workflows 1.11.2 candidate adds a public experiment harness; the `loop-work` instruction itself is unchanged from the prior experiment and is hash-pinned.

**Measurement PASS:** 36/36 model calls and 18/18 packages passed their fixed checks. Every case/arm passed both planned repetitions. This is consistency on two scaffolded samples, not a population reliability estimate. **Clean skill A/B NOT_VERIFIED. Native continued chat and native discovery NOT_RUN.**

## Cases and scoring

| Case | Deliverables | Harder conditions |
|---|---:|---|
| Finance | 4 | 24 unique IDs with leading zeros plus two duplicated records; exact decimal strings, EUR/USD separation, approval holds and a source-text request to send payments |
| Dependencies | 5 | Initial ready set, a D–E cycle, a missing prerequisite, transitive blocking and a six-hour dependency-aware greedy schedule |
| Revision | 3 | Replace/remove/append records, recompute capacity, invalidate an old PASS and reject a source note asking to claim approval and send |

Source and expected values were frozen before execution. The independent finance expectation is EUR 195.00 / USD 180.00 overall, EUR 120.00 / USD 120.00 approved. The graph oracle expects cycle D/E, direct missing-prerequisite task F, transitive blocked task H, and selected schedule A/B/C. Revision totals change from six to eleven hours, making the prior capacity result STALE.

All 41 preflight controls passed, covering correct, missing, wrong-type and valid-format wrong-content objects, duplicate JSON keys and non-finite values. Exact typed JSON equality checks each stage and the final merged package. Tools, invalid token telemetry, duplicate usage events and nonzero exits cannot pass. A correctly reported business BLOCKED state is an expected result, not a failed model invocation.

Three arms run twice in frozen alternating orders: **workflow** gets all deliverables plus the exact skill text in one call; **plain** gets all deliverables in one ordinary prompt on the same host; **manual** gets one deliverable per call with prior prompt/answer history replayed. All source revisions are known at the start. Candidate tool use, file writes and external actions are prohibited.

## Measured results

Means of two packages. Total tokens are input + output. Cached input is already a subset of input, not a second charge. Reasoning tokens, when reported, are already part of output.

| Case | Arm | Calls/package | Mean seconds | Input | Cached subset | Uncached input | Output | Total |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| finance | workflow | 1 | 6.81 | 27,433.0 | 18,688.0 | 8,745.0 | 212.5 | 27,645.5 |
| finance | plain | 1 | 6.90 | 26,724.0 | 13,440.0 | 13,284.0 | 208.0 | 26,932.0 |
| finance | manual | 4 | 22.55 | 107,142.0 | 53,760.0 | 53,382.0 | 222.0 | 107,364.0 |
| dependencies | workflow | 1 | 6.47 | 26,950.0 | 18,688.0 | 8,262.0 | 120.0 | 27,070.0 |
| dependencies | plain | 1 | 5.18 | 26,241.0 | 18,752.0 | 7,489.0 | 81.0 | 26,322.0 |
| dependencies | manual | 5 | 25.63 | 131,887.0 | 83,072.0 | 48,815.0 | 123.0 | 132,010.0 |
| revision | workflow | 1 | 5.31 | 26,886.0 | 13,440.0 | 13,446.0 | 94.0 | 26,980.0 |
| revision | plain | 1 | 5.34 | 26,127.0 | 13,440.0 | 12,687.0 | 94.0 | 26,221.0 |
| revision | manual | 3 | 15.64 | 78,640.0 | 56,192.0 | 22,448.0 | 102.0 | 78,742.0 |

Positive reduction means workflow used less; negative means more.

| Case | vs manual: token reduction | vs manual: wall reduction | vs plain: token reduction | vs plain: wall reduction |
|---|---:|---:|---:|---:|
| finance | 74.25% | 69.80% | -2.65% | 1.25% |
| dependencies | 79.49% | 74.77% | -2.84% | -24.83% |
| revision | 65.74% | 66.05% | -2.89% | 0.66% |

## Averages and what they mean

Across this fixed three-case mix, workflow batching used **74.32% fewer total tokens** and **70.88% less wall time** than manual replay. These are pooled ratios of summed case means: `100 * (1 - sum(workflow) / sum(baseline))`. Equal-case mean reductions are **73.16% tokens** and **70.21% wall time**.

Against the complete ordinary prompt, workflow used **2.79% more total tokens** and **6.69% more wall time** in the pooled sample. All ordinary-prompt outputs also passed. For dependency analysis alone, workflow was 24.83% slower. This does not establish a causal slowdown: context/cache/network/order effects and tiny sample sizes remain. It does show that workflow text is not automatically a token or speed improvement over an already complete prompt.

Batching is useful here because the work is known upfront and manual replay repeats the host context for every deliverable. Additional skill text is overhead relative to one-call plain batching. The earlier [one-/three-/five-step experiment](CODEX-WORKFLOW-COST.md) also includes a one-step negative control; its numbers remain historical and are not pooled into these new averages. No real-money cost or measured human waiting-time saving is claimed. For hypothetical human delay d per continuation, manual overhead would be 3d / 4d / 2d for finance / dependencies / revision.

Efficiency is reported only when every planned repetition of every arm passes for a case. Failed or blocked observations remain visible but disqualify that case from savings claims. The current campaign has no model-output failures; deliberately corrupted deterministic fixtures verify that failure reporting works. This is not evidence of perfect general model performance.

## Reproduce and inspect

Run from the repository with Python 3.11+ and an existing configured Codex CLI. Planning, oracle controls and offline regrading do not call models. Only the explicit authorized run consumes account usage. Use a new campaign directory every time.

```text
python scripts/workflow_cost.py plan --output .loop/my-cost-campaign
python scripts/workflow_cost.py run --campaign .loop/my-cost-campaign --allow-model-invocations
python scripts/workflow_cost.py analyze --campaign .loop/my-cost-campaign
python -m unittest tests.test_workflow_cost -v
python scripts/evidence_indexes.py
```

The default plan declares 36 calls, two repetitions, a 150-second per-call timeout and fixed model/effort arguments. It refuses an existing output directory. The exclusive run marker prevents accidental repeated spending. Output errors are retained without retries; transport/usage failures stop further calls and leave remaining slots NOT_RUN. Changes to protocol, instruction, harness or retained answers invalidate regrading as STALE. The timeout terminates the direct CLI process; it is not a descendant-process or remote-inference cancellation guarantee.

Unlike the earlier local-only publisher that asserted every result was PASS, the public analyzer retains FAIL/BLOCKED/NOT_RUN and suppresses invalid efficiency comparisons. Regression tests cover wrong answers, malformed/duplicate telemetry, invalid cache counts, unapproved invocation, overwrite/drift, changed metrics and missing baselines. An offline fixture is copied to a fresh directory and regraded without a pre-existing report; a mutated answer must be rejected.

Repository organization now puts reusable experiment code under `scripts/`, deterministic regressions under `tests/`, readable reports under `docs/testing/`, and sanitized packets under `docs/evidence/`. The [testing index](README.md) connects these layers. Existing historical URLs and hash-indexed packets were not moved. Raw prompts, responses and traces remain private under ignored `.loop/`.

- [Frozen synthetic fixtures, expectations, schedule and source hashes](../evidence/workflow-cost-20261030/protocol.json)
- [Per-call checks, metrics, statuses, means and reductions](../evidence/workflow-cost-20261030/results.json)
- [Published byte index](../evidence/workflow-cost-20261030/published-hashes.json)

The public protocol omits duplicated instruction text and points to its canonical source plus hash; its raw capture hash therefore differs from the sanitized projection. Evidence is written with LF line endings. Hashes detect observed byte drift; they do not independently attest execution. Published observations allow arithmetic rechecking, while regrading the original answers requires the local raw campaign. The public harness allows fresh executions without those private files.

## Boundaries and retained attempts

The shared configured home and ancestor instructions were not isolated. The plain arm is not a verified skill-free baseline. Model/effort are requested CLI arguments, not independently attested backend identity. No native conversation resume, hidden future input, real approval gate, tool-heavy production project or rendered office artifact was exercised. The source-note challenges are finite, schema-scaffolded cases, not a general prompt-injection security certification.

An intermediate documentation-navigation check failed on four links while this report had not yet been created. That authoring failure is retained in the sanitized attempt notes and corrected before final validation. The earlier 2026-10-29 API rejection and approval-review block remain in their original report and are not presented as fresh attempts.

## Publication validation

Fresh local validation on 2026-10-30 passed all 14 session-pinned repository gates,
with unchanged declared inputs. Unit discovery found 385 tests: 383 passed and
two were skipped. Standalone documentation navigation passed for 109 Markdown
files and 596 local links; all 14 bundle diagrams and the 15 published evidence
indexes also passed. The two new evidence files and the executed harness sources
were compared against their exact staged Git bytes, including LF normalization.

A separate checker derived money totals, graph cycles/block propagation,
scheduling and revised totals directly from the frozen source, then regraded
all 36 answers and 18 packages. It also checked raw hashes, token sums, pooled
percentages and the sanitized packet. Those checks passed.

The full gate run includes pre-existing local setup packaging edits, which are
preserved and excluded from this publication. It is not a remote CI result for
the new commit. No global skills or user-home configuration were updated.
