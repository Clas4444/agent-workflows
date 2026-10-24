import json
from pathlib import Path
import tempfile
import unittest

from scripts.catalog import check_catalog, render
from scripts.validate import validate

ROOT = Path(__file__).resolve().parents[1]


class CatalogTests(unittest.TestCase):
    def test_group_partition_and_generated_readme_match(self):
        self.assertEqual(check_catalog(ROOT), [])
        groups = json.loads((ROOT/'skill-groups.json').read_text(encoding='utf-8'))
        self.assertEqual(len(groups), 7)
        names = [name for group in groups.values() for name in group['skills']]
        self.assertEqual(len(names), 29)
        self.assertEqual(len(set(names)), 29)

    def test_duplicate_and_missing_routes_fail_even_with_valid_skill_files(self):
        from test_validate import make_fixture
        import shutil
        root = make_fixture()
        try:
            shutil.copy2(ROOT/'README.md', root/'README.md')
            groups = json.loads((ROOT/'skill-groups.json').read_text(encoding='utf-8'))
            groups['verification']['skills'].append('loop-review')
            (root/'skill-groups.json').write_text(json.dumps(groups), encoding='utf-8')
            self.assertTrue(check_catalog(root))
            self.assertTrue(validate(root))
            groups['verification']['skills'].remove('loop-review')
            groups['verification']['skills'].remove('loop-test-adversarial')
            (root/'skill-groups.json').write_text(json.dumps(groups), encoding='utf-8')
            self.assertTrue(check_catalog(root))
        finally:
            shutil.rmtree(root)

    def test_historical_runtime_manifest_is_frozen_and_new_skill_not_claimed(self):
        historical = json.loads((ROOT/'docs/evidence/manifest-1.2.json').read_text(encoding='utf-8'))
        current = json.loads((ROOT/'skills-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(len(historical['skills']), 27)
        self.assertEqual(set(current['skills'])-set(historical['skills']), {'loop-test-adversarial', 'loop-test-compatibility'})
        text = (ROOT/'docs/RUNTIME-TEST-MATRIX.md').read_text(encoding='utf-8')
        for name in ('loop-test-adversarial', 'loop-test-compatibility'):
            row = next(line for line in text.splitlines() if f'| {name} |' in line)
            self.assertIn('NOT_RUN', row)
