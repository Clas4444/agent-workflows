import json
from pathlib import Path
import unittest
import re

REPO = Path(__file__).resolve().parents[1]


class SkillExpansionTests(unittest.TestCase):
    def test_all_skills_have_ordered_input_output_and_example_contracts(self):
        manifest = json.loads((REPO / 'skills-manifest.json').read_text(encoding='utf-8'))
        sections = ('## Use when', '## Inputs', '## Workflow', '## Output',
                    '## Boundaries and evidence', '## Example')
        for name in manifest['skills']:
            text = (REPO / '.github' / 'skills' / name / 'SKILL.md').read_text(encoding='utf-8')
            positions = [text.index(section) for section in sections]
            self.assertEqual(positions, sorted(positions), name)
            self.assertIn(f'/{name} ', text)

    def test_readme_catalog_and_local_links_resolve(self):
        readme = (REPO / 'README.md').read_text(encoding='utf-8')
        manifest = json.loads((REPO / 'skills-manifest.json').read_text(encoding='utf-8'))
        for name in manifest['skills']:
            self.assertIn(f'[{name}](.github/skills/{name}/SKILL.md)', readme)
        for destination in re.findall(r'\]\(([^)]+)\)', readme):
            if destination.startswith(('https://', 'http://', '#')):
                continue
            self.assertTrue((REPO / destination.split('#')[0]).exists(), destination)

    def test_manifest_and_documented_routes_cover_all_skills(self):
        manifest = json.loads((REPO / 'skills-manifest.json').read_text(encoding='utf-8'))
        self.assertEqual(len(manifest['skills']), 49)
        usage = (REPO / 'docs' / 'SKILL-USAGE.md').read_text(encoding='utf-8')
        for name in manifest['skills']:
            self.assertIn(f'`{name}`', usage)

    def test_new_workflows_have_evidence_and_distinct_acceptance_gates(self):
        contracts = {
            'loop-debug': ('reproduce', 'regression', 'root cause'),
            'loop-security': ('trust boundaries', 'redact', 'confidence'),
            'loop-refactor': ('characterization', 'baseline', 'observable behavior'),
            'loop-ci': ('run/job', 'local and remote', 'least-privilege'),
            'loop-release': ('checksums', 'rollback', 'do not tag'),
            'loop-plan': ('acceptance criteria', 'dependency-ordered', 'out-of-scope'),
            'loop-dependencies': ('lockfile', 'lifecycle scripts', 'rollback'),
            'loop-migrate': ('dry-run', 'idempotent', 'byte-identical'),
            'loop-test-e2e': ('real entry point', 'invalid-input', 'side effects'),
            'loop-evaluate': ('false positives', 'denominators', 'before looking'),
        }
        for name, terms in contracts.items():
            text = (REPO / '.github' / 'skills' / name / 'SKILL.md').read_text(encoding='utf-8').lower()
            for term in terms:
                self.assertIn(term, text, name)
            for section in ('## use when', '## workflow', '## boundaries and evidence'):
                self.assertIn(section, text, name)
