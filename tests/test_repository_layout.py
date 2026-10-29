from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
COMPATIBILITY = {
    'docs/ACCEPTANCE-GATE.md': 'docs/reference/acceptance-gate.md',
    'docs/EVIDENCE.md': 'docs/testing/evidence.md',
    'docs/testing/BUNDLE-ATLAS-2026-10-26.md': 'docs/testing/history/2026-10-26-bundle-atlas.md',
    'docs/testing/DOCS-REVIEW-1.10-2026-10-26.md': 'docs/testing/history/2026-10-26-docs-review-1.10.md',
}


class RepositoryLayoutTests(unittest.TestCase):
    def test_compatibility_links_reach_canonical_documents(self):
        for old, new in COMPATIBILITY.items():
            text = (ROOT/old).read_text(encoding='utf-8')
            link = re.search(r'\]\(([^)]+)\)', text)
            self.assertIsNotNone(link, old)
            self.assertEqual(((ROOT/old).parent/link[1]).resolve(), (ROOT/new).resolve())
            self.assertTrue((ROOT/new).is_file())

    def test_document_names_and_top_level_placement(self):
        self.assertEqual({p.name for p in (ROOT/'docs').glob('*.md')},
                         {'README.md', 'ACCEPTANCE-GATE.md', 'EVIDENCE.md'})
        for base in ('guides', 'reference', 'testing'):
            for path in (ROOT/'docs'/base).rglob('*.md'):
                relative = path.relative_to(ROOT).as_posix()
                if path.name == 'README.md' or relative in COMPATIBILITY:
                    continue
                self.assertRegex(path.name, r'^[a-z0-9][a-z0-9.-]*\.md$', relative)


if __name__ == '__main__':
    unittest.main()
