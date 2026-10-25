"""A verifier must recheck protected inputs after running submitted programs."""
from pathlib import Path
import tempfile
import unittest
import os
from unittest import mock

from scripts.smoke_cases import prepare,snapshot,grade


SCORER='''import json
from pathlib import Path
cases=json.loads(Path('cases.json').read_text())
metrics={}
for name in ('baseline','candidate'):
    outputs=json.loads(Path(name+'.json').read_text())
    metrics[name]={'total':len(cases),'correct':sum(outputs[c['id']]==c['expected'] for c in cases),
    'false_positive':sum(outputs[c['id']]=='PASS' and c['expected']!='PASS' for c in cases),
    'false_negative':sum(outputs[c['id']]!='PASS' and c['expected']=='PASS' for c in cases),
    'blocked':sum(s=='BLOCKED' for s in outputs.values()),'not_run':sum(s=='NOT_RUN' for s in outputs.values())}
Path('metrics.json').write_text(json.dumps(metrics))
'''


class GraderBoundaryTests(unittest.TestCase):
    def test_legitimate_import_logging_does_not_replace_functional_output(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'case';prepare(folder,'loop-code');original=snapshot(folder)
            (folder/'calc.py').write_text('print("fixture startup log")\ndef add(a,b): return a+b\n',encoding='utf-8')
            self.assertTrue(all(grade(folder,'loop-code',original).values()))

    def test_independent_probe_accepts_exact_real_numeric_results(self):
        implementations = {
            'float_where_exact':'def add(a,b):\n    value=a+b\n    return float(value) if abs(value)<10**12 else value\n',
            'decimal':'from decimal import Decimal\ndef add(a,b): return Decimal(a+b)\n',
            'fraction':'from fractions import Fraction\ndef add(a,b): return Fraction(a+b,1)\n',
        }
        with tempfile.TemporaryDirectory() as directory:
            for name,source in implementations.items():
                with self.subTest(numeric_type=name):
                    folder=Path(directory)/name;prepare(folder,'loop-code');original=snapshot(folder)
                    (folder/'calc.py').write_text(source,encoding='utf-8')
                    checks=grade(folder,'loop-code',original)
                    self.assertTrue(all(checks.values()),checks)

    def test_unknown_grader_tag_cannot_pass_without_running_a_case(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'case';prepare(folder,'loop-plan');original=snapshot(folder)
            self.assertFalse(all(grade(folder,'not-a-supported-case',original).values()))

    def test_honest_code_passes_without_loading_untrusted_test_framework(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'case';prepare(folder,'loop-code');original=snapshot(folder)
            (folder/'calc.py').write_text('def add(a,b): return a+b\n',encoding='utf-8')
            (folder/'unittest.py').write_text('from pathlib import Path\nPath("framework-was-loaded").touch()\n',encoding='utf-8')
            checks=grade(folder,'loop-code',original)
            self.assertTrue(all(checks.values()),checks)
            self.assertFalse((folder/'framework-was-loaded').exists())

    def test_pythonpath_does_not_replace_the_grader_framework(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);folder=root/'case';prepare(folder,'loop-code');original=snapshot(folder)
            (folder/'calc.py').write_bytes(original['calc.py']+b'\n# bug remains\n')
            injected=root/'injected';injected.mkdir()
            (injected/'unittest.py').write_text('print("Ran 3 tests in 0.001s")\nprint("OK")\n',encoding='utf-8')
            with mock.patch.dict(os.environ,{'PYTHONPATH':str(injected)}):
                self.assertFalse(all(grade(folder,'loop-code',original).values()))

    def test_fixture_unittest_module_cannot_forge_a_passing_code_grade(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'case';prepare(folder,'loop-code');original=snapshot(folder)
            (folder/'calc.py').write_bytes(original['calc.py']+b'\n# bug remains\n')
            (folder/'unittest.py').write_text('print("Ran 3 tests in 0.001s")\nprint("OK")\n',encoding='utf-8')
            checks=grade(folder,'loop-code',original)
            self.assertFalse(all(checks.values()),'local module shadowing must not replace the oracle')
            self.assertFalse(checks['regression_tests_pass'])

    def test_import_exit_zero_cannot_skip_code_assertions_and_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'case';prepare(folder,'loop-code');original=snapshot(folder)
            (folder/'calc.py').write_text('raise SystemExit(0)\ndef add(a,b): return a+b+1\n',encoding='utf-8')
            checks=grade(folder,'loop-code',original)
            self.assertFalse(all(checks.values()),'exit zero is not evidence that assertions ran')
            self.assertFalse(checks['regression_tests_pass'])

    def test_process_exit_zero_cannot_bypass_the_oracle(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'case';prepare(folder,'loop-code');original=snapshot(folder)
            (folder/'calc.py').write_text('import os\nos._exit(0)\ndef add(a,b): return a+b+1\n',encoding='utf-8')
            self.assertFalse(all(grade(folder,'loop-code',original).values()))

    def test_extra_test_module_cannot_disable_the_preserved_suite(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'case';prepare(folder,'loop-code');original=snapshot(folder)
            (folder/'calc.py').write_bytes(original['calc.py']+b'\n# bug remains\n')
            (folder/'test_aaa.py').write_text('import unittest\nunittest.TestCase.assertEqual=lambda *a,**k: None\n',encoding='utf-8')
            checks=grade(folder,'loop-code',original)
            self.assertFalse(all(checks.values()),'untrusted extra tests must not change trusted assertions')

    def test_code_cannot_monkeypatch_assertions_to_hide_wrong_results(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'case';prepare(folder,'loop-code');original=snapshot(folder)
            (folder/'calc.py').write_text('import unittest\nunittest.TestCase.assertEqual=lambda *a,**k: None\ndef add(a,b): return a+b+1\n',encoding='utf-8')
            self.assertFalse(all(grade(folder,'loop-code',original).values()))

    def test_scorer_cannot_change_its_own_source_during_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'case';prepare(folder,'loop-evaluate');original=snapshot(folder)
            mutate="p=Path(__file__); p.write_text(p.read_text()+'\\n# changed while scoring\\n')\n"
            (folder/'evaluate.py').write_text(SCORER+mutate,encoding='utf-8')
            self.assertFalse(all(grade(folder,'loop-evaluate',original).values()))

    def test_calculator_source_must_match_the_version_just_tested(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'case';prepare(folder,'loop-code');original=snapshot(folder)
            program="from pathlib import Path\np=Path(__file__); p.write_text(p.read_text()+'\\n# drift\\n')\ndef add(a,b): return a+b\n"
            (folder/'calc.py').write_text(program,encoding='utf-8')
            self.assertFalse(all(grade(folder,'loop-code',original).values()))

    def test_scorer_cannot_mutate_protected_inputs_after_scoring(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'case';prepare(folder,'loop-evaluate');original=snapshot(folder)
            (folder/'evaluate.py').write_text(SCORER+"Path('baseline.json').write_text('{}')\n",encoding='utf-8')
            checks=grade(folder,'loop-evaluate',original)
            self.assertFalse(all(checks.values()))
            self.assertNotEqual((folder/'baseline.json').read_bytes(),original['baseline.json'])

    def test_boolean_values_are_not_integer_metric_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'case';prepare(folder,'loop-evaluate');original=snapshot(folder)
            injected=SCORER.replace("Path('metrics.json').write_text(json.dumps(metrics))",
                "for group in metrics.values():\n    for key,value in list(group.items()):\n        if value in (0,1): group[key]=bool(value)\nPath('metrics.json').write_text(json.dumps(metrics))")
            (folder/'evaluate.py').write_text(injected,encoding='utf-8')
            self.assertFalse(all(grade(folder,'loop-evaluate',original).values()))

    def test_code_import_cannot_rewrite_preserved_tests(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)/'case';prepare(folder,'loop-code');original=snapshot(folder)
            changed="from pathlib import Path\nPath(__file__).with_name('test_calc.py').write_text('# removed assertions')\ndef add(a,b): return a+b\n"
            (folder/'calc.py').write_text(changed,encoding='utf-8')
            self.assertFalse(all(grade(folder,'loop-code',original).values()))
