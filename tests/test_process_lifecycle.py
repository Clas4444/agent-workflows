"""Real subprocess regressions for runner timeout containment."""
import subprocess
import os
import sys
import tempfile
import time
import threading
import queue
import unittest
from pathlib import Path
from unittest import mock

from scripts.run_loop import _run_command, _StreamResult, _read_stream


class ProcessLifecycleTests(unittest.TestCase):
    @unittest.skipUnless(os.name=='nt','Windows DWORD exit-code propagation')
    def test_windows_full_width_exit_code_matches_direct_process(self):
        for requested in (-1,-1073741819,256,65535):
            with self.subTest(requested=requested):
                command=[sys.executable,'-I','-c',f'import os; os._exit({requested})']
                direct=subprocess.run(command,capture_output=True,timeout=5).returncode
                _,observed,*_=_run_command(command,'',5)
                self.assertEqual(observed,direct)

    def test_successful_invocation_closes_owned_background_descendant(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ready, marker = root/'ready', root/'late'
            child = root/'child.py'
            child.write_text('from pathlib import Path\nimport time\n'
                f'Path({str(ready)!r}).touch()\ntime.sleep(4)\n'
                f'Path({str(marker)!r}).touch()\n',encoding='utf-8')
            parent = ('import subprocess,sys,time\nfrom pathlib import Path\n'
                      f'subprocess.Popen([sys.executable,{str(child)!r}],stdin=subprocess.DEVNULL,'
                      'stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n'
                      f'while not Path({str(ready)!r}).exists(): time.sleep(.01)\n'
                      'print("LOOP_STATUS: PASS")\n')
            started = time.monotonic()
            output,code,*_ = _run_command([sys.executable,'-c',parent],'',3)
            self.assertEqual(code,0)
            self.assertIn('LOOP_STATUS: PASS',output)
            self.assertTrue(ready.exists())
            while time.monotonic()-started < 6 and not marker.exists():time.sleep(.05)
            self.assertFalse(marker.exists())

    def test_invalid_executable_preserves_launch_error(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = Path(directory)/'invalid.exe'
            executable.write_bytes(b'not an executable\n')
            executable.chmod(0o700)
            with self.assertRaises(OSError):
                _run_command([str(executable)],'',5)

    def test_timeout_does_not_leave_readers_blocked_on_full_queue(self):
        queue_type = queue.Queue
        queues = []
        def capture_queue(*args,**kwargs):
            result = queue_type(*args,**kwargs)
            queues.append(result)
            return result
        original_add = _StreamResult.add
        def slow_consumer(result,chunk):
            time.sleep(.03)
            original_add(result,chunk)
        initial = set(threading.enumerate())
        child = 'import os\nwhile True: os.write(1,b"x"*8192)\n'
        try:
            with mock.patch('scripts.run_loop.queue.Queue',side_effect=capture_queue):
                with mock.patch.object(_StreamResult,'add',slow_consumer):
                    with self.assertRaises(subprocess.TimeoutExpired):
                        _run_command([sys.executable,'-I','-c',child],'',1)
            leaked = [t for t in threading.enumerate() if t not in initial
                      and getattr(t,'_target',None) == _read_stream]
            self.assertEqual(leaked,[], 'timeout left readers blocked on a full queue')
        finally:
            # Drain after observation, so even the failing baseline leaves no daemon.
            until = time.monotonic()+2
            while time.monotonic()<until:
                active = [t for t in threading.enumerate() if t not in initial
                          and getattr(t,'_target',None) == _read_stream]
                if not active:
                    break
                for events in queues:
                    while True:
                        try: events.get_nowait()
                        except queue.Empty: break
                for thread in active:thread.join(timeout=.02)

    def test_stdin_bytes_survive_windows_launcher_gate(self):
        prompt = 'đúng dữ liệu\n' * 20000
        child = ('import sys,hashlib; data=sys.stdin.buffer.read(); '
                 'print(hashlib.sha256(data).hexdigest()); print("LOOP_STATUS: PASS")')
        import hashlib
        output,code,*_ = _run_command([sys.executable,'-I','-c',child],prompt,10)
        self.assertEqual(code,0)
        self.assertIn(hashlib.sha256(prompt.encode()).hexdigest(),output)

    def test_nonzero_exit_is_preserved(self):
        for expected in (7,125,255):
            with self.subTest(exit_code=expected):
                _,code,*_ = _run_command([sys.executable,'-I','-c',f'raise SystemExit({expected})'],'',5)
                self.assertEqual(code,expected)

    @unittest.skipUnless(os.name == 'nt','Windows job assignment boundary')
    def test_assignment_failure_does_not_launch_target(self):
        with tempfile.TemporaryDirectory() as directory:
            marker = Path(directory)/'must-not-exist'
            command = [sys.executable,'-c',f'from pathlib import Path; Path({str(marker)!r}).touch()']
            with mock.patch('scripts.run_loop._windows_job',side_effect=OSError('assignment refused')):
                with self.assertRaisesRegex(OSError,'assignment refused'):
                    _run_command(command,'',5)
            self.assertFalse(marker.exists())

    def test_timeout_after_parent_exit_stops_pipe_inheriting_descendant(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ready, marker = root/'ready', root/'late'
            child = root/'child.py'
            child.write_text('from pathlib import Path\nimport time\n'
                f'Path({str(ready)!r}).touch()\ntime.sleep(5)\n'
                f'Path({str(marker)!r}).touch()\n',encoding='utf-8')
            parent = ('import subprocess,sys; '
                      f'subprocess.Popen([sys.executable,{str(child)!r}],stdin=subprocess.DEVNULL)')
            started = time.monotonic()
            with self.assertRaises(subprocess.TimeoutExpired):
                _run_command([sys.executable,'-c',parent],'',2)
            self.assertTrue(ready.exists())
            while time.monotonic()-started < 7 and not marker.exists():
                time.sleep(.05)
            self.assertFalse(marker.exists())

    def test_timeout_stops_descendant_before_post_timeout_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            ready, marker = root/'ready.txt', root/'late.txt'
            child, parent = root/'child.py', root/'parent.py'
            child.write_text(
                'from pathlib import Path\nimport time\n'
                f'Path({str(ready)!r}).write_text("ready")\n'
                'time.sleep(5)\n'
                f'Path({str(marker)!r}).write_text("late")\n', encoding='utf-8')
            parent.write_text(
                'import subprocess,sys,time\n'
                f'subprocess.Popen([sys.executable,{str(child)!r}],'
                'stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)\n'
                'time.sleep(30)\n', encoding='utf-8')
            started = time.monotonic()
            with self.assertRaises(subprocess.TimeoutExpired):
                _run_command([sys.executable,str(parent)],'',2)
            self.assertTrue(ready.exists(), 'fixture descendant must actually start')
            # Observe the fixture's known delayed action, not an arbitrary long sleep.
            while time.monotonic()-started < 7 and not marker.exists():
                time.sleep(.05)
            self.assertFalse(marker.exists(), 'descendant wrote after runner timeout')


if __name__ == '__main__':
    unittest.main()
