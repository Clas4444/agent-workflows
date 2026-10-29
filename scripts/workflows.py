#!/usr/bin/env python3
"""Render/check role guidance against the current skill inventory; no model calls."""
import argparse
from html import escape
from pathlib import Path
import re
import textwrap

if __package__:
    from .validation.json_data import loads_json
    from .bundle_docs import check_bundle_guide
    from .bundle_workflows import check as check_bundle_workflows
else:
    from validation.json_data import loads_json
    from bundle_docs import check_bundle_guide
    from bundle_workflows import check as check_bundle_workflows

GUIDE = 'docs/guides/role-workflows.md'
IMAGE = 'docs/assets/skill-stacks.svg'


def load_presets(repo: Path):
    names = loads_json((repo/'skills-manifest.json').read_text(encoding='utf-8'))['skills']
    data = loads_json((repo/'workflow-presets.json').read_text(encoding='utf-8'))
    if not isinstance(data, dict) or type(data.get('version')) is not int or data['version'] != 1:
        raise ValueError('unsupported workflow preset version')
    profiles = data.get('profiles')
    if not isinstance(profiles, list) or not profiles:
        raise ValueError('workflow profiles must be a non-empty list')
    ids = set()
    for row in profiles:
        if not isinstance(row, dict):
            raise ValueError('workflow profile must be an object')
        key = row.get('id')
        if not isinstance(key, str) or not re.fullmatch(r'[a-z][a-z0-9-]*', key) or key in ids:
            raise ValueError('workflow profile IDs must be unique slugs')
        ids.add(key)
        for field in ('title', 'goal'):
            if not isinstance(row.get(field), str) or not row[field].strip() or '\n' in row[field]:
                raise ValueError(f'{key}: {field} must be a non-empty single line')
        for field in ('core', 'optional', 'do', 'dont'):
            values = row.get(field)
            if not isinstance(values, list) or (field != 'optional' and not values):
                raise ValueError(f'{key}: invalid {field} list')
            if any(not isinstance(v, str) or not v.strip() or '\n' in v for v in values):
                raise ValueError(f'{key}: invalid {field} value')
            if len(set(values)) != len(values):
                raise ValueError(f'{key}: duplicate {field} value')
        if any(name not in names for name in row['core']+row['optional']):
            raise ValueError(f'{key}: unknown skill')
        if set(row['core']) & set(row['optional']):
            raise ValueError(f'{key}: core and optional skills overlap')
    return profiles


def markdown(profiles):
    lines = ['# Choose skills for your work', '',
             '<!-- Generated from workflow-presets.json by scripts/workflows.py. -->', '',
             'These are small recommended toolkits, not mandatory sequences. Install or invoke',
             'only what the task needs. A skill provides instructions; it does not enforce a sandbox.', '',
             'See [practical English prompts](workflow-examples.md) for concrete role-specific requests.', '',
             'For non-coding work, see [everyday examples](everyday-work.md) and [install by need](install-by-need.md).', '',
             'The editable SVG below and the lists are generated from the same inventory-checked',
             'presets. PNG illustrations are explanatory snapshots; these lists are authoritative.', '',
             '![Recommended skill stacks](../assets/skill-stacks.svg)', '']
    for row in profiles:
        lines += [f"## {row['title']}", '', row['goal'], '',
                  '**Core toolkit:** '+', '.join(f'`{n}`' for n in row['core'])+'.', '',
                  '**Add when needed:** '+(', '.join(f'`{n}`' for n in row['optional']) or 'None')+'.', '',
                  '**Do**', '']
        lines += ['- '+value for value in row['do']]
        lines += ['', '**Do not**', '']+['- '+value for value in row['dont']]+['']
    lines += ['## Software workflow illustrations', '',
              'These developer/project examples are optional for software work. Everyday tasks do not need a coding lifecycle.', '',
              '![Developer workflow](../assets/developer-workflow.png)', '',
              '![Project workflows](../assets/project-workflows.png)', '',
              '## Evidence and invocation', '',
              'PASS means the named check actually met its criterion. FAIL means an observed',
              'violation. BLOCKED means a prerequisite prevented execution. NOT_RUN means the',
              'check was not executed. Unit-test PASS does not establish host discovery, live',
              'service recovery, remote CI approval or production readiness.', '',
              'Use the syntax supported by your host (for example `$loop-test` in Codex).',
              'Start a new session after installation and ask the host which skills it sees.',
              'Reusing existing authorization is appropriate; skill text does not grant new',
              'permission to publish, deploy, send messages or change production data.', '',
              'See [testing](../testing/procedure.md), [runtime evidence](../reference/runtime-test-matrix.md)',
              'and [installation compatibility](../reference/compatibility.md).', '']
    return '\n'.join(lines)


def svg(profiles):
    rows = []
    y = 110
    for row in profiles:
        title_lines = textwrap.wrap(row['title'], width=72)
        content = [('Core: '+', '.join(row['core']), '#18324f'),
                   ('Optional: '+(', '.join(row['optional']) or 'none'), '#385d85'),
                   ('DO: '+row['do'][0], '#126246'), ('DO NOT: '+row['dont'][0], '#9c2941')]
        lines = [(line, color) for value, color in content
                 for line in textwrap.wrap(value, width=105)]
        card_height = max(225, 42+len(title_lines)*32+len(lines)*24)
        rows.append((y, card_height, title_lines, lines))
        y += card_height+15
    height = y+5
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="{height}" viewBox="0 0 1200 {height}" role="img" aria-labelledby="title desc">',
             '<title id="title">Recommended Loop skill toolkits</title>',
             '<desc id="desc">Role-specific recommendations. Skills are optional instructions, not a sandbox.</desc>',
             '<rect width="1200" height="100%" fill="#f4f8fc"/>',
             '<g font-family="Arial, sans-serif" fill="#18324f">',
             '<text x="35" y="48" font-size="30" font-weight="bold">Choose a focused toolkit for your work</text>',
             '<text x="35" y="83" font-size="19">Recommendations, not mandatory sequences. Run only the skills your task needs.</text>']
    for y, card_height, title_lines, lines in rows:
        parts.append(f'<rect x="25" y="{y}" width="1150" height="{card_height}" rx="15" fill="white" stroke="#c4d9ed"/>')
        offset = 34
        for line in title_lines:
            parts.append(f'<text x="45" y="{y+offset}" font-size="25" font-weight="bold">{escape(line)}</text>')
            offset += 32
        for line, color in lines:
            parts.append(f'<text x="45" y="{y+offset}" font-size="18" fill="{color}">{escape(line)}</text>')
            offset += 24
    parts += ['</g>', '</svg>', '']
    return '\n'.join(parts)


def outputs(repo):
    profiles = load_presets(repo)
    return {GUIDE: markdown(profiles), IMAGE: svg(profiles)}


def check_workflows(repo):
    try:
        expected = outputs(repo)
        errors = [f'{name} is missing or stale; run scripts/workflows.py --write'
                for name, content in expected.items()
                if not (repo/name).is_file() or (repo/name).read_text(encoding='utf-8') != content]
        if (repo/'skill-bundles.json').is_file():
            errors.extend(check_bundle_guide(repo))
            errors.extend(check_bundle_workflows(repo))
        return errors
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return [f'invalid workflow presets: {exc}']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    repo = args.repo.resolve()
    if args.write:
        try:
            expected = outputs(repo)  # Validate everything before writing any output.
            for name, content in expected.items():
                path = repo/name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding='utf-8')
        except (OSError, ValueError, KeyError, TypeError) as exc:
            parser.exit(1, f'FAIL: {exc}\n')
    errors = check_workflows(repo)
    print('\n'.join(errors) if errors else 'PASS: role workflow guides and SVG')
    return int(bool(errors))


if __name__ == '__main__':
    raise SystemExit(main())
