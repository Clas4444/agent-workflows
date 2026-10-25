# Verification input-pin adversarial reproduction

Classification: **CONFIRMED_BUG, P2**, repaired in this session. The contract in
`docs/testing/TESTING.md` says edited verification inputs cannot validate as
current. A repository beneath an ancestor named `__pycache__` violated it.

## Observed results

| Observation | Before repair | After repair |
| --- | --- | --- |
| Actual exported CLI campaign | All 11 gates PASS | All 11 gates PASS |
| Unit discovery | 246 tests, 1 SKIP | 248 tests, 1 SKIP |
| Input pin | 12 explicit files; no scripts | 335 files, including scripts |
| Fresh report verification | PASS | PASS |
| Append a comment to `scripts/catalog.py`, then verify | **Exit 0, false PASS** | Exit 1, stale |
| Focused regression suite | 9 tests, 1 failure | 9 tests PASS on Python 3.12 and 3.14 |

The initial focused failure was recorded before changing the implementation.
The new regression checks source inclusion and stale-report rejection beneath
the cache-named ancestor. A second control checks that actual repository-relative
bytecode remains excluded. The unit regression injects successful commands to
test input-pin behavior; the separate exported campaigns execute the real gates.

## Minimal operational reproduction

Run from a checkout containing the historical base commit, using Python 3.11+.
Use a new fixture directory and keep all operations inside it. These PowerShell
commands export the vulnerable revision without changing the real worktree:

```powershell
$fixtureRoot = Join-Path (Get-Location) '.loop/cache-pin-repro'
New-Item -ItemType Directory -Path $fixtureRoot -ErrorAction Stop | Out-Null
git archive --format=zip --output="$fixtureRoot/base.zip" 393104e50f1007b30d04638259db72c6c19f011b
$fixtureRepo = Join-Path $fixtureRoot '__pycache__/repo'
Expand-Archive -LiteralPath "$fixtureRoot/base.zip" -DestinationPath $fixtureRepo
Push-Location $fixtureRepo
New-Item -ItemType Directory -Force .loop/tmp | Out-Null
$env:TEMP = (Resolve-Path .loop/tmp).Path
$env:TMP = $env:TEMP
python scripts/verification_session.py --session cache-before --output ../run-before
python scripts/verification_session.py --session cache-before --verify ../run-before/verification.json
Add-Content scripts/catalog.py '# changed after the verification campaign'
python scripts/verification_session.py --session cache-before --verify ../run-before/verification.json
Pop-Location
```

The final command incorrectly returns exit 0 on the vulnerable base. The input
filter checks `__pycache__` against absolute path components, so it discards all
source roots. Only the separately enumerated top-level files remain pinned.

For the fixed control, make a **second fresh export**, copy the repaired
`scripts/verification_session.py` and `tests/test_verification_session.py` into
that export, and repeat using a new session and output directory. The final
verification must return exit 1 and report stale verification inputs. In the
published observation, the fixed export contains only those two changes to the
base, and its source pin has 335 files. Final session publication adds evidence
files, so 335 is an intermediate fixture count, not the final repository count.

On Windows, the repository's filesystem tests need permission to create ordinary
hardlinks and junctions. The observed file-symlink privilege case remained SKIP.
The actual first campaign printed an earlier PowerShell `Resolve-Path` error
because its export-local temporary directory did not yet exist; the campaign
itself subsequently completed all eleven gates PASS. The fixed campaign used an
existing explicit temporary directory. The reproduction above creates it first.

## Evidence interpretation

- `verification-before.json` and `verification-after.json` are actual campaign
  reports; their `log_sha256` fields refer to original private gate logs.
- `unit-before.txt` and `unit-after.txt` expose sanitized complete unit logs,
  including the outer summaries independently checked before publication.
- `regression-before.txt` preserves the failing regression; the two after logs
  preserve successful Python 3.12 and Python 3.14 reruns.
- `verify-stale-before.txt`, `verify-fresh-after.txt`, and
  `verify-stale-after.txt` preserve the actual verifier outputs.
- `finding.json` retains hashes labeled `raw_private_hashes`. They identify
  private original artifacts, not sanitized public bytes.
- `published-hashes.json` hashes the UTF-8 LF bytes of every public artifact in
  this directory except itself. Paths in textual logs were replaced with
  `<workspace>` and `<user-home>` placeholders. A checkout's line-ending
  conversion can change local bytes; compare the committed Git blob if needed.

Full original gate logs and the two isolated exports remain under ignored
`.loop/audit-ab-20261025T083146Z/platform/`. These are CLI verification results,
**not model runtime validation**. Manually forged reports are not authenticated
attestations; that separate documented limitation is unchanged.
