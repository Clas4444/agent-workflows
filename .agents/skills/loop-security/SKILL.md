---
name: loop-security
description: "Review authorized code and configuration for security risks using threat boundaries, source evidence and safe local tests. Use for a defensive security review or scoped remediation, not unrestricted probing."
argument-hint: "[duration, authorized target, and threat model]"
user-invocable: true
disable-model-invocation: false
---

# Loop Security

## Use when

Review a project's security properties or repair an authorized security defect.
General code quality belongs in loop-review; capability adoption belongs in
loop-research-tools.

## Inputs

Authorized target, threat model, sensitive assets and permitted local checks.
If no duration is supplied, use the task scope as the bound and stop when it is complete.
Reuse authorization already given in the session; clarify only missing information
that prevents safe progress.

## Workflow

1. Define authorized assets, trust boundaries, entry points, attacker control,
   sensitive data and expected protections. Read project security guidance.
2. Trace one risk at a time from input to sensitive operation: authentication,
   authorization, injection, filesystem access, secrets or unsafe configuration.
3. Record the exact source path, reachable conditions, impact, confidence and
   whether a finding is observed or inferred. Redact credentials and private data.
4. Use existing scanners or non-destructive local fixtures when available.
   Do not equate a clean scan with absence of vulnerabilities.
5. Apply only authorized remediation; verify the regression and legitimate use.
   Report severity, evidence, commands, remaining uncertainty and next action.

## Output

Prioritized reachable findings with redacted evidence, confidence and remediation verification.
For each check distinguish PASS (verified), FAIL (check failed), BLOCKED (a
required prerequisite prevents progress) and NOT_RUN (not executed). Include
what was observed, what changed and what remains unverified.

## Boundaries and evidence

Do not test external systems, exploit production, extract secrets, change access
controls, or install scanners without authorization. Do not upload private code.
Report PASS, FAIL, BLOCKED or NOT_RUN; absent tools are NOT_RUN, not PASS.

Stop when no suitable work remains, the deadline or user request ends the run,
a safety boundary is reached, or materially identical results recur more than
three times. Never sleep to consume time; write a consolidated report.

## Example

```text
/loop-security 15m review local file-path handling within this repository
```

Use the host's supported skill invocation syntax; the example expresses intent,
not a guarantee that every host supports slash commands.
