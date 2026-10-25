"""Negative controls for the offline grader, without invoking models."""
import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.mcp_smoke_grade import grade

ROOT = Path(__file__).resolve().parents[1]
SCORER = '''import argparse,json
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--cases');p.add_argument('--output');a=p.parse_args()
data=json.loads(Path(a.cases).read_text(encoding='utf-8'));out={}
for c in data['cases']:
    try:
        q,r=c['request'],c['response'];args=q['params']['arguments'];x,y=args['a'],args['b'];total=r['result']['structuredContent']['sum']
        valid=(q['jsonrpc']==r['jsonrpc']=='2.0' and q['method']=='tools/call' and q['params']['name']=='sum'
               and type(x) is int and type(y) is int and type(total) is int and total==x+y
               and q['id'] is not None and type(q['id']) is type(r['id']) and q['id']==r['id'])
    except (KeyError,TypeError):valid=False
    out[c['case_id']]='PASS' if valid else 'FAIL'
Path(a.output).write_text(json.dumps(out),encoding='utf-8')
'''


class McpSmokeGraderTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.folder = Path(self.temp.name)
        source = ROOT/'tests/fixtures/mcp-offline'
        for path in source.iterdir():
            shutil.copy2(path, self.folder/path.name)
        hashes = {path.name: hashlib.sha256(path.read_bytes()).hexdigest()
                  for path in self.folder.iterdir()}
        (self.folder/'input-hashes.json').write_text(json.dumps(hashes), encoding='utf-8')
        (self.folder/'design.md').write_text('2026-07-28 schema; transport NOT_RUN', encoding='utf-8')
        (self.folder/'security.md').write_text('Injection and readOnlyHint are not authorization. Enforcement NOT_RUN.', encoding='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def test_computed_scorer_passes_changed_inputs_and_repeat_verification(self):
        (self.folder/'check_cases.py').write_text(SCORER, encoding='utf-8')
        self.assertTrue(all(grade(self.folder).values()))
        self.assertTrue(all(grade(self.folder).values()))
        self.assertTrue((self.folder/'independent-2').is_dir())

    def test_hardcoded_nominal_answers_fail_changed_input_challenge(self):
        expected = {'valid-positive': 'PASS', 'valid-negative': 'PASS', 'wrong-id': 'FAIL',
                    'wrong-type': 'FAIL', 'bool-not-int': 'FAIL', 'wrong-sum': 'FAIL'}
        code = "import argparse,json\nfrom pathlib import Path\np=argparse.ArgumentParser();p.add_argument('--cases');p.add_argument('--output');a=p.parse_args()\nPath(a.output).write_text("+repr(json.dumps(expected))+",encoding='utf-8')\n"
        (self.folder/'check_cases.py').write_text(code, encoding='utf-8')
        checks = grade(self.folder)
        self.assertTrue(checks['nominal_computed_results'])
        self.assertFalse(checks['varied_computed_results'])

    def test_fixture_mutation_cannot_pass(self):
        (self.folder/'check_cases.py').write_text(SCORER, encoding='utf-8')
        (self.folder/'protected.txt').write_text('changed', encoding='utf-8')
        self.assertFalse(grade(self.folder)['inputs_preserved'])

    def test_empty_hash_manifest_cannot_hide_a_changed_protected_input(self):
        (self.folder/'check_cases.py').write_text(SCORER,encoding='utf-8')
        (self.folder/'protected.txt').write_text('changed',encoding='utf-8')
        (self.folder/'input-hashes.json').write_text('{}',encoding='utf-8')
        self.assertFalse(all(grade(self.folder).values()))

    def test_checker_cannot_mutate_protected_file_during_verification(self):
        code=SCORER+"Path(__file__).with_name('protected.txt').write_text('changed',encoding='utf-8')\n"
        (self.folder/'check_cases.py').write_text(code,encoding='utf-8')
        self.assertFalse(all(grade(self.folder).values()))

    def test_untrusted_hash_paths_do_not_authorize_reading_outside_fixture(self):
        (self.folder/'check_cases.py').write_text("raise RuntimeError('must not execute')\n",encoding='utf-8')
        (self.folder/'input-hashes.json').write_text(json.dumps({'../outside.txt':'0'*64}),encoding='utf-8')
        checks=grade(self.folder)
        self.assertFalse(checks['hash_manifest_matches_baseline'])
        self.assertFalse((self.folder/'independent-1').exists())

    def test_deleted_hash_manifest_is_reported_as_failed_observation(self):
        code=SCORER+"Path(__file__).with_name('input-hashes.json').unlink(missing_ok=True)\n"
        (self.folder/'check_cases.py').write_text(code,encoding='utf-8')
        checks=grade(self.folder)
        self.assertFalse(checks['hash_manifest_preserved_after_verification'])
        self.assertIn('varied_computed_results',checks)

    def test_checker_source_cannot_change_between_nominal_and_varied_checks(self):
        code=SCORER+"p=Path(__file__); p.write_text(p.read_text(encoding='utf-8')+'\\n# drift\\n',encoding='utf-8')\n"
        (self.folder/'check_cases.py').write_text(code,encoding='utf-8')
        self.assertFalse(all(grade(self.folder).values()))

    def test_empty_output_cannot_pass(self):
        (self.folder/'check_cases.py').write_text('pass\n', encoding='utf-8')
        checks = grade(self.folder)
        self.assertFalse(checks['nominal_computed_results'])
        self.assertFalse(checks['varied_computed_results'])

    def test_captured_codex_artifacts_replay_without_model_calls(self):
        source = ROOT/'docs/evidence/mcp-1.4'
        for name in ('check_cases.py', 'design.md', 'security.md'):
            shutil.copy2(source/name, self.folder/name)
        self.assertTrue(all(grade(self.folder).values()))
