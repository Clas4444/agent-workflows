"""Regression tests. Execution status: NOT_RUN (generation-only mode).

Intended command: python -m unittest -v test_ledger.py
The supplied implementation mutates rows, uses inexact floats, merges currencies,
and omits the required output structure. Baseline and fix verification: NOT_RUN.
"""

import copy
import json
import unittest
from decimal import localcontext

from ledger import summarize


def row(identifier, category, currency, amount):
    return {'id': identifier, 'category': category, 'currency': currency, 'amount': amount}


def group(category, currency, total, missing=None):
    return {'category': category, 'currency': currency, 'known_total': total,
            'missing_ids': [] if missing is None else missing}


class SummarizeTests(unittest.TestCase):
    def test_supplied_example(self):
        rows = [
            row('001', 'Food', 'USD', '10.20'),
            row('002', 'Food', 'USD', '0.10'),
            row('003', 'Food', 'EUR', '5.00'),
            row('004', 'Food', 'USD', ''),
            row('005', 'Travel', 'USD', '-2.00'),
            row('006', 'Travel', 'USD', '2.00'),
            row('007', 'Other', 'JPY', ''),
        ]
        original = copy.deepcopy(rows)
        result = summarize(rows)
        self.assertEqual(result, {
            'row_count': 7, 'complete': False,
            'groups': [group('Food', 'EUR', '5.00'),
                       group('Food', 'USD', '10.30', ['004']),
                       group('Other', 'JPY', None, ['007']),
                       group('Travel', 'USD', '0.00')],
        })
        self.assertEqual(rows, original)
        self.assertEqual(json.loads(json.dumps(result)), result)
        self.assertIs(type(result['row_count']), int)
        self.assertIs(type(result['complete']), bool)

    def test_empty(self):
        self.assertEqual(summarize([]), {'row_count': 0, 'complete': True, 'groups': []})

    def test_sorting_and_missing_source_order(self):
        rows = [row('009', 'Z', 'USD', ''), row('007', 'A', 'USD', ''),
                row('001', 'Z', 'USD', ''), row('008', 'A', 'EUR', '1'),
                row('007', 'A', 'USD', '')]
        self.assertEqual(summarize(rows), {
            'row_count': 5, 'complete': False,
            'groups': [group('A', 'EUR', '1.00'),
                       group('A', 'USD', None, ['007', '007']),
                       group('Z', 'USD', None, ['009', '001'])],
        })

    def test_exact_arithmetic_independent_of_decimal_context(self):
        rows = [row('1', 'A', 'USD', '999999999999999999999999999999.99'),
                row('2', 'A', 'USD', '0.02'),
                row('3', 'B', 'USD', '-0.10'),
                row('4', 'B', 'USD', '-0.20')]
        with localcontext() as context:
            context.prec = 2
            result = summarize(rows)
        self.assertEqual(result, {
            'row_count': 4, 'complete': True,
            'groups': [group('A', 'USD', '1000000000000000000000000000000.01'),
                       group('B', 'USD', '-0.30')],
        })

    def test_arbitrary_integer_precision(self):
        huge = '9' * 5000
        result = summarize([row('001', 'A', 'USD', huge + '.99'),
                            row('002', 'A', 'USD', '0.01')])
        self.assertEqual(result['groups'], [group('A', 'USD', '1' + '0' * 5000 + '.00')])

    def test_zero_is_known_and_negative_zero_is_normalized(self):
        result = summarize([row('01', 'A', 'USD', '0'),
                            row('02', 'B', 'USD', '-0.00'),
                            row('03', 'C', 'USD', '-0.01')])
        self.assertEqual(result, {
            'row_count': 3, 'complete': True,
            'groups': [group('A', 'USD', '0.00'), group('B', 'USD', '0.00'),
                       group('C', 'USD', '-0.01')],
        })

    def test_unknown_and_known_zero_are_distinct(self):
        rows = [row('0001', 'A', 'USD', ''), row('0002', 'A', 'USD', '0.00')]
        original = copy.deepcopy(rows)
        self.assertEqual(summarize(rows), {
            'row_count': 2, 'complete': False,
            'groups': [group('A', 'USD', '0.00', ['0001'])],
        })
        self.assertEqual(rows, original)

    def test_iterable_and_repeated_calls(self):
        rows = [row('01', 'A', 'EUR', '1.2'), row('02', 'A', 'EUR', '-2')]
        expected = {'row_count': 2, 'complete': True,
                    'groups': [group('A', 'EUR', '-0.80')]}
        self.assertEqual(summarize(iter(rows)), expected)
        self.assertEqual(summarize(rows), expected)
        self.assertEqual(summarize(rows), expected)

    def test_blank_variants(self):
        result = summarize([row('001', 'A', 'USD', None), row('002', 'A', 'USD', '  ')])
        self.assertEqual(result, {'row_count': 2, 'complete': False,
                                 'groups': [group('A', 'USD', None, ['001', '002'])]})


if __name__ == '__main__':
    unittest.main()
