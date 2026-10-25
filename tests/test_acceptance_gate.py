"""Behavioral tests for the opt-in acceptance gate, using isolated subprocesses."""
import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.acceptance_gate import run_contract


class AcceptanceGateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'requirements.txt').write_text('accept positive, reject negative', encoding='utf-8')
        self.contract = {
            'version': 1,
            'sources': [{'path': 'requirements.txt', 'sha256': hashlib.sha256(
                (self.root / 'requirements.txt').read_bytes()).hexdigest()}],
            'criteria': [{'id': 'input', 'expectation': 'Accept positive; reject negative.',
                          'checks': ['valid', 'invalid']}],
            'checks': [self.check('valid', 'positive', 0), self.check('invalid', 'negative', 2)],
        }

    @staticmethod
    def check(name, kind, exit_code):
        return {'id': name, 'kind': kind, 'argv': [sys.executable, '-c',
                f"print('observed: {name}'); raise SystemExit({exit_code})"],
                'cwd': '.', 'timeout_seconds': 3, 'expected_exit': exit_code,
                'stdout_contains': f'observed: {name}'}

    def run_gate(self, execute=True):
        return run_contract(self.contract, self.root, execute=execute)

    def test_real_positive_and_rejection_are_pass(self):
        result = self.run_gate()
        self.assertEqual(result['status'], 'PASS')
        self.assertEqual([r['exit_code'] for r in result['checks']], [0, 2])
        self.assertEqual(result['criteria'][0]['status'], 'PASS')

    def test_plan_only_does_not_execute_or_pass(self):
        self.contract['checks'][0]['argv'] = [sys.executable, '-c',
            "from pathlib import Path; Path('sentinel').touch()"]
        result = self.run_gate(False)
        self.assertEqual(result['status'], 'NOT_RUN')
        self.assertFalse((self.root / 'sentinel').exists())

    def test_changed_source_blocks_every_command(self):
        (self.root / 'requirements.txt').write_text('changed', encoding='utf-8')
        result = self.run_gate()
        self.assertEqual(result['status'], 'BLOCKED')
        self.assertTrue(all(r['status'] == 'NOT_RUN' for r in result['checks']))

    def test_missing_source_blocks(self):
        (self.root / 'requirements.txt').unlink()
        self.assertEqual(self.run_gate()['status'], 'BLOCKED')

    def test_zero_tests_exit_zero_is_not_enough(self):
        self.contract['checks'][0]['argv'] = [sys.executable, '-c', "print('Ran 0 tests; OK')"]
        self.contract['checks'][0]['stdout_contains'] = 'OK'
        self.assertEqual(self.run_gate()['status'], 'FAIL')

    def test_missing_cwd_is_blocked(self):
        self.contract['checks'][0]['cwd'] = 'missing-directory'
        self.assertEqual(self.run_gate()['status'], 'BLOCKED')

    def test_acceptance_id_is_not_lost_when_one_control_fails(self):
        self.contract['checks'][1]['expected_exit'] = 0
        result = self.run_gate()
        self.assertEqual(result['criteria'], [{'id': 'input',
            'expectation': 'Accept positive; reject negative.', 'status': 'FAIL'}])

    def test_real_cli_and_deliberately_broken_rejection(self):
        app = self.root / 'app.py'
        original = "import sys\nn = int(sys.argv[1])\nif n < 0:\n    print('rejected')\n    sys.exit(2)\nprint(n * 2)\n"
        app.write_text(original, encoding='utf-8')
        self.contract['checks'][0].update(argv=[sys.executable, str(app), '3'], stdout_contains='6')
        self.contract['checks'][1].update(argv=[sys.executable, str(app), '-1'], stdout_contains='rejected')
        contract = self.root / 'contract.json'
        script = Path(__file__).resolve().parents[1] / 'scripts/acceptance_gate.py'
        for broken, expected in ((False, 'PASS'), (True, 'FAIL')):
            if broken:
                app.write_text(original.replace('if n < 0:', 'if False:'), encoding='utf-8')
            # Pin each intentionally distinct implementation, retaining the same expectations.
            self.contract['sources'] = [{'path': 'app.py', 'sha256': hashlib.sha256(app.read_bytes()).hexdigest()}]
            contract.write_text(json.dumps(self.contract), encoding='utf-8')
            completed = subprocess.run([sys.executable, str(script), str(contract), '--root',
                str(self.root), '--execute'], capture_output=True, text=True)
            self.assertEqual(json.loads(completed.stdout)['status'], expected)
            self.assertEqual(completed.returncode, int(broken))

    def test_duplicate_json_keys_are_rejected(self):
        contract = self.root / 'contract.json'
        contract.write_text('{"version": 1, "version": 1}', encoding='utf-8')
        script = Path(__file__).resolve().parents[1] / 'scripts/acceptance_gate.py'
        completed = subprocess.run([sys.executable, str(script), str(contract), '--root',
            str(self.root)], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 1)
        self.assertIn('duplicate JSON key', json.loads(completed.stdout)['error'])

    def test_missing_executable_is_blocked_even_for_negative_case(self):
        self.contract['checks'][1]['argv'] = [str(self.root / 'missing-tool')]
        self.assertEqual(self.run_gate()['status'], 'BLOCKED')

    def test_timeout_cannot_satisfy_expected_rejection(self):
        row = self.contract['checks'][1]
        row['argv'] = [sys.executable, '-c', 'import time; time.sleep(3)']
        row['timeout_seconds'] = 0.05
        self.assertEqual(self.run_gate()['status'], 'FAIL')

    def test_timeout_preserves_partial_output_for_diagnosis(self):
        row = self.contract['checks'][1]
        row['argv'] = [sys.executable, '-c',
            "import sys,time; print('diagnostic before hang', flush=True); print('stderr before hang', file=sys.stderr, flush=True); time.sleep(5)"]
        row['timeout_seconds'] = 0.3
        result = self.run_gate()
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('diagnostic before hang', result['checks'][1]['stdout'])
        self.assertIn('stderr before hang', result['checks'][1]['stderr'])

    def test_oversized_numeric_timeout_is_rejected_cleanly(self):
        self.contract['checks'][0]['timeout_seconds'] = 10**400
        with self.assertRaisesRegex(ValueError, 'timeout_seconds'):
            self.run_gate()

    def test_failure_does_not_skip_other_checks(self):
        self.contract['checks'][0]['expected_exit'] = 7
        result = self.run_gate()
        self.assertEqual(result['status'], 'FAIL')
        self.assertEqual(result['checks'][1]['status'], 'PASS')

    def test_context_changed_during_execution_invalidates_success(self):
        self.contract['checks'][0]['argv'] = [sys.executable, '-c',
            "from pathlib import Path; Path('requirements.txt').write_text('new'); print('observed: valid')"]
        self.assertEqual(self.run_gate()['status'], 'BLOCKED')

    def test_context_retarget_preserves_completed_command_observations(self):
        work=self.root/'case'; work.mkdir()
        good=work/'original'; good.mkdir()
        outside=self.root/'outside'; outside.mkdir()
        (good/'context.txt').write_bytes(b'pinned input')
        (outside/'context.txt').write_bytes(b'different input')
        link=work/'current'
        if os.name=='nt':
            made=subprocess.run(['cmd','/c','mklink','/J',str(link),str(good)],capture_output=True)
            self.assertEqual(made.returncode,0,made.stderr)
            change=("import os,subprocess; os.rmdir('current'); "
                    "subprocess.run(['cmd','/c','mklink','/J','current',"+repr(str(outside))+"],check=True,capture_output=True); ")
        else:
            link.symlink_to(good,target_is_directory=True)
            change="from pathlib import Path; Path('current').unlink(); Path('current').symlink_to("+repr(str(outside))+"); "
        self.contract['sources']=[{'path':'current/context.txt','sha256':hashlib.sha256(b'pinned input').hexdigest()}]
        self.contract['checks'][0]['argv']=[sys.executable,'-c',change+"print('observed: valid')"]
        path=work/'contract.json'; path.write_text(json.dumps(self.contract),encoding='utf-8')
        script=Path(__file__).resolve().parents[1]/'scripts/acceptance_gate.py'
        completed=subprocess.run([sys.executable,str(script),str(path),'--root',str(work),'--execute'],
            capture_output=True,text=True)
        result=json.loads(completed.stdout)
        self.assertEqual(result['status'],'BLOCKED')
        self.assertEqual(len(result['checks']),2)
        self.assertEqual(result['checks'][0]['status'],'PASS')
        self.assertEqual(result['checks'][0]['exit_code'],0)
        self.assertIn('observed: valid',result['checks'][0]['stdout'])
        self.assertEqual(result['checks'][1]['status'],'NOT_RUN')
        self.assertTrue(result['source_errors'])

    def test_malformed_contracts_fail_before_execution(self):
        variants = []
        for key, value in [('sources', []), ('criteria', []), ('checks', [])]:
            item = copy.deepcopy(self.contract)
            item[key] = value
            variants.append(item)
        for change in ('duplicate', 'unknown', 'no_negative', 'escape', 'boolean_exit', 'nan', 'empty_oracle'):
            item = copy.deepcopy(self.contract)
            if change == 'duplicate': item['checks'][1]['id'] = 'valid'
            if change == 'unknown': item['criteria'][0]['checks'].append('missing')
            if change == 'no_negative': item['checks'][1]['kind'] = 'positive'
            if change == 'escape': item['sources'][0]['path'] = '../outside'
            if change == 'boolean_exit': item['checks'][0]['expected_exit'] = True
            if change == 'nan': item['checks'][0]['timeout_seconds'] = float('nan')
            if change == 'empty_oracle': item['checks'][0]['stdout_contains'] = ''
            variants.append(item)
        for item in variants:
            with self.subTest(item=item), self.assertRaises(ValueError):
                run_contract(item, self.root, execute=True)

    def test_cli_dry_run_is_nonzero_and_machine_readable(self):
        contract_path = self.root / 'contract.json'
        contract_path.write_text(json.dumps(self.contract), encoding='utf-8')
        script = Path(__file__).resolve().parents[1] / 'scripts/acceptance_gate.py'
        result = subprocess.run([sys.executable, str(script), str(contract_path), '--root',
                                 str(self.root)], capture_output=True, text=True)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(json.loads(result.stdout)['status'], 'NOT_RUN')
