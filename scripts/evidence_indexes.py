#!/usr/bin/env python3
"""Check declared published evidence byte indexes; no execution or attestation."""
import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re

if __package__:
    from .skill_resources import plain_path, plain_chain
    from .validation.json_data import loads_json
else:
    from skill_resources import plain_path, plain_chain
    from validation.json_data import loads_json

INDEX_NAME='published-hashes.json'


def check_index(root,index):
    errors=[]
    try:
        plain_chain(root,index)
        data=loads_json(index.read_text(encoding='utf-8'))
        if not isinstance(data,dict)or not data:
            raise ValueError('index must be a nonempty object')
        if 'files' in data:
            if data.get('algorithm')!='sha256':raise ValueError('index algorithm must be sha256')
            rows=data['files']
        else:
            rows=data  # Existing flat SHA256 indexes remain supported.
        if not isinstance(rows,dict)or not rows:raise ValueError('files must be a nonempty object')
        seen=set()
        for relative,expected in rows.items():
            if (not isinstance(relative,str)or not relative or '\\'in relative or ':'in relative
                    or '\x00'in relative or str(PurePosixPath(relative))!=relative
                    or relative.startswith('/')or any(p in ('.','..')for p in relative.split('/'))
                    or any(ord(c)<32 for c in relative)):
                raise ValueError('indexed path must be a safe POSIX relative path')
            for part in relative.split('/'):
                if (part.rstrip(' .')!=part or any(c in '<>"|?*'for c in part)
                        or re.fullmatch(r'(?i:con|prn|aux|nul|com[1-9]|lpt[1-9])',part.split('.')[0])):
                    raise ValueError('indexed path must use portable ordinary filenames')
            if relative.casefold()in seen:raise ValueError('case-colliding index path')
            seen.add(relative.casefold())
            if not isinstance(expected,str)or not re.fullmatch('[0-9a-f]{64}',expected):
                raise ValueError('indexed digest must be lowercase SHA256')
            candidate=index.parent/relative
            if candidate==index:raise ValueError('index cannot hash itself')
            plain_chain(root,candidate)
            if not candidate.is_file():
                errors.append('missing indexed artifact: '+candidate.relative_to(root).as_posix())
                continue
            actual=hashlib.sha256(candidate.read_bytes()).hexdigest()
            if actual!=expected:
                errors.append('published artifact hash differs: '+candidate.relative_to(root).as_posix())
        return errors,len(rows)
    except (OSError,ValueError,KeyError,TypeError)as error:
        return ['invalid published index '+index.relative_to(root).as_posix()+': '+str(error)],0


def check_indexes(root):
    root=root.resolve()
    errors=[];indexes=0;artifacts=0
    try:
        if not root.is_dir():raise ValueError('evidence root must be an existing directory')
        plain_path(root)
        stack=[root]
        while stack:
            folder=stack.pop()
            for path in sorted(folder.iterdir()):
                if path.name=='__pycache__'or path.suffix=='.pyc':continue
                plain_path(path)
                if path.is_dir():stack.append(path)
                elif path.name==INDEX_NAME:
                    indexes+=1
                    findings,count=check_index(root,path)
                    errors.extend(findings);artifacts+=count
        if not indexes:errors.append('no published byte indexes found; empty discovery is not PASS')
    except (OSError,ValueError)as error:errors.append(str(error))
    return {'status':'FAIL'if errors else'PASS','indexes':indexes,'indexed_artifacts':artifacts,
            'errors':errors,'scope':'Declared published bytes only. Unindexed files are not covered; '
            'matching hashes do not authenticate authors, prove execution or validate claims.',
            'runtime_validation':'NOT_RUN','writes':'NONE'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]/'docs/evidence')
    args=parser.parse_args();report=check_indexes(args.root)
    print(json.dumps(report,indent=2,ensure_ascii=True))
    return int(report['status']!='PASS')


if __name__=='__main__':raise SystemExit(main())
