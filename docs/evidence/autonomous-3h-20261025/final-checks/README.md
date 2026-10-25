# Final installation and remote CI observations

Session: `autonomous-3h-20261025T092231Z`. These observations cover source
`d4afbcd94f888667f5fcb0a4e7ddd7aece629c28`; a later evidence-only commit does not
turn them into a new runtime execution. Raw fixture logs remain private in `.loop/`.

- Twelve bundle upgrades: actual install, check and read-only doctor commands all
  succeeded. Four managed payload changes occurred across the selected bundles;
  unchanged bundles are positive preservation controls, not overwrite tests.
  Every actual overwrite backup matched its original bytes. Custom and unrelated
  sentinel files remained unchanged.
- Six independently installed continuation runners: two skills in three layouts.
  Each timeout produced BLOCKED/nonzero, the descendant really started, and no
  delayed marker appeared in the finite six-second observation window. This tests
  the installed CLI payload, not native discovery in three different hosts.
- Exact-head CI logs: Windows Python 3.11/3.12 each ran all 305 unit tests without
  skips. Ubuntu Python 3.11/3.12 each discovered 305 with two Windows-only skips.
  All four jobs succeeded. JSON includes observed run/job IDs and skip reasons.

Reproducible underlying regression suites, from repository root with Python 3.11+:

```text
python -m unittest discover -s tests -p test_backup_preflight.py -v
python -m unittest discover -s tests -p test_process_lifecycle.py -v
python scripts/install_skills.py --list
python scripts/evidence_indexes.py
```

Those commands rerun the maintained regressions; they do not recreate or prove
execution of these historical twelve/six fixture observations. Session reports
record full gate commands and input pins. These summaries attest neither unlimited
process containment nor macOS execution, native activation, model reliability,
installation atomicity or freedom from filesystem races.

## All-skill forced-drift installation replay

The twelve bundles cover only 25 of the 49 skills. A further real CLI campaign
therefore selected all 49 explicitly, in each of three independent fixture roots.
All 58 managed payloads started with distinct custom bytes. Before install, check
and doctor returned nonzero and all 49 rows were DRIFTED. After install, all 58
payload bytes and all 58 original backups matched independently enumerated source
and original bytes; check and doctor passed. A second install made no backup,
and custom/unrelated files remained intact. All three layouts passed. This is
174 actual overwrite/backup comparisons, not 147 model-behavior trials.

Reproduce in a new ignored fixture directory, from repository root:

```text
python docs/evidence/autonomous-3h-20261025/final-checks/replay_all_payloads.py --repo . --output .loop/new-all-payload-replay
```

The script refuses an existing output and paths outside repository `.loop`.
It deliberately replaces only files it creates in its disposable fixture; no
personal skill installation is touched. Each command log is kept under output.
The oracle enumerates manifest resources independently of installer enumeration.
It asserts expected nonzero prechecks as well as exact bytes and positive checks.
Source payload SHA256s and the executed script hash are recorded in all-payloads.json.
