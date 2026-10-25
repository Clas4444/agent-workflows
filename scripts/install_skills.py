#!/usr/bin/env python3
"""Install only the selected need bundles/skills using the existing safe sync engine."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path

if __package__:
    from .skill_bundles import load_bundles, select_skills
    from .sync_skills import REPO, sync
else:
    from skill_bundles import load_bundles, select_skills
    from sync_skills import REPO, sync


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--list', action='store_true', help='List available need bundles without writing')
    parser.add_argument('--bundle', action='append', default=[], help='Need bundle; repeat to combine')
    parser.add_argument('--skill', action='append', default=[], help='Individual skill; repeat to combine')
    parser.add_argument('--target', type=Path, help='Explicit native skill directory in the selected project')
    parser.add_argument('--backup', type=Path)
    parser.add_argument('--check', action='store_true', help='Read-only comparison; exit 1 when files differ')
    args = parser.parse_args()
    try:
        if args.list:
            if args.bundle or args.skill or args.target or args.backup or args.check:
                parser.error('--list cannot be combined with installation options')
            print(json.dumps(load_bundles(REPO), indent=2))
            return 0
        if args.target is None:
            parser.error('--target is required for installation/check')
        selected = select_skills(REPO, args.bundle, args.skill)
        backup = args.backup or REPO/'.loop/backups'/datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
        differences = sync(args.target, backup, args.check, selected=selected)
        print(json.dumps({'target': str(args.target), 'selected_skills': selected,
                          'check': args.check, 'differences': differences, 'backup': str(backup)}, indent=2))
        return int(args.check and bool(differences))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, f'FAIL: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
