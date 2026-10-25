"""User-facing shortcuts must select safely without executing task content."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def finder():
    spec = importlib.util.spec_from_file_location('loop_finder', ROOT/'.github/skills/loop/scripts/find_skill.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SkillFinderTests(unittest.TestCase):
    def setUp(self):
        self.finder = finder()
        self.catalog = self.finder.load_catalog(ROOT/'.github/skills/loop/assets/catalog.json')

    def test_spaced_canonical_short_and_case_variants_resolve_same_skill(self):
        for query in ['/loop code', '/lc', '$loop code', 'LOOP-CODE', 'code']:
            with self.subTest(query=query):
                row = self.finder.resolve(self.catalog, query)
                self.assertEqual(row['kind'], 'skill')
                self.assertEqual(row['skills'], ['loop-code'])

    def test_exact_bundle_expansion_preserves_registered_order(self):
        for query in ['/loop bundle office', 'bundle office', '/b office']:
            row = self.finder.resolve(self.catalog, query)
            self.assertEqual(row['kind'], 'bundle')
            self.assertEqual(row['skills'], self.catalog['bundles']['office']['skills'])

    def test_unknown_and_ambiguous_queries_do_not_guess_or_fall_back_to_all(self):
        for query in ['', '/l', 'office', '/loop bundle no-such-bundle', '/loop cod', '../loop-code']:
            with self.subTest(query=query), self.assertRaises(ValueError):
                self.finder.resolve(self.catalog, query)

    def test_search_can_find_names_aliases_and_function_without_invoking(self):
        for query in ['loop code', 'lc', 'implement']:
            rows = self.finder.search(self.catalog, query)
            self.assertIn('loop-code', [row['id'] for row in rows])
        self.assertEqual(self.finder.search(self.catalog, 'no-such-skill'), [])
        self.assertIn('office', [row['id'] for row in self.finder.search(self.catalog, 'bundle office')])

    def test_all_registered_names_and_aliases_have_one_exact_target(self):
        for name, row in self.catalog['skills'].items():
            for query in [name, *row['aliases']]:
                with self.subTest(query=query):
                    self.assertEqual(self.finder.resolve(self.catalog, query)['skills'], [name])

    def test_colliding_alias_unknown_bundle_member_and_duplicate_json_fail_closed(self):
        data = copy.deepcopy(self.catalog)
        data['skills']['loop-debug']['aliases'].append('lc')
        with self.assertRaises(ValueError): self.finder.validate_catalog(data)
        data = copy.deepcopy(self.catalog)
        data['bundles']['office']['skills'].append('missing-skill')
        with self.assertRaises(ValueError): self.finder.validate_catalog(data)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'catalog.json'
            path.write_text('{"version":1,"version":1}', encoding='utf-8')
            with self.assertRaises(ValueError): self.finder.load_catalog(path)

    def test_catalog_and_ui_metadata_match_actual_manifest_and_bundles(self):
        from scripts.discovery import check
        self.assertEqual(check(ROOT), [])
        self.assertEqual(set(self.catalog['skills']), set(json.loads((ROOT/'skills-manifest.json').read_text())['skills']))

    def test_stale_catalog_is_rejected_by_full_validator(self):
        from scripts.discovery import check
        from scripts.validate import validate
        from unittest import mock
        original = Path.read_text
        def changed(path, *args, **kwargs):
            text = original(path, *args, **kwargs)
            if path == ROOT/'.github/skills/loop/assets/catalog.json':
                return text.replace('"lc"', '"wrong-alias"')
            return text
        with mock.patch.object(Path, 'read_text', changed):
            self.assertTrue(check(ROOT))
            self.assertTrue(any('discovery metadata stale' in error for error in validate(ROOT)))

    def test_installed_gateway_runs_without_repository_imports_and_never_executes_query(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            script = root/'loop/scripts/find_skill.py'; script.parent.mkdir(parents=True)
            script.write_bytes((ROOT/'.github/skills/loop/scripts/find_skill.py').read_bytes())
            catalog = root/'loop/assets/catalog.json';catalog.parent.mkdir()
            catalog.write_bytes((ROOT/'.github/skills/loop/assets/catalog.json').read_bytes())
            argv = [sys.executable, '-I', '-B', str(script), 'resolve', '--query']
            result = subprocess.run([*argv, '/lc'], cwd=root, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            row = json.loads(result.stdout)
            self.assertEqual(row['missing_skills'], ['loop-code'])
            self.assertEqual(row['execution'], 'NONE')
            marker = root/'unsafe.txt'
            result = subprocess.run([*argv, '/lc; touch unsafe.txt'], cwd=root, capture_output=True, text=True, timeout=10)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse(marker.exists())


if __name__ == '__main__':
    unittest.main()
