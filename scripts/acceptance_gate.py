#!/usr/bin/env python3
"""Run an explicitly authorized acceptance contract; dry-run by default.

This is an opt-in subprocess gate, not a sandbox or an agent-quality evaluator.
No shell, model calls, package installation, or command discovery is performed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys
from datetime import datetime, timezone

if __package__:
    from .validation.json_data import loads_json,unique_object
else:
    from validation.json_data import loads_json,unique_object


def confined(root: Path, value: object) -> Path:
    if not isinstance(value, str) or not value.strip() or Path(value).is_absolute():
        raise ValueError('paths must be nonempty and relative to --root')
    path = (root / value).resolve()
    if not path.is_relative_to(root):
        raise ValueError(f'path escapes root: {value}')
    return path


def require_fields(value, fields):
    if not isinstance(value, dict) or set(value) != set(fields):
        raise ValueError(f'expected exactly these fields: {fields}')


def rows(value, label):
    if not isinstance(value, list) or not value or not all(isinstance(v, dict) for v in value):
        raise ValueError(f'{label} must be a nonempty list of objects')
    return value


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_contract(data: dict, root: Path) -> None:
    require_fields(data, ('version', 'sources', 'criteria', 'checks'))
    if type(data['version']) is not int or data['version'] != 1:
        raise ValueError('version must be integer 1')
    sources = rows(data['sources'], 'sources')
    seen_sources = set()
    for source in sources:
        require_fields(source, ('path', 'sha256'))
        resolved = confined(root, source['path'])
        if resolved in seen_sources:
            raise ValueError('duplicate source')
        seen_sources.add(resolved)
        if not isinstance(source['sha256'], str) or not re.fullmatch('[0-9a-f]{64}', source['sha256']):
            raise ValueError('source sha256 must be 64 lowercase hex characters')
    checks = rows(data['checks'], 'checks')
    by_id = {}
    for check in checks:
        require_fields(check, ('id', 'kind', 'argv', 'cwd', 'timeout_seconds',
                               'expected_exit', 'stdout_contains'))
        if not nonempty(check['id']) or check['id'] in by_id:
            raise ValueError('check ids must be unique nonempty strings')
        by_id[check['id']] = check
        if not isinstance(check['kind'], str) or check['kind'] not in ('positive', 'negative'):
            raise ValueError('check kind must be positive or negative')
        if not isinstance(check['argv'], list) or not check['argv'] or not all(
                isinstance(v, str) and v and '\x00' not in v for v in check['argv']):
            raise ValueError('argv must contain nonempty strings without NUL')
        confined(root, check['cwd'])
        timeout = check['timeout_seconds']
        # Check the bounded range before float conversion: JSON integers are
        # arbitrary precision and math.isfinite(10**400) raises OverflowError.
        if type(timeout) not in (int, float) or not 0 < timeout <= 300 or not math.isfinite(timeout):
            raise ValueError('timeout_seconds must be finite and in (0, 300]')
        if type(check['expected_exit']) is not int or not 0 <= check['expected_exit'] <= 255:
            raise ValueError('expected_exit must be an integer in [0, 255]')
        if not nonempty(check['stdout_contains']):
            raise ValueError('stdout_contains must provide nonempty observable evidence')
    criteria = rows(data['criteria'], 'criteria')
    ids, used = set(), set()
    for criterion in criteria:
        require_fields(criterion, ('id', 'expectation', 'checks'))
        if not nonempty(criterion['id']) or criterion['id'] in ids or not nonempty(criterion['expectation']):
            raise ValueError('criteria need unique ids and observable expectations')
        ids.add(criterion['id'])
        names = criterion['checks']
        if not isinstance(names, list) or not names or not all(isinstance(n, str) for n in names):
            raise ValueError('criterion checks must be a nonempty list of ids')
        if len(set(names)) != len(names) or any(n not in by_id for n in names):
            raise ValueError('criterion contains duplicate or unknown check ids')
        if {by_id[n]['kind'] for n in names} != {'positive', 'negative'}:
            raise ValueError('each criterion requires positive and negative controls')
        used.update(names)
    if used != set(by_id):
        raise ValueError('every check must be mapped to a criterion')


def aggregate(statuses):
    for status in ('FAIL', 'BLOCKED', 'NOT_RUN'):
        if status in statuses:
            return status
    return 'PASS' if statuses else 'NOT_RUN'


def source_errors(data, root):
    errors = []
    for source in data['sources']:
        try:
            path = confined(root, source['path'])
            actual = hashlib.sha256(path.read_bytes()).hexdigest()
        except (OSError, ValueError):
            errors.append(f"source unavailable or outside root: {source['path']}")
            continue
        if actual != source['sha256']:
            errors.append(f"source changed: {source['path']}")
    return errors


def run_contract(data: dict, root: Path, *, execute: bool = False) -> dict:
    root = root.resolve()
    validate_contract(data, root)
    result = {
        'version': 1,
        'contract_sha256': hashlib.sha256(json.dumps(data, sort_keys=True,
                ensure_ascii=True, allow_nan=False).encode('utf-8')).hexdigest(),
        'observed_at': datetime.now(timezone.utc).isoformat(),
        'sources': data['sources'], 'checks': [], 'criteria': [],
    }
    errors = source_errors(data, root)
    for check in data['checks']:
        row = {'id': check['id'], 'status': 'NOT_RUN', 'argv': check['argv'],
               'cwd': check['cwd'], 'exit_code': None, 'stdout': '', 'stderr': ''}
        result['checks'].append(row)
        if execute and not errors:
            errors = source_errors(data, root)
        if not execute or errors:
            continue
        try:
            completed = subprocess.run(check['argv'], cwd=confined(root, check['cwd']),
                timeout=check['timeout_seconds'], capture_output=True,
                encoding='utf-8', errors='replace', shell=False)
            row.update(exit_code=completed.returncode, stdout=completed.stdout, stderr=completed.stderr)
            empty_suite = re.search(r'\b(?:Ran 0 tests|collected 0 items|no tests ran)\b',
                                    completed.stdout + '\n' + completed.stderr, re.IGNORECASE)
            passed = (completed.returncode == check['expected_exit']
                      and check['stdout_contains'] in completed.stdout and not empty_suite)
            row['status'] = 'PASS' if passed else 'FAIL'
        except subprocess.TimeoutExpired as exc:
            def decoded(value):
                return value.decode('utf-8', errors='replace') if isinstance(value, bytes) else (value or '')
            row.update(status='FAIL', reason='timeout; expected exit was not observed',
                       stdout=decoded(exc.stdout), stderr=decoded(exc.stderr))
        except OSError as exc:
            row.update(status='BLOCKED', reason=f'cannot start command: {exc}')
    # A command may itself change a referenced input. Its exit 0 does not restore freshness.
    errors = sorted(set(errors + source_errors(data, root)))
    by_id = {row['id']: row for row in result['checks']}
    for criterion in data['criteria']:
        result['criteria'].append({'id': criterion['id'], 'expectation': criterion['expectation'],
            'status': 'BLOCKED' if errors else aggregate([by_id[n]['status'] for n in criterion['checks']])})
    result['source_errors'] = errors
    result['status'] = 'BLOCKED' if errors else aggregate([r['status'] for r in result['criteria']])
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('contract', type=Path)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--execute', action='store_true', help='run commands already reviewed and authorized')
    args = parser.parse_args()
    try:
        data = loads_json(args.contract.read_text(encoding='utf-8'))
        result = run_contract(data, args.root, execute=args.execute)
    except (ValueError, OSError) as exc:
        result = {'status': 'FAIL', 'error': str(exc), 'checks': [], 'criteria': []}
    print(json.dumps(result, ensure_ascii=True, indent=2))
    return 0 if result['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
