import hashlib
import json
from pathlib import Path
import unittest
from scripts.instruction_history import instruction_identity

ROOT = Path(__file__).resolve().parents[1]
FOLDER = ROOT/'docs/evidence/noncode-1.8'


class NonCodingEvidenceTests(unittest.TestCase):
    def test_packets_belong_to_this_session_and_instruction_bytes(self):
        data=json.loads((FOLDER/'provenance.json').read_text(encoding='utf-8'))
        self.assertEqual(data['session_id'],'noncode-1.8-20261025T054823Z')
        self.assertTrue(data['expected_criteria_frozen_before_model'])
        self.assertEqual(data['native_discovery'],'NOT_RUN')
        self.assertEqual(data['external_actions'],'NOT_RUN')
        self.assertEqual(len(data['assessment']),6)
        for name, expected in data['instruction_sha256'].items():
            self.assertEqual(instruction_identity(ROOT,'noncode-1.8',name,expected),
                             'HISTORICAL_ONLY_INVALIDATED',name)
        for name, expected in data['artifact_sha256'].items():
            self.assertEqual(hashlib.sha256((FOLDER/name).read_bytes()).hexdigest(),expected,name)

    def test_learning_time_budget_and_unexecuted_assessment_are_preserved(self):
        data=json.loads((FOLDER/'learn.json').read_text(encoding='utf-8'))
        self.assertEqual(len(data['schedule']),14)
        self.assertIsNone(data['assessment']['score'])
        self.assertEqual(data['assessment']['final_assessment'],'NOT_RUN')
        for day in data['schedule']:
            self.assertLessEqual(day['minutes']['total'],20)
            self.assertEqual(day['minutes']['total'],sum(v for k,v in day['minutes'].items() if k!='total'))
        self.assertEqual(sum(day['minutes']['total'] for day in data['schedule']),280)

    def test_missing_evidence_does_not_become_commitment_or_execution(self):
        meeting=json.loads((FOLDER/'meeting.json').read_text(encoding='utf-8'))
        decision=json.loads((FOLDER/'decide.json').read_text(encoding='utf-8'))
        organize=json.loads((FOLDER/'organize.json').read_text(encoding='utf-8'))
        self.assertEqual(meeting['decisions'],[])
        self.assertIsNone(decision['recommendation']['unconditional_choice'])
        self.assertEqual(decision['booking'],'NOT_RUN')
        self.assertEqual(organize['execution_status'],'NOT_RUN')
        self.assertEqual(len({item['destination'].casefold() for item in organize['proposed_mapping']}),2)
        self.assertNotEqual(*[item['sha256'] for item in organize['inventory']])
