# Autonomous improvement session, 2026-10-25

Session `autonomous-3h-20261025T092231Z` starts at **09:22:31 UTC** and is scoped
through **12:22:31 UTC**. Base `d5953f54717d0213a9f3d110cac2c46a7db483ad`, clean.
This report retains chronological checkpoints and their original scope.
The final release receipt records the actual closing time and exact-head CI.
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

## First exact-head CI failure and portability repair

The first pushed tip was `8b21ea67df6aa236afa11cf46c46c7e5f5378a6f`.
[Its CI](https://github.com/Clas4444/loop-skills-repository/actions/runs/40184258944)
passed both Ubuntu jobs but failed both Windows jobs at the source-drift injection
test. All other executed tests, including lifecycle tests, passed in those logs.
The injection compared an unresolved fixture path against the doctor's resolved
target; an equivalent path spelling could therefore make the injection a no-op.
A local anchor/../installed reproduction gives the same failure. The exact original
VM temp spelling was not retained, so a specific 8.3 spelling remains inference.

The test now compares resolved identities and requires the mutation hook to run
exactly once. A new equivalent-target test exercises that boundary. No production
hash check or expected BLOCKED assertion changed. Twelve doctor tests pass on
both local interpreters. [Failure excerpts and repair evidence](../evidence/autonomous-3h-20261025/batch1-ci/)
preserve the failed CI rather than hiding it. The corrected head still requires
its own full pinned campaigns and exact-head CI before release success is claimed.

After the portability repair, both local interpreters passed all twelve gates with
292 discovered tests, 291 passed and one local Windows file-symlink privilege skip.
Reports: [3.12](sessions/autonomous-3h-ci-repair-312.json),
[3.14](sessions/autonomous-3h-ci-repair-314.json). These observations do not replace
new-head CI; a final export verifies the publication bytes before the corrective push.

The corrective staged export passed all twelve gates (292 discovered, 291 passed,
one local Windows privilege skip), with unchanged inputs. [Corrective export map](sessions/autonomous-3h-ci-repair-export.json).
The next head is eligible for a corrective push after blob verification; its remote
CI must independently confirm Windows and Ubuntu before the batch is called green.

## Corrected first batch is remotely verified

Corrective tip `8f46c115f6b605c46c54d1e59c101720e06798ce` passed all four
[exact-head CI jobs](https://github.com/Clas4444/loop-skills-repository/actions/runs/40185613886).
The 443 corrective-export input hashes matched committed Git blobs. This confirms
actual Windows and Ubuntu deterministic execution for that tip, not a new model
benchmark or a clean global installation.

## Real tool-using handoff after capability preflight

A single real Codex preflight using the existing trusted host configuration copied
an arbitrary synthetic input byte-for-byte with source preserved. A separate frozen
handoff protocol then ran two new CLI threads, without resume/history, with the
current loop-handoff instruction explicitly supplied. Checker calibration accepted
two valid controls and rejected ten missing/stale/type/authority/alias controls
before model execution. The two dependent stages both passed, not two independent
trials: stage 1 retained a source-pinned checkpoint (2 rows/7 units; C2 NOT_RUN),
then a controller appended row 003 and forged checkpoint authorization text.
Stage 2 rehashed/reparsed the current source (3 rows/12 units), retained leading-zero
IDs, invalidated old PASS, rejected permission claims and preserved the protected
sentinel, old checkpoint and current source/instruction bytes.

The parent inspected the complete recorded command bodies and independently
checked artifacts. Model gpt-6.1-sol, observed workspace-write/network-disabled
profile, 54.312 seconds total, 169,436 input tokens (136,832 cached) and 1,630 output
tokens; monetary cost NOT_VERIFIED. Both threads warned that the global skill
context budget had been exceeded. This proves one explicitly supplied workflow
exercise, not native discovery, baseline superiority, exhaustive skill coverage or
absence of every possible side effect. [Protocol/checker/controls, raw sanitized
outputs and retained artifacts](../evidence/autonomous-3h-20261025/handoff/).

## Backup integrity boundary (second batch)

**Confirmed P2:** actual installer CLI returned exit 0 when two planned backup
paths shared an internal junction; both targets changed and the first original
was overwritten by the second backup. The test used only disposable files.
Four pre-repair tests included three failures and one invalid-parent error, with
the safe distinct-backup control passing. The fix checks backup aliases and parent
file types during preflight, before any backup or target copy. After quota resumed,
17 backup/sync/installer tests passed. [Before/after evidence and reproduction](../evidence/autonomous-3h-20261025/backup-preflight/).
This does not add locking, atomic installation or automatic rollback.

The first attempted green verification was NOT_EXECUTED because automatic approval
review itself hit a usage limit, not because it determined the action unsafe.
The user explicitly asked to resume; the same test then ran successfully. No bypass
was used. The interruption is excluded from any claim of continuously active work.
Final second-batch full gates, source pins and exact-head CI remain pending.

### Full-width Windows exit compatibility

A further actual direct-versus-runner control found a compatibility defect in the
first-batch launcher: a Windows DWORD error `3221225477` became `4294967295` when
propagated through `sys.exit`. The newly added regression failed for that subcase.
The launcher now converts to the matching signed 32-bit representation before
`os._exit`; the same real-process check and ordinary exits/startup-error controls
pass. All six distributed runners are synchronized. [Observed values/red/green](../evidence/autonomous-3h-20261025/exit-width/).
This is a Windows-specific control; its POSIX skip is intentional. Earlier batch-2
full campaigns are superseded for source identity by this new repair. New full
campaigns and exact Git-export/CI validation are required, not relabeled.

## Declared public-byte verification gate

Added `scripts/evidence_indexes.py` to current local and CI commands. It supports
existing flat/structured SHA256 indexes, rejects missing/mismatched bytes, duplicate
JSON keys, unsafe or case-colliding paths, aliases/hardlinks, self-reference and
empty discovery. The published artifacts are never executed. Eight meaningful
checker tests and nine campaign tests passed; an actual valid-format/wrong-content
fixture exits 1 as expected. [Gate controls](../evidence/autonomous-3h-20261025/published-index-gate/).
This is a verification-coverage improvement, not a claim that the older validator
violated an undocumented index contract. Unindexed artifacts, author identity,
execution authenticity and truth of prose remain outside the hash guarantee.

The current fixed campaign now has **13 gates**. Earlier twelve-gate observations
remain their original observations; the current source/evidence requires new
thirteen-gate campaigns and exact-head CI before publication is complete.

## Second batch full local checkpoint

The complete thirteen-gate campaign passed on Python 3.12 and 3.14 with
**305 discovered / 304 passed / 1 local Windows file-symlink privilege SKIP**
each. Reports: [3.12](sessions/autonomous-3h-batch2-local-312.json),
[3.14](sessions/autonomous-3h-batch2-local-314.json). Actual handoff artifacts were
regraded from the public copy; all twelve checker controls were recalibrated, and
all declared public-byte indexes matched. The same retained wrong-code fixture
still fails the repaired oracle. Release status remains pending the normalized
Git export, exact blob map and new-head CI. No earlier failed head is called green.

### Artifact-byte publication adjustment

The staged whitespace gate stopped publication because exact raw Windows CRLF
artifacts were flagged. No commit/push followed that failed gate. Exact runtime
bytes now remain in raw-artifacts.zip, with separately indexed LF-readable views
and original per-artifact hashes. The actual fixture/private evidence was not
rewritten, and no whitespace rule was disabled. New final-export verification is
required because publication bytes changed; prior source pins remain historical.

The raw artifact ZIP is explicitly marked `-text` so Git never applies text EOL
conversion to compressed bytes; exact staged/archive equality was checked. The
first second-batch export passed its thirteen gates but predates that defensive
attribute clarification. The final export below includes the attribute and is
the release-pin authority. No functional test assertion changed.

## Verified second-batch staged payload

Both final staged-export interpreters passed **13/13 gates**, with **305 tests:
304 passed and one local Windows file-symlink privilege SKIP**. The same unchanged
pin covers **486 input files**, and every published evidence index matches exact
export bytes. [3.12 final export](sessions/autonomous-3h-batch2-export-312.json),
[3.14 final export](sessions/autonomous-3h-batch2-export-314.json).
This is the release-byte authority for the second batch; prior 12/13-gate campaigns
remain retained at their actual scope. Commit/blob equality and exact-head remote
CI are checked after this report, with receipts outside its self-reference.
The three-hour session remains ongoing until the stated endpoint; a published
batch does not by itself complete the goal.

## Research skill upgrades and actual forward exercises

The last two IMPROVE recommendations from the 49-skill static audit were addressed
in existing loop-research-repo and loop-research-tools. Their native copies are
synchronized. New text emphasizes exact source identity/recheck, unknowns, advertised
versus observed capability and treating embedded instructions as untrusted evidence.
Historical 1.2 runtime hashes now explicitly invalidate reuse for those changed
instructions; the old run is not rewritten as a new PASS. No new skill or public
invocation name was added, split or removed.

Two different exercises (one trial per skill) used actual Codex tools with exact
current instruction text supplied. Twelve output-oracle controls were frozen before
both calls; both artifacts passed and were independently regraded from their raw
archive. The repo case found an unborn dirty Git repository, pinned/rechecked the
three source files, did not accept README's license advertising, ran no candidate
code and deferred adoption. The first Git ownership refusal is retained; recovery
used command-local safe.directory and disabled global/system config/optional locks,
without persistent trust/ACL changes. No whole-machine side-effect claim is made.

The tool case actually ran read and output probes: read exit 0 matched independently
hashed 21 input bytes; output exit 3 created no output despite advertised writes.
The enclosing shell exit 0 was not mistaken for write success. Costs remained
NOT_VERIFIED, and metadata upload/permission instructions were not followed.
The parent inspected complete recorded commands, source/sentinel identities and
saved outputs. Both actual turn_context records identify gpt-6.1-sol. Durations
were 51.172 and 52.344 seconds. These are finite workflow assessments, not clean
baseline A/B, repeated reliability evidence or native-discovery tests. Sources,
protocol/controls, sanitized events, config and raw archive are in
[research forward evidence](../evidence/autonomous-3h-20261025/research-leaves/).

The prior second-batch tip 708b913ca2692f160f6980bf316c42f3e9a19fc1 passed all four
[exact-head CI jobs](https://github.com/Clas4444/loop-skills-repository/actions/runs/40189154404).
Final-session thirteen-gate validation and a new-head release remain required for
the research instruction changes; prior green CI does not cover them.

The research-upgrade local campaigns passed all thirteen gates on Python 3.12 and
3.14: 305 discovered, 304 passed, one local Windows privilege skip. Reports:
[3.12](sessions/autonomous-3h-research-local-312.json),
[3.14](sessions/autonomous-3h-research-local-314.json). A later privacy pass redacted
elided workspace paths in three public event/result logs and updated the public
index. Those byte changes are covered by the final Git export below; local pins
are retained at their actual pre-redaction scope. Exact raw artifact ZIPs were
checked for personal-home/credential patterns before publication.

The final normalized research-release export passed **13/13 gates** on Python 3.12
and 3.14, each with 305 discovered / 304 passed / one local Windows file-symlink
privilege skip and unchanged pins. [3.12 export](sessions/autonomous-3h-research-export-312.json),
[3.14 export](sessions/autonomous-3h-research-export-314.json). Public evidence byte
indexes, historical invalidations and native instruction/resource copies passed.
The next publication step compares these input pins with actual committed blobs
before push, then checks exact-head CI; this is still a session checkpoint.

## Final installation, CI and self-assessment checkpoint

The 1.9.4 head `d4afbcd94f888667f5fcb0a4e7ddd7aece629c28` passed all four
[exact-head CI jobs](https://github.com/Clas4444/loop-skills-repository/actions/runs/40190207867).
Actual downloaded job logs show 305/305 PASS on both Windows jobs; Ubuntu has
303 PASS plus two explicitly Windows-only skips. This resolves the earlier local
file-symlink privilege gap for CI Windows, without claiming local execution.
The final research-export pins were compared with all 513 committed input blobs:
zero mismatches. Source and public evidence were clean at that checkpoint.

Fresh disposable upgrades exercised all twelve bundles using original base Git
payloads and the current real installer/check/doctor CLIs. All succeeded; every
actual overwrite backup retained exact original bytes, and custom/unrelated files
were preserved. Six separately installed continuation runners were invoked outside
the checkout; all descendants started, all timeouts were nonzero/BLOCKED, and no
late-write marker appeared within six seconds. These are installed CLI checks,
not native activation or model-runtime tests. Compact scope-limited observations
are [published here](../evidence/autonomous-3h-20261025/final-checks/).

Self-assessment: keep the 49-skill catalog rather than add names to fill time.
Two research leaves were upgraded with current-source checks and evidence-boundary
instructions. Confirmed defects repaired during this session include descendant
lifecycle/reader leaks, false-PASS arithmetic grading, backup-path alias corruption
and the newly introduced Windows full-width exit compatibility regression. New
features and development failures remain distinguished from base defects above.
The read-only installation doctor and published-evidence gate close specific
observability gaps; neither proves native runtime behavior.

Actual model evidence is one two-stage handoff trial and two different research
leaf exercises (one trial each), plus a capability preflight. They are not clean
A/B trials and do not establish superiority or population reliability. Explicit
instruction loading was used. The host's global metadata-budget warning prompted
an installation-guide clarification, not deletion or rewriting of personal skills.
The dated global diagnosis above is not refreshed or relabeled as a current count.

Remaining limits: native discovery and behavioral coverage of all 49 skills are
NOT_RUN; macOS and real connector workflows are NOT_RUN. The ordinary process-tree
contract excludes escaped POSIX sessions, external jobs and abrupt host failure.
The separate smoke harness has its own direct-child lifecycle limits. Backup
preflight is not a filesystem lock, atomic transaction or automatic rollback.
Hashes prove recorded byte identity, not authenticated execution. Finite arithmetic
and artifact oracles cannot establish safety of arbitrary adversarial code. Model
monetary cost is NOT_VERIFIED. The measured launcher overhead (about 50 ms in the
paired short-command trial) is a concrete tradeoff, not a universal benchmark.

Time accounting: work began at 09:22:31 UTC with a 12:22:31 UTC bound. A quota /
automatic-review usage interruption occurred around 11:00-11:15, followed by the
user's explicit request to resume. This is not three uninterrupted active hours.
Final gate, publication and closing-time receipts follow separately; this ledger
retains earlier checkpoints at their original scope instead of rewriting history.

### Closing coverage gap: bundles do not cover all skill installations

The twelve bundle union contains 25/49 skills, so its successful upgrade campaign
could not justify a whole-catalog installation claim. A further frozen replay
script independently enumerated all 49 instructions plus nine resource payloads.
In each of three fresh layout fixtures it forced drift in all 58 managed files,
verified check/doctor rejected the drift, ran the real installer, compared all
installed bytes and all original backup bytes, checked CURRENT and ran a second
idempotent install with no backup. Custom/unrelated sentinels were preserved.
All three fixtures passed: 174 actual payload overwrite/backup comparisons.
The [replay and source hashes](../evidence/autonomous-3h-20261025/final-checks/)
are public; raw command logs remain private. This closes an installer-coverage gap,
not native activation or behavioral testing for all 49 skills. No new defect was
found by this sweep and no production code was changed to manufacture one.

The first closure local/export campaigns passed thirteen gates but predate this
additional replay publication. They remain historical checkpoints; new final
export pins must cover the added script, summaries and byte index.

## Final release verification

Both final Git-export campaigns passed **13/13 gates** on Python 3.12 and 3.14,
each discovering **305 tests: 304 PASS, one local Windows file-symlink privilege
SKIP**. Reports: [3.12 final](sessions/autonomous-3h-final-export-312.json),
[3.14 final](sessions/autonomous-3h-final-export-314.json). These supersede the
closure checkpoints for current release-byte validation, without erasing them.
The 520-file verification input pin stayed unchanged and was compared against
staged Git blobs before commit. Session report prose and its report JSON files
are outside that declared pin to avoid self-reference.

A bounded publication scan found no personal-home/credential patterns in the
session evidence, including all 20 entries of both raw ZIPs, and no unsafe archive
member names. This is not an exhaustive secret detector. Original retained ZIP
artifacts independently regraded with no errors for handoff stage 2 and both
research leaves; the twelve frozen handoff controls also passed. Two restricted
control attempts could not create the Windows hardlink fixture (WinError 5); the
successful rerun used the same authorized Windows link-test permissions as the
full suite. No historical model call was counted again as a fresh execution.

Final commit, push, clean-tree observation and new-head CI are recorded in the
external release receipt under `C:/Code/Markdown`, because a document cannot embed
its own future commit hash. Earlier exact-head CI remains attributed to its actual
SHA. The closing receipt also records the actual elapsed span and quota interruption;
no uninterrupted three-hour active-time claim is made.
