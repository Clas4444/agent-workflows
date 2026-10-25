"""Strict JSON input shared by repository control-plane readers (stdlib only)."""
import json


def unique_object(pairs):
    value={}
    for key,item in pairs:
        if key in value:
            raise ValueError(f'duplicate JSON key: {key}')
        value[key]=item
    return value


def reject_constant(value):
    raise ValueError(f'non-finite JSON constant is not supported: {value}')


def loads_json(text):
    try:
        return json.loads(text,object_pairs_hook=unique_object,parse_constant=reject_constant)
    except RecursionError as exc:
        raise ValueError('JSON nesting exceeds the interpreter validation limit') from exc
