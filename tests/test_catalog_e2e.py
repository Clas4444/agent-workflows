"""Complete local maintainer journeys through the actual CLI entry points."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

from tests.test_validate import make_fixture

ROOT = Path(__file__).resolve().parents[1]


class CatalogJourneyTests(unittest.TestCase):
    def setUp(self):
        self.root = make_fixture()
        for name in ('README.md', 'skill-groups.json'):
            shutil.copy2(ROOT/name, self.root/name)
        self.skill_bytes = {
            str(p.relative_to(self.root)): p.read_bytes()
            for native in ('.github', '.agents', '.claude')
            for p in (self.root/native).rglob('SKILL.md')}

    def tearDown(self):
        shutil.rmtree(self.root)

    def cli(self, *args):
        return subprocess.run([sys.executable, *args], cwd=self.root,
                              capture_output=True, text=True, timeout=30)

    def test_edit_group_rebuild_validate_journey_preserves_all_skill_files(self):
        path = self.root/'skill-groups.json'
        groups = json.loads(path.read_text(encoding='utf-8'))
        groups['verification']['title'] = 'Verification and compatibility checks'
        path.write_text(json.dumps(groups), encoding='utf-8')
        self.assertEqual(self.cli('scripts/catalog.py').returncode, 1)
        self.assertEqual(self.cli('scripts/validate.py').returncode, 1)
        self.assertEqual(self.cli('scripts/catalog.py', '--write').returncode, 0)
        self.assertIn('### Verification and compatibility checks',
                      (self.root/'README.md').read_text(encoding='utf-8'))
        self.assertEqual(self.cli('scripts/validate.py').returncode, 0)
        for relative, before in self.skill_bytes.items():
            self.assertEqual((self.root/relative).read_bytes(), before)

    def test_unknown_route_cannot_rewrite_readme(self):
        before = (self.root/'README.md').read_bytes()
        path = self.root/'skill-groups.json'
        groups = json.loads(path.read_text(encoding='utf-8'))
        groups['verification']['skills'].append('../outside')
        path.write_text(json.dumps(groups), encoding='utf-8')
        result = self.cli('scripts/catalog.py', '--write')
        self.assertEqual(result.returncode, 1)
        self.assertIn('unknown skill', result.stderr)
        self.assertEqual((self.root/'README.md').read_bytes(), before)

    def test_incorrect_advertised_skill_count_fails_real_catalog_gate(self):
        path = self.root/'README.md'
        text = path.read_text(encoding='utf-8')
        import re
        path.write_text(re.sub(r'\*\*[0-9]+ bounded workflows', '**1 bounded workflows', text), encoding='utf-8')
        result = self.cli('scripts/catalog.py')
        self.assertEqual(result.returncode, 1, result.stdout)
        self.assertIn('count', result.stdout)

    def test_available_script_module_matrix_matches_valid_and_invalid_inputs(self):
        for tool in ('validate', 'catalog'):
            script = self.cli(f'scripts/{tool}.py')
            module = self.cli('-m', f'scripts.{tool}')
            self.assertEqual(script.returncode, 0, script.stderr)
            self.assertEqual((script.returncode, script.stdout), (module.returncode, module.stdout))
        for invocation in (['scripts/validate.py'], ['-m', 'scripts.validate']):
            result = self.cli(*invocation, '--profile', 'unsupported')
            self.assertEqual(result.returncode, 2)
            self.assertIn('invalid choice', result.stderr)
