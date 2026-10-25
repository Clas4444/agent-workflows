#!/usr/bin/env python3
"""Reproduce contract violations in fresh fixtures, without model/network calls."""
import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--output-dir', type=Path, required=True)
    parser.add_argument('--expect', choices=('fixed', 'vulnerable'), default='fixed')
    args = parser.parse_args()
    repo, output = args.repo.resolve(), args.output_dir.resolve()
    try:
        output.mkdir(parents=True, exist_ok=False)
    except OSError as exc:
        parser.error(str(exc))
    roots = ['.github/skills', '.agents/skills', '.claude/skills']
    text = (repo/roots[0]/'loop-review/SKILL.md').read_text(encoding='utf-8')
    description = next(line for line in text.splitlines() if line.startswith('description:'))
    rows = []
    for name, value, version in (
        ('description-list', '[]', '1.0.0'),
        ('description-null', 'null', '1.0.0'),
        ('description-bool', 'false', '1.0.0'),
        ('description-unclosed', '"unfinished', '1.0.0'),
        ('unicode-version', None, '\u0661.\u0662.\u0663'),
        ('valid-control', None, '1.0.0'),
    ):
        folder = output/name
        for native in roots:
            path = folder/native/'loop-review/SKILL.md'
            path.parent.mkdir(parents=True)
            path.write_text(text if value is None else text.replace(description, 'description: '+value), encoding='utf-8')
        (folder/'skills-manifest.json').write_text(json.dumps({
            'version': version, 'skills': ['loop-review'], 'project_skill_roots': roots}), encoding='utf-8')
        for profile in ('loop', 'format'):
            result = subprocess.run([sys.executable, str(repo/'scripts/validate.py'),
                                     '--repo', str(folder), '--profile', profile],
                                    capture_output=True, text=True, timeout=30)
            rows.append({'case': name, 'profile': profile, 'exit_code': result.returncode,
                         'stdout': result.stdout.strip(), 'stderr': result.stderr.strip()})
    folder = output/'hardlink-sync'
    (folder/'scripts').mkdir(parents=True)
    shutil.copy2(repo/'scripts/sync_skills.py', folder/'scripts/sync_skills.py')
    resources=repo/'scripts/skill_resources.py'
    if resources.is_file():
        shutil.copy2(resources,folder/'scripts/skill_resources.py')
    # Newer sync readers share strict JSON parsing; old snapshot scripts remain
    # supported when they do not have this module.
    helper=repo/'scripts/validation/json_data.py'
    if helper.is_file():
        (folder/'scripts/validation').mkdir()
        shutil.copy2(helper,folder/'scripts/validation/json_data.py')
        shutil.copy2(repo/'scripts/validation/__init__.py',folder/'scripts/validation/__init__.py')
    source = folder/'.github/skills/loop-review/SKILL.md'
    source.parent.mkdir(parents=True)
    source.write_text(text, encoding='utf-8')
    (folder/'skills-manifest.json').write_text(json.dumps({
        'version': '1.0.0', 'skills': ['loop-review'], 'project_skill_roots': roots}), encoding='utf-8')
    target = folder/'installed'
    destination = target/'loop-review/SKILL.md'
    destination.parent.mkdir(parents=True)
    external = folder/'outside-target.txt'
    original = b'unrelated retained data\n'
    external.write_bytes(original)
    proof = {}
    try:
        os.link(external, destination)
    except OSError as exc:
        proof = {'status': 'BLOCKED', 'reason': str(exc)}
    else:
        proof['link_count'] = destination.stat().st_nlink
        for label, flags in (('sync', []), ('check', ['--check'])):
            result = subprocess.run([sys.executable, str(folder/'scripts/sync_skills.py'),
                                     '--target', str(target), '--backup', str(folder/'backup'), *flags],
                                    capture_output=True, text=True, timeout=30)
            proof[label] = {'exit_code': result.returncode, 'hardlink_rejected': 'hardlink' in result.stderr}
        proof['outside_target_modified'] = external.read_bytes() != original
        proof['backup_created'] = (folder/'backup').exists()
        proof['status'] = 'EXECUTED'
    matched = all(row['exit_code'] == (0 if args.expect == 'vulnerable' or row['case'] == 'valid-control' else 1)
                  for row in rows)
    matched = matched and proof['status'] == 'EXECUTED'
    if proof['status'] == 'EXECUTED':
        expected_code = 0 if args.expect == 'vulnerable' else 1
        matched = matched and all(proof[label]['exit_code'] == expected_code for label in ('sync', 'check'))
        matched = matched and proof['outside_target_modified'] == (args.expect == 'vulnerable')
        if args.expect == 'fixed':
            matched = matched and not proof['backup_created'] and all(proof[label]['hardlink_rejected'] for label in ('sync', 'check'))
    result = {'expectation': args.expect, 'expectation_matched': matched,
              'validator_results': rows, 'hardlink': proof,
              'source_hashes': {name: hashlib.sha256((repo/name).read_bytes()).hexdigest()
                                for name in ('scripts/validate.py', 'scripts/validation/skill_format.py',
                                             'scripts/validation/manifest.py', 'scripts/sync_skills.py')
                                + (('scripts/validation/json_data.py',) if helper.is_file() else ())}}
    (output/'results.json').write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({'expectation': args.expect, 'expectation_matched': matched,
                      'validator_invocations': len(rows), 'hardlink': proof}))
    return 0 if matched else 1


if __name__ == '__main__':
    raise SystemExit(main())
