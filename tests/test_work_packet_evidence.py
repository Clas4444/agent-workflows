"""Regrade retained artifacts and challenge the finite oracle without model calls."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT/'docs/evidence/discovery-20261026'


class WorkPacketEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        with zipfile.ZipFile(EVIDENCE/'raw-artifacts.zip') as archive:
            for name in archive.namelist():
                self.assertFalse(Path(name).is_absolute())
                self.assertNotIn('..', Path(name).parts)
            archive.extractall(self.root)
        self.protocol = json.loads((EVIDENCE/'protocol.json').read_text(encoding='utf-8'))
        spec = importlib.util.spec_from_file_location('packet_oracle', EVIDENCE/'check_runtime.py')
        self.oracle = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.oracle)

    def test_retained_trials_keep_original_failure_separate_from_schema_explicit_retry(self):
        for key, case in self.protocol['cases'].items():
            errors = self.oracle.grade(self.root/key, case)
            self.assertEqual(bool(errors), key == 'work', (key, errors))
        self.assertIn('serialization', self.protocol['measurement_note'])

    def test_recorded_instruction_text_matches_the_retained_input_pins(self):
        for key, case in self.protocol['cases'].items():
            for name in case['skills']:
                path = f'skills/{name}/SKILL.md'
                recorded = (self.root/key/path).read_bytes()
                self.assertEqual(hashlib.sha256(recorded).hexdigest(), case['pins'][path], (key, name))

    def test_positive_control_and_missing_wrong_hash_changed_input_and_type_controls(self):
        for key in ('support', 'knowledge', 'work-schema-explicit'):
            case = self.protocol['cases'][key]
            folder = self.root/key
            self.assertEqual(self.oracle.grade(folder, case), [])
            assessment = folder/'assessment.json'
            original = assessment.read_bytes()
            value = json.loads(original)
            mutations = [dict(value, source_sha256={name: '0'*64 for name in case['sources']}),
                         dict(value, extra='unsupported'),
                         dict(value, **{next(iter(case['expected'])): 999})]
            for mutation in mutations:
                assessment.write_text(json.dumps(mutation), encoding='utf-8')
                self.assertTrue(self.oracle.grade(folder, case), (key, mutation))
            assessment.unlink()
            self.assertTrue(self.oracle.grade(folder, case))
            assessment.write_bytes(original)
            source = folder/next(iter(case['sources']))
            source.write_bytes(b'changed source')
            self.assertTrue(self.oracle.grade(folder, case))

    def test_duplicate_json_keys_and_boolean_numeric_coercion_do_not_pass(self):
        with self.assertRaises(ValueError):
            self.oracle.strict('{"approved":false,"approved":false}')
        self.assertFalse(self.oracle.equal(True, 1))
        self.assertFalse(self.oracle.equal({'total': '3'}, {'total': 3}))
