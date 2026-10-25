"""Adversarial contract tests. Fixture contents are data, never instructions."""
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from scripts.validate import DEFAULT_ROOTS, frontmatter_value, validate
from scripts.run_loop import run_loop
from scripts.sync_skills import sync


class AdversarialTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.text = (ROOT/'.github/skills/loop-review/SKILL.md').read_text(encoding='utf-8')
        self.manifest = {'version': '1.0.0', 'skills': ['loop-review'],
                         'project_skill_roots': list(DEFAULT_ROOTS)}
        self.write(self.text)

    def tearDown(self):
        self.temp.cleanup()

    def write(self, text):
        for native in DEFAULT_ROOTS:
            path = self.root/native/'loop-review/SKILL.md'
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8')
        (self.root/'skills-manifest.json').write_text(json.dumps(self.manifest), encoding='utf-8')

    def description(self, value):
        line = next(line for line in self.text.splitlines() if line.startswith('description:'))
        self.write(self.text.replace(line, 'description: '+value))

    def cli(self, profile):
        return subprocess.run([sys.executable, str(ROOT/'scripts/validate.py'),
                               '--repo', str(self.root), '--profile', profile],
                              capture_output=True, text=True, timeout=30)

    def test_non_string_and_invalid_description_rejected_by_real_cli(self):
        for value in ('[]', '{}', 'null', 'false', '123', '"unfinished', "'unfinished", '"" # empty'):
            with self.subTest(value=value):
                self.description(value)
                for profile in ('loop', 'format'):
                    result = self.cli(profile)
                    self.assertEqual(result.returncode, 1, (value, profile, result.stdout))
                    self.assertIn('description', result.stdout)

    def test_valid_quoted_literals_are_strings_not_yaml_types(self):
        for value in ('"false"', "'null'", '"[]"', "'It''s a review'", 'A scoped review'):
            with self.subTest(value=value):
                self.description(value)
                self.assertEqual(validate(self.root), [])

    def test_plain_yaml_collection_indicators_rejected_by_both_cli_profiles(self):
        for value in ('- item', '? item', '-', '?'):
            self.description(value)
            for profile in ('loop', 'format'):
                with self.subTest(value=value,profile=profile):
                    result=self.cli(profile)
                    self.assertEqual(result.returncode,1,(value,profile,result.stdout))
                    self.assertIn('description',result.stdout)

    def test_plain_safe_indicator_prefixes_and_quoted_indicators_remain_valid(self):
        for value in ('-item', '?item', '"- item"', '"? item"'):
            with self.subTest(value=value):
                self.description(value)
                self.assertEqual(validate(self.root),[])

    def test_invalid_utf8_instruction_returns_findings_without_traceback(self):
        for native in DEFAULT_ROOTS:
            (self.root/native/'loop-review/SKILL.md').write_bytes(b'---\nname: loop-review\ndescription: \xff\n---\n')
        for profile in ('loop','format'):
            with self.subTest(profile=profile):
                result=self.cli(profile)
                self.assertEqual(result.returncode,1)
                self.assertIn('UTF-8',result.stdout)
                self.assertNotIn('Traceback',result.stderr)

    def test_scalar_decoding_counts_actual_description_length(self):
        # JSON's double-quoted escape subset is also valid YAML. Escaped syntax
        # length must not replace the length of the decoded description.
        self.description('"'+'\\u0041'*1025+'"')
        self.assertTrue(validate(self.root))
        self.assertEqual(frontmatter_value('description: "A\\u0042"', 'description'), 'AB')

    def test_duplicate_key_with_yaml_spacing_is_rejected(self):
        self.write(self.text.replace('name: loop-review', 'name: loop-review\nname : loop-review'))
        for profile in ('loop', 'format'):
            self.assertTrue(any('duplicate metadata' in e for e in validate(self.root, profile)))

    def test_unicode_version_rejected_consistently_with_published_schema(self):
        version = '\u0661.\u0662.\u0663'
        schema = json.loads((ROOT/'schemas/manifest-v1.schema.json').read_text(encoding='utf-8'))
        self.assertIsNone(re.search(schema['properties']['version']['pattern'], version))
        self.manifest['version'] = version
        self.write(self.text)
        for profile in ('loop', 'format'):
            result = self.cli(profile)
            self.assertEqual(result.returncode, 1, result.stdout)
            self.assertIn('version', result.stdout)

    def test_copy_integrity_does_not_certify_metadata(self):
        self.description('[]')
        target = self.root/'installed'
        with mock.patch('scripts.sync_skills.REPO', self.root):
            sync(target, self.root/'backup')
            self.assertEqual(sync(target, self.root/'backup', check=True), [])
        self.assertEqual((target/'loop-review/SKILL.md').read_bytes(),
                         (self.root/DEFAULT_ROOTS[0]/'loop-review/SKILL.md').read_bytes())
        # Equality is expected; structural validity must be evaluated separately.
        self.assertTrue(validate(self.root))

    def test_runner_rejects_duplicate_markers_across_real_output_streams(self):
        args = Namespace(command=[sys.executable, '-c',
                         "import sys; print('LOOP_STATUS: PASS'); print('LOOP_STATUS: FAIL',file=sys.stderr)"],
                         prompt='local protocol fixture', max_iterations=1, timeout_seconds=10,
                         state_file=str(self.root/'state.json'), report_file=str(self.root/'report.md'))
        self.assertNotEqual(run_loop(args), 0)
        state = json.loads((self.root/'state.json').read_text(encoding='utf-8'))
        self.assertNotEqual(state['final_status'], 'PASS')

    def test_runner_rejects_pass_marker_with_nonzero_real_child_exit(self):
        args = Namespace(command=[sys.executable, '-c', "print('LOOP_STATUS: PASS'); raise SystemExit(7)"],
                         prompt='local protocol fixture', max_iterations=1, timeout_seconds=10,
                         state_file=str(self.root/'state.json'), report_file=str(self.root/'report.md'))
        self.assertNotEqual(run_loop(args), 0)
        state = json.loads((self.root/'state.json').read_text(encoding='utf-8'))
        self.assertEqual(state['final_status'], 'FAIL')
        self.assertEqual(state['iterations'][0]['returncode'], 7)

    def test_sync_rejects_hardlinked_destination_before_any_writes(self):
        target = self.root/'installed'
        first = target/'loop-review/SKILL.md'
        first.parent.mkdir(parents=True)
        first.write_text('retained installation', encoding='utf-8')
        external = self.root/'outside-target.txt'
        external.write_text('unrelated data', encoding='utf-8')
        second = target/'loop-code/SKILL.md'
        second.parent.mkdir(parents=True)
        os.link(external, second)
        source = self.root/'.github/skills/loop-code/SKILL.md'
        source.parent.mkdir(parents=True)
        source.write_text('replacement skill', encoding='utf-8')
        self.manifest['skills'].append('loop-code')
        self.write(self.text)
        backup = self.root/'backup'
        with mock.patch('scripts.sync_skills.REPO', self.root):
            for check in (True, False):
                with self.subTest(check=check):
                    with self.assertRaisesRegex(ValueError, 'hardlink'):
                        sync(target, backup, check=check)
        self.assertEqual(external.read_text(encoding='utf-8'), 'unrelated data')
        self.assertEqual(first.read_text(encoding='utf-8'), 'retained installation')
        self.assertFalse(backup.exists())

    def test_public_reproducer_checks_fixed_cli_behaviors(self):
        output = self.root/'reproduction'
        result = subprocess.run([sys.executable, str(ROOT/'scripts/adversarial_repro.py'),
                                 '--output-dir', str(output), '--expect', 'fixed'],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout+result.stderr)
        evidence = json.loads((output/'results.json').read_text(encoding='utf-8'))
        self.assertTrue(evidence['expectation_matched'])
        self.assertEqual(len(evidence['validator_results']), 12)
        self.assertFalse(evidence['hardlink']['outside_target_modified'])

    def test_public_reproducer_refuses_existing_evidence_directory(self):
        sentinel = self.root/'sentinel.txt'
        sentinel.write_text('retained evidence', encoding='utf-8')
        result = subprocess.run([sys.executable, str(ROOT/'scripts/adversarial_repro.py'),
                                 '--output-dir', str(self.root)],
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(sentinel.read_text(encoding='utf-8'), 'retained evidence')
