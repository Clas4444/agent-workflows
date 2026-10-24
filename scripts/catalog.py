#!/usr/bin/env python3
"""Maintain the grouped README catalog without moving native skill folders."""
import argparse
from collections import Counter
import json
import re
from pathlib import Path

if __package__:
    from .validation.skill_format import FRONTMATTER_PATTERN, frontmatter_value
else:
    from validation.skill_format import FRONTMATTER_PATTERN, frontmatter_value

START = '<!-- BEGIN GENERATED SKILL GROUPS -->'
END = '<!-- END GENERATED SKILL GROUPS -->'


def render(repo: Path) -> str:
    manifest = json.loads((repo/'skills-manifest.json').read_text(encoding='utf-8'))
    groups = json.loads((repo/'skill-groups.json').read_text(encoding='utf-8'))
    if not isinstance(groups, dict) or not groups:
        raise ValueError('skill groups must be a non-empty object')
    names = []
    lines = [START, '', 'Groups are navigation metadata; native skill directories remain flat.', '']
    for key, group in groups.items():
        if (not isinstance(group, dict) or not isinstance(group.get('title'), str)
                or not group['title'].strip() or '\n' in group['title']
                or not isinstance(group.get('skills'), list) or not group['skills']
                or not all(isinstance(name, str) and name in manifest['skills'] for name in group['skills'])):
            raise ValueError(f'invalid or unknown skill in group {key}')
        names.extend(group['skills'])
        lines += [f"### {group['title']}", '', '| Skill | Purpose |', '|---|---|']
        for name in group['skills']:
            path = repo/'.github/skills'/name/'SKILL.md'
            match = FRONTMATTER_PATTERN.match(path.read_text(encoding='utf-8'))
            description = frontmatter_value(match.group(1), 'description') if match else None
            if not description:
                raise ValueError(f'missing description for {name}')
            purpose = description.split('. ')[0].rstrip('.').replace('|', '\\|')
            lines.append(f'| [{name}](.github/skills/{name}/SKILL.md) | {purpose} |')
        lines.append('')
    if Counter(names) != Counter(manifest['skills']):
        raise ValueError('groups must cover every manifest skill exactly once')
    return '\n'.join(lines + [END])


def check_catalog(repo: Path) -> list[str]:
    try:
        expected = render(repo)
        text = (repo/'README.md').read_text(encoding='utf-8')
        manifest = json.loads((repo/'skills-manifest.json').read_text(encoding='utf-8'))
        count = re.search(r'\*\*([0-9]+) bounded workflows', text)
        if not count or int(count.group(1)) != len(manifest['skills']):
            return ['README advertised skill count does not match manifest']
        if text.count(START) != 1 or text.count(END) != 1:
            return ['README requires one generated skill catalog block']
        if text.index(START) >= text.index(END):
            return ['README skill catalog boundaries are out of order']
        actual = text[text.index(START):text.index(END)+len(END)]
        return [] if actual == expected else ['README grouped skill catalog is stale; run scripts/catalog.py --write']
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f'invalid grouped skill catalog: {exc}']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    repo = args.repo.resolve()
    if args.write:
        try:
            block = render(repo)
            path = repo/'README.md'
            text = path.read_text(encoding='utf-8')
            if text.count(START) != 1 or text.count(END) != 1 or text.index(START) >= text.index(END):
                raise ValueError('refusing to replace ambiguous README catalog boundaries')
            path.write_text(text[:text.index(START)]+block+text[text.index(END)+len(END):], encoding='utf-8')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            parser.exit(1, f'FAIL: {exc}\n')
    errors = check_catalog(repo)
    print('\n'.join(errors) if errors else 'PASS: grouped catalog')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
