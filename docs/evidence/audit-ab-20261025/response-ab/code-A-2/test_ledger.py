import copy
import json
import unittest
from decimal import localcontext

from ledger import summarize


class SummarizeTests(unittest.TestCase):
    def test_example_and_no_mutation(self):
        rows = [
            {'id': '001', 'category': 'Food', 'currency': 'USD', 'amount': '10.20'},
            {'id': '002', 'category': 'Food', 'currency': 'USD', 'amount': '0.10'},
            {'id': '003', 'category': 'Food', 'currency': 'EUR', 'amount': '5.00'},
            {'id': '004', 'category': 'Food', 'currency': 'USD', 'amount': ''},
            {'id': '005', 'category': 'Travel', 'currency': 'USD', 'amount': '-2.00'},
            {'id': '006', 'category': 'Travel', 'currency': 'USD', 'amount': '2.00'},
            {'id': '007', 'category': 'Other', 'currency': 'JPY', 'amount': ''},
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

    def test_missing_order_and_zero(self):
        rows = [
            {'id': '009', 'category': 'B', 'currency': 'USD', 'amount': ''},
            {'id': '002', 'category': 'A', 'currency': 'USD', 'amount': '0'},
            {'id': '001', 'category': 'B', 'currency': 'USD', 'amount': ''},
            {'id': '008', 'category': 'A', 'currency': 'EUR', 'amount': '-0.01'},
        ]
        result = summarize(iter(rows))
        self.assertEqual(result['row_count'], 4)
        self.assertFalse(result['complete'])
        self.assertEqual(result['groups'], [
            {'category': 'A', 'currency': 'EUR', 'known_total': '-0.01', 'missing_ids': []},
            {'category': 'A', 'currency': 'USD', 'known_total': '0.00', 'missing_ids': []},
            {'category': 'B', 'currency': 'USD', 'known_total': None, 'missing_ids': ['009', '001']},
        ])

    def test_exact_arithmetic_independent_of_decimal_context(self):
        amounts = ['123456789012345678901234567890.99', '0.02', '-0.01']
        rows = [dict(id=str(i), category='A', currency='USD', amount=a)
                for i, a in enumerate(amounts)]
        with localcontext() as context:
            context.prec = 3
            result = summarize(rows)
        self.assertTrue(result['complete'])
        self.assertEqual(result['groups'][0]['known_total'], '123456789012345678901234567891.00')

    def test_arbitrary_integer_precision(self):
        huge = '9' * 5000
        rows = [
            dict(id='001', category='A', currency='USD', amount=huge + '.99'),
            dict(id='002', category='A', currency='USD', amount='0.01'),
        ]
        self.assertEqual(summarize(rows)['groups'][0]['known_total'], '1' + '0' * 5000 + '.00')
        rows[0]['amount'] = '-' + huge + '.99'
        rows[1]['amount'] = '-0.01'
        self.assertEqual(summarize(rows)['groups'][0]['known_total'], '-1' + '0' * 5000 + '.00')

    def test_fraction_padding_and_negative_zero(self):
        for amount, expected in [('12', '12.00'), ('-1.2', '-1.20'), ('-0.00', '0.00')]:
            with self.subTest(amount=amount):
                result = summarize([dict(id='001', category='A', currency='USD', amount=amount)])
                self.assertEqual(result['groups'][0]['known_total'], expected)
                self.assertTrue(result['complete'])


if __name__ == '__main__':
    unittest.main()
