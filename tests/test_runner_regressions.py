import json
import subprocess
import sys
import tempfile
import unittest
from argparse import Namespace
from datetime import datetime
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.run_loop import _StreamResult, _run_command, _write_stdin, run_loop, run_batch, status_from, make_prompt, MAX_CAPTURE


class RunnerRegressionTests(unittest.TestCase):
    def test_report_failure_marks_saved_state_failed(self):
        with tempfile.TemporaryDirectory() as directory:
            state, report = Path(directory) / 'state.json', Path(directory) / 'report.md'
            args = Namespace(command=['fake'], prompt='review', max_iterations=1,
                             timeout_seconds=3, state_file=str(state), report_file=str(report))
            original = Path.write_text
            def fail_report(path, data, **kwargs):
                if path == report:
                    raise OSError('injected report failure')
                return original(path, data, **kwargs)
            with mock.patch('scripts.run_loop._run_command', return_value=('done', 0, 'digest', 'LOOP_STATUS: PASS', '')):
                with mock.patch.object(Path, 'write_text', fail_report):
                    self.assertEqual(run_loop(args), 1)
            data = json.loads(state.read_text(encoding='utf-8'))
            self.assertEqual(data['final_status'], 'FAIL')
            self.assertEqual(data['invocation_status'], 'PASS')
            self.assertTrue(data['persistence_errors'])

    def test_state_failure_marks_surviving_report_failed(self):
        with tempfile.TemporaryDirectory() as directory:
            state, report = Path(directory) / 'state.json', Path(directory) / 'report.md'
            args = Namespace(command=['fake'], prompt='review', max_iterations=1,
                             timeout_seconds=3, state_file=str(state), report_file=str(report))
            original = Path.write_text
            def fail_state(path, data, **kwargs):
                if path == state:
                    raise OSError('injected state failure')
                return original(path, data, **kwargs)
            with mock.patch('scripts.run_loop._run_command', return_value=('done', 0, 'digest', 'LOOP_STATUS: PASS', '')):
                with mock.patch.object(Path, 'write_text', fail_state):
                    self.assertEqual(run_loop(args), 1)
            self.assertIn('Final status: `FAIL`', report.read_text(encoding='utf-8'))

    def test_direct_api_rejects_nonpositive_limits_before_running(self):
        with tempfile.TemporaryDirectory() as directory:
            for iterations, timeout in ((0, 1), (1, 0), (-1, 1)):
                args = Namespace(command=['fake'], prompt='review', max_iterations=iterations,
                                 timeout_seconds=timeout, state_file=str(Path(directory) / 'state.json'),
                                 report_file=str(Path(directory) / 'report.md'))
                with mock.patch('scripts.run_loop._run_command') as command:
                    with self.assertRaises(ValueError):
                        run_loop(args)
                    command.assert_not_called()

    def test_missing_prompt_file_reports_error_without_traceback(self):
        with tempfile.TemporaryDirectory() as directory:
            script = Path(__file__).resolve().parents[1] / 'scripts' / 'run_loop.py'
            result = subprocess.run([sys.executable, str(script), '--prompt-file',
                                     str(Path(directory) / 'missing.txt'), '--', 'fake'],
                                    capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 1)
            self.assertIn(b'unable to read or persist', result.stderr)
            self.assertNotIn(b'Traceback', result.stderr)

    def test_batch_preserves_blocked_status_and_actual_iteration_count(self):
        with tempfile.TemporaryDirectory() as directory:
            args = Namespace(command=['fake'], max_iterations=2, timeout_seconds=3,
                             batch_dir=directory, self_prompt=False)
            with mock.patch('scripts.run_loop._run_command', return_value=('need access', 0, 'digest', 'LOOP_STATUS: BLOCKED', '')):
                self.assertEqual(run_batch(args, ['review']), 1)
            data = json.loads((Path(directory) / 'summary.json').read_text(encoding='utf-8'))
            self.assertEqual(data['results'][0]['status'], 'BLOCKED')
            self.assertEqual(data['results'][0]['iterations'], 1)

    def test_run_records_complete_output_fingerprint(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / 'state.json'
            args = Namespace(command=['fake'], prompt='review', max_iterations=1,
                             timeout_seconds=3, state_file=str(state),
                             report_file=str(Path(directory) / 'report.md'), self_prompt=False)
            with mock.patch('scripts.run_loop._run_command', return_value=('tail', 0, 'complete-stream-digest', 'LOOP_STATUS: PASS', '')):
                self.assertEqual(run_loop(args), 0)
            self.assertEqual(json.loads(state.read_text(encoding='utf-8'))['iterations'][0]['output_fingerprint'], 'complete-stream-digest')

    def test_child_closing_stdin_is_handled_and_stream_closed(self):
        stream = mock.Mock()
        stream.write.side_effect = BrokenPipeError('child exited')
        stream.close.side_effect = BrokenPipeError('flush after exit')
        _write_stdin(stream, 'large prompt')
        stream.close.assert_called_once()

    def test_self_prompt_preserves_original_scope_and_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            args = Namespace(command=['fake'], prompt='only inspect target A', max_iterations=2,
                             timeout_seconds=3, state_file=str(Path(directory) / 'state.json'),
                             report_file=str(Path(directory) / 'report.md'), self_prompt=True)
            with mock.patch('scripts.run_loop._run_command', side_effect=[
                ('important verified evidence', 0, 'one', 'LOOP_STATUS: PASS', 'NEXT_PROMPT: inspect next detail'),
                ('done', 0, 'two', 'LOOP_STATUS: PASS', ''),
            ]) as command:
                self.assertEqual(run_loop(args), 0)
            second = command.call_args_list[1].args[1]
            self.assertIn('only inspect target A', second)
            self.assertIn('important verified evidence', second)
            self.assertIn('inspect next detail', second)

    def test_state_and_report_cannot_overwrite_each_other(self):
        with tempfile.TemporaryDirectory() as directory:
            path = str(Path(directory) / 'evidence.json')
            args = Namespace(command=['fake'], prompt='review', max_iterations=1,
                             timeout_seconds=3, state_file=path, report_file=path, self_prompt=False)
            with mock.patch('scripts.run_loop._run_command') as command:
                with self.assertRaises(ValueError):
                    run_loop(args)
                command.assert_not_called()

    def test_capture_preserves_exact_tail_for_large_chunk(self):
        stream = _StreamResult()
        stream.add(b'x' * (MAX_CAPTURE + 10))
        stream.finish()
        self.assertEqual(stream.output(), 'x' * MAX_CAPTURE)

    def test_batch_cannot_pass_when_evidence_write_fails(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = Namespace(command=['fake'], max_iterations=1, timeout_seconds=3,
                             batch_dir=str(root), self_prompt=False)
            original = Path.write_text
            def fail_report(path, data, **kwargs):
                if path.name == 'prompt-001.md':
                    raise OSError('injected report failure')
                return original(path, data, **kwargs)
            with mock.patch('scripts.run_loop._run_command', return_value=('done', 0, 'one', 'LOOP_STATUS: PASS', '')):
                with mock.patch.object(Path, 'write_text', fail_report):
                    self.assertEqual(run_batch(args, ['review']), 1)
            self.assertEqual(json.loads((root / 'summary.json').read_text(encoding='utf-8'))['final_status'], 'FAIL')

    def test_batch_state_failure_does_not_crash_or_read_stale_state(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            args = Namespace(command=['fake'], max_iterations=1, timeout_seconds=3,
                             batch_dir=str(root), self_prompt=False)
            original = Path.write_text
            def fail_state(path, data, **kwargs):
                if path.name == 'prompt-001.json':
                    raise OSError('injected state failure')
                return original(path, data, **kwargs)
            with mock.patch('scripts.run_loop._run_command', return_value=('done', 0, 'one', 'LOOP_STATUS: PASS', '')):
                with mock.patch.object(Path, 'write_text', fail_state):
                    self.assertEqual(run_batch(args, ['review']), 1)

    def test_initial_prompt_explains_status_protocol(self):
        self.assertIn('LOOP_STATUS: PASS', make_prompt('review', 1, ''))

    def test_explicit_zero_followups_runs_once(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / 'state.json'
            script = Path(__file__).resolve().parents[1] / 'scripts' / 'run_loop.py'
            result = subprocess.run([
                sys.executable, str(script), '--prompt', 'review',
                '--follow-up-count', '0', '--state-file', str(state),
                '--report-file', str(Path(directory) / 'report.md'), '--',
                sys.executable, '-c', "print('LOOP_STATUS: PASS')",
            ], capture_output=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            data = json.loads(state.read_text(encoding='utf-8'))
            self.assertEqual(data['requested_max_iterations'], 1)
            self.assertEqual(data['prompt_count'], 1)

    def test_marker_survives_large_chunk_and_duplicate_is_rejected(self):
        result = _StreamResult()
        result.add(b'LOOP_STATUS: FAIL\n' + b'x' * 8192)
        result.add(b'\nLOOP_STATUS: PASS\n')
        result.finish()
        self.assertEqual(result.status_markers, ['LOOP_STATUS: FAIL', 'LOOP_STATUS: PASS'])
        self.assertEqual(status_from('\n'.join(result.status_markers), 0), 'NOT_RUN')

    def test_long_line_suffix_cannot_become_marker(self):
        result = _StreamResult()
        result.add(b'x' * 8192)
        result.add(b'LOOP_STATUS: PASS\n')
        result.finish()
        self.assertEqual(result.status_markers, [])

    def test_split_unicode_and_fragmented_marker(self):
        result = _StreamResult()
        data = 'NEXT_PROMPT: sửa lỗi\nLOOP_STATUS: PASS'.encode()
        for byte in data:
            result.add(bytes([byte]))
        result.finish()
        self.assertEqual(result.next_markers, ['NEXT_PROMPT: sửa lỗi'])
        self.assertEqual(result.status_markers, ['LOOP_STATUS: PASS'])

    def test_timeout_after_child_closes_output(self):
        child = 'import os,time; os.close(1); os.close(2); time.sleep(3)'
        with self.assertRaises(subprocess.TimeoutExpired):
            _run_command([sys.executable, '-c', child], 'test', 1)

    def test_argument_prompt_does_not_also_go_to_stdin(self):
        child = "import sys; print(repr(sys.stdin.buffer.read())); print('LOOP_STATUS: PASS')"
        output, code, *_ = _run_command(
            [sys.executable, '-c', child, 'argument prompt'], 'argument prompt', 3,
            prompt_in_args=True,
        )
        self.assertEqual(code, 0)
        self.assertIn("b''", output)

    def test_continuation_receives_previous_output_and_records_time(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / 'state.json'
            args = Namespace(command=['fake'], prompt='review target', max_iterations=2,
                             timeout_seconds=3, state_file=str(state),
                             report_file=str(Path(directory) / 'report.md'), self_prompt=False)
            with mock.patch('scripts.run_loop._run_command', side_effect=[
                ('progress evidence', 0, 'one', 'LOOP_STATUS: NOT_RUN', ''),
                ('done', 0, 'two', 'LOOP_STATUS: PASS', ''),
            ]) as command:
                self.assertEqual(run_loop(args), 0)
            prompt = command.call_args_list[1].args[1]
            self.assertIn('progress evidence', prompt)
            self.assertIn('iteration 2', prompt)
            data = json.loads(state.read_text(encoding='utf-8'))
            self.assertLessEqual(datetime.fromisoformat(data['started_at']),
                                 datetime.fromisoformat(data['finished_at']))

    def test_normal_mode_stops_on_missing_status(self):
        with tempfile.TemporaryDirectory() as directory:
            state = Path(directory) / 'state.json'
            args = Namespace(command=['fake'], prompt='review', max_iterations=3,
                             timeout_seconds=3, state_file=str(state),
                             report_file=str(Path(directory) / 'report.md'), self_prompt=False)
            with mock.patch('scripts.run_loop._run_command', return_value=('no marker', 0, 'one', '', '')) as command:
                self.assertEqual(run_loop(args), 1)
            self.assertEqual(command.call_count, 1)
            self.assertEqual(json.loads(state.read_text(encoding='utf-8'))['final_status'], 'BLOCKED')
