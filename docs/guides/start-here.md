# Start here: from installation to a checked output

Loop is a collection of instructions for your agent. It helps structure a task,
produce the requested files and report what was checked. The host still supplies
the model, file tools, account connections and permissions. Python is needed for
the repository's installer and helpers, not to write an ordinary prompt.

For reusable conditional work, install the standalone `skills/workflow-setup`
package and ask `$workflow-setup` to design steps, skill choices,
result branches, a bounded cycle and a local agent map. See
[optional workflow setup](workflow-setup.md). Direct skill use below stays available.

![Four steps from request to checked result](../assets/loop-workflow.svg)

## 1. Choose by the result you want

| You need | Focused skill | Bundle to install |
|---|---|---|
| A reply or short summary | `loop-write` / `loop-summarize` | `writing` |
| Ticket triage and response drafts | `loop-support`; intake for unclear requests | `support` |
| Notes or a FAQ retaining conflicting sources | `loop-knowledge` | `knowledge` |
| A feasible work package with actual deliverables | `loop-work` | `work` |
| A broader office toolkit with drafts and documents | Start with the required outcome | `office` |
| Table analysis and a report | `loop-table` / `loop-document` | `data` |
| Organized local files | `loop-files` | `files` |
| A code change or reproducible bug repair | `loop-code` / `loop-debug` | `developer` |

A **skill** describes one workflow. A **bundle** selects folders to install and
can overlap other bundles. A **group** is a navigation category: each skill
belongs to one group. A **role toolkit** recommends useful skills for a role.
None requires executing every member. See the complete
[illustrated bundle workflows](bundle-workflows.md),
[bundle table](install-by-need.md#choose-a-small-bundle) or
[53-skill catalog](../../README.md#skill-catalog).

## 2. Install into the project you intend to use

If you have not cloned the repository:

```text
git clone https://github.com/Clas4444/agent-workflows.git
cd agent-workflows
```

From the repository root, replace `C:/My Project` with your actual project path.
For the support example, use Python 3.11+:

```text
python scripts/install_skills.py --bundle support --target "C:/My Project/.agents/skills" --check
python scripts/install_skills.py --bundle support --target "C:/My Project/.agents/skills"
python scripts/install_skills.py --bundle support --target "C:/My Project/.agents/skills" --check
python scripts/doctor_skills.py --bundle support --target "C:/My Project/.agents/skills"
```

The first read-only check normally exits **1** for a missing installation; inspect
the differences or error. After a successful install, the selected check and
doctor should exit **0**. The installed support folders are `loop`, `loop-intake`,
`loop-support` and `loop-write`, including the gateway's catalog/helper/UI files.
Existing managed files are backed up; unrelated files are preserved.

The example uses the Codex project layout. Other maintained layouts are
`.github/skills` and `.claude/skills`; on macOS/Linux substitute your project path.
For manual copying, preserve the **whole folders**, including supporting files.
See [installation details and recovery limits](install-by-need.md).

## 3. Start a fresh host session and ask for the task

Open the target project and start a fresh session. Check the available skill
names and actual instruction paths. If your host has not discovered the files,
the installation check alone cannot establish that the skills are usable there.

On a Codex host supporting dollar skill mentions, try:

```text
$loop bundle support
Use tickets.txt to create a triage brief and reply drafts. Cite ticket IDs,
keep categories provisional, and preserve missing SLA, ETA, owner and approval.
Save the brief and drafts as local files, reopen them and report checks.
Do not send replies, issue refunds or mark tickets resolved.
```

For a single focused task, `$loop-support ...` is also an explicit form. The
gateway helps select a workflow; it does not install missing skills or supply a
support-service connection. Native slash aliases and picker matching are untested
for this release. See [verified CLI selectors](skill-finder.md).

## 4. Inspect what was delivered

For this support task, look for both the saved files and the evidence behind them:

- Each ticket has a source pointer, provisional category and stated impact.
- Unknown SLA, ETA, dates, owners and approvals remain unknown.
- Replies are drafts. No external action is inferred from draft completion.
- The agent reports which files it reopened and which checks actually ran.

This is an acceptance checklist, not a prediction that every run will succeed.
The recorded 1.10 trial used explicitly supplied instruction paths and a fixed
artifact schema. It did **not** test this native discovery journey. The
[evidence map](../testing/evidence.md#behavioral-evidence) shows real source/output examples,
the original failed work trial and the narrower scope of the passing retry.

## If something looks wrong

| Symptom | Next check |
|---|---|
| Skill is absent in the host | Check the target root, run the selected doctor and verify paths in a fresh session |
| Helper says `missing_skills` | Install the selected members and complete payloads; lookup itself does not install |
| A made-up slash alias does nothing | Use an explicit canonical skill mention; CLI selector parsing does not register host commands |
| Agent returns only a plan | Recheck whether the request asks for actual deliverables and inspect saved outputs |
| An old PASS is cited | Compare its revision, input hashes and tested scope with the files used now |

Next: [everyday prompts](everyday-work.md),
[work and artifacts](work-and-artifacts.md), or
[developer examples](workflow-examples.md).
