"""Filesystem alias regressions: never destroy evidence while reporting PASS."""
from argparse import Namespace
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts.run_loop import run_loop,run_batch
from scripts.sync_skills import sync


class EvidenceAliasTests(unittest.TestCase):
    def test_child_created_batch_summary_alias_is_not_overwritten(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); summary=root/'summary.json'; report=root/'summary.md'
            summary.write_bytes(b'keep summary')
            child_code="import os; os.link("+repr(str(summary))+','+repr(str(report))+"); print('LOOP_STATUS: PASS')"
            args=Namespace(command=[sys.executable,'-c',child_code],max_iterations=1,
                timeout_seconds=3,batch_dir=str(root),self_prompt=False)
            self.assertEqual(run_batch(args,['review']),1)
            self.assertEqual(summary.read_bytes(),b'keep summary')
            self.assertEqual(report.read_bytes(),b'keep summary')
            self.assertEqual(json.loads((root/'prompt-001.json').read_text(encoding='utf-8'))['final_status'],'PASS')

    def test_batch_summary_hardlinks_rejected_before_any_child(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); summary=root/'summary.json'; report=root/'summary.md'
            summary.write_bytes(b'preserve summary'); os.link(summary,report)
            args=Namespace(command=['must-not-execute'],max_iterations=1,timeout_seconds=3,
                batch_dir=str(root),self_prompt=False)
            with mock.patch('scripts.run_loop._run_command',return_value=('done',0,'digest','LOOP_STATUS: PASS','')) as child:
                with self.assertRaisesRegex(ValueError,'hardlink|alias|same file'):
                    run_batch(args,['review'])
                child.assert_not_called()
            self.assertEqual(summary.read_bytes(),b'preserve summary')

    def test_batch_summary_link_to_unrelated_file_is_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); unrelated=root/'retained.txt'; unrelated.write_bytes(b'keep this')
            os.link(unrelated,root/'summary.json')
            args=Namespace(command=[sys.executable,'-c',"print('LOOP_STATUS: PASS')"],
                max_iterations=1,timeout_seconds=3,batch_dir=str(root),self_prompt=False)
            with self.assertRaisesRegex(ValueError,'hardlink|alias|same file'):
                run_batch(args,['review'])
            self.assertEqual(unrelated.read_bytes(),b'keep this')

    def test_sync_rejects_internal_file_symlink_before_touching_unrelated_skill(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            source=root/'source'; target=root/'installed'; backup=root/'backup'
            skill=source/'.github/skills/loop-code/SKILL.md'
            skill.parent.mkdir(parents=True); skill.write_bytes(b'canonical')
            (source/'skills-manifest.json').write_text(json.dumps({'skills':['loop-code']}),encoding='utf-8')
            unrelated=target/'unrelated/SKILL.md'
            unrelated.parent.mkdir(parents=True); unrelated.write_bytes(b'keep unrelated')
            destination=target/'loop-code/SKILL.md'; destination.parent.mkdir()
            try:
                destination.symlink_to(unrelated)
            except OSError as exc:
                if os.name=='nt' and getattr(exc,'winerror',None)==1314:
                    self.skipTest('Windows account lacks file-symlink privilege; junction test is separate')
                raise
            with mock.patch('scripts.sync_skills.REPO',source):
                for check in (True,False):
                    with self.subTest(check=check), self.assertRaisesRegex(ValueError,'symlink|alias|reparse'):
                        sync(target,backup,check=check)
            self.assertEqual(unrelated.read_bytes(),b'keep unrelated')
            self.assertFalse(backup.exists())

    def test_sync_rejects_internal_directory_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            source=root/'source'; target=root/'installed'; backup=root/'backup'
            skill=source/'.github/skills/loop-code/SKILL.md'
            skill.parent.mkdir(parents=True); skill.write_bytes(b'canonical')
            (source/'skills-manifest.json').write_text(json.dumps({'skills':['loop-code']}),encoding='utf-8')
            unrelated=target/'unrelated/SKILL.md'
            unrelated.parent.mkdir(parents=True); unrelated.write_bytes(b'keep unrelated')
            if os.name=='nt':
                made=subprocess.run(['cmd','/c','mklink','/J',str(target/'loop-code'),str(unrelated.parent)],capture_output=True)
                self.assertEqual(made.returncode,0,made.stderr)
            else:
                (target/'loop-code').symlink_to(unrelated.parent,target_is_directory=True)
            with mock.patch('scripts.sync_skills.REPO',source), self.assertRaisesRegex(ValueError,'symlink|alias|reparse'):
                sync(target,backup)
            self.assertEqual(unrelated.read_bytes(),b'keep unrelated')

    def test_child_created_alias_is_rejected_before_persistence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state, report = root/'state.json', root/'report.md'
            original = b'preserve child-created alias'
            state.write_bytes(original)
            child = ("import os; os.link(" + repr(str(state)) + ',' + repr(str(report))
                     + "); print('LOOP_STATUS: PASS')")
            args = Namespace(command=[sys.executable, '-c', child], prompt='isolated alias',
                max_iterations=1, timeout_seconds=5, state_file=str(state),
                report_file=str(report), self_prompt=False)
            self.assertEqual(run_loop(args), 1)
            self.assertIsNone(args._verified_state)
            self.assertEqual(state.read_bytes(), original)
            self.assertEqual(report.read_bytes(), original)

    def test_state_and_report_hardlink_alias_rejected_before_child(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            state, report, executed = root/'state.json', root/'report.md', root/'executed.txt'
            original = b'{"existing": "preserve"}'
            state.write_bytes(original)
            os.link(state, report)
            args = Namespace(command=[sys.executable, '-c',
                "from pathlib import Path; Path(" + repr(str(executed)) + ").touch(); print('LOOP_STATUS: PASS')"],
                prompt='isolated alias check', max_iterations=1, timeout_seconds=5,
                state_file=str(state), report_file=str(report), self_prompt=False)
            with self.assertRaisesRegex(ValueError, 'hardlink|alias|same file'):
                run_loop(args)
            self.assertEqual(state.read_bytes(), original)
            self.assertEqual(report.read_bytes(), original)
            self.assertFalse(executed.exists())

    def test_evidence_hardlink_to_unrelated_file_is_rejected(self):
        for destination in ('state.json', 'report.md'):
            with self.subTest(destination=destination), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                outside = root/'unrelated.txt'
                outside.write_bytes(b'keep unrelated data')
                os.link(outside, root/destination)
                args = Namespace(command=[sys.executable, '-c', "print('LOOP_STATUS: PASS')"],
                    prompt='preserve unrelated fixture', max_iterations=1, timeout_seconds=5,
                    state_file=str(root/'state.json'), report_file=str(root/'report.md'), self_prompt=False)
                with self.assertRaisesRegex(ValueError, 'hardlink|alias|same file'):
                    run_loop(args)
                self.assertEqual(outside.read_bytes(), b'keep unrelated data')
