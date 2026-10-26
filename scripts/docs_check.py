#!/usr/bin/env python3
"""Read-only local Markdown navigation check; supported syntax, no network."""
import argparse
from html import unescape
import json
import os
from pathlib import Path
import re
import sys
import unicodedata
from urllib.parse import unquote, urlsplit

if __package__:
    from .skill_resources import plain_chain, plain_path
else:
    from skill_resources import plain_chain, plain_path

LINK = re.compile(r'!?\[[^\]]*\]\(\s*(<[^>\n]*>|(?:\\.|[^\s()\\]+|\([^()\n]*\))+?)'
                  r'(?:[ \t]+(?:"[^"\n]*"|\x27[^\x27\n]*\x27))?\s*\)')
REFERENCE = re.compile(r'(?<!\w)!?\[[^\]\n]+\]\[[^\]\n]*\]|^ {0,3}\[[^\]\n]+\]:', re.M)
CANDIDATE = re.compile(r'!?\[[^\]]*\]\(')
SCOPE = 'Root, docs/ and schemas/ Markdown; inline file/image links and local Markdown anchors. No network or rendering.'


def blank(value):
    return re.sub(r'[^\n]', ' ', value)


def escaped(text, position):
    start = position
    while start and text[start-1] == '\\': start -= 1
    return bool((position-start) % 2)


def prose(text):
    """Keep offsets stable while masking comments and fenced code."""
    text = re.sub(r'<!--.*?-->', lambda m: blank(m[0]), text, flags=re.S)
    result = []; fence = None
    for line in text.splitlines(keepends=True):
        match = re.match(r'^ {0,3}(`{3,}|~{3,})(.*)$', line)
        if fence:
            result.append(blank(line))
            if match and match[1][0] == fence[0] and len(match[1]) >= fence[1] and not match[2].strip():
                fence = None
        elif match:
            fence = (match[1][0], len(match[1])); result.append(blank(line))
        else:
            result.append(line)
    return ''.join(result)


def without_code_spans(text):
    result = list(text); position = 0
    while match := re.search(r'`+', text[position:]):
        start = position+match.start(); end = position+match.end()
        if escaped(text, start):
            position = end; continue
        closing = re.search(r'(?<!`)`{'+str(end-start)+r'}(?!`)', text[end:])
        if closing:
            stop = end+closing.end()
            result[start:stop] = blank(text[start:stop]); position = stop
        else:
            position = end
    return ''.join(result)


def heading_anchors(text):
    text = prose(text)
    titles = [(m.start(), m[1]) for m in re.finditer(r'^ {0,3}#{1,6}[ \t]+(.+?)\s*#*$', text, re.M)]
    titles += [(m.start(), m[1]) for m in re.finditer(r'^([^\n]+)\n {0,3}(?:={3,}|-{3,})[ \t]*$', text, re.M)]
    # The repository uses ATX headings. Setext support is deliberately basic.
    found = set(); used = set()
    for _, title in sorted(titles):
        title = re.sub(r'!?\[([^]]*)\]\([^)]*\)', r'\1', title)
        title = re.sub(r'<[^>]*>', '', title)
        title = re.sub(r'(?<!\w)_([^_]+)_(?!\w)', r'\1', title)
        title = unescape(title).strip().lower()
        slug = ''.join(c for c in title if c in ' _-' or unicodedata.category(c)[0] in 'LNM').replace(' ', '-')
        candidate = slug; suffix = 0
        while candidate in used:
            suffix += 1; candidate = slug+'-'+str(suffix)
        used.add(candidate); found.add(candidate)
    found.update(re.findall(r'<a\b[^>]*\b(?:name|id)=["\x27]([^"\x27]+)["\x27]', without_code_spans(text), re.I))
    return found


def documents(repo, errors):
    paths = set(repo.glob('*.md'))
    stack = [repo/name for name in ('docs', 'schemas') if (repo/name).exists()]
    while stack:
        folder = stack.pop()
        try:
            plain_chain(repo, folder)
            for path in folder.iterdir():
                plain_chain(repo, path)
                if path.name == '__pycache__': continue
                if path.is_dir(): stack.append(path)
                elif path.suffix.lower() == '.md': paths.add(path)
        except (OSError, ValueError) as exc:
            errors.append({'file':folder.relative_to(repo).as_posix(), 'line':None, 'error':str(exc)})
    return sorted(paths)


def destination(repo, source, value):
    path = unquote(value)
    path = re.sub(r'\\([\\`*_{}\[\]()#+.!<> -])', r'\1', path)
    if '\\' in path or '\x00' in path:
        raise ValueError('unsupported local path spelling')
    candidate = repo/path.lstrip('/') if path.startswith('/') else source.parent/path if path else source
    candidate = Path(os.path.abspath(candidate))  # Normalize .. without following aliases.
    try: candidate.relative_to(repo)
    except ValueError: raise ValueError('local target is outside the repository') from None
    plain_chain(repo, candidate)
    parent = repo
    for part in candidate.relative_to(repo).parts:
        if not parent.is_dir(): raise ValueError('missing local target')
        names = {entry.name for entry in parent.iterdir()}
        if part not in names:
            if part.casefold() in {name.casefold() for name in names}:
                raise ValueError('local target case does not match repository spelling')
            raise ValueError('missing local target')
        parent = parent/part
    if not candidate.exists(): raise ValueError('missing local target')
    return candidate


def check(repo):
    repo = Path(repo).resolve()
    result = {'status':'FAIL', 'scope':SCOPE, 'markdown_files':0, 'local_links':0,
              'heading_anchors':0, 'external_links_not_fetched':0,
              'non_markdown_fragments_not_checked':0, 'external_urls':'NOT_RUN',
              'writes':'NONE', 'errors':[]}
    errors = result['errors']; texts = {}; anchor_cache = {}
    if not (repo/'README.md').is_file():
        errors.append({'file':'README.md', 'line':None, 'error':'required README.md is missing'})
    for path in documents(repo, errors):
        name = path.relative_to(repo).as_posix()
        try:
            plain_chain(repo, path)
            texts[path] = prose(path.read_text(encoding='utf-8'))
        except (OSError, ValueError) as exc:
            errors.append({'file':name, 'line':None, 'error':str(exc)})
    result['markdown_files'] = len(texts)
    for path, text in texts.items():
        visible = without_code_spans(text)
        matches = [m for m in LINK.finditer(visible)
                   if not escaped(visible, m.start()+int(m[0].startswith('!')))]
        for unsupported in list(REFERENCE.finditer(visible))+list(CANDIDATE.finditer(visible)):
            opener = unsupported.start()+int(unsupported[0].startswith('!'))
            if not escaped(visible, opener) and not any(m.start() <= unsupported.start() < m.end() for m in matches):
                errors.append({'file':path.relative_to(repo).as_posix(), 'line':visible[:unsupported.start()].count('\n')+1,
                               'error':'unsupported Markdown link syntax; use a supported inline link'})
        for match in matches:
            value = match[1].strip('<>')
            error = {'file':path.relative_to(repo).as_posix(), 'line':visible[:match.start()].count('\n')+1, 'target':value}
            try:
                url = urlsplit(value)
                if url.scheme or url.netloc:
                    result['external_links_not_fetched'] += 1; continue
                result['local_links'] += 1
                target = destination(repo, path, url.path)
                if url.fragment and target.suffix.lower() == '.md':
                    if not target.is_file(): raise ValueError('Markdown anchor target must be a file')
                    result['heading_anchors'] += 1
                    if target not in anchor_cache:
                        anchor_cache[target] = heading_anchors(target.read_text(encoding='utf-8'))
                    if unquote(url.fragment) not in anchor_cache[target]: raise ValueError('unresolved heading anchor')
                elif url.fragment:
                    result['non_markdown_fragments_not_checked'] += 1
            except (OSError, ValueError) as exc:
                errors.append(dict(error, error=str(exc)))
    result['status'] = 'FAIL' if errors else 'PASS'
    return result


def main():
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(errors='backslashreplace')
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo', type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument('--json', action='store_true', help='Print scoped counts and diagnostics as JSON')
    args = parser.parse_args(); result = check(args.repo)
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=True))
    else:
        print(f"{result['status']}: documentation navigation; {result['markdown_files']} Markdown files, {result['local_links']} local links")
        for row in result['errors']:
            print(f"- {row['file']}:{row['line'] or '?'}: {row['error']}")
    return int(result['status'] != 'PASS')


if __name__ == '__main__':
    raise SystemExit(main())
