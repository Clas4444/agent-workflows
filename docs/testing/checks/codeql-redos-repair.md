# Markdown checker ReDoS repair

Historical internal 1.10.3-experimental candidate, now included in the unpushed
1.11.0 candidate. The session counts below belong to their named input pins,
not the later setup implementation. Base commit:
`30a0b0b4e24e7387f7499bfdc8c8bd9c950b479e`.

[CodeQL alert 1](https://github.com/Clas4444/agent-workflows/security/code-scanning/1)
reports py/redos, severity High, in the inline-link regex in scripts/docs_check.py.
The scan job succeeded while the security finding remained open.

The plain-character alternative had an inner repetition inside an outer
repetition. A missing closing delimiter allowed exponentially many partitions of
the same destination. Removing the inner repetition preserves the accepted token
sequence while removing that ambiguity. No alert suppression or dismissal is used.

## Local evidence

- Before: malformed `[](` followed by 50,000 exclamation marks exceeded a bounded
  three-second subprocess timeout. The new regression also failed against the
  baseline at its five-second bound.
- After: the same malformed input returned in 0.0743 seconds including process
  startup. This is a single observation, not a guaranteed timing threshold.
- 19 documentation tests pass on Windows Python 3.14 and 3.12, including malformed,
  unterminated-title and valid long destinations using three character classes.
- 112,347 exhaustive short-input comparisons preserve match spans and captured
  destinations against the base version. This bounded corpus is not a proof for
  all possible Markdown.
- Full code-fix suite: 343 tests, 342 pass, one skip, exit 0. Documentation check:
  98 Markdown files and 529 local links at that snapshot. These counts precede
  this added report; final candidate gates are recorded separately in local logs.

Local CodeQL analysis is NOT_RUN because its CLI is unavailable. Remote analysis
of the repair is NOT_RUN because this candidate has not been pushed. The GitHub
alert must not be described as closed until a new scan confirms it.

The earlier code-fix-only candidate passed all 14 fixed repository gates in local session
`dual-repo-20261028`, including 343 discovered tests (342 pass, one skip).
The report verifier confirms unchanged inputs against fingerprint
`8766ce92274acc2cab8480a7e6d868739ea40176fd28d44e84a33170d671d5ab`.
That input pin does not certify the later installation-plan feature. Raw logs
remain machine-local; this is local verification, not remote CodeQL
attestation or a new runtime-model campaign.

The expanded candidate, including installation plans, separately passes 14/14
gates in session dual-repo-expanded-20261028: 348 tests, 347 pass and one skip.
Its unchanged-input fingerprint is
`25ecafbecfda4bf06a70498fcbb8e7a1c46d3ceef564fe9864f0adbdee688dcb`.
Plan-specific integration tests cover review/apply, target drift, reference drift,
blocked hardlinks and incompatible CLI modes. The 25-test install/doctor subset
also passes on Python 3.12 and 3.14. This still does not close the remote alert.

## Publication and rollback

Run the documented repository gates before publication, push only the reviewed
candidate, then inspect CodeQL and Windows/Linux CI on that exact commit. If the
patch regresses supported navigation, revert its code/version commit and keep the
security finding open for a replacement fix. Existing illustrations and skills do
not need regeneration for this patch.
