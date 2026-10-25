import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.routing_check import check_routes, grade_predictions, load_routes

ROOT = Path(__file__).resolve().parents[1]


class RoutingReviewTests(unittest.TestCase):
    def setUp(self):
        self.data = load_routes(ROOT)

    def test_every_skill_has_a_decision_and_an_accepted_primary_case(self):
        self.assertEqual(check_routes(ROOT), [])
        self.assertEqual(len(self.data['decisions']), 53)
        self.assertEqual(len(self.data['cases']), 57)
        self.assertEqual({row['skill'] for row in self.data['decisions'] if row['action']=='upgrade'},
                         {'loop-plan', 'loop-summarize', 'loop-test', 'loop-review', 'loop-skill-create', 'loop-workflow-project', 'loop-learn', 'loop-decide', 'loop-organize', 'loop-diagnose', 'loop-write', 'loop-code', 'loop-research', 'loop-evaluate', 'loop-meeting'})
        self.assertEqual({row['skill'] for row in self.data['decisions'] if row['action']=='add'},
                         {'loop-table', 'loop-context', 'loop-handoff', 'loop-workflow-incident', 'loop-deploy', 'loop-work', 'loop-observe', 'loop-workflow-pr', 'loop-files', 'loop-document', 'loop', 'loop-intake', 'loop-support', 'loop-knowledge'})

    def test_missing_decision_or_no_skill_controls_cannot_pass(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'skills-manifest.json').write_bytes((ROOT/'skills-manifest.json').read_bytes())
            for mutation in ('decision', 'control'):
                data = copy.deepcopy(self.data)
                if mutation == 'decision':
                    data['decisions'].pop()
                else:
                    data['cases'] = [row for row in data['cases'] if row['acceptable'] != ['NONE']]
                (root/'skill-routing.json').write_text(json.dumps(data), encoding='utf-8')
                self.assertTrue(check_routes(root))

    def test_unknown_routes_and_duplicate_ids_are_rejected(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'skills-manifest.json').write_bytes((ROOT/'skills-manifest.json').read_bytes())
            for mutation in ('route', 'id'):
                data = copy.deepcopy(self.data)
                if mutation == 'route':
                    data['cases'][0]['acceptable'] = ['missing-skill']
                else:
                    data['cases'][1]['id'] = data['cases'][0]['id']
                (root/'skill-routing.json').write_text(json.dumps(data), encoding='utf-8')
                self.assertTrue(check_routes(root))

    def test_broad_acceptable_sets_cannot_erase_primary_and_none_controls(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            manifest=json.loads((ROOT/'skills-manifest.json').read_text(encoding='utf-8'))
            (root/'skills-manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
            data=copy.deepcopy(self.data)
            for row in data['cases']:
                row['acceptable']=manifest['skills']+['NONE']
            (root/'skill-routing.json').write_text(json.dumps(data),encoding='utf-8')
            self.assertTrue(check_routes(root))

    def test_prediction_grader_counts_failures_and_never_drops_cases(self):
        predictions = {row['id']: row['acceptable'][0] for row in self.data['cases']}
        self.assertEqual(grade_predictions(self.data, predictions)['correct'], 57)
        predictions[self.data['cases'][0]['id']] = 'NONE'
        result = grade_predictions(self.data, predictions)
        self.assertEqual((result['status'], result['total'], result['correct']), ('FAIL', 57, 56))
        predictions.pop(self.data['cases'][1]['id'])
        with self.assertRaises(ValueError):
            grade_predictions(self.data, predictions)

    def test_real_cli_reports_wrong_predictions_as_failure(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp)/'predictions.json'
            path.write_text(json.dumps({row['id']: 'NONE' for row in self.data['cases']}), encoding='utf-8')
            result = subprocess.run([sys.executable, str(ROOT/'scripts/routing_check.py'), '--predictions', str(path)],
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 1)
            observed = json.loads(result.stdout)
            self.assertEqual((observed['total'], observed['correct']), (57, 3))
