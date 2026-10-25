#!/usr/bin/env python3
"""Read-only inventory, move-plan checks and post-move verification. Never moves files."""
import argparse
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys


def plain(path):
    info = path.lstat()
    reparse = getattr(info,'st_file_attributes',0) & getattr(stat,'FILE_ATTRIBUTE_REPARSE_POINT',0)
    if stat.S_ISLNK(info.st_mode) or reparse or (stat.S_ISREG(info.st_mode) and info.st_nlink>1):
        raise ValueError(f'alias/hardlink is outside the supported file-plan contract: {path.name}')


def relative(value):
    if (not isinstance(value,str) or not value or '\\' in value or ':' in value
            or value.startswith('/') or str(PurePosixPath(value))!=value
            or any(p in ('.','..') for p in value.split('/'))):
        raise ValueError('mapping paths must be canonical relative paths using forward slashes')
    for part in value.split('/'):
        if (part.rstrip(' .')!=part or any(ord(c)<32 or c in '<>"|?*' for c in part)
                or re.fullmatch(r'(?i:con|prn|aux|nul|com[1-9]|lpt[1-9])',part.split('.')[0])):
            raise ValueError('mapping contains a non-portable filename')
    return value


def inventory(root):
    plain(root)
    if not root.is_dir():
        raise ValueError('selected root must be a real directory')
    root = root.resolve()
    files, entries, folded = {}, [], {}
    stack = [root]
    while stack:
        folder = stack.pop()
        for path in sorted(folder.iterdir()):
            plain(path)
            name = path.relative_to(root).as_posix()
            relative(name)
            if name.casefold() in folded and folded[name.casefold()]!=name:
                raise ValueError('selected root contains case-colliding paths')
            folded[name.casefold()] = name
            entries.append(name)
            if path.is_dir():
                stack.append(path)
            elif path.is_file():
                data = path.read_bytes()
                files[name] = {'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data)}
            else:
                raise ValueError('selected root contains an unsupported file type')
    token = hashlib.sha256(os.path.normcase(str(root)).encode('utf-8')).hexdigest()
    return {'root_token':token,'files':dict(sorted(files.items())),'entries':sorted(entries)}


def moves_from(data, files):
    if not isinstance(data,dict) or type(data.get('version')) is not int or data['version']!=1:
        raise ValueError('mapping/plan requires version 1')
    moves = data.get('moves')
    if not isinstance(moves,list) or not moves:
        raise ValueError('moves must be a non-empty list')
    sources, destinations = set(), set()
    for row in moves:
        if not isinstance(row,dict) or set(row)!= {'source','destination'}:
            raise ValueError('each move requires only source and destination')
        source, destination = relative(row['source']),relative(row['destination'])
        if source not in files or source in sources or source.casefold()==destination.casefold():
            raise ValueError('source missing/duplicated or case-only self move')
        if destination.casefold() in destinations:
            raise ValueError('destinations collide after case folding')
        sources.add(source);destinations.add(destination.casefold())
    for row in moves:
        destination = row['destination']
        if any(destination.casefold().startswith(other+'/') or other.startswith(destination.casefold()+'/')
               for other in destinations if other!=destination.casefold()):
            raise ValueError('destinations overlap as file and directory')
    return moves


def make_plan(root, mapping):
    state = inventory(root)
    moves = moves_from(mapping,state['files'])
    existing = {name.casefold():name for name in state['entries']}
    for row in moves:
        destination = row['destination']
        if destination.casefold() in existing:
            raise ValueError('destination already exists; overwrites and rename cycles are unsupported')
        parts = destination.split('/')
        for i in range(1,len(parts)):
            parent = '/'.join(parts[:i]);alias=existing.get(parent.casefold())
            if alias is not None and (alias!=parent or alias in state['files']):
                raise ValueError('destination parent is a file or case alias')
    return {'version':1,'root_token':state['root_token'],'source_inventory':state['files'],
            'moves':moves,'scope':'Regular files only; plan/check/verify never move or delete anything.'}


def verify_plan(root, plan, after=False):
    if not isinstance(plan,dict) or not isinstance(plan.get('source_inventory'),dict):
        raise ValueError('plan requires its source inventory')
    old = plan['source_inventory']
    for name,record in old.items():
        relative(name)
        if (not isinstance(record,dict) or set(record)!= {'sha256','bytes'}
                or not isinstance(record['sha256'],str) or not re.fullmatch(r'[0-9a-f]{64}',record['sha256'])
                or type(record['bytes']) is not int or record['bytes']<0):
            raise ValueError('invalid pinned file identity')
    moves = moves_from(plan,old)
    current = inventory(root)
    if plan.get('root_token')!=current['root_token']:
        raise ValueError('plan belongs to a different selected root')
    expected = dict(old)
    if after:
        for row in moves:
            destination = row['destination']
            if destination.casefold() in {name.casefold() for name in old}:
                raise ValueError('plan contains an overwrite or rename cycle')
            expected[destination] = expected.pop(row['source'])
    else:
        regenerated = make_plan(root,{'version':1,'moves':moves})
        if regenerated['source_inventory']!=old:
            raise ValueError('source inventory changed after planning')
    if current['files']!=expected:
        raise ValueError('file inventory/content does not match the pinned move plan')
    return {'status':'PASS','phase':'after' if after else 'before','file_count':len(expected),
            'moves_executed_by_helper':'NOT_RUN','scope':'Observed path/content equality only, not a concurrency lock.'}


def unique_object(pairs):
    out = {}
    for key,value in pairs:
        if key in out:raise ValueError('duplicate JSON key in mapping/plan')
        out[key]=value
    return out


def read_json(path):
    try:
        return json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=unique_object,
                          parse_constant=lambda value: (_ for _ in ()).throw(ValueError('non-finite JSON')))
    except RecursionError as exc:
        raise ValueError('mapping/plan nesting is excessive') from exc


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('inventory','plan','check','verify'))
    parser.add_argument('root',type=Path)
    parser.add_argument('--mapping',type=Path)
    parser.add_argument('--plan',type=Path)
    args = parser.parse_args()
    if hasattr(sys.stdout,'reconfigure'):sys.stdout.reconfigure(encoding='utf-8')
    try:
        if args.mode=='inventory':result=inventory(args.root)
        elif args.mode=='plan':
            if not args.mapping:parser.error('plan requires --mapping')
            result=make_plan(args.root,read_json(args.mapping))
        else:
            if not args.plan:parser.error('check/verify requires --plan')
            result=verify_plan(args.root,read_json(args.plan),after=args.mode=='verify')
        print(json.dumps(result,ensure_ascii=False,indent=2));return 0
    except (OSError,ValueError,KeyError,TypeError) as exc:
        parser.exit(1,f'FAIL: {exc}\n')


if __name__=='__main__':
    raise SystemExit(main())
