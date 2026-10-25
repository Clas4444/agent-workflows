# Read-only file-plan helper

Use an available Python 3.11+ executable and the script inside this installed skill.
The helper only reads; native file moves are a separate authorized action. Keep
mapping, plan and result files **outside** the selected root so they do not alter
the inventory being verified.

```text
python scripts/file_plan.py inventory "/selected/folder"
python scripts/file_plan.py plan "/selected/folder" --mapping "/outside/mapping.json"
python scripts/file_plan.py check "/selected/folder" --plan "/outside/plan.json"
python scripts/file_plan.py verify "/selected/folder" --plan "/outside/plan.json"
```

Paths above are examples relative to the skill directory. `plan` prints JSON;
save that stdout as the plan using UTF-8 without including diagnostic stderr.
Exit 0 means that named check completed; exit 1 reports a violation. No command
performs a move. The final `verify` checks the expected post-move inventory.

Mapping example:

```json
{"version":1,"moves":[{"source":"A/receipt.txt","destination":"Finance/A-receipt.txt"}]}
```

Paths are root-relative and use forward slashes. Each source must be a regular
file; the destination must be absent. Overwrites, rename cycles, directory moves,
case aliases, path escapes, links/hardlinks and non-portable names are rejected.
The root token binds the plan to the selected directory. Inventory hashes bind
both moved and protected files, including unexpected additions/removals.

After a passing preflight, execute only authorized native moves and immediately
verify. A partial failure needs inspection of actual state; do not blindly replay
or roll back. For an authorized rollback, create and check a fresh inverse mapping
from the verified current state. This is not a transaction manager or a lock
against concurrent writers. Empty directory layout is not part of byte/file-count
verification; report directory checks separately when they matter.
