import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
HELPER=ROOT/'.github/skills/loop-files/scripts/file_plan.py'


class FilePlanTests(unittest.TestCase):
    def fixture(self, root):
        selected=root/'selected';(selected/'A').mkdir(parents=True);(selected/'Finance').mkdir()
        (selected/'A/receipt.txt').write_bytes(b'first receipt\n')
        (selected/'Finance/receipt.txt').write_bytes(b'keep existing\n')
        mapping=root/'mapping.json';mapping.write_text(json.dumps({'version':1,'moves':[
            {'source':'A/receipt.txt','destination':'Finance/A-receipt.txt'}]}),encoding='utf-8')
        return selected,mapping

    def command(self, mode, root, *args):
        return subprocess.run([sys.executable,str(HELPER),mode,str(root),*map(str,args)],
                              capture_output=True,text=True,encoding='utf-8',timeout=20)

    def plan(self, root, mapping):
        result=self.command('plan',root,'--mapping',mapping)
        self.assertEqual(result.returncode,0,result.stderr)
        path=mapping.parent/'plan.json';path.write_text(result.stdout,encoding='utf-8')
        return path

    def test_plan_check_actual_native_move_and_verify_preserve_protected_file(self):
        with tempfile.TemporaryDirectory() as directory:
            selected,mapping=self.fixture(Path(directory));plan=self.plan(selected,mapping)
            self.assertEqual(self.command('check',selected,'--plan',plan).returncode,0)
            self.assertTrue((selected/'A/receipt.txt').is_file())  # Helper never moved it.
            (selected/'A/receipt.txt').rename(selected/'Finance/A-receipt.txt')
            verified=self.command('verify',selected,'--plan',plan)
            self.assertEqual(verified.returncode,0,verified.stderr)
            self.assertEqual((selected/'Finance/receipt.txt').read_bytes(),b'keep existing\n')
            self.assertEqual(json.loads(verified.stdout)['moves_executed_by_helper'],'NOT_RUN')

    def test_drift_unexpected_files_and_wrong_root_cannot_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);selected,mapping=self.fixture(root);plan=self.plan(selected,mapping)
            other=root/'other';other.mkdir()
            self.assertEqual(self.command('check',other,'--plan',plan).returncode,1)
            (selected/'extra.txt').write_bytes(b'new')
            self.assertEqual(self.command('check',selected,'--plan',plan).returncode,1)
            (selected/'extra.txt').unlink();(selected/'A/receipt.txt').write_bytes(b'changed')
            self.assertEqual(self.command('check',selected,'--plan',plan).returncode,1)

    def test_destination_collision_escape_case_alias_and_file_parent_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            selected,mapping=self.fixture(Path(directory))
            for destination in ['Finance/receipt.txt','../outside.txt','C:/outside','finance/new.txt',
                                'A/receipt.txt/nested.txt','Finance/NUL.txt']:
                mapping.write_text(json.dumps({'version':1,'moves':[{
                    'source':'A/receipt.txt','destination':destination}]}),encoding='utf-8')
                self.assertEqual(self.command('plan',selected,'--mapping',mapping).returncode,1,destination)
                self.assertEqual((selected/'A/receipt.txt').read_bytes(),b'first receipt\n')

    def test_post_move_content_or_protected_file_tampering_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            selected,mapping=self.fixture(Path(directory));plan=self.plan(selected,mapping)
            (selected/'A/receipt.txt').rename(selected/'Finance/A-receipt.txt')
            (selected/'Finance/receipt.txt').write_bytes(b'unrelated change')
            self.assertEqual(self.command('verify',selected,'--plan',plan).returncode,1)

    def test_hardlinks_and_duplicate_json_keys_fail_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);selected,mapping=self.fixture(root)
            mapping.write_text('{"version":1,"moves":[],"moves":[]}',encoding='utf-8')
            self.assertEqual(self.command('plan',selected,'--mapping',mapping).returncode,1)
            outside=root/'outside';outside.write_bytes(b'fixture outside')
            os.link(outside,selected/'alias.txt')
            self.assertEqual(self.command('inventory',selected).returncode,1)
            self.assertEqual(outside.read_bytes(),b'fixture outside')
