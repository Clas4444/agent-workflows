#!/usr/bin/env python3
"""Portable read-only lookup for canonical skill names and full bundle selectors."""
import argparse
import json
from pathlib import Path
import re


def normalize(query):
    if not isinstance(query, str) or any(ord(c) < 32 and c not in '\t\n\r' for c in query):
        raise ValueError('query must be ordinary text')
    return ' '.join(query.strip().lstrip('/$').casefold().split())


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError('duplicate catalog key: ' + key)
        result[key] = value
    return result


def validate_catalog(data):
    if not isinstance(data, dict) or type(data.get('version')) is not int or data['version'] != 1:
        raise ValueError('unsupported catalog version')
    skills, bundles = data.get('skills'), data.get('bundles')
    if not isinstance(skills, dict) or not skills or not isinstance(bundles, dict) or not bundles:
        raise ValueError('catalog needs nonempty skills and bundles')
    aliases = {}
    for name, row in skills.items():
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', name) or not isinstance(row, dict):
            raise ValueError('invalid skill catalog entry')
        if not isinstance(row.get('description'), str) or not row['description'].strip():
            raise ValueError('skill description required')
        values = row.get('aliases')
        terms = row.get('search_terms', [])
        if (not isinstance(terms, list) or any(not isinstance(term, str)
                or not re.fullmatch(r'[a-z0-9]+', term) for term in terms)):
            raise ValueError('invalid search terms')
        if not isinstance(values, list):
            raise ValueError('skill aliases must be a list')
        for alias in [name, *values]:
            if (not isinstance(alias, str) or not re.fullmatch(r'[a-z0-9]+(?:[ -][a-z0-9]+)*', alias)
                    or alias.startswith(('bundle ', 'b '))):
                raise ValueError('invalid or reserved alias')
            if alias in aliases:
                raise ValueError('colliding alias: ' + alias)
            aliases[alias] = name
    for key, row in bundles.items():
        if not re.fullmatch(r'[a-z][a-z0-9-]*', key) or not isinstance(row, dict):
            raise ValueError('invalid bundle ID')
        names = row.get('skills')
        if (not isinstance(names, list) or not names or any(not isinstance(n, str) or n not in skills for n in names)
                or len(set(names)) != len(names) or not isinstance(row.get('purpose'), str) or not row['purpose'].strip()):
            raise ValueError('bundle requires unique known skills and purpose')
    return data


def load_catalog(path):
    return validate_catalog(json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=unique_object,
                                      parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value))))


def resolve(data, query):
    query = normalize(query)
    for prefix in ('bundle ',):
        if query.startswith(prefix):
            key = query[len(prefix):]
            if key not in data['bundles']:
                raise ValueError('unknown bundle; search or list bundles first')
            return {'kind': 'bundle', 'id': key, 'skills': data['bundles'][key]['skills'], 'execution': 'NONE'}
    for name, row in data['skills'].items():
        if query == name:
            return {'kind': 'skill', 'id': name, 'skills': [name], 'execution': 'NONE'}
    raise ValueError('unknown selector; use an exact canonical name or full bundle selector, or search first')


def search(data, query):
    query = normalize(query)
    if not query:
        return []
    tokens = query.replace('-', ' ').split()
    rows = []
    for kind, entries in (('skill', data['skills']), ('bundle', data['bundles'])):
        for key, row in entries.items():
            text = ' '.join([kind, key, *row.get('search_terms', []), row.get('description', row.get('purpose', ''))]).casefold().replace('-', ' ')
            words = re.findall(r'[a-z0-9]+', text)
            if all(token in words or (len(token) >= 4 and any(word.startswith(token) for word in words)) for token in tokens):
                rows.append({'kind': kind, 'id': key, 'description': row.get('description', row.get('purpose'))})
    return rows


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode', choices=('resolve', 'search', 'bundles'))
    parser.add_argument('--query', default='')
    parser.add_argument('--catalog', type=Path, default=Path(__file__).resolve().parents[1]/'assets/catalog.json')
    parser.add_argument('--skills-root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    try:
        data = load_catalog(args.catalog)
        if args.mode == 'resolve':
            result = resolve(data, args.query)
            result['missing_skills'] = [name for name in result['skills'] if not (args.skills_root/name/'SKILL.md').is_file()]
            result['instructions'] = [str(args.skills_root/name/'SKILL.md') for name in result['skills']]
            result['native_discovery'] = 'NOT_RUN'
        elif args.mode == 'search':
            result = {'matches': search(data, args.query), 'execution': 'NONE', 'native_discovery': 'NOT_RUN'}
        else:
            result = {'bundles': data['bundles'], 'execution': 'NONE'}
        print(json.dumps(result, indent=2, ensure_ascii=True))
        return 0
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, 'FAIL: ' + str(error) + '\n')


if __name__ == '__main__':
    raise SystemExit(main())
