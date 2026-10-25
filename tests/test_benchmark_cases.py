"""Independent controls for the small benchmark's frozen artifact oracle.

These exercise the checker, not model performance. Reference implementation is
derived from TASK contracts and never used as an agent-produced benchmark result.
"""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts import benchmark_cases as bench


REFERENCE = '''from decimal import Decimal, localcontext
def summarize(rows):
    grouped = {}
    for row in rows:
        bucket = grouped.setdefault((row['category'], row['currency']), [[], []])
        if row['amount'].strip():
            bucket[0].append(row['amount'])
        else:
            bucket[1].append(row['id'])
    groups = []
    for (category, currency), (amounts, missing) in sorted(grouped.items()):
        with localcontext() as context:
            context.prec = max([len(x) for x in amounts] + [1]) + len(str(len(rows))) + 10
            total = format(sum((Decimal(x) for x in amounts), Decimal(0)), '.2f') if amounts else None
        groups.append(dict(category=category, currency=currency, known_total=total, missing_ids=missing))
    result = {'row_count':len(rows), 'complete':all(not x['missing_ids'] for x in groups), 'groups':groups}
    return result
'''


class BenchmarkCasesTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'case'

    def office(self):
        bench.prepare(self.root, 'office')
        source_hash = bench.digest(self.root / 'expenses.csv')
        (self.root / 'report.json').write_text(json.dumps(bench.EXPECTED), encoding='utf-8')
        (self.root / 'briefing.md').write_text(
            'Known Food subtotals: USD 10.30 and EUR 5.00. Travel USD 0.00. '
            'Amounts for source IDs 004 and 007 are missing; JPY has no known total. '
            'These are incomplete known-value subtotals, with no currency conversion.',
            encoding='utf-8')
        return source_hash

    def code(self, source=REFERENCE):
        bench.prepare(self.root, 'code')
        (self.root / 'ledger.py').write_text(source, encoding='utf-8')

    def test_controls_include_real_rejections(self):
        controls = bench.controls()
        self.assertEqual([row['id'] for row in controls],
                         ['correct', 'wrong', 'missing', 'valid-format-wrong-content'])
        self.assertEqual([row['accepted'] for row in controls], [True, False, False, False])
        self.assertTrue(all(row['accepted'] == row['expected_accept'] for row in controls))
        self.assertTrue(all(row['errors'] for row in controls[1:]))

    def test_report_types_are_not_coerced(self):
        for key, value in [('row_count', True), ('row_count', '7'), ('complete', 0)]:
            with self.subTest(key=key, value=value):
                report = copy.deepcopy(bench.EXPECTED)
                report[key] = value
                self.assertTrue(bench.validate_report(report))

    def test_report_missing_extra_and_wrong_numeric_content_rejected(self):
        missing = copy.deepcopy(bench.EXPECTED)
        del missing['groups']
        extra = dict(bench.EXPECTED, explanation='not in schema')
        wrong = copy.deepcopy(bench.EXPECTED)
        wrong['groups'][1]['known_total'] = '15.30'
        for report in (missing, extra, wrong, [], None):
            with self.subTest(report=report):
                self.assertTrue(bench.validate_report(report))

    def test_office_correct_saved_artifacts_and_source_preservation(self):
        source_hash = self.office()
        self.assertEqual(bench.check_office(self.root, source_hash), [])
        self.assertEqual(bench.digest(self.root / 'expenses.csv'), source_hash)

    def test_office_missing_artifact_is_not_accepted(self):
        source_hash = self.office()
        (self.root / 'report.json').unlink()
        with self.assertRaises(FileNotFoundError):
            bench.check_office(self.root, source_hash)
        result = subprocess.run([sys.executable, str(Path(bench.__file__)), 'check',
                                 '--case', 'office', '--root', str(self.root),
                                 '--source-hash', source_hash], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)['status'], 'FAIL')

    def test_office_source_alteration_is_rejected(self):
        source_hash = self.office()
        with (self.root / 'expenses.csv').open('a', encoding='utf-8') as stream:
            stream.write('008,Food,USD,100.00\n')
        self.assertIn('source CSV changed', bench.check_office(self.root, source_hash))

    def test_office_duplicate_escaped_equivalent_key_is_rejected(self):
        source_hash = self.office()
        report = json.dumps(bench.EXPECTED)
        report = '{"row_\\u0063ount": 7,' + report[1:]
        (self.root / 'report.json').write_text(report, encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'duplicate JSON key'):
            bench.check_office(self.root, source_hash)

    def test_office_requires_missing_data_disclosure(self):
        source_hash = self.office()
        (self.root / 'briefing.md').write_text('USD EUR JPY 004 007 10.30 5.00', encoding='utf-8')
        self.assertIn('briefing does not disclose missing data',
                      bench.check_office(self.root, source_hash))

    def test_office_requires_actual_briefing_file(self):
        source_hash = self.office()
        (self.root / 'briefing.md').unlink()
        with self.assertRaises(FileNotFoundError):
            bench.check_office(self.root, source_hash)

    def test_code_starter_is_rejected(self):
        self.code(bench.STARTER)
        errors = bench.check_code(self.root)
        self.assertIn('input rows were mutated', errors)
        self.assertTrue(any('report' in value for value in errors))

    def test_code_hardcoded_fixture_answer_is_rejected(self):
        self.code('def summarize(rows):\n    return ' + repr(bench.EXPECTED) + '\n')
        errors = bench.check_code(self.root)
        self.assertIn('empty input is incorrect', errors)
        self.assertIn('unseen high-precision inputs are incorrect', errors)

    def test_code_reference_is_exact_nonmutating_and_accepted(self):
        self.code()
        before = bench.digest(self.root / 'ledger.py')
        self.assertEqual(bench.check_code(self.root), [])
        self.assertEqual(bench.digest(self.root / 'ledger.py'), before)

    def test_code_boolean_empty_count_cannot_pass_as_integer_zero(self):
        self.code(REFERENCE.replace("'row_count':len(rows)",
                                    "'row_count':False if not rows else len(rows)"))
        self.assertIn('empty input is incorrect', bench.check_code(self.root))

    def test_code_unseen_rows_must_also_remain_unchanged(self):
        self.code(REFERENCE.replace('    return result\n',
                  "    if rows and rows[0]['id'] == '009':\n"
                  "        rows[0]['amount'] = '0.00'\n"
                  '    return result\n'))
        self.assertIn('unseen input rows were mutated', bench.check_code(self.root))


if __name__ == '__main__':
    unittest.main()
