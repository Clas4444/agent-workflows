import copy
import json
import unittest
from decimal import localcontext

from ledger import summarize


def row(identifier, category, currency, amount):
    return {'id': identifier, 'category': category, 'currency': currency, 'amount': amount}


class SummarizeTests(unittest.TestCase):
    def test_example_and_no_mutation(self):
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
            'row_count': 7,
            'complete': False,
            'groups': [
                {'category': 'Food', 'currency': 'EUR', 'known_total': '5.00', 'missing_ids': []},
                {'category': 'Food', 'currency': 'USD', 'known_total': '10.30', 'missing_ids': ['004']},
                {'category': 'Other', 'currency': 'JPY', 'known_total': None, 'missing_ids': ['007']},
                {'category': 'Travel', 'currency': 'USD', 'known_total': '0.00', 'missing_ids': []},
            ],
        })
        self.assertEqual(rows, original)
        self.assertEqual(json.loads(json.dumps(result)), result)
        self.assertIs(type(result['row_count']), int)
        self.assertIs(type(result['complete']), bool)

    def test_empty(self):
        self.assertEqual(summarize([]), {'row_count': 0, 'complete': True, 'groups': []})

    def test_missing_ids_preserve_source_order_and_duplicates(self):
        result = summarize([
            row('009', 'B', 'USD', ''),
            row('002', 'A', 'USD', ''),
            row('001', 'B', 'USD', ''),
            row('009', 'B', 'USD', ''),
        ])
        self.assertEqual(result['groups'][0]['missing_ids'], ['002'])
        self.assertEqual(result['groups'][1]['missing_ids'], ['009', '001', '009'])
        self.assertTrue(all(g['known_total'] is None for g in result['groups']))

    def test_exact_arithmetic_and_negative_fraction(self):
        result = summarize([
            row('1', 'A', 'USD', '0.10'),
            row('2', 'A', 'USD', '0.20'),
            row('3', 'A', 'USD', '-0.31'),
        ])
        self.assertEqual(result['groups'][0]['known_total'], '-0.01')
        self.assertIs(result['complete'], True)

    def test_known_zero_is_not_unknown(self):
        result = summarize([
            row('001', 'A', 'USD', '-0.00'),
            row('002', 'A', 'USD', ''),
        ])
        self.assertEqual(result['groups'][0]['known_total'], '0.00')
        self.assertEqual(result['groups'][0]['missing_ids'], ['002'])
        self.assertIs(result['complete'], False)

    def test_precision_independent_of_decimal_context(self):
        with localcontext() as context:
            context.prec = 3
            result = summarize([
                row('1', 'A', 'USD', '123456789012345678901234567890.12'),
                row('2', 'A', 'USD', '0.89'),
            ])
        self.assertEqual(result['groups'][0]['known_total'], '123456789012345678901234567891.01')

    def test_arbitrarily_large_integer_and_carry(self):
        amount = '9' * 5000 + '.99'
        result = summarize([
            row('1', 'A', 'USD', amount),
            row('2', 'A', 'USD', '0.01'),
        ])
        self.assertEqual(result['groups'][0]['known_total'], '1' + '0' * 5000 + '.00')

    def test_sorting_and_two_decimal_places(self):
        result = summarize(iter([
            row('1', 'Z', 'EUR', '2'),
            row('2', 'A', 'USD', '-1.2'),
            row('3', 'A', 'EUR', '3.4'),
        ]))
        self.assertEqual(
            [(g['category'], g['currency'], g['known_total']) for g in result['groups']],
            [('A', 'EUR', '3.40'), ('A', 'USD', '-1.20'), ('Z', 'EUR', '2.00')],
        )
        self.assertEqual(result['row_count'], 3)
        self.assertIs(result['complete'], True)


if __name__ == '__main__':
    unittest.main()
