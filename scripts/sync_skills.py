#!/usr/bin/env python3
"""Synchronize an explicitly selected skill root, preserving overwritten files."""
import argparse
import json
import re
import shutil
import stat
from datetime import datetime, timezone
from pathlib import Path

if __package__:
    from .validation.json_data import loads_json
    from .skill_resources import load_resources, payload_files
else:
    from validation.json_data import loads_json
    from skill_resources import load_resources, payload_files

REPO = Path(__file__).resolve().parents[1]


def reject_destination_aliases(destination: Path, target: Path) -> None:
    for component in (destination, *destination.parents):
        if component == target:
            break
        try:
            metadata = component.lstat()
        except FileNotFoundError:
            continue
        # Windows junctions are reparse points, but are not is_symlink() on
        # Python 3.11. Inspect attributes as well as POSIX symlink mode.
        reparse = getattr(metadata, 'st_file_attributes', 0) & getattr(stat, 'FILE_ATTRIBUTE_REPARSE_POINT', 0)
        if stat.S_ISLNK(metadata.st_mode) or reparse:
            raise ValueError(f'symlink/reparse destination alias is not supported: {component}')


def sync(target: Path, backup: Path, check: bool = False, *, selected: list[str] | None = None) -> list[str]:
    manifest = loads_json((REPO / 'skills-manifest.json').read_text(encoding='utf-8'))
    names = manifest.get('skills') if isinstance(manifest, dict) else None
    if (not isinstance(names, list) or not names
            or any(not isinstance(name, str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name)
                   or len(name) > 64 for name in names)
            or len(names) != len(set(names))):
        raise ValueError('manifest skills must be unique, valid skill names')
    resources = load_resources(REPO,names)
    if selected is not None:
        if (not isinstance(selected, list) or not selected
                or any(not isinstance(name, str) or name not in names for name in selected)
                or len(selected) != len(set(selected))):
            raise ValueError('selected skills must be a non-empty list of unique manifest names')
        names = [name for name in names if name in selected]
    target, backup = target.resolve(), backup.resolve()
    if backup == target or target in backup.parents:
        raise ValueError('backup must be outside target')
    differences = []
    plan = []
    for name in names:
        files = [(original,target/name/relative) for relative,original in payload_files(REPO,name,resources)]
        for original, destination in files:
            if not original.is_file():
                raise ValueError(f'missing source file: {original}')
            if not destination.resolve().is_relative_to(target):
                raise ValueError(f'destination escapes target: {destination}')
            reject_destination_aliases(destination, target)
            if destination.exists() and not destination.is_file():
                raise ValueError(f'destination is not a file: {destination}')
            # copy2 overwrites the existing inode. A second hardlink may live
            # outside the selected root even when resolve() stays inside it.
            # Reject in preflight (including check mode), before any backups or
            # writes, rather than silently modifying an unrelated alias.
            if destination.is_file() and destination.stat().st_nlink > 1:
                raise ValueError(f'hardlinked destination is not supported: {destination}')
            for parent in destination.parents:
                if parent.exists() and not parent.is_dir():
                    raise ValueError(f'destination parent is not a directory: {parent}')
            if destination.is_file() and destination.read_bytes() == original.read_bytes():
                continue
            differences.append(str(destination))
            saved = backup / destination.relative_to(target)
            if not saved.resolve().is_relative_to(backup):
                raise ValueError(f'backup escapes backup root: {saved}')
            # Missing backup files can still share an inode later through an
            # internal directory alias. Reject aliases before planning either
            # backup; otherwise a later save can overwrite an earlier original.
            for parent in saved.parents:
                if parent.exists() and not parent.is_dir():
                    raise ValueError(f'backup parent is not a directory: {parent}')
            reject_destination_aliases(saved, backup)
            if saved.exists() and not saved.is_file():
                raise ValueError(f'backup destination is not a file: {saved}')
            if destination.exists() and saved.exists() and not check:
                raise ValueError(f'backup already exists: {saved}')
            plan.append((original, destination, saved))
    if check:
        return differences
    # Complete preflight before touching any destination, then back up every
    # overwrite before beginning to copy source files.
    for original, destination, saved in plan:
        if destination.exists():
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(destination, saved)
    for original, destination, saved in plan:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, destination)
    return differences


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--target', type=Path, required=True)
    parser.add_argument('--backup', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    backup = args.backup or REPO / '.loop' / 'backups' / datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
    try:
        differences = sync(args.target, backup, args.check)
    except (OSError, ValueError) as exc:
        parser.exit(1, f'FAIL: {exc}\n')
    print(json.dumps({'target': str(args.target), 'check': args.check,
                      'differences': differences, 'backup': str(backup)}, indent=2))
    return int(args.check and bool(differences))


if __name__ == '__main__':
    raise SystemExit(main())
