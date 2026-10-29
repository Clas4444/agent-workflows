"""Characterize the full gate while exercising the separated policy layers."""
import subprocess
import sys
import unittest
from pathlib import Path

from scripts.validate import DEFAULT_ROOTS, Manifest, frontmatter_value, validate
from scripts.validation.manifest import Manifest as ManifestType
from scripts.validation.skill_format import check_format
from scripts.validation.loop_policy import check_loop_policy
from tests import test_contract_validation as fixtures

ROOT = Path(__file__).resolve().parents[1]
MINIMAL = "---\nname: loop-review\ndescription: Review a scoped change.\n---\n\nReview the supplied diff.\n"


class LayerUnitTests(unittest.TestCase):
    def test_minimal_metadata_does_not_require_loop_conventions(self):
        self.assertEqual(check_format(MINIMAL, 'loop-review', 'SKILL.md'), [])
        self.assertTrue(check_loop_policy(MINIMAL, 'loop-review', 'SKILL.md'))

    def test_format_still_rejects_bad_identity(self):
        self.assertTrue(check_format(MINIMAL, 'different-name', 'SKILL.md'))

    def test_legacy_imports_are_preserved(self):
        self.assertIs(Manifest, ManifestType)
        self.assertEqual(frontmatter_value('description: value', 'description'), 'value')
        self.assertEqual(len(DEFAULT_ROOTS), 3)

    def test_cli_and_module_invocation_work(self):
        for args in (['scripts/validate.py'], ['-m', 'scripts.validate']):
            result = subprocess.run([sys.executable, *args], cwd=ROOT,
                                    capture_output=True, text=True, timeout=30)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout.strip(), 'PASS: structural validation')

    def test_reduced_profile_cannot_write_full_summary(self):
        result = subprocess.run([sys.executable, 'scripts/validate.py', '--profile',
                                 'format', '--write-summary'], cwd=ROOT,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 2)
        self.assertIn('requires the full loop profile', result.stderr)


class LayerRepositoryTests(unittest.TestCase):
    # Reuse fixture setup without inheriting/rerunning its test methods.
    setUp = fixtures.ContractValidationTests.setUp
    tearDown = fixtures.ContractValidationTests.tearDown
    write = fixtures.ContractValidationTests.write

    def test_default_gate_matches_explicit_full_gate(self):
        self.write(MINIMAL)
        self.assertEqual(validate(self.root), validate(self.root, profile='loop'))
        self.assertTrue(validate(self.root))
        self.assertEqual(validate(self.root, profile='format'), [])

    def test_format_keeps_synchronization_checks(self):
        self.write(MINIMAL)
        path = self.root / DEFAULT_ROOTS[1] / 'loop-review/SKILL.md'
        path.write_text(MINIMAL + '\nChanged\n', encoding='utf-8')
        self.assertTrue(any('not identical' in e for e in validate(self.root, 'format')))

    def test_format_keeps_manifest_path_checks(self):
        (self.root/'skills-manifest.json').write_text('{"version":"1.0.0","skills":["../escape"],"project_skill_roots":[]}', encoding='utf-8')
        self.assertTrue(validate(self.root, 'format'))

    def test_unknown_profile_is_rejected(self):
        with self.assertRaises(ValueError):
            validate(self.root, 'unknown')
