# Install only what you need

You do not need to code to use the everyday skills. They guide an agent's work;
they do not install an email service, calendar connection, file manager or tutor.
Your host still needs its own tools, permissions and account access when applicable.

## Choose a small bundle

| Need | Bundle | Included skills |
|---|---|---|
| Write emails, letters and short summaries | `writing` | write, summarize |
| Meeting notes and personal organization | `office` | write, summarize, meeting, organize |
| Study and understand material | `learning` | learn, summarize, decide |
| Compare everyday options | `decisions` | decide, research, summarize |
| Work on existing code | `developer` | research-repo, code, debug, test, review |
| Deliver a small software project | `project` | workflow-project, plan, code, test, handoff |
| Test/review repository guarantees | `qa` | test-adversarial, evaluate, ci, review |
| Assess service incidents | `incident` | workflow-incident, diagnose, observe |

Names in the table omit the `loop-` prefix. The authoritative membership is
`skill-bundles.json`; `python scripts/install_skills.py --list` validates and
prints it. Bundles are convenient selections, not mandatory runtime pipelines.

## Ask your agent to install a bundle

After opening this repository, a non-programmer can ask:

```text
Install the office bundle from this repository into my selected project's
.agents/skills folder. Show the four selected skill names, preserve unrelated
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
The installer copies only the selection, preserves unrelated skills and backs
up overwritten managed files under this repository's `.loop/backups/` by default.
`--backup` can select another directory outside the target. Keep backups private.

Combine bundles or add an individual skill:

```text
python scripts/install_skills.py --bundle writing --bundle learning --skill loop-meeting --target "/home/you/my-project/.agents/skills"
```

Repeated selections are combined without duplicates. An unknown name or empty
selection fails before destination writes; it never falls back to installing all
skills. Existing `scripts/sync_skills.py --target ...` still selects the **full**
catalog, so use the need-based installer for a small subset.

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
