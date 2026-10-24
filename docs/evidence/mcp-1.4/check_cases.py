"""Offline synthetic sum acceptance checker; not an MCP conformance validator."""
import argparse
import json
from pathlib import Path


def check(case):
    try:
        request, response = case['request'], case['response']
        args = request['params']['arguments']
        value = response['result']['structuredContent']['sum']
        return (
            request['jsonrpc'] == '2.0'
            and response['jsonrpc'] == '2.0'
            and request['method'] == 'tools/call'
            and request['params']['name'] == 'sum'
            and set(args) == {'a', 'b'}
            and type(args['a']) is int and type(args['b']) is int
            and request['id'] is not None and response['id'] is not None
            and type(request['id']) is type(response['id'])
            and request['id'] == response['id']
            and type(value) is int
            and value == args['a'] + args['b']
        )
    except (KeyError, TypeError, AttributeError):
        return False


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--cases', required=True, type=Path)
    parser.add_argument('--output', required=True, type=Path)
    options = parser.parse_args()
    if options.cases.resolve() == options.output.resolve():
        parser.error('output must differ from immutable input')
    data = json.loads(options.cases.read_text(encoding='utf-8-sig'))
    results = {case['case_id']: 'PASS' if check(case) else 'FAIL'
               for case in data['cases']}
    options.output.write_text(json.dumps(results, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(results, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
