import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import shutil

from scripts.verification_session import COMMANDS, git_context, run_session, verify_report


class VerificationSessionTests(unittest.TestCase):
    def fixture(self, root):
        repo=root/'repo';(repo/'scripts').mkdir(parents=True)
        (repo/'scripts/example.py').write_text('value = 1\n',encoding='utf-8')
        (repo/'README.md').write_text('fixture\n',encoding='utf-8')
        return repo

    def successful_command(self, argv, **kwargs):
        return subprocess.CompletedProcess(argv,0,'','Ran 1 test in 0.001s\n\nOK\n')

    def test_correct_session_accepts_unchanged_input_and_rejects_other_session(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);repo=self.fixture(root);out=root/'run'
            report=run_session(repo,out,'session-a',execute=self.successful_command)
            self.assertEqual(report['status'],'PASS')
            self.assertEqual(len(report['checks']),len(COMMANDS))
            self.assertEqual(verify_report(repo,out/'verification.json','session-a'),[])
            self.assertTrue(verify_report(repo,out/'verification.json','session-b'))
            with self.assertRaises(FileExistsError):
                run_session(repo,out,'session-a',execute=self.successful_command)

    def test_edit_after_campaign_makes_previous_result_stale(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);repo=self.fixture(root);out=root/'run'
            run_session(repo,out,'session-a',execute=self.successful_command)
            (repo/'scripts/example.py').write_text('value = 2\n',encoding='utf-8')
            self.assertTrue(any('stale' in e for e in verify_report(repo,out/'verification.json','session-a')))

    def test_change_during_command_cannot_finish_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);repo=self.fixture(root);out=root/'run'
            def command(argv,**kwargs):
                (repo/'scripts/example.py').write_text('changed\n',encoding='utf-8')
                return self.successful_command(argv,**kwargs)
            report=run_session(repo,out,'session-a',execute=command)
            self.assertEqual(report['status'],'STALE')
            self.assertFalse(report['inputs_unchanged'])

    def test_omitted_gate_or_zero_test_discovery_cannot_validate(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);repo=self.fixture(root);out=root/'run'
            run_session(repo,out,'session-a',execute=self.successful_command)
            path=out/'verification.json';original=json.loads(path.read_text(encoding='utf-8'))
            for mutation in ('missing','zero','after-pin'):
                data=json.loads(json.dumps(original))
                if mutation=='missing':data['checks'].pop()
                elif mutation=='zero':data['checks'][0]['discovered']=0
                else:data['after_fingerprint']='wrong'
                path.write_text(json.dumps(data),encoding='utf-8')
                self.assertTrue(verify_report(repo,path,'session-a'))

    def test_zero_discovery_or_start_failure_is_retained_as_failed_campaign(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);repo=self.fixture(root)
            def empty(argv,**kwargs):
                return subprocess.CompletedProcess(argv,0,'','Ran 0 tests in 0.001s\nOK\n')
            self.assertEqual(run_session(repo,root/'empty','session-a',execute=empty)['status'],'FAIL')
            def unavailable(argv,**kwargs):raise OSError('unavailable test process')
            report=run_session(repo,root/'unavailable','session-a',execute=unavailable)
            self.assertEqual(report['status'],'FAIL')
            self.assertEqual(len(report['checks']),len(COMMANDS))
            self.assertTrue(all(row['exit_code'] is None for row in report['checks']))

    def test_nested_child_summary_does_not_replace_outer_suite_counts(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);repo=self.fixture(root)
            def nested(argv,**kwargs):
                return subprocess.CompletedProcess(argv,0,'Ran 999 tests in 1s\nOK (skipped=99)\n',
                    'Ran 1 test in 0.001s\n\nOK\n')
            report=run_session(repo,root/'run','session-a',execute=nested)
            self.assertEqual(report['checks'][0]['discovered'],1)
            self.assertEqual(report['checks'][0]['skipped'],0)

    @unittest.skipUnless(shutil.which('git'), 'git unavailable')
    def test_export_folder_does_not_claim_its_parent_repository_head(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);parent=root/'parent';parent.mkdir()
            subprocess.run(['git','init',str(parent)],check=True,capture_output=True)
            (parent/'anchor.txt').write_text('fixture',encoding='utf-8')
            subprocess.run(['git','-C',str(parent),'add','anchor.txt'],check=True,capture_output=True)
            subprocess.run(['git','-C',str(parent),'-c','user.name=Fixture',
                            '-c','user.email=fixture@example.invalid','-c','commit.gpgsign=false',
                            '-c',f'core.hooksPath={root / "no-hooks"}',
                            'commit','-m','fixture'],check=True,capture_output=True)
            exported=parent/'exported';exported.mkdir()
            self.assertIsNotNone(git_context(parent)['head_at_start'])
            self.assertIsNone(git_context(exported)['head_at_start'])
