#!/usr/bin/env python3
"""Grade offline MCP skill artifacts; not a protocol conformance test."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def grade(folder: Path) -> dict[str, bool]:
    hashes = json.loads((folder/'input-hashes.json').read_text(encoding='utf-8'))
    checks = {'inputs_preserved': all((folder/name).is_file() and
              hashlib.sha256((folder/name).read_bytes()).hexdigest() == value
              for name, value in hashes.items())}
    design = (folder/'design.md').read_text(encoding='utf-8').lower()
    security = (folder/'security.md').read_text(encoding='utf-8').lower()
    checks['design_scope'] = all(term in design for term in ('2026-07-28', 'schema', 'not_run'))
    checks['security_scope'] = all(term in security for term in ('injection', 'readonlyhint', 'authorization', 'not_run'))
    script = (folder/'check_cases.py').resolve()
    expected = {'valid-positive': 'PASS', 'valid-negative': 'PASS', 'wrong-id': 'FAIL',
                'wrong-type': 'FAIL', 'bool-not-int': 'FAIL', 'wrong-sum': 'FAIL'}
    # Fresh directories preserve failed attempts and detect scorer prerequisites.
    number = 1
    while (folder/f'independent-{number}').exists():
        number += 1
    probe = folder/f'independent-{number}'
    probe.mkdir()
    for label, varied in (('nominal', False), ('varied', True)):
        data = json.loads((folder/'cases.json').read_text(encoding='utf-8'))
        oracle = dict(expected)
        if varied:
            by_name = {case['case_id']: case for case in data['cases']}
            by_name['valid-positive']['response']['id'] = 'unexpected'
            oracle['valid-positive'] = 'FAIL'
            by_name['wrong-type']['request']['params']['arguments']['a'] = 2
            oracle['wrong-type'] = 'PASS'
            by_name['valid-negative']['request']['params']['arguments'] = {'a': -8, 'b': 3}
            by_name['valid-negative']['response']['result']['structuredContent']['sum'] = -5
            by_name['valid-negative']['request']['id'] = 'changed'
            by_name['valid-negative']['response']['id'] = 'changed'
        source, output = probe/(label+'.json'), probe/(label+'-result.json')
        source.write_text(json.dumps(data), encoding='utf-8')
        run = subprocess.run([sys.executable, str(script), '--cases', str(source.resolve()),
                              '--output', str(output.resolve())], cwd=probe, capture_output=True,
                             text=True, timeout=15)
        (probe/(label+'.log')).write_text(run.stdout+run.stderr, encoding='utf-8')
        checks[label+'_computed_results'] = run.returncode == 0 and output.is_file() and json.loads(output.read_text(encoding='utf-8')) == oracle
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fixture', type=Path, required=True)
    args = parser.parse_args()
    try:
        checks = grade(args.fixture.resolve())
    except (OSError, ValueError, KeyError, TypeError, subprocess.TimeoutExpired) as exc:
        print(json.dumps({'status': 'FAIL', 'reason': str(exc)}))
        return 1
    result = {'status': 'PASS' if all(checks.values()) else 'FAIL', 'checks': checks,
              'scope': 'Offline synthetic tool-acceptance subset only; live MCP transport/auth/discovery NOT_RUN.'}
    print(json.dumps(result))
    return int(not all(checks.values()))


if __name__ == '__main__':
    raise SystemExit(main())
