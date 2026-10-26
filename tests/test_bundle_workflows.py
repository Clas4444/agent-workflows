"""Check exact coverage and refusal of stale or invalid bundle guidance."""
import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from scripts.bundle_workflows import ASSETS, DATA, GUIDE, check, load_workflows, outputs, svg

ROOT = Path(__file__).resolve().parents[1]


class BundleWorkflowTests(unittest.TestCase):
    def fixture(self, root):
        for name in ('skills-manifest.json', 'skill-bundles.json', DATA):
            target = root/name; target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT/name, target)
        for name, text in outputs(root).items():
            path = root/name; path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding='utf-8', newline='\n')

    def test_every_bundle_has_one_accessible_current_diagram_and_text_equivalent(self):
        self.assertEqual(check(ROOT), [])
        bundles, rows = load_workflows(ROOT)
        self.assertEqual(set(bundles), set(rows))
        self.assertEqual(len(list((ROOT/ASSETS).glob('*.svg'))), len(bundles))
        guide = (ROOT/GUIDE).read_text(encoding='utf-8')
        for key, row in rows.items():
            tree = ET.parse(ROOT/ASSETS/(key+'.svg'))
            text = ''.join(tree.getroot().itertext())
            self.assertIsNotNone(tree.find('{http://www.w3.org/2000/svg}title'))
            self.assertIsNotNone(tree.find('{http://www.w3.org/2000/svg}desc'))
            for name in bundles[key]['skills']:
                self.assertIn(name, text)
            for value in [row['when'], row['why'], *row['do'], *row['dont']]:
                self.assertIn(value, guide)
            self.assertIn('$loop bundle '+key, guide)

    def test_missing_stale_and_extra_svg_fail_without_rewriting(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.fixture(root)
            image = root/ASSETS/'support.svg'; original = image.read_bytes()
            image.write_bytes(original+b'changed')
            self.assertTrue(any('support.svg' in e for e in check(root)))
            self.assertEqual(image.read_bytes(), original+b'changed')
            image.unlink()
            self.assertTrue(any('support.svg' in e for e in check(root)))
            image.write_bytes(original)
            (root/ASSETS/'duplicate.svg').write_text('<svg/>', encoding='utf-8')
            self.assertTrue(any('unexpected' in e for e in check(root)))

    def test_invalid_bundle_coverage_or_step_member_refuses_write_before_outputs_change(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp); self.fixture(root)
            data = json.loads((root/DATA).read_text(encoding='utf-8'))
            before = {name: (root/name).read_bytes() for name in outputs(root)}
            for kind in ('missing', 'extra', 'outside-member', 'bad-version'):
                bad = copy.deepcopy(data)
                if kind == 'missing': del bad['bundles']['files']
                elif kind == 'extra': bad['bundles']['fake'] = bad['bundles']['files']
                elif kind == 'outside-member': bad['bundles']['files']['steps'][0]['skills'] = ['loop-code']
                else: bad['version'] = True
                (root/DATA).write_text(json.dumps(bad), encoding='utf-8')
                result = subprocess.run([sys.executable, str(ROOT/'scripts/bundle_workflows.py'),
                                         '--repo', str(root), '--write'], capture_output=True, text=True, timeout=20)
                self.assertEqual(result.returncode, 1, (kind, result.stdout, result.stderr))
                self.assertEqual(before, {name: (root/name).read_bytes() for name in before})

    def test_svg_escapes_source_text_and_refuses_overflow(self):
        bundles, rows = load_workflows(ROOT)
        row = copy.deepcopy(rows['files'])
        row['title'] = '<script>safe & visible</script>'
        tree = ET.fromstring(svg('files', row, bundles['files']))
        self.assertEqual(tree.findall('.//{http://www.w3.org/2000/svg}script'), [])
        self.assertIn(row['title'], ''.join(tree.itertext()))
        row['title'] = 'long title '*100
        with self.assertRaisesRegex(ValueError, 'reserved area'):
            svg('files', row, bundles['files'])
        row['title'] = 'x'*200
        with self.assertRaisesRegex(ValueError, 'reserved area'):
            svg('files', row, bundles['files'])


if __name__ == '__main__':
    unittest.main()
