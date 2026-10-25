# Runner process lifecycle

The standalone `run_loop.py` owns the command tree for one bounded invocation.
It does not grant command permissions or sandbox hostile code. Model output
markers are still self-reports; successful process cleanup is not task acceptance.

On Windows the runner creates a private kill-on-close Job Object. A small Python
launcher waits for a one-byte stdin gate before starting the target command. The
runner assigns that launcher to the job before releasing the gate, closing the
ordinary assignment-versus-child-spawn race. The gate consumes no target prompt
bytes. Target stdout/stderr and exit status keep their existing protocols.
Windows job setup failure aborts before the target is launched; there is no silent
fallback to an uncontained process. This requires a Windows host that permits
nested jobs. One extra isolated Python launcher process is the compatibility cost.

On POSIX the runner starts a new session and kills the owned process group on
timeout and invocation cleanup. Ordinary descendants remaining in that group are
covered even if their parent exits first. A process deliberately creating a new
session can escape that group; this is lifecycle control, not an isolation boundary.

Timeout cleanup cancels reader-queue delivery before terminating the owned tree.
Readers can stop when the bounded queue is full instead of waiting forever for a
consumer that has already stopped. The direct process is reaped and reader/stdin
threads receive bounded joins. Process creation and kernel teardown are not
hard real-time deadlines; the command timeout excludes platform process creation.

Owned background descendants are also closed when a command completes normally.
Do not rely on a server started by one invocation surviving into a later one;
services intended to outlive an invocation need a separately authorized lifecycle.

Limits remain explicit: Windows child creation via external services or WMI,
detached POSIX sessions, remote jobs, filesystem side effects already performed,
and external API operations are outside this mechanism. Nothing rolls back data.
The opt-in runtime-smoke harness has its own subprocess code and must not inherit
this guarantee merely because the continuation runner was changed.

Authoritative references inspected on 2026-10-25:

- [Microsoft Job Objects](https://learn.microsoft.com/en-us/windows/win32/procthread/job-objects): inheritance, nesting and job termination.
- [AssignProcessToJobObject](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject): required access rights and assignment failures.
- [Python subprocess](https://docs.python.org/3/library/subprocess.html): process groups, sessions, pipes and timeout semantics. Local tests use Python 3.12/3.14; the live documentation may describe a newer release.

Actual before/after evidence belongs to the current session report. Do not infer
POSIX runtime execution from Windows tests or native model execution from these
deterministic process fixtures.
