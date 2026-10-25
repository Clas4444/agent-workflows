"""Preserve historical exercise identity without relabeling changed instructions PASS."""
import hashlib
import re
from pathlib import Path, PurePosixPath

if __package__:
    from .validation.json_data import loads_json
    from .skill_resources import plain_chain
else:
    from validation.json_data import loads_json
    from skill_resources import plain_chain

INDEX = 'docs/evidence/instruction-history.json'
ARCHIVE = 'docs/evidence/instruction-history'


def instruction_identity(repo, campaign, name, expected):
    if (not isinstance(name,str) or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*',name)
            or not isinstance(campaign,str) or not re.fullmatch(r'[a-z0-9][a-z0-9.-]*',campaign)
            or not isinstance(expected,str) or not re.fullmatch(r'[0-9a-f]{64}',expected)):
        raise ValueError('invalid campaign, skill name or instruction digest')
    current = repo/'.github/skills'/name/'SKILL.md'
    plain_chain(repo,current)
    digest = hashlib.sha256(current.read_bytes()).hexdigest()
    if digest==expected:
        return 'CURRENT_BYTE_IDENTICAL'
    data = loads_json((repo/INDEX).read_text(encoding='utf-8'))
    row = data[campaign][name]
    relative = row['archive']
    if (not isinstance(relative,str) or '\\' in relative or ':' in relative
            or str(PurePosixPath(relative))!=relative or '..' in PurePosixPath(relative).parts
            or not relative.startswith(ARCHIVE+'/')):
        raise ValueError('historical instruction archive must stay in its declared directory')
    archived = repo/relative
    plain_chain(repo,archived)
    if (row.get('historical_sha256')!=expected
            or hashlib.sha256(archived.read_bytes()).hexdigest()!=expected
            or row.get('current_sha256')!=digest
            or row.get('historical_reuse_status')!='INVALIDATED'
            or row.get('automatic_discovery_status')!='NOT_RUN'
            or not isinstance(row.get('reason'),str) or not row['reason'].strip()):
        raise ValueError(f'historical/current identity record is invalid for {campaign}/{name}')
    return 'HISTORICAL_ONLY_INVALIDATED'


def check_history(repo):
    path = repo/INDEX
    if not path.is_file():
        return []
    try:
        data = loads_json(path.read_text(encoding='utf-8'))
        for campaign, rows in data.items():
            for name,row in rows.items():
                if instruction_identity(repo,campaign,name,row['historical_sha256'])!='HISTORICAL_ONLY_INVALIDATED':
                    raise ValueError('invalidation record no longer describes a changed instruction')
        return []
    except (OSError,ValueError,KeyError,TypeError,AttributeError) as exc:
        return [f'invalid historical instruction identity: {exc}']
