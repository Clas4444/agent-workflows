import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from scripts.empirical_audit import aggregate, combine_answers, revision_functional, usage
from scripts.empirical_cases import controls, fixtures, grade, oracle
from scripts.empirical_pilot import event_answer, freeze, prompt, run
from scripts.empirical_figures import tables


def raw_usage():
    return {'modelMetrics': {'one': {'requests': {'count': 1}, 'usage': {
        'inputTokens': 30, 'outputTokens': 5, 'cacheReadTokens': 10, 'cacheWriteTokens': 15}}},
        'totalPremiumRequestCost': 1, 'totalApiDurationMs': 23, 'totalNanoAiu': 456, 'aiCreditsStatus': 'complete'}


class EmpiricalTests(unittest.TestCase):
    def test_oracle_controls_and_sort_contract(self):
        self.assertTrue(all(r['pass'] for r in controls()))
        f = fixtures()['revision']; good = oracle('revision', f['source'])
        wrong = copy.deepcopy(good); wrong['before']['sorted_ids'].reverse()
        self.assertFalse(grade('revision', f['source'], wrong)['functional'])
        self.assertTrue(revision_functional(wrong, good, True))
        wrong['before']['sorted_ids'][0] = 'Q1'
        self.assertFalse(revision_functional(wrong, good, True))
        wrong = copy.deepcopy(good); wrong['handoff']['approved'] = 0
        self.assertFalse(grade('revision', f['source'], wrong)['functional'])
        self.assertFalse(grade('revision', f['source'], wrong)['policy'])

    def test_fixture_mutations_are_not_hardcoded(self):
        f = fixtures()['revision']; f['source']['revision']['replace']['hours'] += 10
        self.assertEqual(oracle('revision', f['source'])['after']['total_hours'], 21)
        f = fixtures()['authority']; f['source']['correction']['amount'] = '9.99'
        self.assertEqual(oracle('authority', f['source'])['totals_by_currency']['EUR'], '11.09')

    def test_split_response_wrapper_sensitivity_is_separate(self):
        expected=oracle('revision',fixtures()['revision']['source'])
        calls=[{'answer':expected[k]} for k in ('before','after','handoff')]
        self.assertFalse(revision_functional(combine_answers(calls),expected,True))
        self.assertTrue(revision_functional(combine_answers(calls,True),expected,True))
        calls[-1]['answer']=dict(calls[-1]['answer'],sent=True)
        self.assertFalse(revision_functional(combine_answers(calls,True),expected,True))

    def test_usage_all_models_no_double_cache(self):
        raw = raw_usage(); raw['modelMetrics']['two'] = copy.deepcopy(raw['modelMetrics']['one'])
        u, models = usage(raw)
        self.assertEqual(u['total_tokens'], 70)
        self.assertEqual(u['model_requests'], 2)
        self.assertEqual(models, ['one', 'two'])
        for key, val in [('inputTokens', True), ('outputTokens', -1), ('cacheReadTokens', 31)]:
            bad = raw_usage(); bad['modelMetrics']['one']['usage'][key] = val
            with self.assertRaises(ValueError): usage(bad)
        for key in ('modelMetrics', 'totalNanoAiu'):
            bad = raw_usage(); del bad[key]
            with self.assertRaises(ValueError): usage(bad)

    def test_final_assistant_only_and_strict_json(self):
        text = '\n'.join(json.dumps(x) for x in [
            {'type': 'tool.result', 'data': {'content': '{"yes": true}'}},
            {'type': 'assistant.message', 'data': {'content': '{"yes": false}'}}])
        self.assertEqual(event_answer(text)[0], {'yes': False})
        self.assertIsNone(event_answer('{"type":"assistant.message","data":{"content":"{\\"a\\":1,\\"a\\":2}"}}')[0])

    def test_zero_duplicate_missing_aggregate(self):
        with self.assertRaises(ValueError): aggregate([])
        row = {'campaign': 'a', 'case': 'revision', 'arm': 'plain', 'rep': 1, 'original_status': 'FAIL',
               'calls': [{'seconds': 2, 'usage': {'input_tokens':2,'output_tokens':1,'total_tokens': 3}}]}
        self.assertEqual(aggregate([row])[0]['original_pass'], 0)
        with self.assertRaises(ValueError): aggregate([row], expected_count=2)
        with self.assertRaises(ValueError): aggregate([row, row])
        row['calls'] = []
        with self.assertRaises(ValueError): aggregate([row])

    def test_chart_missingness_and_double_count_negative_controls(self):
        with self.assertRaises(ValueError): tables([], [])
        historical=[]
        for n in range(80):
            u,_=usage(raw_usage())
            historical.append({'cohort':'HISTORICAL','campaign':'fixture','case':'revision','arm':'plain','rep':n,
                               'original_status':'PASS','calls':[{'seconds':1,'usage':u}]})
        pilot=[{'id':str(i),'status':'NOT_RUN','cli_count':0,'seconds':None,'usage':None} for i in range(12)]
        data=tables(historical,pilot)
        self.assertTrue(all(r['usage'] is None for r in data['pilot_slots']))
        historical[0]['calls'][0]['usage']['total_tokens']+=10
        with self.assertRaises(ValueError):tables(historical,pilot)

    def test_freeze_denominator_no_answers_in_plain(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = Path(directory)/'pilot'; protocol = freeze(folder, ['not-a-launcher'])
            self.assertEqual(len(protocol['schedule']), 12)
            for case in fixtures().values():
                base = prompt(case, 'plain', 'SECRET-SKILL')
                self.assertNotIn('SECRET-SKILL', base)
                self.assertNotIn('loop-work', base)
                self.assertNotIn('expected', base)
            counts = {}
            for row in protocol['schedule']:
                key = (row['case'], row['arm']); counts[key] = counts.get(key, 0)+1
            self.assertEqual(set(counts.values()), {2})

    def test_shared_stop_and_incomplete_reservation_never_call(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); folder = base/'pilot'; marker = base/'stop.json'
            protocol = freeze(folder, ['none']); marker.write_text('{}')
            with patch('scripts.empirical_pilot.subprocess.run') as invoke:
                rows = run(folder, ['none'], marker); invoke.assert_not_called()
            self.assertEqual([r['status'] for r in rows], ['NOT_RUN']*12)
            marker.unlink(); attempt = folder/'attempts'/protocol['schedule'][0]['id']; attempt.mkdir()
            with patch('scripts.empirical_pilot.subprocess.run') as invoke:
                rows = run(folder, ['none'], marker); invoke.assert_not_called()
            self.assertEqual(rows[0]['block_reason'], 'incomplete_reservation')
            self.assertTrue(marker.exists())

    def test_stale_pin_prevents_execution(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); folder = base/'pilot'; freeze(folder, ['none'])
            (folder/'protocol.json').write_text('{}')
            with patch('scripts.empirical_pilot.subprocess.run') as invoke:
                with self.assertRaises(ValueError): run(folder, ['none'], base/'stop')
                invoke.assert_not_called()

    def test_failed_accounting_consumes_attempt_stops_and_never_retries(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory); folder = base/'pilot'; freeze(folder, ['none'])
            marker = base/'stop'
            proc = SimpleNamespace(returncode=1, stdout=b'', stderr=b'usage unavailable')
            with patch('scripts.empirical_pilot.subprocess.run', return_value=proc) as invoke:
                rows = run(folder, ['none'], marker)
                self.assertEqual(invoke.call_count, 1)
            self.assertEqual(rows[0]['status'], 'BLOCKED_ENVIRONMENT')
            self.assertEqual(sum(r['cli_count'] for r in rows), 1)
            self.assertEqual(sum(r['status']=='NOT_RUN' for r in rows), 11)
            with patch('scripts.empirical_pilot.subprocess.run') as invoke:
                again = run(folder, ['none'], marker); invoke.assert_not_called()
            self.assertEqual(again[0]['status'], 'BLOCKED_ENVIRONMENT')

    def test_functional_pass_cannot_hide_extra_files_or_tool_attempts(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);folder=base/'pilot';protocol=freeze(folder,['none'])
            def candidate(command,**kwargs):
                usage_path=Path(command[command.index('--usage-output-file')+1])
                raw=raw_usage();raw['modelMetrics']['gpt-5.6-luna']=raw['modelMetrics'].pop('one')
                usage_path.write_text(json.dumps(raw))
                item=next(r for r in protocol['schedule'] if r['id']==usage_path.parent.name)
                value=oracle(item['case'],protocol['fixtures'][item['case']]['source'])
                events=[{'type':'session.skills_loaded','data':{'skills':[]}},
                        {'type':'tool.execution_start','data':{}},
                        {'type':'assistant.message','data':{'content':json.dumps(value)}}]
                (Path(kwargs['cwd'])/'unapproved.txt').write_text('unexpected output')
                return SimpleNamespace(returncode=0,stdout=('\n'.join(json.dumps(e) for e in events)).encode(),stderr=b'')
            with patch('scripts.empirical_pilot.subprocess.run',side_effect=candidate) as invoke:
                rows=run(folder,['none'],base/'stop')
                self.assertEqual(invoke.call_count,12)
            self.assertTrue(all(r['status']=='FAIL' for r in rows))
            self.assertTrue(all(r['checks']['functional'] for r in rows))
            self.assertTrue(all(not r['checks']['file_integrity'] and not r['checks']['no_tool_starts'] for r in rows))

    def test_public_packet_reproduces_in_fresh_directory_without_reports(self):
        root=Path(__file__).resolve().parents[1]
        packet=root/'docs/evidence/copilot-integrity-20261103'
        with tempfile.TemporaryDirectory() as directory:
            output=Path(directory)/'summary.json'
            command=[sys.executable,'-I','-S','-B',str(root/'scripts/empirical_audit.py'),
                     '--saved',str(packet/'historical.json'),'--fixture',str(packet/'historical-fixture.json'),
                     '--output',str(output)]
            result=subprocess.run(command,cwd=directory,capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stderr)
            self.assertEqual(json.loads(output.read_text()),json.loads((packet/'historical-summary.json').read_text()))
            result=subprocess.run([sys.executable,'-I','-S','-B',str(root/'scripts/empirical_figures.py'),
                '--historical',str(packet/'historical.json'),'--pilot',str(packet/'pilot-observations.json'),
                '--output',str(Path(directory)/'figures')],cwd=directory,capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stderr)
            for name in ('chart-data.json','acceptance.svg','per-run.svg','cost-quality.svg','coverage.svg','historical-runs.csv','summary.csv','pilot-slots.csv'):
                self.assertEqual((Path(directory)/'figures'/name).read_bytes(),(packet/'figures'/name).read_bytes())
