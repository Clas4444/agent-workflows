import json
import ast
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.runtime_smoke import classify,parse_response
from scripts.smoke_cases import prepare,snapshot,grade,NEW_SKILLS

class RuntimeSmokeTests(unittest.TestCase):
    def test_production_text_io_declares_encoding(self):
        scripts=Path(__file__).resolve().parents[1]/'scripts'
        missing=[]
        for path in scripts.glob('*.py'):
            for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute) and node.func.attr in ('read_text','write_text'):
                    if not any(keyword.arg=='encoding' for keyword in node.keywords):
                        missing.append((path.name,node.lineno))
        self.assertEqual(missing,[])
    def test_usage_limit_is_blocked_even_with_pass_response(self):
        self.assertEqual(classify(1,'ERROR: usage limit',{'status':'PASS'}),'BLOCKED')
        self.assertEqual(classify(0,'rate limit',{'status':'PASS'}),'BLOCKED')

    def test_success_needs_zero_exit_and_pass_response(self):
        self.assertEqual(classify(0,'',{'status':'PASS'}),'PASS')
        self.assertEqual(classify(1,'',{'status':'PASS'}),'FAIL')
        self.assertEqual(classify(0,'',{}),'FAIL')

    def test_runtime_summary_preserves_nonexecuted_and_blocked_statuses(self):
        self.assertEqual(classify(0,'',{'status':'NOT_RUN'}),'NOT_RUN')
        self.assertEqual(classify(0,'',{'status':'BLOCKED'}),'BLOCKED')
        self.assertEqual(classify(1,'',{'status':'NOT_RUN'}),'FAIL')

    def test_parse_response_rejects_nonobject_and_malformed(self):
        self.assertEqual(parse_response('[]'),{})
        self.assertEqual(parse_response('bad json'),{})
        self.assertEqual(parse_response('```json\n{"status":"PASS"}\n```'),{'status':'PASS'})

    def test_cli_requires_explicit_model_authorization(self):
        script=Path(__file__).resolve().parents[1]/'scripts/runtime_smoke.py'
        result=subprocess.run([sys.executable,str(script),'--skill-root','.','--output-dir','unused'],capture_output=True,timeout=15)
        self.assertEqual(result.returncode,2)
        self.assertIn(b'authorization',result.stderr)

    def test_fixture_requires_fresh_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'case';prepare(folder,'loop-plan')
            (folder/'calc.py').write_text('keep existing attempt', encoding='utf-8')
            with self.assertRaises(FileExistsError):prepare(folder,'loop-plan')
            self.assertEqual((folder/'calc.py').read_text(encoding='utf-8'),'keep existing attempt')

    def test_unsupported_case_does_not_create_directory(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'unknown'
            with self.assertRaises(ValueError):prepare(folder,'unknown')
            self.assertFalse(folder.exists())

    def test_missing_artifacts_never_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            for skill in NEW_SKILLS:
                folder=Path(temp)/skill;prepare(folder,skill)
                self.assertFalse(all(grade(folder,skill,snapshot(folder)).values()),skill)

    def test_plan_requires_contract_and_preserved_source(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'case';prepare(folder,'loop-plan');before=snapshot(folder)
            (folder/'plan.md').write_text('Acceptance; out-of-scope; batches; verification; rollback', encoding='utf-8')
            self.assertTrue(all(grade(folder,'loop-plan',before).values()))
            (folder/'plan.md').write_text('Acceptance; out of scope; batches; verification; rollback', encoding='utf-8')
            self.assertTrue(all(grade(folder,'loop-plan',before).values()))
            (folder/'plan.md').write_text('Acceptance; batches; verification; rollback', encoding='utf-8')
            self.assertFalse(all(grade(folder,'loop-plan',before).values()))
            (folder/'plan.md').write_text('Acceptance; out of scope; batches; verification; rollback', encoding='utf-8')
            (folder/'calc.py').write_text('changed', encoding='utf-8')
            self.assertFalse(all(grade(folder,'loop-plan',before).values()))

    def test_plan_accepts_utf8_report_on_windows_locales(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'case';prepare(folder,'loop-plan');before=snapshot(folder)
            (folder/'plan.md').write_text('Acceptance \u201cJSON\u201d; out of scope; batches; verification; rollback',encoding='utf-8')
            self.assertTrue(all(grade(folder,'loop-plan',before).values()))

    def test_dependency_grader_rejects_drift_and_unrelated_change(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'case';prepare(folder,'loop-dependencies');before=snapshot(folder)
            (folder/'manifest.before.json').write_bytes(before['manifest.json'])
            versions={'fixture-lib':'1.1.0','keep-lib':'2.0.0'}
            (folder/'manifest.json').write_text(json.dumps({'dependencies':versions}), encoding='utf-8')
            self.assertFalse(all(grade(folder,'loop-dependencies',before).values()))
            (folder/'lock.json').write_text(json.dumps({'packages':versions}), encoding='utf-8')
            self.assertTrue(all(grade(folder,'loop-dependencies',before).values()))
            versions['keep-lib']='3.0.0'
            (folder/'lock.json').write_text(json.dumps({'packages':versions}), encoding='utf-8')
            self.assertFalse(all(grade(folder,'loop-dependencies',before).values()))

    def test_evaluation_grader_rejects_hardcoded_totals(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'case';prepare(folder,'loop-evaluate');before=snapshot(folder)
            metrics={'baseline':{'total':6,'correct':4,'false_positive':1,'false_negative':1,'blocked':1,'not_run':1},
                     'candidate':{'total':6,'correct':6,'false_positive':0,'false_negative':0,'blocked':1,'not_run':1}}
            (folder/'evaluate.py').write_text("from pathlib import Path\nPath('metrics.json').write_text("+repr(json.dumps(metrics))+")\n", encoding='utf-8')
            result=grade(folder,'loop-evaluate',before)
            self.assertTrue(result['fixed_rubric_metrics'])
            self.assertFalse(result['perturbed_outputs_scored'])

    def test_evaluation_grader_accepts_actual_scoring_and_repeat_verification(self):
        scorer='''import json
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
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'case';prepare(folder,'loop-evaluate');before=snapshot(folder)
            (folder/'evaluate.py').write_text(scorer, encoding='utf-8')
            self.assertTrue(all(grade(folder,'loop-evaluate',before).values()))
            self.assertTrue(all(grade(folder,'loop-evaluate',before).values()))
            self.assertTrue((folder/'independent-evaluation-2').is_dir())

    def test_evaluation_grader_rejects_undocumented_report_dependency(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'case';prepare(folder,'loop-evaluate');before=snapshot(folder)
            metrics={'baseline':{'total':6,'correct':4,'false_positive':1,'false_negative':1,'blocked':1,'not_run':1},
                     'candidate':{'total':6,'correct':6,'false_positive':0,'false_negative':0,'blocked':1,'not_run':1}}
            (folder/'evidence.md').write_text('existing report', encoding='utf-8')
            (folder/'evaluate.py').write_text("from pathlib import Path\nPath('evidence.md').read_text()\nPath('metrics.json').write_text("+repr(json.dumps(metrics))+")\n", encoding='utf-8')
            checks=grade(folder,'loop-evaluate',before)
            self.assertFalse(checks.get('artifact_verification',True))
