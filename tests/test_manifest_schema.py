"""Keep the published contract aligned with the stdlib manifest reader.

These are contract parity tests, not a general JSON Schema implementation.
"""
import json
import re
import tempfile
import unittest
from pathlib import Path

from scripts.validation.manifest import DEFAULT_ROOTS, NAME_PATTERN, load_manifest

ROOT = Path(__file__).resolve().parents[1]


class ManifestSchemaTests(unittest.TestCase):
    def setUp(self):
        self.schema = json.loads((ROOT/'schemas/manifest-v1.schema.json').read_text(encoding='utf-8'))

    def test_schema_names_required_fields_and_native_root_order(self):
        self.assertEqual(self.schema['$schema'], 'https://json-schema.org/draft/2020-12/schema')
        self.assertEqual(set(self.schema['required']), {'version', 'skills', 'project_skill_roots'})
        self.assertEqual(self.schema['properties']['project_skill_roots']['const'], list(DEFAULT_ROOTS))
        self.assertTrue(self.schema['additionalProperties'])

    def test_name_constraints_agree_with_reader(self):
        spec = self.schema['properties']['skills']['items']
        for name in ('loop-code', 'a', '-bad', 'bad--name', '../escape', 'UPPER', 'a'*64, 'a'*65, ''):
            expected = spec['minLength'] <= len(name) <= spec['maxLength'] and bool(re.fullmatch(spec['pattern'], name))
            self.assertEqual(bool(NAME_PATTERN.fullmatch(name)), expected, name)

    def test_manifest_mutations_follow_published_constraints(self):
        base = json.loads((ROOT/'skills-manifest.json').read_text(encoding='utf-8'))
        cases = [({}, True), ({'skills': []}, False), ({'skills': ['a', 'a']}, False),
                 ({'skills': ['../escape']}, False), ({'skills': [12]}, False),
                 ({'project_skill_roots': list(reversed(DEFAULT_ROOTS))}, False),
                 ({'version': 'bad-version'}, False), ({'extra_metadata': 'kept'}, True)]
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for changes, valid in cases:
                (root/'skills-manifest.json').write_text(json.dumps(base | changes), encoding='utf-8')
                manifest, errors = load_manifest(root)
                self.assertEqual(manifest is not None and not errors, valid, changes)
