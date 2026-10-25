import json
import ast
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.runtime_smoke import classify,parse_response,run_case
from scripts.smoke_cases import prepare,snapshot,grade,NEW_SKILLS

class RuntimeSmokeTests(unittest.TestCase):
    def test_instruction_change_during_host_call_cannot_receive_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp); skill_root=root/'instructions'; folder=root/'case'
            instruction=skill_root/'loop-plan/SKILL.md'
            instruction.parent.mkdir(parents=True); instruction.write_bytes(b'original instructions')
            before=hashlib.sha256(instruction.read_bytes()).hexdigest()
            def host_boundary(argv,**kwargs):
                # A deterministic host stub, not a model call: emulate an install update.
                instruction.write_bytes(b'changed while host was running')
                (folder/'plan.md').write_text('Acceptance; out of scope; batches; verification; rollback',encoding='utf-8')
                (folder/'evidence.md').write_text('retained observation',encoding='utf-8')
                (folder/'response.json').write_text(json.dumps({'skill':'loop-plan','status':'PASS',
                    'loaded_skill_path':str(instruction.resolve())}),encoding='utf-8')
                return subprocess.CompletedProcess(argv,0)
            with mock.patch('scripts.runtime_smoke.subprocess.run',side_effect=host_boundary):
                row=run_case(folder,'loop-plan',skill_root,'host-stub',10)
            self.assertEqual(row['status'],'BLOCKED')
            self.assertEqual(row['instruction_sha256'],before)
            self.assertFalse(row['checks']['instruction_unchanged'])
            self.assertEqual(row['response']['status'],'PASS')
            self.assertTrue((folder/'verified.json').is_file())

    def test_production_text_io_declares_encoding(self):
        scripts=Path(__file__).resolve().parents[1]/'scripts'
        missing=[]
        for path in scripts.rglob('*.py'):
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

    def test_response_fence_must_be_closed_not_discard_arbitrary_last_line(self):
        self.assertEqual(parse_response('```json\n{"status":"PASS"}\nnot a closing fence'),{})
        self.assertEqual(parse_response('```unsupported\n{"status":"PASS"}\n```'),{})

    def test_ambiguous_response_keys_and_nonfinite_json_are_rejected(self):
        self.assertEqual(parse_response('{"status":"FAIL","status":"PASS"}'),{})
        self.assertEqual(parse_response('{"status":"PASS","score":NaN}'),{})

    def test_missing_source_artifact_is_a_failed_grade_not_an_exception(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'case';prepare(folder,'loop-plan');before=snapshot(folder)
            (folder/'plan.md').write_text('Acceptance; out of scope; batches; verification; rollback',encoding='utf-8')
            (folder/'calc.py').unlink()
            result=grade(folder,'loop-plan',before)
            self.assertFalse(all(result.values()))

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

    def test_dependency_grader_rejects_replaced_checker_with_no_update(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'case';prepare(folder,'loop-dependencies');before=snapshot(folder)
            (folder/'manifest.before.json').write_bytes(before['manifest.json'])
            (folder/'check_dependency.py').write_text("print('DEPENDENCIES_PASS')\n",encoding='utf-8')
            self.assertFalse(all(grade(folder,'loop-dependencies',before).values()))

    def test_e2e_grader_rejects_empty_suite(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'case';prepare(folder,'loop-test-e2e');before=snapshot(folder)
            (folder/'test_e2e.py').write_text('# no tests\n',encoding='utf-8')
            self.assertFalse(all(grade(folder,'loop-test-e2e',before).values()))

    def test_e2e_grader_rejects_meaningless_passing_suite(self):
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'case';prepare(folder,'loop-test-e2e');before=snapshot(folder)
            (folder/'test_e2e.py').write_text('import unittest\nclass Tests(unittest.TestCase):\n    def test_green(self): self.assertTrue(True)\n',encoding='utf-8')
            self.assertFalse(all(grade(folder,'loop-test-e2e',before).values()))

    def test_e2e_grader_accepts_portable_behavioral_suite_and_regrades(self):
        suite='''import json,subprocess,sys,unittest
from pathlib import Path
class Journey(unittest.TestCase):
    def call(self,*args):
        before=Path('sentinel.txt').read_bytes()
        result=subprocess.run([sys.executable,'app.py',*args],capture_output=True,text=True,timeout=3)
        self.assertEqual(Path('sentinel.txt').read_bytes(),before)
        return result
    def test_valid(self):
        for a,b in ((2,3),(0,0),(-2,-3)):
            result=self.call(str(a),str(b))
            self.assertEqual(result.returncode,0)
            self.assertEqual(json.loads(result.stdout),{'sum':a+b})
    def test_invalid(self):
        for args in (('oops','3'),('2',)):
            result=self.call(*args)
            self.assertEqual(result.returncode,2)
            self.assertTrue(result.stderr)
            self.assertFalse(result.stdout.strip())
'''
        with tempfile.TemporaryDirectory() as temp:
            folder=Path(temp)/'case';prepare(folder,'loop-test-e2e');before=snapshot(folder)
            (folder/'test_e2e.py').write_text(suite,encoding='utf-8')
            self.assertTrue(all(grade(folder,'loop-test-e2e',before).values()))
            self.assertTrue(all(grade(folder,'loop-test-e2e',before).values()))
            self.assertTrue((folder/'independent-e2e-wrong_sum-2').is_dir())
            self.assertEqual((folder/'app.py').read_bytes(),before['app.py'])

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
