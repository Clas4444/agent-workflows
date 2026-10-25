# Install only what you need

You do not need to code to use the everyday skills. They guide an agent's work;
they do not install an email service, calendar connection, file manager or tutor.
Your host still needs its own tools, permissions and account access when applicable.

## Choose a small bundle

<!-- BEGIN GENERATED NEED BUNDLES -->

| Need | Bundle | Installed skills |
|---|---|---|
| Draft everyday communication and summarize supplied material | `writing` | `loop-write`, `loop-summarize` |
| Complete everyday work packages with source-grounded drafts, records and document artifacts | `office` | `loop-work`, `loop-write`, `loop-summarize`, `loop-meeting`, `loop-organize`, `loop-document` |
| Plan study, understand supplied material and compare learning choices | `learning` | `loop-learn`, `loop-summarize`, `loop-decide` |
| Compare options with explicit priorities and source-grounded evidence | `decisions` | `loop-decide`, `loop-research`, `loop-summarize` |
| Understand, implement or repair, test and review existing code | `developer` | `loop-research-repo`, `loop-code`, `loop-debug`, `loop-test`, `loop-review` |
| Coordinate a small software project and verified implementation slices | `project` | `loop-workflow-project`, `loop-plan`, `loop-code`, `loop-test`, `loop-handoff` |
| Challenge contracts, assess evidence and inspect CI/review results | `qa` | `loop-test-adversarial`, `loop-evaluate`, `loop-ci`, `loop-review` |
| Assess impact, investigate and verify operational signals | `incident` | `loop-workflow-incident`, `loop-diagnose`, `loop-observe` |
| Coordinate feasible everyday deliverables and checkpoints | `work` | `loop-work`, `loop-write`, `loop-meeting`, `loop-decide` |
| Inventory and verify scoped local file organization | `files` | `loop-files` |
| Draft, summarize and verify usable document files | `documents` | `loop-document`, `loop-write`, `loop-summarize` |
| Analyze tables and create source-grounded report artifacts | `data` | `loop-table`, `loop-document` |

<!-- END GENERATED NEED BUNDLES -->

The table is generated from `skill-bundles.json`; the installer validates the same registry.
Bundles are installation selections, not mandatory runtime pipelines.

## Ask your agent to install a bundle

After opening this repository, a non-programmer can ask:

```text
Install the office bundle from this repository into my selected project's
.agents/skills folder. Show the selected skill names, preserve unrelated
skills and custom files, use the repository installer with backups, and run
the same selected-bundle check afterward. Do not change my global installation.
```

Name the actual project directory. Use `.agents/skills` for the Codex project
layout, `.github/skills` for Copilot, or `.claude/skills` for Claude Code. These are
the layouts maintained by this repository; matching files alone do not prove
native discovery or equivalent behavior on every host/version.

## Run the installer yourself

From the cloned repository root with Python 3.11+ available:

```text
python scripts/install_skills.py --list
python scripts/install_skills.py --bundle office --target "C:/My Project/.agents/skills" --check
python scripts/install_skills.py --bundle office --target "C:/My Project/.agents/skills"
python scripts/install_skills.py --bundle office --target "C:/My Project/.agents/skills" --check
```

Replace the target with your project. On macOS/Linux, an example target is
`/home/you/my-project/.agents/skills`; quote paths containing spaces. On Windows,
use an installed interpreter path or `py -3` if that launcher is available.

The first check is read-only. **Exit 1 with a differences list means the selected
files need installation/update**, not that installation already happened. A
validation error prints `FAIL` to stderr. A successful post-install check exits 0.
The installer copies the selected instructions and all declared scripts/references/assets, preserves unrelated skills and backs
up overwritten managed files under this repository's `.loop/backups/` by default.
`--backup` can select another directory outside the target. Keep backups private.
Planned backup paths reject internal symlink/junction aliases and invalid parent
types before any copies. Use a distinct ordinary backup directory; a preflight
failure means inspect the reported path rather than retrying with alias checks
disabled. This does not make a multi-file installation atomic.

Combine bundles or add an individual skill:

```text
python scripts/install_skills.py --bundle writing --bundle learning --skill loop-meeting --target "/home/you/my-project/.agents/skills"
```

Repeated selections are combined without duplicates. An unknown name or empty
selection fails before destination writes; it never falls back to installing all
skills. Existing `scripts/sync_skills.py --target ...` still selects the **full**
catalog, so use the need-based installer for a small subset.

## Diagnose an existing installation without changing it

If the repository has newer workflows but your host still lists old skills, ask:

```text
Diagnose my selected skill installation with scripts/doctor_skills.py. Compare
the office bundle against this checkout, distinguish absent skills, missing
resources and changed files, and report what a fresh host session still needs
to verify. Do not install, overwrite, execute or delete anything.
```

Or run the read-only command yourself:

```text
python scripts/doctor_skills.py --bundle office --target "C:/My Project/.agents/skills"
python scripts/doctor_skills.py --all --target "C:/My Project/.agents/skills"
```

An explicit selection is required: repeat `--bundle`/`--skill`, or choose `--all`.
The tool reports `CURRENT`, `NOT_INSTALLED`, `INCOMPLETE`, `DRIFTED`, or `BLOCKED`
per skill, with hashes for managed files. `reference_version` identifies this
checkout's declared version; it is not a guessed installed version. Exit 0 means
the selected bytes matched and the reference stayed unchanged during observation.
Exit 1 means differences, a blocked path or an error. Always inspect overall
`status` and `reference_errors`; an individual CURRENT row cannot override a
changed reference. No directory, backup, installation receipt or cache is created.

Unmanaged extras are preserved and not inspected. Native discovery and runtime
are always `NOT_RUN`: matching bytes cannot prove your host has activated them.
If the doctor finds drift, review custom changes and explicitly select an install
target before using the installer. Restart or open a fresh host session afterward,
then verify its actual available skill names and paths. The repository does not
silently repair a personal/global installation.

## Without Python

Copy the chosen **skill folders**, not only their `SKILL.md`, from `.github/skills`
into your selected project's native root. For example, the writing bundle is
`loop-write/` and `loop-summarize/`. Preserve existing folders or back them up
before replacing them. The continuation skills include a `scripts/` folder that
must travel with them; manual copying does not run the repository's alias checks.

## Confirm your host sees the skills

Start a fresh host session, ask which skills are available and verify the actual
paths before relying on them. For an everyday task, try:

```text
Use $loop-write to draft a polite email from these facts. Leave the date I have
not decided as a placeholder. Produce a draft only; do not send it.
```

Use the invocation syntax your host supports. If it cannot find the skill, report
discovery as BLOCKED/NOT_RUN and check the path and host configuration. A successful
file-copy check is not proof of activation. See [everyday examples](EVERYDAY-WORK.md)
and the [runtime matrix](../RUNTIME-TEST-MATRIX.md).

## When a host omits installed skills

A host can omit skill descriptions when its metadata/context budget is exceeded.
In the 2026-10-25 Codex CLI exercises, the existing global installation emitted
budget warnings and reported 372 omitted skills. That is an observation from this
host configuration, not a universal Codex limit or proof that a selected skill was
activated. Read-only doctor results still describe files only.

Start with the smallest bundle needed for the task and inspect the fresh host's
actual available names and paths. Check the host's documented precedence if both
project and global installations exist; adding project copies alone may not reduce
an oversized global catalog. Do not delete personal skills automatically. If the
host supports explicitly reading an instruction file, record that as explicit
loading, then verify the resulting artifacts separately from native discovery.
See the [session evidence](../testing/AUTONOMOUS-3H-2026-10-25.md) for the observed
configuration and limits.

## Supporting files and recovery

Keep the entire selected folder when copying manually. Managed resources are listed in `skill-resources.json`; matching SKILL.md alone does not prove a complete install. Repository-native copies require the same managed inventory, while the installer preserves unrelated custom files. A failed or partial operation needs inspection of actual state; backups are recovery inputs, not automatic permission to overwrite newer work.
