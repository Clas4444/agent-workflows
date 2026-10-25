"""Strict JSON input shared by repository control-plane readers (stdlib only)."""
import json

MAX_JSON_DEPTH = 512


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
    # C-stack limits vary by interpreter and process launch mode. Bound the
    # control-plane format before parsing rather than relying on RecursionError.
    if isinstance(text, (bytes, bytearray)):
        text = text.decode(json.detect_encoding(text), 'surrogatepass')
    if isinstance(text, str):
        depth = 0
        quoted = False
        escaped = False
        for char in text:
            if quoted:
                if escaped:
                    escaped = False
                elif char == '\\':
                    escaped = True
                elif char == '"':
                    quoted = False
            elif char == '"':
                quoted = True
            elif char in '[{':
                depth += 1
                if depth > MAX_JSON_DEPTH:
                    raise ValueError(f'JSON nesting exceeds {MAX_JSON_DEPTH} containers')
            elif char in ']}':
                depth -= 1
    try:
        return json.loads(text,object_pairs_hook=unique_object,parse_constant=reject_constant)
    except RecursionError as exc:
        raise ValueError('JSON nesting exceeds the interpreter validation limit') from exc
