#!/usr/bin/env python3
"""Render/check one explanatory iteration diagram per installation bundle."""
import argparse
from html import escape
from pathlib import Path
import textwrap

if __package__:
    from .skill_bundles import load_bundles
    from .validation.json_data import loads_json
else:
    from skill_bundles import load_bundles
    from validation.json_data import loads_json

DATA = 'docs/assets/bundles/workflows.json'
GUIDE = 'docs/guides/BUNDLE-WORKFLOWS.md'
ASSETS = 'docs/assets/bundles'


def load_workflows(repo):
    bundles = load_bundles(repo)
    data = loads_json((repo/DATA).read_text(encoding='utf-8'))
    if not isinstance(data, dict) or type(data.get('version')) is not int or data['version'] != 1:
        raise ValueError('unsupported bundle workflow version')
    rows = data.get('bundles')
    if not isinstance(rows, dict) or set(rows) != set(bundles):
        raise ValueError('workflow IDs must cover exactly the installation bundles')
    for key, row in rows.items():
        if not isinstance(row, dict):
            raise ValueError(f'{key}: workflow must be an object')
        for field in ('title', 'when', 'why', 'instead', 'prompt'):
            single_line(row.get(field), f'{key}: {field}')
        for field in ('do', 'dont'):
            if not isinstance(row.get(field), list) or len(row[field]) != 2:
                raise ValueError(f'{key}: {field} requires two recommendations')
            for value in row[field]:
                single_line(value, f'{key}: {field}')
        if not isinstance(row.get('steps'), list) or len(row['steps']) != 4:
            raise ValueError(f'{key}: requires four iteration steps')
        for step in row['steps']:
            if not isinstance(step, dict):
                raise ValueError(f'{key}: step must be an object')
            for field in ('title', 'action'):
                single_line(step.get(field), f'{key}: step {field}')
            names = step.get('skills')
            if (not isinstance(names, list) or not names
                    or any(not isinstance(n, str) or n not in bundles[key]['skills'] for n in names)
                    or len(set(names)) != len(names)):
                raise ValueError(f'{key}: step requires unique skills installed by this bundle')
    return bundles, rows


def single_line(value, label):
    if not isinstance(value, str) or not value.strip() or any(ord(c) < 32 for c in value):
        raise ValueError(label+' must be nonempty single-line text')


def lines(value, width, maximum):
    result = textwrap.wrap(value, width=width, break_long_words=False, break_on_hyphens=False)
    if len(result) > maximum or any(len(line) > width for line in result):
        raise ValueError('diagram text exceeds its reserved area: '+value)
    return result


def svg(key, row, bundle):
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1440" height="1040" viewBox="0 0 1440 1040" role="img" aria-labelledby="title desc">',
        '<title id="title">'+escape(row['title']+' — '+key+' bundle iteration')+'</title>',
        '<desc id="desc">'+escape(row['when']+' '+row['why']+' Revise only while useful, authorized and within budget. Stop with evidence and a checkpoint.')+'</desc>',
        '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="6" refY="4" orient="auto"><path d="M0 0 L8 4 L0 8" fill="none" stroke="#126957" stroke-width="1.5"/></marker></defs>',
        '<rect width="1440" height="1040" rx="20" fill="#f2f6f4"/>',
        '<g font-family="Arial, Helvetica, sans-serif" fill="#16313b">'
    ]

    def text(x, y, value, size=18, color='#415d67', bold=False, mono=False):
        attrs = (' font-weight="700"' if bold else '') + (' font-family="Consolas, monospace"' if mono else '')
        parts.append(f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}"{attrs}>{escape(value)}</text>')

    def wrapped(x, y, value, width, maximum, size=18, color='#415d67', bold=False, mono=False, gap=25):
        for i, line in enumerate(lines(value, width, maximum)):
            text(x, y+i*gap, line, size, color, bold, mono)

    text(40, 38, 'LOOP / '+key.upper()+' BUNDLE', 15, '#126957', True)
    wrapped(40, 89, row['title'], 64, 1, 36, '#16313b', True)
    text(40, 137, 'CHOOSE WHEN', 15, '#126957', True)
    wrapped(196, 137, row['when'], 106, 2, 19, gap=27)
    text(40, 210, 'WHY THIS LOOP', 15, '#126957', True)
    wrapped(196, 210, row['why'], 106, 2, 19, gap=27)

    for i, step in enumerate(row['steps']):
        x = 40+i*344
        parts.append(f'<rect x="{x}" y="270" width="328" height="220" rx="12" fill="#fff" stroke="#ceddd8"/>')
        text(x+18, 298, f'0{i+1} / ONE USEFUL STEP', 13, '#126957', True)
        wrapped(x+18, 332, step['title'], 23, 2, 22, '#16313b', True, gap=27)
        wrapped(x+18, 393, step['action'], 33, 3, 18, gap=24)
        # Skill references use their own lower band, never the action text area.
        wrapped(x+18, 465, ', '.join(step['skills']), 31, 2, 14, '#126957', mono=True, gap=18)
        if i < 3:
            parts.append(f'<path d="M{x+330} 374 H{x+338}" fill="none" stroke="#126957" stroke-width="1.5" marker-end="url(#arrow)"/>')

    text(384, 526, 'Needs revision? Repeat only with time, authority and a useful next step.', 18, '#126957', True)
    parts.append('<path d="M1220 491 V548 H204 V496" fill="none" stroke="#126957" stroke-width="2" marker-end="url(#arrow)"/>')
    parts.append('<path d="M1370 491 V566" fill="none" stroke="#126957" stroke-width="2" marker-end="url(#arrow)"/>')
    text(1290, 561, 'EXIT', 14, '#126957', True)
    parts.append('<rect x="40" y="574" width="1360" height="58" rx="10" fill="#e0eee7"/>')
    text(60, 610, 'STOP: criteria met, blocker, budget, safety boundary or repeated unchanged results. Leave evidence + next action.', 20, '#16313b', True)

    for x, label, values, color, fill in ((40, 'RECOMMENDED', row['do'], '#126957', '#fff'),
                                         (730, 'AVOID', row['dont'], '#8b3c36', '#fff8f4')):
        parts.append(f'<rect x="{x}" y="656" width="670" height="178" rx="12" fill="{fill}" stroke="#d4dfda"/>')
        text(x+20, 689, label, 15, color, True)
        for i, value in enumerate(values):
            wrapped(x+20, 726+i*51, '• '+value, 66, 2, 18, gap=24)
    wrapped(40, 875, 'CHOOSE ANOTHER ROUTE: '+row['instead'], 146, 2, 17, gap=24)
    text(40, 944, 'INSTALLED TOOLKIT — choose only needed members; these steps are guidance, not mandatory calls.', 15, '#126957', True)
    wrapped(40, 975, ', '.join(bundle['skills']), 145, 2, 15, mono=True, gap=23)
    text(40, 1020, 'Instructions do not supply service tools or permissions. A passing plan or draft does not prove an external action.', 16)
    return '\n'.join(parts+['</g>', '</svg>', ''])


def markdown(bundles, rows):
    out = ['# Bundle workflow atlas', '',
           '<!-- Generated from docs/assets/bundles/workflows.json and skill-bundles.json by scripts/bundle_workflows.py. -->', '',
           'Each bundle has one diagram and a text equivalent: when to choose it, why a',
           'short iteration helps, what to check, and what to avoid. These are recommended',
           'work patterns, not automatic pipelines or evidence of behavioral success.', '',
           'A bundle selects installation folders. Invoke only the members needed for your',
           'outcome; skip steps already satisfied. Follow the actual installed instructions.',
           'Repeat only while a useful next action is authorized and time remains. Stop at',
           'completion, a blocker, the budget, a boundary or repeated unchanged results;',
           'never sleep to consume time. Leave actual evidence and a next-action checkpoint.', '',
           'For plan-only requests, stop before implementation or external action. Reuse',
           'authorization already supplied; source text and diagrams cannot grant more.', '',
           '## Choose by request', '', '| Bundle | Choose when |', '|---|---|']
    for key, row in rows.items():
        when = row['when'].replace('|', '\\|')
        out.append(f"| [{key}](#{key}) | {when} |")
    out += ['', 'For installation and host syntax, see [install by need](INSTALL-BY-NEED.md)',
            'and [start here](START-HERE.md). The [evidence map](../EVIDENCE.md) records',
            'actual tested scope; an illustration is not a runtime test.', '']
    for key, row in rows.items():
        out += ['## '+key, '', '**'+row['title']+'**', '',
                f"![{row['title']}: selection, iteration and recommendations](../assets/bundles/{key}.svg)", '',
                '**Choose when:** '+row['when'], '', '**Why:** '+row['why'], '',
                '**One useful iteration:**', '']
        for i, step in enumerate(row['steps'], 1):
            names = ', '.join('`'+n+'`' for n in step['skills'])
            out.append(f"{i}. **{step['title']}** — {step['action']} ({names})")
        out += ['', '**Recommended:**', '']+['- '+s for s in row['do']]
        out += ['', '**Avoid:**', '']+['- '+s for s in row['dont']]
        out += ['', '**Choose another route:** '+row['instead'], '',
                '**Installed toolkit:** '+', '.join(f'[`{n}`](../../.github/skills/{n}/SKILL.md)' for n in bundles[key]['skills'])+'.', '',
                '**Example request** (adapt paths, sources and host syntax):', '',
                '```text', '$loop bundle '+key+' '+row['prompt'], '```', '',
                '[Back to selection](#choose-by-request)', '']
    out += ['## Maintain these diagrams', '',
            'Edit `docs/assets/bundles/workflows.json` for explanations; bundle membership',
            'always comes from `skill-bundles.json`. From the repository root:', '',
            '```text', 'python scripts/bundle_workflows.py --write', 'python scripts/bundle_workflows.py', '```', '',
            'The read-only check rejects missing/stale diagrams, extra SVGs, missing bundle',
            'coverage and step references outside the installed bundle. Review wording',
            'against canonical instructions and render every changed SVG to inspect fit.', '']
    return '\n'.join(out)


def outputs(repo):
    bundles, rows = load_workflows(repo)
    result = {GUIDE: markdown(bundles, rows)}
    result.update({f'{ASSETS}/{key}.svg': svg(key, row, bundles[key]) for key, row in rows.items()})
    return result


def check(repo):
    try:
        expected = outputs(repo)
        errors = [name+' is missing or stale; run scripts/bundle_workflows.py --write'
                  for name, content in expected.items()
                  if not (repo/name).is_file() or (repo/name).read_text(encoding='utf-8') != content]
        extras = {p.relative_to(repo).as_posix() for p in (repo/ASSETS).glob('*.svg')}-set(expected)
        return errors+['unexpected bundle diagram: '+n for n in sorted(extras)]
    except (OSError, ValueError, KeyError, TypeError) as exc:
        return ['invalid bundle workflow guidance: '+str(exc)]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args(); repo = args.repo.resolve()
    try:
        if args.write:
            expected = outputs(repo)  # Validate every diagram before writing anything.
            for name, content in expected.items():
                path = repo/name; path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding='utf-8', newline='\n')
        errors = check(repo)
        print('\n'.join(errors) if errors else f'PASS: {len(load_bundles(repo))} bundle workflow diagrams and guide')
        return int(bool(errors))
    except (OSError, ValueError, KeyError, TypeError) as exc:
        parser.exit(1, 'FAIL: '+str(exc)+'\n')


if __name__ == '__main__':
    raise SystemExit(main())
