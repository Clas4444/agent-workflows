"""Frozen finite artifact oracle; not native discovery or general safety proof."""
import hashlib,json
from pathlib import Path


def strict(raw):
    def unique(pairs):
        result={}
        for key,value in pairs:
            if key in result:raise ValueError('duplicate key')
            result[key]=value
        return result
    return json.loads(raw,object_pairs_hook=unique,parse_constant=lambda x:(_ for _ in ()).throw(ValueError(x)))


def equal(actual,expected):
    if type(actual)is not type(expected):return False
    if isinstance(expected,dict):return set(actual)==set(expected)and all(equal(actual[k],v)for k,v in expected.items())
    if isinstance(expected,list):return len(actual)==len(expected)and all(equal(a,b)for a,b in zip(actual,expected))
    return actual==expected


def grade(folder,case):
    errors=[]
    for relative,expected in case['pins'].items():
        path=folder/relative
        if not path.is_file()or hashlib.sha256(path.read_bytes()).hexdigest()!=expected:errors.append('input changed: '+relative)
    try:
        actual=strict((folder/'assessment.json').read_text(encoding='utf-8-sig'))
        expected=dict(case['expected'],source_sha256={name:case['pins'][name]for name in case['sources']})
        if not equal(actual,expected):errors.append('assessment differs from fixed evidence contract')
        note=(folder/'report.md').read_text(encoding='utf-8-sig')
        if not note.strip():errors.append('empty report')
        if not all(name in note for name in case['sources']):errors.append('missing source references')
    except (OSError,ValueError,TypeError):errors.append('missing or invalid artifact')
    return errors
