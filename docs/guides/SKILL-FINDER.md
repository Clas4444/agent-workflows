# Find a skill, shortcut or bundle

Use the smallest workflow that fits the requested outcome. A bundle is a toolkit,
not an instruction to execute all its members. No alias grants permissions.

## In a host

Canonical explicit forms on Codex hosts supporting dollar skill mentions:

```text
$loop code add the requested export and run relevant tests
$loop lc add the requested export and run relevant tests
$loop dbg fix this reproducible failure
$loop kb build a source-linked FAQ from these policies
$loop bundle office prepare the requested work packet; do not send anything
$loop bundle support triage these tickets and draft replies only
$loop bundle knowledge update the FAQ and flag unsupported claims
```

The distributed `agents/openai.yaml` requests display names such as
**Loop Code (lc)**, **Loop Debug (dbg)** and **Loop**, plus starter prompts.
You can try those names in a supporting host picker after installation; their
actual search behavior has not been verified for this release.
Search ranking, matching of spaced text and native `/lc` commands are host behavior,
not controlled by this repository. If your host routes `/loop code` or `/lc` here,
the gateway understands that selector; if it does not, use `$loop code` or the
canonical `$loop-code`. We do not install global custom slash commands.

Official [Build skills documentation](https://learn.chatgpt.com/docs/build-skills),
read 2026-10-26, describes explicit mentions/selectors and optional UI metadata.
That does not establish native slash aliases or fuzzy picker matching on every host.
UI/native discovery for this release is NOT_RUN until observed on the target host.

## Read-only CLI lookup

From repository root, Python 3.11+:

```text
python .github/skills/loop/scripts/find_skill.py search --query "loop code"
python .github/skills/loop/scripts/find_skill.py resolve --query "/lc"
python .github/skills/loop/scripts/find_skill.py resolve --query "/loop bundle office"
python .github/skills/loop/scripts/find_skill.py bundles
python scripts/discovery.py
```

After installing, use the finder's actual path inside `loop/scripts`. It imports
only Python's standard library and carries its own generated catalog. `resolve`
requires an exact registered selector; search returns candidates without choosing
or executing them. Unknown/ambiguous selectors fail, never select the full catalog.
A valid catalog match can still have `missing_skills`: lookup success is distinct
from installation completeness. No commands, task text or model responses are eval'd.

| Short selector | Canonical skill |
|---|---|
| `lc`, `code` | `loop-code` |
| `dbg`, `debug` | `loop-debug` |
| `rv`, `review` | `loop-review` |
| `tst`, `test` | `loop-test` |
| `wk`, `work` | `loop-work` |
| `tbl`, `table` | `loop-table` |
| `doc`, `document` | `loop-document` |
| `mtg`, `meeting` | `loop-meeting` |
| `kb`, `knowledge` | `loop-knowledge` |
| `intake` | `loop-intake` |
| `support` | `loop-support` |

Other skills accept their canonical name and spaced suffix, e.g. `test integration`.
Use `bundle <id>` or `b <id>` to avoid collisions with skill names such as work.
Keep the actual task separate from the CLI selector; `--query` accepts only the
lookup string for resolution. It does not parse an arbitrary task into shell code.

## Installation and maintenance

All need bundles include the single `loop` gateway, not a second folder for each
alias. For an individual skill, select the gateway too if you want shortcut lookup:

```text
python scripts/install_skills.py --skill loop --skill loop-code --target "/my/project/.agents/skills"
python scripts/install_skills.py --bundle support --target "/my/project/.agents/skills"
```

Restart/open a fresh host session and check the actual selected instruction paths.
Do not infer activation from file equality. The catalog lists all available choices.
The helper returns selected instruction paths and checks whether their SKILL.md
files exist; the agent must read the current selected instructions before use.
Missing members stay explicit;
there is no automatic install or authentication. Installing fewer skills still
helps keep metadata small; UI metadata and one router cannot guarantee elimination
of a host context-budget warning.

When changing names/descriptions/bundles, run `python scripts/discovery.py --write`,
register resources and sync the maintained roots. The read-only gate and full
validator reject stale catalog/UI bytes. This generator owns the minimal UI files
in this repo; do not add unrelated policy/dependency fields and regenerate over them.
