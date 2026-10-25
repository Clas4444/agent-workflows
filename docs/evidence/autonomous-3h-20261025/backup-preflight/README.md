# Backup preflight reproducer

In an isolated directory create two distinct customized target skills (`loop-write`
and `loop-summarize`). Create a backup directory with `loop-write/` as an ordinary
folder and `loop-summarize` as a junction/symlink to that first folder. The two
planned SKILL.md backup files are initially absent. Run the writing-bundle install
with this explicit backup root. Before repair it returned zero, overwrote both
target files, and left both backup spellings containing only the second original.

The regression in tests/test_backup_preflight.py uses actual Windows junctions or
POSIX symlinks, also exercises read-only check mode and the installer CLI, and
requires rejection before any copies. It independently asserts original bytes.
A valid distinct-backup control must continue preserving each original. Another
control puts a regular file in a later backup-parent position and requires failure
before an earlier backup is written. Run with a real Python and disposable TEMP.
Do not create aliases inside a real installation or real backups as a test.

Public text is sanitized/whitespace-normalized; original private hashes identify
retained raw evidence. This folder does not claim filesystem locks or atomic sync.
