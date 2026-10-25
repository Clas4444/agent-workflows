import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

from scripts.workflows import GUIDE, IMAGE, check_workflows, load_presets, outputs, svg

ROOT = Path(__file__).resolve().parents[1]


class WorkflowGuideTests(unittest.TestCase):
    def fixture(self, root):
        for name in ('skills-manifest.json', 'workflow-presets.json'):
            shutil.copy2(ROOT/name, root/name)
        for name, content in outputs(root).items():
            path = root/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding='utf-8')

    def test_current_guide_and_accessible_svg_match_known_skills(self):
        self.assertEqual(check_workflows(ROOT), [])
        tree = ET.fromstring((ROOT/IMAGE).read_text(encoding='utf-8'))
        text = ''.join(tree.itertext())
        for row in load_presets(ROOT):
            for name in row['core']+row['optional']:
                self.assertIn(name, text)
        self.assertIsNotNone(tree.find('{http://www.w3.org/2000/svg}title'))
        self.assertIsNotNone(tree.find('{http://www.w3.org/2000/svg}desc'))

    def test_stale_guide_or_image_fails_without_rewriting(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root)
            for name in (GUIDE, IMAGE):
                path = root/name
                original = path.read_bytes()
                path.write_bytes(original+b'changed')
                self.assertTrue(any(name in error for error in check_workflows(root)))
                self.assertEqual(path.read_bytes(), original+b'changed')
                path.write_bytes(original)

    def test_invalid_inventory_or_duplicate_profiles_fail_before_any_write(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            self.fixture(root)
            original = json.loads((root/'workflow-presets.json').read_text(encoding='utf-8'))
            before = {name: (root/name).read_bytes() for name in (GUIDE, IMAGE)}
            for mutation in ('unknown', 'duplicate', 'overlap', 'version'):
                data = copy.deepcopy(original)
                if mutation == 'unknown':
                    data['profiles'][0]['core'][0] = 'nonexistent-skill'
                elif mutation == 'duplicate':
                    data['profiles'].append(data['profiles'][0])
                elif mutation == 'overlap':
                    data['profiles'][0]['optional'].append(data['profiles'][0]['core'][0])
                else:
                    data['version'] = True
                (root/'workflow-presets.json').write_text(json.dumps(data), encoding='utf-8')
                result = subprocess.run([sys.executable, str(ROOT/'scripts/workflows.py'),
                                         '--repo', str(root), '--write'], capture_output=True,
                                        text=True, timeout=20)
                self.assertEqual(result.returncode, 1, result.stdout+result.stderr)
                self.assertEqual(before, {name: (root/name).read_bytes() for name in before})

    def test_svg_escapes_text_instead_of_creating_elements(self):
        profiles = copy.deepcopy(load_presets(ROOT))
        profiles[0]['title'] = '<script>example & text</script>'
        tree = ET.fromstring(svg(profiles))
        self.assertIn(profiles[0]['title'], ''.join(tree.itertext()))
        self.assertEqual(tree.findall('.//{http://www.w3.org/2000/svg}script'), [])

    def test_long_valid_toolkit_does_not_overlap_the_next_card(self):
        profiles = copy.deepcopy(load_presets(ROOT))
        names = json.loads((ROOT/'skills-manifest.json').read_text(encoding='utf-8'))['skills']
        profiles[0]['core'] = names
        profiles[0]['optional'] = []
        tree = ET.fromstring(svg(profiles))
        namespace = '{http://www.w3.org/2000/svg}'
        cards = tree.findall('.//'+namespace+'rect')[1:]
        texts = tree.findall('.//'+namespace+'text')[2:]
        # Cards own contiguous text spans. First toolkit contains all manifest names.
        second_top = float(cards[1].attrib['y'])
        first_core_end = next(i for i, node in enumerate(texts)
                              if ''.join(node.itertext()).startswith('Optional:'))
        self.assertTrue(all(float(node.attrib['y']) < second_top
                            for node in texts[:first_core_end+3]))
        self.assertGreater(float(cards[0].attrib['height']), 225)
