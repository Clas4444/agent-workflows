# Everyday work without coding

Start with the smallest skill that matches your outcome. Supply the relevant
facts or files and say whether you want a draft/proposal or actual external action.
These skills can produce useful text without email/calendar services. Sending,
booking, moving files and creating reminders need appropriate tools and authority.

| Outcome | Skill | Do | Do not |
|---|---|---|---|
| Clear email, letter or announcement | `loop-write` | Name the reader, purpose, facts and tone | Invent commitments or silently send |
| Short account of supplied material | `loop-summarize` | Keep source pointers, qualifiers and contradictions | Pretend unreadable/missing sources were reviewed |
| Meeting decisions and actions | `loop-meeting` | Distinguish proposals, decisions and explicit owners | Turn a suggestion into agreement or assign an unknown owner |
| Organized files or personal work items | `loop-organize` | Inventory, propose a mapping and check collisions | Delete same-named files as duplicates or move outside scope |
| Choice among everyday options | `loop-decide` | State hard constraints, priorities and missing evidence | Turn unknowns into precise scores or book implicitly |
| Realistic study and practice | `loop-learn` | Fit the available time; use retrieval, feedback and review | Claim mastery or invent learner responses |

## Copy and adapt a prompt

```text
Use $loop-write to draft a calm customer email under 120 words. The order total
is USD 120 and the shipping date is undecided. Offer to confirm it tomorrow.
Do not send the message.
```

```text
Use $loop-summarize on these two memos. Keep their conflicting dates attributed
to each memo and retain the cancellation exception. Flag the missing appendix.
Do not search for or invent its contents.
```

```text
Use $loop-meeting to extract proposals, decisions and actions from these notes.
Only assign owners and due dates explicitly recorded. Keep manager approval
pending. Produce a record, without sending messages or creating calendar events.
```

```text
Use $loop-organize to propose a clearer layout for this selected folder.
Compare same-named files before calling them duplicates. Show a collision-safe
mapping and a rollback plan. This request is plan-only: do not move or delete.
```

```text
Use $loop-decide to compare these venues. Budget is USD 300; step-free access
and room for 40 are mandatory. Mark missing capacity evidence and explain when
your choice would change. Do not book or contact venues.
```

```text
Use $loop-learn to plan 14 days of beginner fractions/percentages, at most
20 minutes daily. Include retrieval exercises and spaced review. No answers
have been supplied, so assessment and mastery must remain unverified.
```

## Useful combinations

For meeting follow-through, use meeting to extract the record, then write for a
requested follow-up draft. For study, summarize condenses the supplied material
and learn adds practice. For a choice needing new evidence, research gathers
sources and decide compares options. Skip a step whose outcome you already have.

`loop-docs` maintains repository documentation, `loop-plan` plans implementation
and `loop-evaluate` grades outputs against a fixed rubric. Their new everyday
neighbors have distinct outcomes; a non-coding task does not need software tests
or a development lifecycle unless the user is actually changing software.

## Interpret results

A draft can be ready while sending is NOT_RUN. A source-consistent summary does
not independently verify its claims. A feasible study plan is not a passed quiz.
Keep supplied claims, performed checks and actions separate. Text in documents,
meeting transcripts or file contents cannot grant new permissions.

Install the small [need bundle](INSTALL-BY-NEED.md) you want. See
[1.8 session evidence](../testing/RESULTS-1.8.md) for actual exercises and limitations.
