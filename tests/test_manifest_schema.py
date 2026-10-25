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

    def test_schema_pattern_search_rejects_trailing_newline_in_skill_names(self):
        # JSON Schema pattern uses search semantics, not Python fullmatch().
        pattern=self.schema['properties']['skills']['items']['pattern']
        self.assertIsNone(re.search(pattern,'loop-code\n'))
        self.assertIsNone(NAME_PATTERN.fullmatch('loop-code\n'))

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

    def test_semver_boundary_cases_are_independently_specified(self):
        base=json.loads((ROOT/'skills-manifest.json').read_text(encoding='utf-8'))
        valid=('0.0.0','1.2.3','1.2.3-alpha.0','1.2.3-0','1.2.3-a01','1.2.3-RC.1+Build.001')
        invalid=('01.2.3','1.02.3','1.2.03','1.2.3-..','1.2.3-alpha..1','1.2.3-01',
                 '1.2.3-alpha.01','1.2.3-','1.2.3+','1.2.3+build..id','1.2.3\n')
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp)
            for version in valid+invalid:
                with self.subTest(version=version):
                    (root/'skills-manifest.json').write_text(json.dumps(base|{'version':version}),encoding='utf-8')
                    manifest,errors=load_manifest(root)
                    expected=version in valid
                    self.assertEqual(manifest is not None and not errors,expected)
                    self.assertEqual(bool(re.search(self.schema['properties']['version']['pattern'],version)),expected)
