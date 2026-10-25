"""Exercise all selected payloads through real installer CLIs in new fixtures.

Run from repository root: python <this-file> --repo . --output .loop/new-replay
No model calls or native host discovery. Output must be a new directory in .loop.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def digest(data):
    return hashlib.sha256(data).hexdigest()


def run(repo, output):
    if not output.is_relative_to(repo / '.loop') or output == repo / '.loop':
        raise ValueError('output must be a new child directory of repository .loop')
    manifest = json.loads((repo / 'skills-manifest.json').read_text())
    resources = json.loads((repo / 'skill-resources.json').read_text())['resources']
    # Independent inventory: do not call the installer's payload enumeration.
    expected = {}
    for name in manifest['skills']:
        files = ['SKILL.md', *resources.get(name, [])]
        if name in ('loop-prompt', 'loop-orchestrate'):
            files.append('scripts/run_loop.py')
        for relative in files:
            expected[name + '/' + relative] = (repo / '.github/skills' / name / relative).read_bytes()
    output.mkdir(parents=True, exist_ok=False)
    rows = []
    for layout in manifest['project_skill_roots']:
        case = output / layout.split('/')[0].lstrip('.')
        target = case / layout
        original = {name: ('Original customization: ' + name + '\n').encode() for name in expected}
        for name, data in original.items():
            path = target / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        custom = target / manifest['skills'][0] / 'personal-note.txt'
        unrelated = target / 'unrelated-fixture/SKILL.md'
        custom.write_bytes(b'custom preserved\n')
        unrelated.parent.mkdir()
        unrelated.write_bytes(b'unrelated preserved\n')
        backup = case / 'backup'
        selection = [item for name in manifest['skills'] for item in ('--skill', name)]
        install = [sys.executable, str(repo / 'scripts/install_skills.py'),
                   *selection, '--target', str(target), '--backup', str(backup)]
        doctor = [sys.executable, str(repo / 'scripts/doctor_skills.py'),
                  '--all', '--target', str(target)]

        def command(label, argv, wanted):
            result = subprocess.run(argv, cwd=case, capture_output=True, timeout=60)
            (case / (label + '.log')).write_bytes(result.stdout + result.stderr)
            if result.returncode != wanted:
                raise AssertionError((layout, label, result.returncode, wanted))
            return result

        command('before-check', install + ['--check'], 1)
        before = json.loads(command('before-doctor', doctor, 1).stdout)
        assert before['counts']['DRIFTED'] == len(manifest['skills'])
        command('install', install, 0)
        assert all((target / name).read_bytes() == data for name, data in expected.items())
        assert all((backup / name).read_bytes() == data for name, data in original.items())
        command('after-check', install + ['--check'], 0)
        after = json.loads(command('after-doctor', doctor, 0).stdout)
        assert after['counts']['CURRENT'] == len(manifest['skills'])
        no_op_backup = case / 'no-op-backup'
        command('idempotent', install[:-1] + [str(no_op_backup)], 0)
        assert not no_op_backup.exists()
        assert custom.read_bytes() == b'custom preserved\n'
        assert unrelated.read_bytes() == b'unrelated preserved\n'
        rows.append({'layout': layout, 'selected_skills': len(manifest['skills']),
                     'payloads': len(expected), 'before_drift_detected': True,
                     'all_installed_bytes_match': True, 'all_backups_exact': True,
                     'custom_and_unrelated_preserved': True, 'idempotent_no_backup': True})
    assert all((repo / '.github/skills' / name).read_bytes() == data for name, data in expected.items())
    report = {'observed_at': datetime.now(timezone.utc).isoformat(), 'status': 'PASS',
              'scope': 'Forced-drift all-skill CLI installation and backup checks in three new fixtures.',
              'source_payload_sha256': {name: digest(data) for name, data in expected.items()},
              'results': rows, 'native_discovery': 'NOT_RUN', 'model_runtime': 'NOT_RUN'}
    (output / 'results.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run(args.repo.resolve(), args.output.resolve())
    print(json.dumps({'status': result['status'], 'results': result['results']}))
