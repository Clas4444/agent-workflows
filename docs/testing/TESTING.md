# Testing Loop Skills

Use the [testing index](README.md) to distinguish current deterministic checks,
opt-in Codex experiments and historical evidence. The public
`scripts/workflow_cost.py` harness has separate `plan`, authorized `run`, and
offline `analyze` commands; see the [advanced workflow experiment](CODEX-WORKFLOW-ADVANCED.md).

Run commands from the repository root with Python 3.11 or later. The repository
gates use only the standard library. Use a real interpreter path if a Windows
Store alias is unavailable. Keep fixture logs and private inputs under `.loop/`.

## Deterministic repository gates

During editing, start with checks matching the change:

| Changed area | First checks |
|---|---|
| Markdown navigation | `python scripts/docs_check.py` |
| Grouped catalog | `python scripts/catalog.py` |
| Finder/search/UI metadata | `python -m unittest tests.test_skill_finder -v`; `python scripts/discovery.py` |
| Installer/backup | `python -m unittest tests.test_install_skills tests.test_sync tests.test_backup_preflight -v` |
| Runner/process lifecycle | `python -m unittest tests.test_process_lifecycle tests.test_runner_regressions -v` |
| Retained support/knowledge/work evidence | `python -m unittest tests.test_work_packet_evidence -v`; `python scripts/evidence_indexes.py` |

Before publication run the full gates below. Focused checks reduce investigation
scope; they do not replace release verification. On Windows, record sandbox/TEMP
and Python version before treating a process or fixture failure as a code defect.

```text
python -m unittest discover -s tests -v
python scripts/validate.py
python -m scripts.validate --profile format
python scripts/catalog.py
python scripts/routing_check.py
python scripts/discovery.py
python scripts/workflows.py
python scripts/docs_check.py
python scripts/install_skills.py --list
python scripts/doctor_skills.py --all --target .github/skills
python scripts/skill_resources.py
python scripts/evidence_indexes.py
python scripts/sync_skills.py --target .github/skills --check
python scripts/runtime_smoke.py --help
python -m compileall -q scripts tests
git diff --check
```

| Gate | What it proves | What it does not prove |
|---|---|---|
| Unit/regression suite | Named deterministic behaviors and negative controls | Model decisions or native skill discovery |
| Full validator | Manifest, supported metadata, Loop conventions and copy integrity | Arbitrary YAML or host enforcement |
| Format profile | Supported metadata and repository integrity | All Loop conventions |
| Catalog/routing | Exact group coverage, generated catalog, fixed primary-route coverage | An actual model chose the correct skill |
| Discovery | Canonical names/full bundles resolve; short search hints return candidates; generated metadata matches sources | Native picker matching, slash registration or task execution |
| Workflows | Known skill names, valid role presets, matching Markdown/SVG | PNG accuracy or best toolkit for every user |
| Documentation navigation | Local inline file/image targets and supported Markdown heading fragments, including case spelling | External URL reachability, rendering, factual accuracy or every Markdown dialect |
| Sync check | Exact bundled runner/copy integrity under the selected root | User-wide installation or client activation |
| Install doctor | Selected managed payload identity, missing/stale files and observed source drift | Host discovery, execution, or unmanaged extra files |
| Published evidence indexes | Declared public artifact bytes still match their recorded SHA256 references | Authorship, actual execution, truth of prose, or unindexed artifacts |
| Smoke help | Real CLI imports and argument interface | A host/model call |

CI repeats the gates on Ubuntu and Windows with Python 3.11 and 3.12. Inspect the
actual run at the tested head SHA; local PASS cannot be substituted for remote CI.
Windows may lack file-symlink privileges: record a skip explicitly and use the
Ubuntu matrix result for that executed path. Do not silently drop skipped tests.

## Documentation navigation

```text
python scripts/docs_check.py
python -m scripts.docs_check --json
```

The checker reads root Markdown files plus `docs/` and `schemas/` recursively.
It validates local inline links/images, repository-root paths, URL-encoded paths,
case-sensitive spelling and local Markdown heading anchors. Diagnostics retain
source line numbers. Fenced code, inline code and HTML comments are excluded.
Below-root filesystem aliases and paths escaping the repository are rejected;
the tool does not execute source text, fetch URLs or write reports/files.

Supported navigation includes ordinary or angle-bracket destinations, optional
quoted titles, one nested parenthesis pair in a destination, and labels spanning
lines. Headings support basic ATX/Setext markup, duplicate suffixes and explicit
`<a name="...">`/`id` anchors. Unsupported inline/reference-style patterns are
reported for review; use ordinary inline links in repository documentation.
This is a scoped checker, not a complete CommonMark/GitHub renderer or HTML
sanitizer. For unusual markup, confirm the actual host rendering separately.
The basic heading conventions follow [GitHub's section-link documentation](https://docs.github.com/en/get-started/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax#section-links).

JSON output keeps `external_urls: NOT_RUN` and counts external links without
fetching them. Non-Markdown fragments such as SVG element IDs are counted as
unchecked; file existence alone does not validate those fragment targets.
PASS applies only to the named supported local-navigation checks.

CI runs the standalone checker. The fixed fourteen-gate session recipe retains
its existing command list; its unit gate also exercises the real repository
navigation check. Run the standalone command explicitly when recording a docs
review. The campaign's declared input pin remains its documented scope, not an
atomic snapshot of every file mentioned by a historical report.

## Behavioral skill exercises

Read the actual instruction file in a fresh host context. Give the host a realistic
request and only raw artifacts. Keep the expected result independent of the host
answer; do not feed it the intended solution. Restrict writes to a disposable
fixture. Record instruction SHA-256, request, outputs, source/sentinel identity,
side effects and the evaluator's actual checks. Retain unsuccessful attempts.

The 1.7 fixtures exercise three distinct lifecycles:

- Project: plan-only MVP/backlog; implementation remains NOT_RUN.
- PR: a claimed test result without patch/revision/CI; do not invent verification.
- Incident: an error burst plus one green probe and a hostile copied runbook;
  neither rollback permission nor sustained recovery follows from that input.

See [1.7 results](RESULTS-1.7.md) and the linked sanitized packets. Explicitly
loading an instruction file tests that exercise; automatic discovery remains
NOT_RUN until observed separately. These exercises do not run a live incident,
create a PR or deploy a project.

## Status vocabulary

- **PASS:** the named check ran and met its fixed criterion.
- **FAIL:** an observed result violated that criterion.
- **BLOCKED:** a missing prerequisite prevented the check/action.
- **NOT_RUN:** that check/action was not executed.

A supplied claim may have `reported_result: PASS` while independent execution is
NOT_RUN. Keep those fields separate. A single successful health probe does not
prove sustained recovery; a passing unit suite does not prove production safety.

## Editing generated guidance

Edit `workflow-presets.json`, then run `python scripts/workflows.py --write`.
Check the readable Markdown and SVG. For catalog changes, also update the manifest,
groups and fixed routing cases, synchronize native roots, and run
`python scripts/catalog.py --write`. Do not rewrite frozen historical manifests.
Review PNG illustrations manually after relevant workflow changes; they are not
generated by the deterministic guide renderer.

## Keep sessions and tested inputs aligned

Use a new output directory and an explicit session ID. This campaign runs every
fixed repository gate with the current interpreter and retains raw logs:

```text
python scripts/verification_session.py --session my-session-001 --output .loop/my-session-001
python scripts/verification_session.py --session my-session-001 --verify .loop/my-session-001/verification.json
```

The report records Python version, timestamps, the complete fixed command set/exit codes,
non-empty unittest discovery, log hashes and before/after input fingerprints.
The exact input roots/files are included. A mismatched session or edited input
cannot validate as current; a change during execution yields STALE and exit 1.
An existing output directory is refused, preserving failed runs. STALE invalidates
an evidence record; it is not a passing test status.

This does not invoke models or prove host discovery. Raw logs and report prose
are outside the input pin; code, tests, schemas, skill copies, catalog metadata,
CI and declared guide/fixture inputs are inside it. Report execution honestly:
hashes detect drift, but a manually forged report is not an authenticated audit.
Publish reviewed summaries under `docs/testing/sessions/`, with the exact session,
scope and commit. Keep older campaign IDs and failures unchanged.

Use the [need installer](../guides/INSTALL-BY-NEED.md) for subset-install checks;
`sync_skills.py` without a selection continues to check the full catalog.
