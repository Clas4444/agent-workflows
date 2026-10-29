# Codex: workflow batching versus sequential prompts

Recorded 2026-10-29 on Windows with Codex CLI 0.165.0-alpha.1.2, requested model `gpt-6.1-sol`, reasoning effort `low`. Agent Workflows candidate: `loop-work` from version 1.11.1, with its exact instruction hash in the protocol.

**Measurement PASS:** 18/18 packages and 30/30 measured calls passed exact artifact/usage checks. **Clean skill A/B NOT_VERIFIED:** the configured host includes global skills and ancestor instructions. **Native continuation and native skill discovery NOT_RUN.**

The measured advantage is primarily fewer model calls with less repeated host context. It is not proof that adding workflow instructions itself saves tokens, that these percentages apply to native Codex chats, or that all Agent Workflows skills improve efficiency.

## Experimental design

- Three fixed cases: one metrics deliverable, three deliverables (triage, metrics, capacity brief), and five deliverables (add greedy allocation and risk flags). All use the same seven synthetic records, including one duplicate.
- Three arms: **workflow** completes all deliverables in one call with the full `loop-work` text; **plain** completes all in one call without that explicit append on the same configured host; **manual** produces one deliverable per call with earlier prompts/answers replayed verbatim.
- Two repetitions of each case/arm. Frozen alternating execution orders are in the protocol. Each call starts an ephemeral read-only Codex process; no tools, files, external actions or spawned agents are permitted.
- Expected results and 25 scorer controls were fixed before the measured calls. Controls accept the correct value and reject missing fields, wrong types, valid-format wrong content and duplicate JSON keys. Stage and merged results must match exact typed JSON.
- The default calibration header reported `gpt-6.1-sol` / OpenAI / effort `none`. Explicit `none` was then rejected by the API; the preserved failed campaign was stopped. The subsequent measured campaign explicitly used supported `low` for every call, without changing the rubric.

## Per-case results

Means of two completed packages per cell. Total tokens = input + output; input already includes cached input. Positive reduction means workflow used less than the named baseline; negative means more.

| Case | Arm | Calls/package | Mean seconds (min–max) | Mean input | Cached subset | Uncached input | Output | Total |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| single | workflow | 1 | 6.26 (5.95–6.57) | 26,752 | 18,688 | 8,064 | 34 | 26,786 |
| single | plain | 1 | 6.34 (6.15–6.52) | 26,043 | 13,440 | 12,603 | 34 | 26,077 |
| single | manual | 1 | 5.67 (5.17–6.17) | 26,064 | 13,440 | 12,624 | 34 | 26,098 |
| three | workflow | 1 | 7.11 (6.61–7.61) | 26,819 | 13,440 | 13,379 | 171 | 26,990 |
| three | plain | 1 | 7.14 (6.52–7.75) | 26,160 | 13,440 | 12,720 | 171 | 26,331 |
| three | manual | 3 | 20.21 (19.73–20.70) | 78,785 | 40,320 | 38,465 | 181 | 78,966 |
| five | workflow | 1 | 8.72 (7.81–9.63) | 26,954 | 18,688 | 8,266 | 282 | 27,236 |
| five | plain | 1 | 10.27 (10.25–10.29) | 26,245 | 13,440 | 12,805 | 289 | 26,534 |
| five | manual | 5 | 29.56 (29.29–29.82) | 132,070 | 67,200 | 64,870 | 252 | 132,322 |

| Case | Workflow vs manual: total tokens | Workflow vs manual: wall time | Workflow vs plain: total tokens | Workflow vs plain: wall time |
|---|---:|---:|---:|---:|
| single | -2.64% | -10.35% | -2.72% | 1.30% |
| three | 65.82% | 64.82% | -2.50% | 0.37% |
| five | 79.42% | 70.51% | -2.65% | 15.09% |

## Averages and interpretation

Reduction formula: `100 * (1 - workflow / baseline)`. The primary pooled reduction is calculated from the sums across this equally repeated three-case mix. It gives longer manual chains more baseline weight; it is not a universal average across real user tasks. The equal-case mean averages the three percentage reductions instead.

| Baseline | Pooled total-token reduction | Pooled wall-time reduction | Pooled uncached-input reduction | Equal-case mean total-token reduction | Equal-case mean wall-time reduction |
|---|---:|---:|---:|---:|---:|
| plain | -2.62% | 6.98% | 22.08% | -2.62% | 5.59% |
| manual | 65.87% | 60.17% | 74.38% | 47.53% | 41.66% |

Across this fixed mix, workflow batching used **65.87% fewer total tokens and
60.17% less wall time than sequential replay**. However, the complete ordinary
prompt also passed every case; the workflow arm used **2.62% more total tokens
than that ordinary prompt**. Extra workflow text did not reduce total tokens relative to that
one-call control. The workflow arm's 6.98% lower pooled time against plain is a
small-sample observation with unequal cache hits, not evidence of a causal speedup.

For known multi-step work, the replayed manual condition repeats the host context for each deliverable. Batching removes those repeated calls. Compare plain against workflow to assess whether the same batching can be achieved with a complete ordinary prompt. For a one-step task there are no continuations to remove; additional workflow text is overhead. `loop-work` itself says not to turn a small request into a process.

Uncached input and wall time may respond differently from total tokens because cache hits vary by call and order. Only two samples are available; time ranges above expose the variation. No statistical significance, reliability estimate, or token-to-price conversion is claimed.

## Human waiting time

Human reading/typing was not observed and no artificial sleeps were inserted. For an assumed delay `d` per continuation, add `(steps - 1) * d` seconds to the manual package. Add 0 seconds for the single case, 30/60/120 seconds for the three-step case with d=15/30/60, or 60/120/240 seconds for the five-step case. These are scenarios, not measured savings. Complete numerical scenarios are in results.json.

## What this cannot establish

- Native resumed chat has different context/cache/startup behavior from these independent processes. Native picker activation was not exercised.
- The plain arm is not isolated from globally installed skills or ancestor instructions. The comparison is explicitly NOT_VERIFIED as a clean test of skill effectiveness. Model/provider identity was observed in a calibration header and model/effort pinned in CLI arguments; there is no independent backend attestation.
- All source information is available at the start. Unknown future inputs, changing requirements, mandatory approvals, tool-heavy coding, recovery from substantive failures, long-project compaction and artifact rendering were not tested.
- A single complete plain prompt may remove the same human continuations. The experiment does not attribute the batching advantage exclusively to Agent Workflows.
- The tiny fixed arithmetic workload does not establish broad quality or token/time improvements. PASS means these finite checks passed.

## Preserved attempts and historical pilot

The earlier pilot remains historical: four packages / eight calls on unverified model defaults, with mean total tokens 27,096 for workflow and 78,842 for manual, and mean wall seconds 22.29 versus 51.88. Those observations are not new runs and are excluded from every expanded average.

An initial content-export approval rejection executed zero model calls; explicit user approval followed. For this expansion, one successful READY calibration and one API-rejected `none` call are retained separately. The rejected campaign has 17 remaining packages NOT_RUN; it is not included as a fast completed package. No failed output was retried until it passed. The separate `low` campaign completed all 30 planned calls. See ancillary_attempts for sanitized observations and local raw hashes.

## Evidence and reproduction limits

- [Frozen protocol and synthetic source/expected values](../../evidence/workflow-cost-20261029/protocol.json)
- [Per-call metrics/checks, package means, formulas, scenarios and attempt statuses](../../evidence/workflow-cost-20261029/results.json)
- [Published byte index](../../evidence/workflow-cost-20261029/published-hashes.json)

Raw prompts, model answers and traces remain local under ignored storage and are not published. Published rows contain sanitized observations and hashes only. Hashes detect byte changes; they do not authenticate execution or reconstruct private traces. The experiment harness is local-only, so readers can recompute aggregates from the published observations, but cannot claim an exact runtime replay from this packet alone.

After the campaign, a separate local checker derived expected values directly
from the source records and regraded all 30 answers / 18 merged packages. It
also recomputed package sums, case means and pooled reductions, checked usage
bounds, and scanned the public JSON for machine paths and credential fields.
All of those checks passed; raw answer regrading requires the private local files.

Public JSON uses LF line endings. Local capture hashes identify the original
raw capture bytes; published-hashes.json identifies the normalized public bytes.
The first repository gate session passed but became STALE when publication
line endings were normalized. That session was retained, and the 14 gates were
rerun against the final normalized evidence rather than reusing the stale pin.

Publication validation, 2026-10-29: a fresh session-pinned 14-gate repository
campaign passed with unchanged declared inputs. Its unit gate discovered 373
tests, with two skips. Standalone documentation navigation (107 Markdown files,
571 local links), all 14 bundle diagrams, published evidence indexes and
`git diff --check` also passed. These local gates ran on the working tree with
the unrelated setup edits present; they are not remote CI results for the
documentation-only commit. Remote CI is tracked separately after publication.

Verify published bytes with `python scripts/evidence_indexes.py`. Recompute a case mean by summing its two package values and dividing by two; recompute the primary pooled reduction using the sums of the three case means. Source revision and candidate SHA256 are pinned in protocol.json; unrelated local setup packaging edits were preserved and are not part of this publication. Version remains 1.11.1 because this is report-only work.
