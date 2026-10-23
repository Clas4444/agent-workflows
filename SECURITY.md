# Security Policy

## Scope

This repository contains Markdown workflow instructions, a local Python runner,
and validation scripts; it is not a hosted service. Report:

- instructions that could cause unsafe or unauthorized changes;
- guidance that could expose credentials or private data;
- misleading permission, installation, or verification claims;
- committed secrets or unsafe repository configuration.

The runner writes captured agent output to local state and report files. Treat
that output as sensitive until reviewed.

## Reporting

Use GitHub's private security advisory flow for sensitive vulnerabilities when
available. For a non-sensitive documentation issue, open a public issue with:

1. the affected file, skill, and version or commit;
2. the exact instruction or behavior;
3. a minimal reproduction or supporting evidence;
4. the safer expected behavior.

Never include credentials, tokens, private source code, or personal data in a
public report.

## Response

This is an experimental independent project. Reports are reviewed on a
best-effort basis; no response-time or remediation guarantee is provided.
