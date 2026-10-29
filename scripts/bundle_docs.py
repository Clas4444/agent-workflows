#!/usr/bin/env python3
"""Keep the need-installation table tied to the validated bundle registry."""
import argparse
from pathlib import Path

if __package__:
    from .skill_bundles import load_bundles
else:
    from skill_bundles import load_bundles

START='<!-- BEGIN GENERATED NEED BUNDLES -->'
END='<!-- END GENERATED NEED BUNDLES -->'
GUIDE='docs/guides/install-by-need.md'


def render(repo):
    rows=[START,'','| Need | Bundle | Installed skills |','|---|---|---|']
    for key,row in load_bundles(repo).items():
        purpose=row['purpose'].replace('|','\\|')
        names=', '.join('`'+name+'`' for name in row['skills'])
        rows.append(f'| {purpose} | `{key}` | {names} |')
    return '\n'.join(rows+['',END])


def section(text):
    if text.count(START)!=1 or text.count(END)!=1 or text.index(START)>=text.index(END):
        raise ValueError('installation guide requires exactly one ordered generated bundle block')
    return text.index(START),text.index(END)+len(END)


def check_bundle_guide(repo):
    try:
        text=(repo/GUIDE).read_text(encoding='utf-8');start,end=section(text)
        return [] if text[start:end]==render(repo) else ['installation bundle table is stale; run scripts/bundle_docs.py --write']
    except (OSError,ValueError,KeyError,TypeError) as exc:
        return [f'invalid installation bundle guide: {exc}']


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--write',action='store_true')
    args=parser.parse_args();repo=args.repo.resolve()
    try:
        if args.write:
            expected=render(repo);path=repo/GUIDE;text=path.read_text(encoding='utf-8');start,end=section(text)
            path.write_text(text[:start]+expected+text[end:],encoding='utf-8')
        errors=check_bundle_guide(repo)
        print('\n'.join(errors) if errors else 'PASS: need-installation bundle guide')
        return int(bool(errors))
    except (OSError,ValueError,KeyError,TypeError) as exc:
        parser.exit(1,f'FAIL: {exc}\n')


if __name__=='__main__':raise SystemExit(main())
