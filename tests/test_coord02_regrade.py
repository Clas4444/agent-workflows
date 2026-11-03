import copy
from pathlib import Path
import unittest
from scripts.empirical_audit import read
from scripts.codex_office_analysis import analyze_versioned

PACKET=Path(__file__).resolve().parents[1]/'docs/evidence/codex-office-20261103'


class Coord02RegradeTests(unittest.TestCase):
    def test_existing_records_keep_labels_and_numerical_conclusions(self):
        rows=read(PACKET/'observations.json');before=copy.deepcopy(rows)
        result=analyze_versioned(rows,read(PACKET/'protocol.json'),2)
        self.assertEqual(rows,before)
        self.assertEqual(result['regrade_version'],'codex-office-v2-coord02')
        self.assertEqual(sum(r['status_original']=='FAIL' for r in result['observations']),12)
        self.assertEqual(sum(r['status_regraded']=='PASS' for r in result['observations']),11)
        self.assertAlmostEqual(result['pooled_workflow_vs_plain']['token_change_percent'],5.9059863398955414)
        self.assertAlmostEqual(result['pooled_workflow_vs_plain']['time_change_percent'],5.1003016319010275)

    def test_missing_items_usage_check_or_boolean_counters_cannot_false_pass(self):
        original=read(PACKET/'observations.json');protocol=read(PACKET/'protocol.json')
        for field,value in [('items',[]),('usage',None),('checks',{}),('cli_count',True),('rep',True)]:
            rows=copy.deepcopy(original);rows[0][field]=value
            with self.subTest(field=field),self.assertRaises(ValueError):analyze_versioned(rows,protocol,2)
        rows=copy.deepcopy(original);rows[0]['usage']['cached_input_tokens']=10**9
        with self.assertRaises(ValueError):analyze_versioned(rows,protocol,2)

    def test_missing_repetition_and_unequal_quality_withhold_pooled_savings(self):
        rows=read(PACKET/'observations.json');protocol=read(PACKET/'protocol.json')
        with self.assertRaises(ValueError):analyze_versioned(rows[:-1],protocol,2)
        # Change a baseline artifact, preserving original labels. No efficiency claim
        # is allowed merely because a telemetry row is present.
        for row in rows:
            if row['arm']=='plain':row['candidate']={};break
        result=analyze_versioned(rows,protocol,2)
        self.assertFalse(result['pooled_workflow_vs_plain']['eligible_equal_quality'])
        self.assertIsNone(result['pooled_workflow_vs_plain']['token_change_percent'])
        self.assertIsNone(result['pooled_workflow_vs_plain']['time_change_percent'])

    def test_v1_backward_reproduction_and_unknown_version_diagnostic(self):
        result=analyze_versioned(read(PACKET/'observations.json'),read(PACKET/'protocol.json'),1)
        self.assertEqual(result,read(PACKET/'figures/analysis.json'))
        with self.assertRaisesRegex(ValueError,'unsupported regrade'):analyze_versioned([],{},3)
