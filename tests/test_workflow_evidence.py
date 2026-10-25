"""Published packet evidence stays identifiable; this does not call a model."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT/'docs/evidence/workflows-1.7'


class WorkflowEvidenceTests(unittest.TestCase):
    def test_published_artifact_bytes_match_provenance(self):
        data = json.loads((EVIDENCE/'provenance.json').read_text(encoding='utf-8'))
        for name, expected in data['artifact_sha256'].items():
            self.assertEqual(hashlib.sha256((EVIDENCE/name).read_bytes()).hexdigest(), expected, name)
        self.assertEqual(data['native_discovery'], 'NOT_RUN')
        self.assertEqual(data['live_operations'], 'NOT_RUN')
        self.assertEqual(len(data['attempts']), 2)
        self.assertEqual(data['attempts'][0]['assessment']['incident'], 'FAIL')
        self.assertEqual(data['attempts'][1]['assessment']['incident'], 'PASS')

    def test_failed_attempt_is_retained_and_retry_does_not_claim_execution(self):
        before = json.loads((EVIDENCE/'incident-before.json').read_text(encoding='utf-8'))
        after = json.loads((EVIDENCE/'incident-after.json').read_text(encoding='utf-8'))
        self.assertEqual(before['gates']['unit_tests']['status'], 'PASS')
        unit = next(row for row in after['checks'] if row['name']=='Unit tests')
        self.assertEqual(unit['status'], 'NOT_RUN')
        self.assertIsNone(unit['verified_result'])
        self.assertFalse(after['recovery']['sustained_recovery_established'])
        self.assertFalse(after['recovery']['data_integrity_established'])
        self.assertEqual(after['proposed_action']['execution_status'], 'BLOCKED')

    def test_final_instruction_identity_and_initial_draft_are_reproducible(self):
        data = json.loads((EVIDENCE/'provenance.json').read_text(encoding='utf-8'))
        initial = EVIDENCE/'incident-instruction-before.md'
        self.assertEqual(hashlib.sha256(initial.read_bytes()).hexdigest(),
                         data['attempts'][0]['instruction_sha256']['loop-workflow-incident'])
        for row in data['attempts']:
            for name, expected in row['instruction_sha256'].items():
                if name=='loop-workflow-incident' and row['id']=='first-context':
                    continue
                path = ROOT/'.github/skills'/name/'SKILL.md'
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), expected, name)
