# Autonomous improvement session, 2026-10-25 (IN PROGRESS)

Session `autonomous-3h-20261025T092231Z` starts at **09:22:31 UTC** and is scoped
through **12:22:31 UTC**. Base `d5953f54717d0213a9f3d110cac2c46a7db483ad`, clean.
This is an ongoing work ledger, not completion of the three-hour session.
Batch release checkpoints are recorded below; current-session raw evidence stays
in `.loop/`. Exact commit/CI receipts are retained outside the self-referential
release report and summarized in the final session update.

## Selection and self-assessment

The previous generation-only A/B tied; broad effectiveness remains unproven. More
skill names would not resolve that evidence gap. Work starts with a demonstrable
runtime weakness, then installation drift, handoff and evidence boundaries. Applied
workflows are loop-review, loop-debug and loop-test. Model quota previously failed;
no fresh model-runtime claim may be substituted with a mock or a deterministic test.

## Phase 1: process ownership

Two base defects were observed in isolated disposable fixtures:

1. **Confirmed lifecycle gap, P2:** timeout returned after ~2 seconds, but an
   ordinary descendant wrote its marker at ~6 seconds. The original runner killed
   only its direct process. A real subprocess regression failed before repair.
2. **Confirmed resource leak, P2:** a real high-output child plus deliberately slow
   consumption saturated the bounded reader queue. Timeout left two daemon reader
   threads blocked in queue delivery. The regression failed before cancellation
   support and passed afterward. The failing test drains the queue after observing
   the leak so its own baseline leaves no daemon behind.

Implementation uses a Windows kill-on-close Job Object with a gated launcher;
POSIX gets a new session and process-group cleanup. Reader queue operations can
stop on cancellation. All six distributed copies are synchronized. See
[process lifecycle contract and primary references](../PROCESS-LIFECYCLE.md).
This is lifecycle ownership, not a sandbox or rollback mechanism.

A defect introduced during patch development was retained separately: an invalid
executable's original startup exception became an ordinary launcher exit status.
A new regression failed against that intermediate patch, then passed after launch
errors were transported back to the parent. This was not a base-repository defect.
Positive controls preserve large UTF-8 stdin, exit codes 7/125/255, marker output,
normal completion, early-parent-exit timeout and failure-before-target job setup.

Focused initial expanded run: 27 PASS. Subsequent full campaigns (before the final
normal-descendant positive test was added) passed all eleven gates on Python 3.12
and 3.14; they are retained as **superseded**, not final release validation. Current
complete-source final gates and POSIX runtime execution remain **NOT_RUN** until
recorded. No remote CI or push is claimed for this phase yet.

## Read-only diagnosis of the actual global installation

The current global skill directory contains only **27/49** manifest instruction
files. The developer bundle check returned exit 1 for three changed instruction
payloads; the office check returned exit 1 for missing skill/resource payloads.
Both were actual read-only installer CLI checks. No global skill was modified.
Folder presence is not native discovery. This explains why repository validation
and the host's available installed workflow set can differ. Need-based diagnosis
and installation guidance are a useful next improvement; do not silently overwrite
personal modifications or label an uninstalled skill as runtime tested.

## Initial queue (historical checkpoint)

- Independent final-source full gates and actual POSIX CI coverage.
- Further adversarial launch/error/cancellation review before publishing phase 1.
- Installation diagnosis/DX, handoff permissions and evidence freshness review.
- Real host tool-use experiment only if runtime prerequisites and quota permit.
- Current-session sanitized evidence, release pin, authorized push and exact-SHA CI.
- Final time/activity accounting at the session endpoint, with failures and skips.

## Phase 2: read-only install diagnosis

Implemented `scripts/doctor_skills.py` using the existing manifest/resource and
alias rules. It never writes a target or starts a host. Selected managed payloads
are classified as CURRENT / NOT_INSTALLED / INCOMPLETE / DRIFTED / BLOCKED; native
activation and runtime stay NOT_RUN. A source-change adversarial test exposed a
false CURRENT in the first new implementation; the red control is retained. The
repaired implementation records reference input pins and checks observed drift
and inventory validity after comparisons. This is a new-tool development defect,
not a defect attributed to the base release. Before/after checks are not locks.

Eleven focused doctor tests passed; twenty-eight doctor/installer/session tests
passed together. Actual canonical all-skill diagnosis returned PASS for 49/49.
The actual global target returned FAIL with 17 CURRENT, 10 DRIFTED and 22 absent;
only a sanitized status summary is public. No global installation changed.
A canonical-doctor gate was added to the fixed campaign and CI, increasing the
current required set from eleven to twelve. Older campaigns retain their original
scope and must not be relabeled as twelve-gate verification.

## Phase 3: independent runtime oracle integrity

**Confirmed false PASS, P2:** `loop-code` grading launched `python -m unittest`
from the untrusted fixture. A local `unittest.py` printed OK and returned zero.
All grader booleans were true even though unchanged defective addition returned
6 for (2,3). The original minimal fixture is retained and now returns failed
regression/independent-arithmetic checks.

Related proven variants: extra discovered test modules could disable assertions,
submitted code could monkeypatch child unittest assertions, and `os._exit(0)`
could return success without assertions. The direct grading API also returned only
successful preservation checks for an unsupported tag (**P3**, direct API only;
the runtime CLI already rejected that tag). An exact base export plus new tests
ran six controls: five failures exposed these acceptances, while ordinary handled
`SystemExit(0)` was already rejected. That unsuccessful attack is not called a bug.

The repair isolates Python startup with `-I -S -B`, preloads standard-library
unittest before adding the fixture import path, selects the exact protected test
file, requires nonempty collection and adds a separate typed arithmetic probe
compared in the parent process. Unsupported direct tags fail closed. Correct
code still passes in the presence of an unused local fake framework, and the fake
framework is not executed. The retained suite at that checkpoint ran 35 tests,
all PASS; subsequent unsupported-tag regression passed too. These are deterministic
subprocess/fixture results, **not actual model-runtime validation**. Arbitrary
submitted code is not sandboxed, and a finite oracle is not exhaustive.

[Sanitized batch-1 evidence and provenance](../evidence/autonomous-3h-20261025/batch1/)
retain before/after logs, actual fixture results, independent controls and a
separate public-byte hash index. Publication metadata identifies local raw bytes
and normalized text separately; no historical runtime PASS is promoted.

## Measured compatibility cost

Thirty paired Windows short-command trials used the same interpreter/input and
alternating arm order. Base median was 22.88 ms; candidate median was 73.34 ms:
about 50 ms extra per short invocation in this environment. This is a real
launcher cost, not an improvement claim. A separate warmed sixty-invocation run
observed zero status/input failures and zero process-handle growth (163 before
and after explicit GC). Neither diagnostic proves all resources leak-free or
predicts model throughput. Persistent background children are now closed at
invocation completion; separately owned services require a separate lifecycle.

Local WSL is not installed and Docker was not found. No installation was attempted;
actual POSIX execution remains NOT_RUN pending exact-commit Linux CI. Complete
current-source twelve-gate campaigns and release identity are pending below.

## Batch 1 local gate checkpoint

Both Python 3.12.14 and 3.14.7 completed all **12 gates PASS**, each with
**289 discovered / 288 passed / 1 Windows file-symlink privilege SKIP**.
[Local 3.12 report](sessions/autonomous-3h-batch1-local-312.json),
[local 3.14 report](sessions/autonomous-3h-batch1-local-314.json).
Those observed pins precede a README-only clarification making the doctor's
bundle selection identical to the install example. Retain them as local evidence;
the separately executed Git export is the release-byte authority. Historical
eleven-gate reports remain eleven-gate reports. Publication is still pending
exact export tests, Git-blob comparison and exact-SHA CI. The three-hour session
continues after this batch; a batch release does not imply session completion.

### Oracle compatibility control after the first export

A review of the original mathematical-sum contract found that the first probe
unnecessarily required an integer return type. Three exact real-numeric
implementations (exact float where representable, Decimal and Fraction) passed
original tests but failed that new probe. The retained compatibility test ran
one test with three failing subcases before repair. The probe now transports
exact rational representations for supported real scalar outputs; the parent
compares these against the same arithmetic expectations, rejects booleans/non-
numeric outputs and still catches all demonstrated bypasses. No original test
or expected numeric value was weakened. All 37 focused smoke/oracle tests passed.
This was a new-oracle development defect, not a bug attributed to base d5953f5.
The first 289-test export campaigns passed but are superseded by this justified
compatibility correction. Fresh final-batch export verification is required.

A second positive compatibility control confirmed that ordinary startup logging
must not corrupt the functional probe's result channel. Its regression failed
before output separation and passed afterward. Probe results are emitted after
capturing ordinary Python-level stdout logs; the trusted parent still checks the
same exact numeric expectations. Verification Python uses explicit UTF-8 mode.
The focused smoke/oracle suite now passes 38 tests. This does not prevent hostile
code from attempting arbitrary I/O or prove universal resistance to overfitting.

## Verified batch 1 release candidate

The final staged Git export completed **12/12 gates PASS** on Python 3.12.14 and
3.14.7, with **291 discovered / 290 passed / 1 Windows file-symlink privilege SKIP**
in each suite. Both report the same unchanged input fingerprint and **436 pinned
input files**. All public evidence byte-index entries match the normalized export.
Reports: [3.12 export](sessions/autonomous-3h-batch1-export-312.json),
[3.14 export](sessions/autonomous-3h-batch1-export-314.json).
The earlier 289-test local/export campaigns are retained as superseded evidence;
no earlier PASS is relabeled as the final bytes. Source/document/report scope is
explicit in each map. The next publication check compares every map entry with
the committed Git blob, then pushes the verified batch and inspects exact-SHA CI.
This batch does not complete the remaining three-hour autonomous work.

### Publication correction retained before push

The staged whitespace gate detected a trailing space in a published unittest log.
The PowerShell command sequence nevertheless continued into a local commit
(`b16b59a`) because a native nonzero exit did not stop subsequent commands. That
commit was not pushed at the time of detection. The public text log was normalized,
its public-byte index updated, and a fresh export campaign was required; the raw
private failure log and its hash were preserved. The local intermediate commit is
retained rather than rewritten to hide this workflow error. Future publication
commands explicitly test native exit codes before committing or pushing.

After public-log normalization, fresh publication export campaigns again passed
all 12 gates on Python 3.12 and 3.14: 291 discovered, 290 passed, one Windows
privilege skip, unchanged inputs. These publication reports supersede the
pre-normalization maps: [3.12](sessions/autonomous-3h-batch1-publish-312.json),
[3.14](sessions/autonomous-3h-batch1-publish-314.json). The staged whitespace gate
now returns zero, and published hash indexes match the exact export bytes.
