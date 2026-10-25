"""Validate need-based installation selections without changing destinations."""
from pathlib import Path
import re

if __package__:
    from .validation.json_data import loads_json
else:
    from validation.json_data import loads_json


def load_bundles(repo: Path):
    manifest = loads_json((repo/'skills-manifest.json').read_text(encoding='utf-8'))
    names = manifest['skills']
    data = loads_json((repo/'skill-bundles.json').read_text(encoding='utf-8'))
    if not isinstance(data, dict) or type(data.get('version')) is not int or data['version'] != 1:
        raise ValueError('unsupported skill bundle version')
    bundles = data.get('bundles')
    if not isinstance(bundles, dict) or not bundles:
        raise ValueError('bundles must be a non-empty object')
    for key, row in bundles.items():
        if not re.fullmatch(r'[a-z][a-z0-9-]*', key) or not isinstance(row, dict):
            raise ValueError('bundle IDs must be slugs with object values')
        if not isinstance(row.get('purpose'), str) or not row['purpose'].strip():
            raise ValueError(f'{key}: bundle purpose is required')
        skills = row.get('skills')
        if (not isinstance(skills, list) or not skills
                or any(not isinstance(n, str) or n not in names for n in skills)
                or len(set(skills)) != len(skills)):
            raise ValueError(f'{key}: bundle requires unique known skill names')
    return bundles


def select_skills(repo, bundle_ids, extra_skills):
    bundles = load_bundles(repo)
    names = loads_json((repo/'skills-manifest.json').read_text(encoding='utf-8'))['skills']
    chosen = set()
    for key in bundle_ids:
        if key not in bundles:
            raise ValueError(f'unknown bundle: {key}')
        chosen.update(bundles[key]['skills'])
    for name in extra_skills:
        if name not in names:
            raise ValueError(f'unknown skill: {name}')
        chosen.add(name)
    if not chosen:
        raise ValueError('select at least one --bundle or --skill')
    return [name for name in names if name in chosen]
