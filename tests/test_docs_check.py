"""Documentation navigation checks against real filesystem fixtures."""
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts.docs_check import check

ROOT = Path(__file__).resolve().parents[1]


class DocsCheckTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)/'repo'
        self.root.mkdir()
        self.write('README.md', '# Fixture\n')

    def write(self, name, text):
        path = self.root/name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding='utf-8')
        return path

    def test_real_repository_and_explicit_unchecked_network_scope(self):
        result = check(ROOT)
        self.assertEqual(result['status'], 'PASS', result['errors'])
        self.assertGreater(result['local_links'], 500)
        self.assertEqual(result['external_urls'], 'NOT_RUN')
        self.assertEqual(result['writes'], 'NONE')

    def test_heading_markup_unicode_duplicate_collisions_and_custom_anchors(self):
        self.write('docs/guide.md', '# Guide\n## Details\n## Details-1\n## Details\n'
                   '## **Types** and `my_field`\n## Kiểm tra\n<a name="guide-nav"></a>\n')
        self.write('README.md', '\n'.join('[link](docs/guide.md#'+anchor+')' for anchor in
                   ['details','details-1','details-2','types-and-my_field','kiểm-tra','guide-nav']))
        result = check(self.root)
        self.assertEqual(result['status'], 'PASS', result['errors'])
        self.assertEqual(result['heading_anchors'], 6)

    def test_missing_file_or_anchor_fails_with_original_line_and_no_write(self):
        source = self.write('README.md', '# Fixture\n\n[missing](docs/missing.md)\n[anchor](#absent)\n')
        before = source.read_bytes()
        result = check(self.root)
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual({e['line'] for e in result['errors']}, {3,4})
        self.assertEqual(source.read_bytes(), before)
        self.assertFalse((self.root/'docs').exists())

    def test_fences_comments_and_inline_code_are_not_navigation(self):
        self.write('README.md', '# Fixture\n````text\n[no](missing.md)\n```\n'
                   '[still code](also-missing.md)\n````\n'
                   '<!--\n[comment](comment-missing.md)\n-->\n'
                   '``code ` literal [link](inline-missing.md)``\n[real](#fixture)\n')
        result = check(self.root)
        self.assertEqual(result['status'], 'PASS', result['errors'])
        self.assertEqual(result['local_links'], 1)

    def test_anchor_example_inside_inline_code_cannot_validate_a_real_link(self):
        self.write('README.md', '# Fixture\n`<a name="not-real"></a>`\n[link](#not-real)\n')
        result = check(self.root)
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(any('anchor' in e['error'] for e in result['errors']))

    def test_escaped_literal_link_is_not_navigation(self):
        self.write('README.md', '# Fixture\n\\[literal](missing.md)\n[real](#fixture)\n')
        result = check(self.root)
        self.assertEqual(result['status'], 'PASS', result['errors'])
        self.assertEqual(result['local_links'], 1)

    def test_even_backslashes_cannot_hide_a_broken_link(self):
        for count in range(5):
            self.write('README.md', '# Fixture\n'+'\\'*count+'[missing](missing.md)\n')
            self.assertEqual(check(self.root)['status'], 'PASS' if count % 2 else 'FAIL', count)

    def test_escaping_image_bang_still_leaves_a_real_text_link(self):
        self.write('README.md', '# Fixture\n\\![still a link](missing.md)\n')
        self.assertEqual(check(self.root)['status'], 'FAIL')
        self.write('README.md', '# Fixture\n!\\[literal](missing.md)\n')
        self.assertEqual(check(self.root)['status'], 'PASS')

    def test_root_relative_encoded_spaces_parentheses_titles_and_query(self):
        self.write('docs/Guide (draft).md', '# A title\n')
        self.write('docs/page.md', '[root](/README.md#fixture)\n'
                   '[encoded](Guide%20%28draft%29.md?raw=1#a-title)\n'
                   '[angle](<Guide (draft).md> "a title")\n')
        self.write('docs/plain(draft).md', '# Other\n')
        self.write('README.md', '# Fixture\n[balanced](docs/plain(draft).md)\n')
        self.assertEqual(check(self.root)['status'], 'PASS')

    def test_multiline_label_and_plain_index_expression_are_not_false_failures(self):
        self.write('docs/target.md', '# Target\n')
        self.write('README.md', "Use grade(protocol['cases'][case_name]).\n"
                   '[Recorded commands,\noutputs](docs/target.md#target)\n')
        result = check(self.root)
        self.assertEqual(result['status'], 'PASS', result['errors'])
        self.assertEqual(result['local_links'], 1)

    def test_mixed_heading_styles_keep_document_order_and_case_errors_are_portable(self):
        self.write('docs/guide.md', '# Part\nPart-1\n------\n## Part\n')
        self.write('README.md', '[third](docs/guide.md#part-2)\n')
        self.assertEqual(check(self.root)['status'], 'PASS')
        self.write('README.md', '[wrong case](docs/Guide.md)\n')
        result = check(self.root)
        self.assertEqual(result['status'], 'FAIL')
        self.assertTrue(any('case' in e['error'] for e in result['errors']))

    def test_external_and_non_markdown_fragments_are_separate_not_network_pass(self):
        self.write('image.svg', '<svg/>')
        self.write('README.md', '[web](https://example.invalid/no-network)\n'
                   '[mail](mailto:example@example.invalid)\n![image](image.svg#shape)\n')
        result = check(self.root)
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual(result['external_links_not_fetched'], 2)
        self.assertEqual(result['non_markdown_fragments_not_checked'], 1)

    def test_escape_is_rejected_before_any_external_read(self):
        outside = Path(self.temp.name)/'private.md'
        outside.write_text('# Private\n', encoding='utf-8')
        self.write('README.md', '[escape](../private.md#private)\n[encoded](%2e%2e/private.md)\n')
        original = Path.read_text
        reads = []
        def reading(path, *args, **kwargs):
            reads.append(path)
            return original(path, *args, **kwargs)
        with mock.patch.object(Path, 'read_text', reading):
            result = check(self.root)
        self.assertEqual(result['status'], 'FAIL')
        self.assertNotIn(outside, reads)
        self.assertTrue(all('outside' in e['error'] for e in result['errors']))

    def test_hardlinked_markdown_cannot_be_used_as_a_source_or_target(self):
        outside = Path(self.temp.name)/'private.md'
        outside.write_text('# Private\n', encoding='utf-8')
        os.link(outside, self.root/'linked.md')
        self.write('README.md', '[alias](linked.md#private)\n')
        self.assertEqual(check(self.root)['status'], 'FAIL')

    def test_reference_style_and_unhandled_inline_syntax_do_not_silently_pass(self):
        for source in ('[label][missing-ref]\n', '[deep](a(b(c)).md)\n'):
            self.write('README.md', source)
            result = check(self.root)
            self.assertEqual(result['status'], 'FAIL', source)
            self.assertTrue(any('unsupported' in e['error'] for e in result['errors']))

    def test_long_inline_destinations_do_not_backtrack_exponentially(self):
        # Isolate the vulnerable expression so a regression cannot hang the
        # entire suite. Both rejecting and accepting long destinations matter.
        code = ("from scripts.docs_check import LINK\n"
                "for char in ('!', 'a', '-'):\n"
                "    body = char * 50000\n"
                "    assert LINK.search('[](' + body) is None\n"
                "    assert LINK.search('[](' + body + ' ' + chr(34) + 'unterminated') is None\n"
                "    assert LINK.fullmatch('[](' + body + ')') is not None\n")
        try:
            result = subprocess.run([sys.executable, '-c', code], cwd=ROOT,
                                    capture_output=True, text=True, timeout=5)
        except subprocess.TimeoutExpired:
            self.fail('inline-link matching exceeded the bounded regression timeout')
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_missing_readme_and_invalid_utf8_are_controlled_failures(self):
        (self.root/'README.md').unlink()
        self.assertEqual(check(self.root)['status'], 'FAIL')
        (self.root/'README.md').write_bytes(b'\xff')
        self.assertEqual(check(self.root)['status'], 'FAIL')

    def test_real_cli_json_and_module_forms_agree_without_artifacts(self):
        self.write('README.md', '# Fixture\n[home](#fixture)\n')
        for args in ([str(ROOT/'scripts/docs_check.py')], ['-m','scripts.docs_check']):
            result = subprocess.run([sys.executable,*args,'--repo',str(self.root),'--json'],
                                    cwd=ROOT,capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['status'], 'PASS')
        self.assertEqual(sorted(p.name for p in self.root.iterdir()), ['README.md'])

    def test_ascii_terminal_reports_unicode_source_without_traceback(self):
        self.write('docs/ghi-chú.md', '[missing](absent.md)\n')
        env = dict(os.environ, PYTHONIOENCODING='ascii')
        result = subprocess.run([sys.executable,str(ROOT/'scripts/docs_check.py'),
                                 '--repo',str(self.root)], cwd=ROOT, env=env,
                                capture_output=True,text=True,encoding='ascii',timeout=20)
        self.assertEqual(result.returncode, 1)
        self.assertIn('missing local target', result.stdout)
        self.assertNotIn('Traceback', result.stderr)


if __name__ == '__main__':
    unittest.main()
