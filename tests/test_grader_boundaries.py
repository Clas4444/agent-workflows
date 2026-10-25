"""A verifier must recheck protected inputs after running submitted programs."""
from pathlib import Path
import tempfile
import unittest

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
