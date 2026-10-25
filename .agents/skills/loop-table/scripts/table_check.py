#!/usr/bin/env python3
"""Read-only CSV inspection and exact, unit-separated aggregation; no spreadsheet engine."""
import argparse
import csv
from decimal import Decimal, localcontext
import hashlib
import io
import json
from pathlib import Path
import re
import sys

NUMBER = re.compile(r'[+-]?(?:[0-9]+(?:\.[0-9]*)?|\.[0-9]+)\Z')


def read_table(path, delimiter=',', max_rows=100000):
    if len(delimiter)!=1 or delimiter in '\r\n\x00"' or max_rows<=0:
        raise ValueError('use a single safe delimiter and a positive row limit')
    raw = path.read_bytes()
    reader = csv.reader(io.StringIO(raw.decode('utf-8-sig'),newline=''),delimiter=delimiter,strict=True)
    try:
        headers = next(reader)
    except StopIteration:
        raise ValueError('CSV has no header')
    normalized = [value.strip().casefold() for value in headers]
    if not headers or any(not value for value in normalized) or len(set(normalized))!=len(headers):
        raise ValueError('CSV headers must be non-empty and unambiguous after trimming/case folding')
    rows = []
    for index, values in enumerate(reader,1):
        if index>max_rows:
            raise ValueError(f'CSV exceeds row limit {max_rows}')
        if len(values)!=len(headers):
            raise ValueError(f'CSV record {index} has {len(values)} fields; expected {len(headers)}')
        rows.append(values)
    return {'headers':headers,'rows':rows,'source_sha256':hashlib.sha256(raw).hexdigest()}


def inspect_table(table):
    headers, rows = table['headers'], table['rows']
    formula_text = []
    for number, row in enumerate(rows,1):
        for header, value in zip(headers,row):
            text = value.lstrip()
            if text.startswith(('=','@')) or (text.startswith(('+','-')) and not NUMBER.fullmatch(text)):
                formula_text.append({'record':number,'column':header})
    return {'status':'PASS','source_sha256':table['source_sha256'],'headers':headers,
            'row_count':len(rows),'blank_cells':{header:sum(not row[i].strip() for row in rows)
                                               for i,header in enumerate(headers)},
            'formula_like_text':formula_text,'formula_execution':'NOT_RUN',
            'scope':'UTF-8 CSV structure only; cell strings are never executed or rewritten.'}


def aggregate(table, value_column, group_column=None, unit_column=None, unit_label=None, allow_missing=False):
    if (unit_column is None)==(unit_label is None):
        raise ValueError('select exactly one unit column or explicit single-unit label')
    if unit_label is not None and not unit_label.strip():
        raise ValueError('unit label cannot be empty')
    headers = table['headers']
    for field in (value_column,group_column,unit_column):
        if field is not None and field not in headers:
            raise ValueError(f'unknown column: {field}')
    vi = headers.index(value_column)
    gi = headers.index(group_column) if group_column is not None else None
    ui = headers.index(unit_column) if unit_column is not None else None
    buckets = {}
    missing = []
    integer_digits, fractional_digits = 1, 0
    for number,row in enumerate(table['rows'],1):
        group = row[gi] if gi is not None else ''
        unit = row[ui] if ui is not None else unit_label
        if not unit.strip():
            raise ValueError(f'empty unit at CSV record {number}')
        bucket = buckets.setdefault((group,unit),{'records':0,'values':[]})
        bucket['records'] += 1
        text = row[vi].strip()
        if not text:
            if not allow_missing:
                raise ValueError(f'missing numeric value at CSV record {number}; no complete aggregate')
            missing.append(number)
            continue
        if not NUMBER.fullmatch(text):
            raise ValueError(f'invalid decimal at CSV record {number}; no aggregate produced')
        number_value = Decimal(text)
        digits = number_value.as_tuple()
        integer_digits = max(integer_digits,len(digits.digits)+digits.exponent)
        fractional_digits = max(fractional_digits,-digits.exponent)
        bucket['values'].append(number_value)
    results = []
    with localcontext() as context:
        context.prec = integer_digits+fractional_digits+len(str(len(table['rows'])+1))+4
        for (group,unit),bucket in sorted(buckets.items()):
            values = bucket['values']
            total = format(sum(values,Decimal(0)),'f') if values else None
            results.append({'group':group,'unit':unit,'records':bucket['records'],
                            'known_values':len(values),'known_value_sum':total})
    return {'status':'PASS','source_sha256':table['source_sha256'],'row_count':len(table['rows']),
            'complete':not missing,'missing_value_records':missing,'subtotals':results,
            'unit_policy':'separate exact labels; no conversion or assumed exchange rate',
            'source_modification':'NOT_RUN','scope':'Known-value sums only; incomplete data is explicitly marked.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('mode',choices=('inspect','aggregate'))
    parser.add_argument('input',type=Path)
    parser.add_argument('--delimiter',default=',',help='One delimiter character, or \\t for tab')
    parser.add_argument('--max-rows',type=int,default=100000)
    parser.add_argument('--value')
    parser.add_argument('--group')
    units = parser.add_mutually_exclusive_group()
    units.add_argument('--unit')
    units.add_argument('--unit-label')
    parser.add_argument('--allow-missing',action='store_true')
    args = parser.parse_args()
    if hasattr(sys.stdout,'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    try:
        table = read_table(args.input,'\t' if args.delimiter=='\\t' else args.delimiter,args.max_rows)
        if args.mode=='inspect':
            result = inspect_table(table)
        else:
            if not args.value:
                parser.error('aggregate requires --value and --unit or --unit-label')
            result = aggregate(table,args.value,args.group,args.unit,args.unit_label,args.allow_missing)
        print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (OSError,ValueError,csv.Error) as exc:
        parser.exit(1,f'FAIL: {exc}\n')


if __name__=='__main__':
    raise SystemExit(main())
