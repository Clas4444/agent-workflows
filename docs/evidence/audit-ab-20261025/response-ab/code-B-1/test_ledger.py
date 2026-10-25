"""Regression checks. Execution status: NOT_RUN (generation-only mode).
Planned command: python -m unittest -v test_ledger.py
The supplied implementation mutates rows, uses floats, and groups only by category.
"""
import copy
import json
import unittest
from decimal import localcontext

from ledger import summarize


class SummarizeTests(unittest.TestCase):
    def test_supplied_example(self):
        rows = [
            {'id': '001', 'category': 'Food', 'currency': 'USD', 'amount': '10.20'},
            {'id': '002', 'category': 'Food', 'currency': 'USD', 'amount': '0.10'},
            {'id': '003', 'category': 'Food', 'currency': 'EUR', 'amount': '5.00'},
            {'id': '004', 'category': 'Food', 'currency': 'USD', 'amount': ''},
            {'id': '005', 'category': 'Travel', 'currency': 'USD', 'amount': '-2.00'},
            {'id': '006', 'category': 'Travel', 'currency': 'USD', 'amount': '2.00'},
            {'id': '007', 'category': 'Other', 'currency': 'JPY', 'amount': ''},
        ]
        before = copy.deepcopy(rows)
        expected = {
            'row_count': 7, 'complete': False,
            'groups': [
                {'category': 'Food', 'currency': 'EUR', 'known_total': '5.00', 'missing_ids': []},
                {'category': 'Food', 'currency': 'USD', 'known_total': '10.30', 'missing_ids': ['004']},
                {'category': 'Other', 'currency': 'JPY', 'known_total': None, 'missing_ids': ['007']},
                {'category': 'Travel', 'currency': 'USD', 'known_total': '0.00', 'missing_ids': []},
            ],
        }
        actual = summarize(rows)
        self.assertEqual(actual, expected)
        self.assertEqual(rows, before)
        self.assertEqual(summarize(rows), expected)
        self.assertEqual(json.loads(json.dumps(actual)), expected)
        self.assertIs(type(actual['row_count']), int)
        self.assertIs(type(actual['complete']), bool)

    def test_empty(self):
        self.assertEqual(summarize([]), {'row_count': 0, 'complete': True, 'groups': []})

    def test_missing_ids_preserve_source_order_and_leading_zeros(self):
        rows = [
            {'id': identifier, 'category': 'A', 'currency': 'USD', 'amount': amount}
            for identifier, amount in [('009', ''), ('001', '0'), ('003', ''), ('009', '')]
        ]
        result = summarize(rows)
        self.assertFalse(result['complete'])
        self.assertEqual(result['groups'], [
            {'category': 'A', 'currency': 'USD', 'known_total': '0.00', 'missing_ids': ['009', '003', '009']}
        ])

    def test_exact_arithmetic_and_decimal_context_independence(self):
        amounts = ['123456789012345678901234567890.99', '0.02', '-123456789012345678901234567890', '-1.2']
        rows = [{'id': str(i), 'category': 'A', 'currency': 'USD', 'amount': a} for i, a in enumerate(amounts)]
        with localcontext() as context:
            context.prec = 2
            result = summarize(rows)
        self.assertTrue(result['complete'])
        self.assertEqual(result['groups'][0]['known_total'], '-0.19')

    def test_arbitrary_integer_precision(self):
        digits = '9' * 6000
        rows = [
            {'id': '01', 'category': 'A', 'currency': 'USD', 'amount': digits + '.99'},
            {'id': '02', 'category': 'A', 'currency': 'USD', 'amount': '0.01'},
        ]
        self.assertEqual(summarize(rows)['groups'][0]['known_total'], '1' + '0' * 6000 + '.00')

    def test_sorting_and_negative_zero(self):
        rows = [
            {'id': '1', 'category': 'B', 'currency': 'AUD', 'amount': '-0.00'},
            {'id': '2', 'category': 'A', 'currency': 'USD', 'amount': '-0.01'},
            {'id': '3', 'category': 'A', 'currency': 'EUR', 'amount': '2.5'},
        ]
        result = summarize(rows)
        self.assertEqual(result['groups'], [
            {'category': 'A', 'currency': 'EUR', 'known_total': '2.50', 'missing_ids': []},
            {'category': 'A', 'currency': 'USD', 'known_total': '-0.01', 'missing_ids': []},
            {'category': 'B', 'currency': 'AUD', 'known_total': '0.00', 'missing_ids': []},
        ])
        self.assertTrue(result['complete'])


if __name__ == '__main__':
    unittest.main()
