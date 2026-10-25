import hashlib
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class RuntimeEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.data=json.loads((ROOT/'docs/evidence/runtime-1.2-2026-10-24.json').read_text(encoding='utf-8'))

    def test_evidence_covers_manifest_without_duplicate_results(self):
        # This immutable 1.2 campaign covers its recorded 27-skill manifest.
        # New skills require separate evidence; never fabricate a historical PASS.
        names=json.loads((ROOT/'docs/evidence/manifest-1.2.json').read_text(encoding='utf-8'))['skills']
        rows=self.data['results']
        self.assertEqual(len(rows),len(names))
        self.assertEqual({row['skill'] for row in rows},set(names))
        for row in rows:self.assertEqual(row['status'],'PASS',row['skill'])

    def test_instruction_text_hashes_match_current_source_cross_platform(self):
        invalidations=json.loads((ROOT/'docs/evidence/runtime-invalidations-1.3.json').read_text(encoding='utf-8'))
        for row in self.data['results']:
            text=(ROOT/'.github/skills'/row['skill']/'SKILL.md').read_text(encoding='utf-8')
            current=hashlib.sha256(text.encode('utf-8')).hexdigest()
            if row['skill'] in invalidations:
                record=invalidations[row['skill']]
                self.assertEqual(record['historical_instruction_text_sha256'],row['instruction_text_sha256'])
                self.assertEqual(record['current_instruction_text_sha256'],current)
                self.assertEqual(record['current_runtime_status'],'NOT_RUN')
                self.assertTrue(record['reason'])
                self.assertNotEqual(current,row['instruction_text_sha256'])
            else:
                self.assertEqual(current,row['instruction_text_sha256'],row['skill'])
        self.assertEqual(set(invalidations),{'loop-orchestrate','loop-prompt','loop-review','loop-code','loop-diagnose','loop-test','loop-plan','loop-research'})

    def test_new_execution_and_historical_reuse_are_distinct(self):
        current=[row for row in self.data['results'] if row['basis']=='current_fixture_execution']
        historical=[row for row in self.data['results'] if row['basis']=='historical_byte_identical_instruction']
        self.assertEqual(len(current),8)
        self.assertEqual(len(historical),19)
        for row in current:
            self.assertTrue(row['instruction_read_command_observed'],row['skill'])
            self.assertTrue(row['checks'])
            self.assertTrue(all(row['checks'].values()),row['skill'])
        prior=json.loads((ROOT/'docs/evidence/codex-smoke-2026-10-24.json').read_text(encoding='utf-8'))
        prior_names={row['skill'] for row in prior['results']}
        for row in historical:
            self.assertTrue(row['raw_instruction_matches_prior'])
            self.assertIn(row['skill'],prior_names)
