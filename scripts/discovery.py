#!/usr/bin/env python3
"""Generate/check the portable lookup catalog and requested Codex UI metadata."""
import argparse
import importlib.util
import json
from pathlib import Path

if __package__:
    from .validation.json_data import loads_json
    from .validation.skill_format import FRONTMATTER_PATTERN, frontmatter_value
    from .skill_bundles import load_bundles
else:
    from validation.json_data import loads_json
    from validation.skill_format import FRONTMATTER_PATTERN, frontmatter_value
    from skill_bundles import load_bundles

CATALOG = '.github/skills/loop/assets/catalog.json'
SEARCH_TERMS = {'loop-code': 'lc', 'loop-debug': 'dbg', 'loop-review': 'rv',
                'loop-test': 'tst', 'loop-work': 'wk', 'loop-table': 'tbl',
                'loop-document': 'doc', 'loop-meeting': 'mtg', 'loop-knowledge': 'kb'}


def expected(repo):
    manifest = loads_json((repo/'skills-manifest.json').read_text(encoding='utf-8'))
    data = {'version': 1, 'skills': {}, 'bundles': load_bundles(repo)}
    metadata = {}
    for name in manifest['skills']:
        text = (repo/'.github/skills'/name/'SKILL.md').read_text(encoding='utf-8')
        match = FRONTMATTER_PATTERN.match(text)
        description = frontmatter_value(match.group(1), 'description') if match else None
        if not description: raise ValueError('missing description: '+name)
        short = name.removeprefix('loop-')
        data['skills'][name] = {'description': description, 'aliases': [],
                                'search_terms': [SEARCH_TERMS[name]] if name in SEARCH_TERMS else []}
        title = 'Loop' if name == 'loop' else 'Loop '+short.replace('-', ' ').title()
        blurb = ('Find skills or set up a conditional loop' if name == 'loop' else 'Use '+title+' for a focused workflow')[:64]
        prompt = 'Use $'+name+' '+('to choose a focused skill/bundle or help me set up a conditional workflow.' if name == 'loop' else 'for this task; verify the result and report any limits.')
        metadata[name] = 'interface:\n'+''.join('  '+key+': '+json.dumps(value)+'\n' for key, value in
            [('display_name', title), ('short_description', blurb), ('default_prompt', prompt)])
    return data, metadata


def check(repo, write=False):
    data, metadata = expected(repo)
    path = repo/'.github/skills/loop/scripts/find_skill.py'
    spec = importlib.util.spec_from_file_location('loop_finder', path)
    finder = importlib.util.module_from_spec(spec);spec.loader.exec_module(finder)
    finder.validate_catalog(data)
    texts = {repo/CATALOG: json.dumps(data, indent=2, ensure_ascii=False)+'\n'}
    texts.update({repo/'.github/skills'/name/'agents/openai.yaml': text for name, text in metadata.items()})
    errors = []
    for path, text in texts.items():
        if write:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8', newline='\n')
        elif not path.is_file() or path.read_text(encoding='utf-8') != text:
            errors.append('discovery metadata stale: '+path.relative_to(repo).as_posix())
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write', action='store_true')
    args = parser.parse_args()
    try:
        errors = check(args.repo.resolve(), args.write)
        print('\n'.join(errors) if errors else 'PASS: portable discovery catalog and UI metadata')
        return int(bool(errors))
    except (OSError, ValueError, KeyError, TypeError) as error:
        parser.exit(1, 'FAIL: '+str(error)+'\n')


if __name__ == '__main__': raise SystemExit(main())
