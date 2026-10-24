#!/usr/bin/env python3
"""Check curated routing coverage or grade supplied predictions; no model calls."""
import argparse
from collections import Counter
import json
from pathlib import Path


def load_routes(repo: Path):
    names = json.loads((repo/'skills-manifest.json').read_text(encoding='utf-8'))['skills']
    data = json.loads((repo/'skill-routing.json').read_text(encoding='utf-8'))
    decisions = data['decisions']
    if Counter(row['skill'] for row in decisions) != Counter(names):
        raise ValueError('routing decisions must cover every skill exactly once')
    if any(row['action'] not in ('keep', 'upgrade', 'add') or not isinstance(row['reason'], str)
           or not row['reason'].strip() for row in decisions):
        raise ValueError('routing decisions require a known action and reason')
    cases = data['cases']
    ids = [row['id'] for row in cases]
    if not ids or any(not isinstance(value, str) or not value for value in ids) or len(ids) != len(set(ids)):
        raise ValueError('routing case IDs must be non-empty and unique')
    covered = set()
    for row in cases:
        allowed = row['acceptable']
        if (not isinstance(row['prompt'], str) or not row['prompt'].strip()
                or not isinstance(allowed, list) or not allowed
                or any(not isinstance(name, str) or name not in names+['NONE'] for name in allowed)
                or len(allowed) != len(set(allowed))):
            raise ValueError('routing case requires a prompt and known acceptable routes')
        covered.update(allowed)
    if not set(names+['NONE']).issubset(covered):
        raise ValueError('routing cases must cover every skill and a no-skill control')
    for row in data['overlap_decisions']:
        related = row['skills']
        if (not isinstance(related, list) or len(related) < 2
                or any(name not in names for name in related)
                or len(related) != len(set(related)) or not row['decision'].strip()):
            raise ValueError('overlap decisions require distinct known skills and rationale')
    return data


def check_routes(repo: Path) -> list[str]:
    try:
        load_routes(repo)
        return []
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        return [f'invalid routing review: {exc}']


def grade_predictions(data, predictions):
    expected = {row['id']: row for row in data['cases']}
    if not isinstance(predictions, dict) or set(predictions) != set(expected):
        raise ValueError('predictions must cover exactly the fixed case IDs')
    failed = [key for key, row in expected.items() if predictions[key] not in row['acceptable']]
    return {'status': 'FAIL' if failed else 'PASS', 'total': len(expected),
            'correct': len(expected)-len(failed), 'failed_case_ids': failed,
            'scope': 'Curated route classification only, not host discovery or skill execution.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--predictions', type=Path)
    args = parser.parse_args()
    try:
        data = load_routes(args.repo.resolve())
        if args.predictions:
            result = grade_predictions(data, json.loads(args.predictions.read_text(encoding='utf-8')))
            print(json.dumps(result))
            return int(result['status'] != 'PASS')
    except (OSError, ValueError, KeyError, TypeError, AttributeError) as exc:
        parser.exit(1, f'FAIL: {exc}\n')
    print('PASS: curated routing coverage')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
