import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.trial_metrics import score_trials


class TrialMetricsTests(unittest.TestCase):
    def setUp(self):
        self.data={'expected_cases':['stable','flaky','unavailable'],'trials_per_case':2,
            'trials':{'stable':['PASS','PASS'],'flaky':['PASS','FAIL'],'unavailable':['BLOCKED','NOT_RUN']}}

    def test_every_declared_case_and_trial_remains_in_denominator(self):
        result=score_trials(self.data)
        self.assertEqual(result['declared_attempts'],6)
        self.assertEqual(result['status_counts'],{'PASS':3,'FAIL':1,'BLOCKED':1,'NOT_RUN':1})
        self.assertEqual(result['any_pass_cases'],2)
        self.assertEqual(result['all_pass_cases'],1)
        self.assertEqual(result['observed_all_pass_fraction'],1/3)
        self.assertEqual(result['per_case'][2]['outcomes'],['BLOCKED','NOT_RUN'])

    def test_missing_duplicate_unknown_and_malformed_trials_fail(self):
        for mode in ('missing','extra','short','unknown','duplicate','boolean','empty'):
            value=copy.deepcopy(self.data)
            if mode=='missing':value['trials'].pop('unavailable')
            if mode=='extra':value['trials']['extra']=['PASS','PASS']
            if mode=='short':value['trials']['flaky']=['PASS']
            if mode=='unknown':value['trials']['stable']=['PASS','SKIP']
            if mode=='duplicate':value['expected_cases'].append('stable')
            if mode=='boolean':value['trials_per_case']=True
            if mode=='empty':value['expected_cases']=[]
            with self.subTest(mode=mode),self.assertRaises(ValueError):score_trials(value)

    def test_cli_matches_function_and_rejects_omitted_trials(self):
        script=Path(__file__).resolve().parents[1]/'scripts/trial_metrics.py'
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'trials.json'
            path.write_text(json.dumps(self.data),encoding='utf-8')
            run=subprocess.run([sys.executable,str(script),str(path)],capture_output=True,text=True,timeout=10)
            self.assertEqual(run.returncode,0)
            self.assertEqual(json.loads(run.stdout),score_trials(self.data))
            self.data['trials'].pop('unavailable')
            path.write_text(json.dumps(self.data),encoding='utf-8')
            run=subprocess.run([sys.executable,str(script),str(path)],capture_output=True,text=True,timeout=10)
            self.assertEqual(run.returncode,1)
            self.assertEqual(json.loads(run.stdout)['status'],'FAIL')
