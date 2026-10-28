# Find a skill or bundle

Use the smallest workflow that fits the requested outcome. A bundle is a toolkit,
not an instruction to execute all its members.

## In a host

Use canonical skill names on hosts supporting dollar skill mentions:

```text
$loop-code add the requested export and run relevant tests
$loop-debug fix this reproducible failure
$loop-knowledge build a source-linked FAQ from these policies
```

The distributed `agents/openai.yaml` requests canonical display names and starter
prompts. You can try those names in a supporting host picker after installation;
their actual search behavior has not been verified for this release. Search ranking
and native slash commands are host behavior, not controlled by this repository.
Use canonical skill names such as `$loop-code`; we do not install global custom
slash commands or publish shortcut invocation aliases. Short search terms such as
`lc`, `dbg` and `kb` remain candidate-search hints: `search --query lc` finds
`loop-code`, while `resolve --query lc` and `$loop lc` are rejected. A suggestion
does not execute a skill. Select the canonical result and give the task directly.

Official [Build skills documentation](https://learn.chatgpt.com/docs/build-skills),
read 2026-10-26, describes explicit mentions/selectors and optional UI metadata.
That does not establish native slash aliases or fuzzy picker matching on every host.
UI/native discovery for this release is NOT_RUN until observed on the target host.

## Read-only CLI lookup

From repository root, Python 3.11+:

```text
python .github/skills/loop/scripts/find_skill.py search --query "loop-code"
python .github/skills/loop/scripts/find_skill.py resolve --query "loop-code"
python .github/skills/loop/scripts/find_skill.py resolve --query "bundle office"
python .github/skills/loop/scripts/find_skill.py bundles
python scripts/discovery.py
```

After installing, use the finder's actual path inside `loop/scripts`. It imports
only Python's standard library and carries its own generated catalog. `resolve`
requires an exact canonical skill name or full bundle selector; search returns candidates without choosing
or executing them. Unknown/ambiguous selectors fail, never select the full catalog.
A valid catalog match can still have `missing_skills`: lookup success is distinct
from installation completeness. No commands, task text or model responses are eval'd.

| Canonical skill | Use it for |
|---|---|
| `loop-code` | authorized implementation work |
| `loop-debug` | a reproducible failure |
| `loop-review` | an evidence-backed review |
| `loop-test` | selecting a test strategy |
| `loop-work` | an office or personal work package |
| `loop-table` | table analysis and report artifacts |
| `loop-document` | a document artifact |
| `loop-meeting` | meeting preparation or synthesis |
| `loop-knowledge` | source-linked notes or FAQ |
| `loop-intake` | scoping an unclear request |
| `loop-support` | support-ticket triage |

Every skill accepts only its canonical name. Use the full `bundle <id>` selector.
Keep the actual task separate from the CLI selector; `--query` accepts only the
lookup string for resolution. It does not parse an arbitrary task into shell code.

## Installation and maintenance

See [bundle starting points and worked examples](BUNDLE-QUICKSTART.md) for the
first skill, minimum inputs and expected output for each bundle.

All need bundles include the single `loop` gateway. For an individual skill, select
the gateway too only if you want its read-only canonical-name/bundle lookup:

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
