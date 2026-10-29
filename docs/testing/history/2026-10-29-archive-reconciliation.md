# Archive reconciliation — 2026-10-29

Version remains **1.11.1**. This is a historical evidence audit and report update,
not a new product test or model run. The private archive was checked against its
manifests: **3,321 retained files in 77 logical groups**. Raw prompts, commands,
private machine paths, fixture Git metadata and backups are not published.

## What was already published and what was missing

Most release checks were already summarized in the existing reports. The archive
contains **26 verification captures: 20 PASS, 4 FAIL, 2 STALE**. These are repeated
campaign snapshots with different input pins, not 26 independent experiments or
model calls. Nine input pins had no reference in the existing testing reports;
the companion JSON now indexes all 26, including their original statuses,
failed-test names, nonpassing gates and any prior public pin references.
A pin-reference match identifies earlier coverage, not equivalence of all prose.

The failed captures include the earlier documentation/evidence checks and the
three outdated routing-count assertions after adding the setup route. STALE
captures retain their status even when their individual gates passed: changed
inputs invalidate that campaign. The latest setup separation capture is 14/14
PASS, 372 discovered tests, 370 pass and two Windows symlink skips. This remains
a deterministic result on its own source pin, not proof of model adherence.

See [setup separation](../checks/setup-separation.md), [historical setup capture](1.11.0-workflow-setup.md),
[documentation review](2026-10-26-docs-review-1.10.md),
[ReDoS repair](../checks/codeql-redos-repair.md) and the
[existing session records](../sessions/patch-1.10.2-20261028.json).

Four old Temp demos are also indexed: batch demo, six-iteration prompt demo,
a Unicode demo PASS and a second Unicode demo FAIL caused by a missing sys import
in its test command. These are deterministic demos, not model tests; the fixture
command failure is not evidence of a current runner regression. Intermediate
fixture files, backups and publication scripts are supporting material rather
than additional successful experiments.

## Retention and reproducibility limits

[Machine-readable reconciliation](2026-10-29-archive-reconciliation.json) retains the archive
SHA-256, group inventory digests, relevant record/trace hashes and original
observations. Hashes identify data; they do not reconstruct it or independently
attest model execution. At the user's request, the local raw archive is to be
deleted after this report is pushed and the remote bytes are verified. It is not
uploaded to GitHub. Thereafter, only the already-published sanitized evidence and
this reconciliation remain; full raw-trace replay is no longer possible.
No new model effectiveness, token-saving or archive reproducibility claim is made.
