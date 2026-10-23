---
name: loop-test
description: "Run a bounded testing loop for a project or change: select tests, reproduce failures, improve coverage or fixtures when authorized, run checks, and report results. Use when the user asks to test repeatedly or improve verification."
argument-hint: "[duration and target]"
user-invocable: true
disable-model-invocation: false
---

# Loop Test

Identify the project test gate, baseline command, environment, and target risk.
Run the smallest relevant bounded test first, then broaden only when evidence
requires it. Distinguish `PASS`, `FAIL`, `BLOCKED`, and `NOT_RUN`; missing tools
are not PASS. Change tests or fixtures only with authorization and never weaken
acceptance criteria.

Checkpoint command, exit code, failure evidence, coverage/test gap, action, and
next test. If no new test angle remains, or materially identical results occur
more than three consecutive times, write the consolidated report and stop. Never
sleep to consume duration.
