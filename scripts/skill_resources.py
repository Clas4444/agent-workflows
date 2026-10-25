#!/usr/bin/env python3
"""Declared skill resources, shared by validation and installation (stdlib only)."""
import argparse
import json
import re
from pathlib import Path, PurePosixPath
import stat

if __package__:
    from .validation.json_data import loads_json
else:
    from validation.json_data import loads_json

RUNNER_SKILLS = ('loop-orchestrate','loop-prompt')
REGISTRY = 'skill-resources.json'


def plain_path(path):
    metadata = path.lstat()
    reparse = getattr(metadata,'st_file_attributes',0) & getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0)
    if stat.S_ISLNK(metadata.st_mode) or reparse:
        raise ValueError(f'source resource alias is not supported: {path}')
    if stat.S_ISREG(metadata.st_mode) and metadata.st_nlink>1:
        raise ValueError(f'hardlinked source resource is not supported: {path}')


def plain_chain(repo, path):
    current = repo
    for part in path.relative_to(repo).parts:
        current = current/part
        try:
            plain_path(current)
        except FileNotFoundError:
            break


def canonical_files(folder):
    plain_path(folder)
    stack = [folder]
    files = set()
    while stack:
        current = stack.pop()
        for path in current.iterdir():
            plain_path(path)
            if path.name=='__pycache__' or path.suffix=='.pyc':
                continue
            if path.is_dir():
                stack.append(path)
            elif path.is_file():
                files.add(path.relative_to(folder).as_posix())
            else:
                raise ValueError(f'unsupported source resource type: {path}')
    return files


def load_resources(repo, names):
    manifest = loads_json((repo/'skills-manifest.json').read_text(encoding='utf-8'))
    declared = manifest.get('resource_manifest')
    if declared is not None and declared!=REGISTRY:
        raise ValueError('resource_manifest must name skill-resources.json')
    path = repo/REGISTRY
    if not path.exists():
        if declared is not None:
            raise ValueError('missing declared skill-resources.json')
        return {}
    plain_path(path)
    data = loads_json(path.read_text(encoding='utf-8'))
    if not isinstance(data,dict) or type(data.get('version')) is not int or data['version']!=1:
        raise ValueError('unsupported skill resource registry version')
    resources = data.get('resources')
    if not isinstance(resources,dict):
        raise ValueError('resources must be an object')
    for name, paths in resources.items():
        if name not in names or not isinstance(paths,list) or not paths:
            raise ValueError('resources require a known skill and non-empty path list')
        seen = set()
        components = {'skill.md':'SKILL.md'}
        if name in RUNNER_SKILLS:
            components.update({'scripts':'scripts','scripts/run_loop.py':'scripts/run_loop.py'})
        for value in paths:
            if (not isinstance(value,str) or not value or '\\' in value or ':' in value
                    or '\x00' in value or value.startswith('/') or str(PurePosixPath(value))!=value
                    or any(part in ('.','..') for part in value.split('/'))
                    or value=='SKILL.md' or (name in RUNNER_SKILLS and value=='scripts/run_loop.py')):
                raise ValueError(f'unsafe or implicit resource path for {name}: {value!r}')
            for part in value.split('/'):
                if (part.rstrip(' .')!=part or any(ord(c)<32 or c in '<>"|?*' for c in part)
                        or re.fullmatch(r'(?i:con|prn|aux|nul|com[1-9]|lpt[1-9])',part.split('.')[0])):
                    raise ValueError(f'non-portable resource path for {name}: {value!r}')
            folded = value.casefold()
            if folded in seen:
                raise ValueError(f'duplicate/case-colliding resource path for {name}')
            seen.add(folded)
            parts = value.split('/')
            for i in range(1,len(parts)+1):
                prefix = '/'.join(parts[:i]);alias=components.get(prefix.casefold())
                if alias is not None and alias!=prefix:
                    raise ValueError(f'implicit/parent case alias in resources for {name}')
                components[prefix.casefold()]=prefix
    return resources


def payload_files(repo, name, resources):
    folder = repo/'.github/skills'/name
    plain_chain(repo,folder)
    if not folder.is_dir():
        raise ValueError(f'missing source file: {folder}/SKILL.md')
    implicit = {'SKILL.md'}
    if name in RUNNER_SKILLS:
        implicit.add('scripts/run_loop.py')
    expected = implicit | set(resources.get(name,[]))
    actual = canonical_files(folder)
    # A legacy source fixture may keep the runner only at scripts/run_loop.py.
    allowed_missing = {'scripts/run_loop.py'} if name in RUNNER_SKILLS else set()
    if actual-expected or expected-actual-allowed_missing:
        raise ValueError(f'unregistered or missing source resources for {name}: '
                         f'extra={sorted(actual-expected)}, missing={sorted(expected-actual-allowed_missing)}')
    pairs = []
    for relative in sorted(expected):
        source = repo/'scripts/run_loop.py' if name in RUNNER_SKILLS and relative=='scripts/run_loop.py' else folder/relative
        if not source.is_file():
            raise ValueError(f'missing source file: {source}')
        plain_chain(repo,source)
        pairs.append((relative,source))
    return pairs


def check_resources(repo, names=None, roots=None):
    try:
        manifest = loads_json((repo/'skills-manifest.json').read_text(encoding='utf-8'))
        names = names if names is not None else manifest['skills']
        roots = roots if roots is not None else manifest['project_skill_roots']
        resources = load_resources(repo,names)
        errors = []
        for name in names:
            payload = payload_files(repo,name,resources)
            expected = {relative for relative,_ in payload}
            for native in roots:
                folder = repo/native/name
                plain_chain(repo,folder)
                actual = canonical_files(folder)
                if actual!=expected:
                    errors.append(f'{native}/{name} resource inventory differs from canonical payload')
                for relative,source in payload:
                    copy = folder/relative
                    if not copy.is_file() or copy.read_bytes()!=source.read_bytes():
                        errors.append(f'{native}/{name}/{relative} resource copy is missing or not identical')
        return errors
    except (OSError,ValueError,KeyError,TypeError) as exc:
        return [f'invalid skill resources: {exc}']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = check_resources(args.repo.resolve())
    print('\n'.join(errors) if errors else 'PASS: declared skill resources and native copies')
    return int(bool(errors))


if __name__=='__main__':
    raise SystemExit(main())
