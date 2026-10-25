import json
import shutil
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.validate import validate, validation_fingerprint
from scripts.run_loop import run_loop, status_from


def make_fixture() -> Path:
    temp = Path(tempfile.mkdtemp(prefix="loop-skills-validator-"))
    for root in (".github", ".agents", ".claude", "scripts"):
        shutil.copytree(REPO / root, temp / root)
    shutil.copy2(REPO / "skills-manifest.json", temp / "skills-manifest.json")
    return temp


class ValidateRepositoryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = make_fixture()

    def tearDown(self) -> None:
        shutil.rmtree(self.temp)

    def test_repository_fixture_passes(self) -> None:
        self.assertEqual(validate(self.temp), [])

    def test_duplicate_manifest_entry_fails(self) -> None:
        path = self.temp / "skills-manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["skills"].append(manifest["skills"][0])
        path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assertTrue(any("duplicate" in error for error in validate(self.temp)))

    def test_missing_copy_fails(self) -> None:
        (self.temp / ".claude" / "skills" / "loop-review" / "SKILL.md").unlink()
        self.assertTrue(any("missing" in error for error in validate(self.temp)))

    def test_mismatched_copy_fails(self) -> None:
        path = self.temp / ".agents" / "skills" / "loop-review" / "SKILL.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
        self.assertTrue(any("not identical" in error for error in validate(self.temp)))

    def test_invalid_frontmatter_and_name_fail(self) -> None:
        path = self.temp / ".github" / "skills" / "loop-review" / "SKILL.md"
        text = path.read_text(encoding="utf-8").replace("name: loop-review", "name: Invalid Name", 1)
        path.write_text(text.replace("---\n\n# Loop Review", "# Loop Review", 1), encoding="utf-8")
        errors = validate(self.temp)
        self.assertTrue(any("frontmatter" in error for error in errors))
        self.assertTrue(any("mismatched name" in error for error in errors))

    def test_unexpected_skill_directory_fails(self) -> None:
        unexpected = self.temp / ".github" / "skills" / "unexpected"
        unexpected.mkdir()
        self.assertTrue(any("directories do not match" in error for error in validate(self.temp)))

    def test_malformed_manifest_fails(self) -> None:
        (self.temp / "skills-manifest.json").write_text("{", encoding="utf-8")
        self.assertTrue(any("invalid skills-manifest" in error for error in validate(self.temp)))

    def test_skill_name_over_64_characters_fails(self) -> None:
        path = self.temp / "skills-manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["skills"][0] = "a" * 65
        path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assertTrue(any("invalid skill name" in error for error in validate(self.temp)))

    def test_headless_runner_stops_on_pass_marker(self) -> None:
        from argparse import Namespace

        state = self.temp / "state.json"
        report = self.temp / "report.md"
        result = run_loop(
            Namespace(
                command=[sys.executable, "-c", "print('LOOP_STATUS: PASS')"],
                prompt="continue",
                max_iterations=3,
                timeout_seconds=10,
                state_file=str(state),
                report_file=str(report),
            )
        )
        self.assertEqual(result, 0)
        self.assertIn('"final_status": "PASS"', state.read_text(encoding="utf-8"))
        self.assertTrue(report.is_file())

    def test_headless_runner_starts_follow_up_iteration(self) -> None:
        from argparse import Namespace

        agent = self.temp / "fake_agent.py"
        counter = self.temp / "counter.txt"
        agent.write_text(
            "from pathlib import Path\n"
            "import sys\n"
            f"counter = Path({str(counter)!r})\n"
            "count = int(counter.read_text()) if counter.exists() else 0\n"
            "counter.write_text(str(count + 1))\n"
            "print('LOOP_STATUS: PASS' if count else 'LOOP_STATUS: NOT_RUN')\n",
            encoding="utf-8",
        )
        state = self.temp / "follow-up-state.json"
        result = run_loop(
            Namespace(
                command=[sys.executable, str(agent)],
                prompt="continue",
                max_iterations=3,
                timeout_seconds=10,
                state_file=str(state),
                report_file=str(self.temp / "follow-up-report.md"),
            )
        )
        self.assertEqual(result, 0)
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(len(data["iterations"]), 2)
        self.assertEqual(data["final_status"], "PASS")

    def test_skill_creation_workflow_contract_is_enforced(self) -> None:
        path = self.temp / ".github" / "skills" / "loop-skill-create" / "SKILL.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace("sleep to consume duration", "pause", 1),
            encoding="utf-8",
        )
        errors = validate(self.temp)
        self.assertTrue(any("not identical" in error for error in errors))

    def test_batch_runner_processes_multiple_prompts(self) -> None:
        from argparse import Namespace

        agent = self.temp / "batch_agent.py"
        agent.write_text("print('LOOP_STATUS: PASS')\n", encoding="utf-8")
        batch_dir = self.temp / "batch"
        args = Namespace(
            command=[sys.executable, str(agent)],
            max_iterations=2,
            timeout_seconds=10,
            batch_dir=str(batch_dir),
        )
        from scripts.run_loop import run_batch

        self.assertEqual(run_batch(args, ["first prompt", "second prompt"]), 0)
        summary = json.loads((batch_dir / "summary.json").read_text(encoding="utf-8"))
        self.assertEqual(summary["prompt_count"], 2)
        self.assertEqual(summary["final_status"], "PASS")

    def test_self_prompt_runs_requested_follow_ups(self) -> None:
        from argparse import Namespace

        agent = self.temp / "self_prompt_agent.py"
        counter = self.temp / "self_prompt_counter.txt"
        agent.write_text(
            "from pathlib import Path\n"
            f"counter = Path({str(counter)!r})\n"
            "count = int(counter.read_text()) if counter.exists() else 0\n"
            "counter.write_text(str(count + 1))\n"
            "print(f'NEXT_PROMPT: develop step {count + 1}')\n"
            "print('LOOP_STATUS: PASS')\n",
            encoding="utf-8",
        )
        state = self.temp / "self-prompt-state.json"
        result = run_loop(
            Namespace(
                command=[sys.executable, str(agent)],
                prompt="develop the initial idea",
                max_iterations=4,
                timeout_seconds=10,
                state_file=str(state),
                report_file=str(self.temp / "self-prompt-report.md"),
                self_prompt=True,
            )
        )
        self.assertEqual(result, 0)
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(len(data["iterations"]), 4)

    def test_self_prompt_accepts_unicode_input(self) -> None:
        from argparse import Namespace

        result = run_loop(
            Namespace(
                command=[sys.executable, "-c", "import sys; sys.stdin.read(); print('LOOP_STATUS: PASS')"],
                prompt="Sửa lỗi tiếng Việt",
                max_iterations=1,
                timeout_seconds=10,
                state_file=str(self.temp / "unicode-state.json"),
                report_file=str(self.temp / "unicode-report.md"),
                self_prompt=False,
            )
        )
        self.assertEqual(result, 0)

    def test_self_prompt_stops_after_initial_pass_without_follow_up(self) -> None:
        from argparse import Namespace

        state = self.temp / "terminal-state.json"
        result = run_loop(
            Namespace(
                command=[sys.executable, "-c", "print('LOOP_STATUS: PASS')"],
                prompt="finish this task",
                max_iterations=4,
                timeout_seconds=10,
                state_file=str(state),
                report_file=str(self.temp / "terminal-report.md"),
                self_prompt=True,
            )
        )
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(result, 1)
        self.assertEqual(len(data["iterations"]), 1)
        self.assertEqual(data["final_status"], "BLOCKED")
        self.assertIn("NEXT_PROMPT", data["stop_reason"])

    def test_self_prompt_rejects_duplicate_next_prompt(self) -> None:
        from argparse import Namespace

        agent = self.temp / "duplicate_prompt_agent.py"
        agent.write_text(
            "print('NEXT_PROMPT: repeat')\n"
            "print('LOOP_STATUS: PASS')\n",
            encoding="utf-8",
        )
        state = self.temp / "duplicate-prompt-state.json"
        result = run_loop(
            Namespace(
                command=[sys.executable, str(agent)],
                prompt="repeat",
                max_iterations=3,
                timeout_seconds=10,
                state_file=str(state),
                report_file=str(self.temp / "duplicate-prompt-report.md"),
                self_prompt=True,
            )
        )
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(result, 1)
        self.assertEqual(len(data["iterations"]), 1)
        self.assertEqual(data["final_status"], "BLOCKED")
        self.assertIn("repeated follow-up", data["stop_reason"])

    def test_self_prompt_stops_on_repeated_result(self) -> None:
        from argparse import Namespace

        agent = self.temp / "repeated_result_agent.py"
        agent.write_text(
            "print('NEXT_PROMPT: continue once')\n"
            "print('LOOP_STATUS: PASS')\n",
            encoding="utf-8",
        )
        state = self.temp / "repeated-result-state.json"
        result = run_loop(
            Namespace(
                command=[sys.executable, str(agent)],
                prompt="start",
                max_iterations=3,
                timeout_seconds=10,
                state_file=str(state),
                report_file=str(self.temp / "repeated-result-report.md"),
                self_prompt=True,
            )
        )
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(result, 1)
        self.assertEqual(len(data["iterations"]), 2)
        self.assertEqual(data["final_status"], "BLOCKED")
        self.assertEqual(data["stop_reason"], "repeated agent output")

    def test_self_prompt_stops_on_repeated_large_result(self) -> None:
        from argparse import Namespace

        agent = self.temp / "repeated-large-agent.py"
        agent.write_text(
            "print('NEXT_PROMPT: continue')\n"
            "print('z' * 120000)\n"
            "print('LOOP_STATUS: PASS')\n",
            encoding="utf-8",
        )
        state = self.temp / "repeated-large-state.json"
        result = run_loop(
            Namespace(
                command=[sys.executable, str(agent)],
                prompt="start",
                max_iterations=3,
                timeout_seconds=10,
                state_file=str(state),
                report_file=str(self.temp / "repeated-large-report.md"),
                self_prompt=True,
            )
        )
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(result, 1)
        self.assertEqual(data["prompt_count"], 2)
        self.assertEqual(data["stop_reason"], "repeated agent output")

    def test_self_prompt_rejects_duplicate_markers(self) -> None:
        from argparse import Namespace

        state = self.temp / "duplicate-marker-state.json"
        result = run_loop(
            Namespace(
                command=[
                    sys.executable,
                    "-c",
                    "print('NEXT_PROMPT: one'); print('NEXT_PROMPT: two'); print('LOOP_STATUS: PASS')",
                ],
                prompt="start",
                max_iterations=3,
                timeout_seconds=10,
                state_file=str(state),
                report_file=str(self.temp / "duplicate-marker-report.md"),
                self_prompt=True,
            )
        )
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(result, 1)
        self.assertEqual(len(data["iterations"]), 1)
        self.assertEqual(data["final_status"], "BLOCKED")

    def test_self_prompt_rejects_empty_next_prompt(self) -> None:
        from argparse import Namespace

        state = self.temp / "empty-next-state.json"
        result = run_loop(
            Namespace(
                command=[
                    sys.executable,
                    "-c",
                    "print('NEXT_PROMPT:   '); print('LOOP_STATUS: PASS')",
                ],
                prompt="start",
                max_iterations=2,
                timeout_seconds=10,
                state_file=str(state),
                report_file=str(self.temp / "empty-next-report.md"),
                self_prompt=True,
            )
        )
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(result, 1)
        self.assertEqual(data["prompt_count"], 1)
        self.assertEqual(data["final_status"], "BLOCKED")

    def test_runner_records_timeout_and_startup_failure(self) -> None:
        from argparse import Namespace

        for name, command, expected in (
            ("timeout", [sys.executable, "-c", "import time; time.sleep(2)"], "timed out"),
            ("startup", [str(self.temp / "does-not-exist.exe")], "could not start"),
        ):
            state = self.temp / f"{name}-state.json"
            result = run_loop(
                Namespace(
                    command=command,
                    prompt="bounded check",
                    max_iterations=2,
                    timeout_seconds=1,
                    state_file=str(state),
                    report_file=str(self.temp / f"{name}-report.md"),
                )
            )
            data = json.loads(state.read_text(encoding="utf-8"))
            self.assertEqual(result, 1)
            self.assertEqual(data["prompt_count"], 1)
            self.assertEqual(data["final_status"], "BLOCKED")
            self.assertIn(expected, data["stop_reason"])

    def test_runner_reports_state_write_failure_after_pass(self) -> None:
        from argparse import Namespace

        state = self.temp / "state-failure.json"
        report = self.temp / "report-after-state-failure.md"
        original = Path.write_text

        def fail_state(path, data, **kwargs):
            if path == state:
                raise OSError("injected state failure")
            return original(path, data, **kwargs)

        with mock.patch.object(Path, "write_text", fail_state):
            result = run_loop(
                Namespace(
                    command=[sys.executable, "-c", "print('LOOP_STATUS: PASS')"],
                    prompt="persist evidence",
                    max_iterations=1,
                    timeout_seconds=10,
                    state_file=str(state),
                    report_file=str(report),
                )
            )
        self.assertEqual(result, 1)
        self.assertFalse(state.exists())
        self.assertTrue(report.exists())

    def test_runner_reports_report_write_failure_after_pass(self) -> None:
        from argparse import Namespace

        state = self.temp / "state-before-report-failure.json"
        report = self.temp / "report-failure.md"
        original = Path.write_text

        def fail_report(path, data, **kwargs):
            if path == report:
                raise OSError("injected report failure")
            return original(path, data, **kwargs)

        with mock.patch.object(Path, "write_text", fail_report):
            result = run_loop(
                Namespace(
                    command=[sys.executable, "-c", "print('LOOP_STATUS: PASS')"],
                    prompt="persist report",
                    max_iterations=1,
                    timeout_seconds=10,
                    state_file=str(state),
                    report_file=str(report),
                )
            )
        self.assertEqual(result, 1)
        self.assertTrue(state.exists())
        self.assertFalse(report.exists())

    def test_runner_reports_evidence_directory_failure(self) -> None:
        from argparse import Namespace

        state = self.temp / "missing" / "state.json"
        report = self.temp / "missing" / "report.md"
        with mock.patch.object(Path, "mkdir", side_effect=OSError("injected mkdir failure")):
            result = run_loop(
                Namespace(
                    command=[sys.executable, "-c", "print('LOOP_STATUS: PASS')"],
                    prompt="persist directory",
                    max_iterations=1,
                    timeout_seconds=10,
                    state_file=str(state),
                    report_file=str(report),
                )
            )
        self.assertEqual(result, 1)

    def test_validation_fingerprint_excludes_generated_report(self) -> None:
        first = validation_fingerprint(self.temp)
        report = self.temp / "docs" / "VALIDATION-RESULT.md"
        report.parent.mkdir()
        report.write_text("first", encoding="utf-8")
        second = validation_fingerprint(self.temp)
        self.assertEqual(first, second)
        source = self.temp / "scripts" / "validate.py"
        source.write_text(source.read_text(encoding="utf-8") + "\nchanged\n", encoding="utf-8")
        self.assertNotEqual(second, validation_fingerprint(self.temp))

    def test_fingerprint_ignores_only_repo_relative_exclusions(self) -> None:
        for ancestor in ('.loop', '.git', '__pycache__'):
            with self.subTest(ancestor=ancestor):
                nested = self.temp / ancestor / 'isolated-repo'
                nested.mkdir(parents=True)
                source = nested / 'source.txt'
                source.write_text('before', encoding='utf-8')
                before = validation_fingerprint(nested)
                source.write_text('after', encoding='utf-8')
                self.assertNotEqual(before, validation_fingerprint(nested))
                # Excluded directories inside that repository must still be ignored.
                after = validation_fingerprint(nested)
                ignored = nested / '.loop'
                ignored.mkdir()
                (ignored / 'private.log').write_text('ignored', encoding='utf-8')
                self.assertEqual(after, validation_fingerprint(nested))

    def test_fingerprint_frames_names_and_contents_unambiguously(self) -> None:
        left, right = self.temp/'tree-left', self.temp/'tree-right'
        left.mkdir(); right.mkdir()
        (left/'a').write_bytes(b'bc')
        (right/'ab').write_bytes(b'c')
        self.assertNotEqual(validation_fingerprint(left), validation_fingerprint(right))

    def test_runner_records_nonzero_exit_and_report_metadata(self) -> None:
        from argparse import Namespace

        state = self.temp / "failure-state.json"
        report = self.temp / "failure-report.md"
        result = run_loop(
            Namespace(
                command=[sys.executable, "-c", "raise SystemExit(3)"],
                prompt="fail safely",
                max_iterations=2,
                timeout_seconds=10,
                state_file=str(state),
                report_file=str(report),
            )
        )
        data = json.loads(state.read_text(encoding="utf-8"))
        report_text = report.read_text(encoding="utf-8")
        self.assertEqual(result, 1)
        self.assertEqual(data["final_status"], "FAIL")
        self.assertIn("agent invocation failed", data["stop_reason"])
        self.assertIn("Stop reason:", report_text)

    def test_runner_stops_after_nonzero_exit(self) -> None:
        from argparse import Namespace

        counter = self.temp / "nonzero-counter.txt"
        agent = self.temp / "nonzero_agent.py"
        agent.write_text(
            "from pathlib import Path\n"
            f"counter = Path({str(counter)!r})\n"
            "count = int(counter.read_text()) if counter.exists() else 0\n"
            "counter.write_text(str(count + 1))\n"
            "raise SystemExit(4)\n",
            encoding="utf-8",
        )
        state = self.temp / "nonzero-stop-state.json"
        result = run_loop(
            Namespace(
                command=[sys.executable, str(agent)],
                prompt="fail once",
                max_iterations=3,
                timeout_seconds=10,
                state_file=str(state),
                report_file=str(self.temp / "nonzero-stop-report.md"),
            )
        )
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(result, 1)
        self.assertEqual(data["prompt_count"], 1)
        self.assertEqual(counter.read_text(encoding="utf-8"), "1")

    def test_runner_bounds_captured_output(self) -> None:
        from argparse import Namespace

        state = self.temp / "bounded-output-state.json"
        result = run_loop(
            Namespace(
                command=[sys.executable, "-c", "print('x' * 150000); print('LOOP_STATUS: PASS')"],
                prompt="bound output",
                max_iterations=1,
                timeout_seconds=10,
                state_file=str(state),
                report_file=str(self.temp / "bounded-output-report.md"),
            )
        )
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(result, 0)
        self.assertLessEqual(len(data["iterations"][0]["output"]), 100000)

    def test_runner_streams_both_outputs_and_replaces_invalid_bytes(self) -> None:
        from argparse import Namespace

        agent = self.temp / "dual-stream-agent.py"
        agent.write_text(
            "import sys\n"
            "sys.stdout.buffer.write(b'x' * 120000 + b'\\xff\\nLOOP_STATUS: PASS\\n')\n"
            "sys.stderr.buffer.write(b'NEXT_PROMPT: ignored\\n')\n",
            encoding="utf-8",
        )
        state = self.temp / "dual-stream-state.json"
        result = run_loop(
            Namespace(
                command=[sys.executable, str(agent)],
                prompt="stream safely",
                max_iterations=1,
                timeout_seconds=10,
                state_file=str(state),
                report_file=str(self.temp / "dual-stream-report.md"),
            )
        )
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(result, 0)
        self.assertEqual(data["final_status"], "PASS")
        self.assertLessEqual(len(data["iterations"][0]["output"]), 100000)
        self.assertIn("ignored", data["iterations"][0]["output"])

    def test_self_prompt_parses_markers_before_output_truncation(self) -> None:
        from argparse import Namespace

        agent = self.temp / "large_output_agent.py"
        agent.write_text(
            "from pathlib import Path\n"
            f"counter = Path({str(self.temp / 'large-counter.txt')!r})\n"
            "count = int(counter.read_text()) if counter.exists() else 0\n"
            "counter.write_text(str(count + 1))\n"
            "print(f'NEXT_PROMPT: next step {count + 1}')\n"
            "print('x' * 150000)\n"
            "print('LOOP_STATUS: PASS')\n",
            encoding="utf-8",
        )
        state = self.temp / "large-output-state.json"
        result = run_loop(
            Namespace(
                command=[sys.executable, str(agent)],
                prompt="start",
                max_iterations=2,
                timeout_seconds=10,
                state_file=str(state),
                report_file=str(self.temp / "large-output-report.md"),
                self_prompt=True,
            )
        )
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(result, 0)
        self.assertEqual(len(data["iterations"]), 2)

    def test_self_prompt_stops_on_malformed_status_with_next_prompt(self) -> None:
        from argparse import Namespace

        state = self.temp / "malformed-status-state.json"
        result = run_loop(
            Namespace(
                command=[
                    sys.executable,
                    "-c",
                    "print('NEXT_PROMPT: unsafe follow-up'); print('LOOP_STATUS: PASS extra')",
                ],
                prompt="start",
                max_iterations=2,
                timeout_seconds=10,
                state_file=str(state),
                report_file=str(self.temp / "malformed-status-report.md"),
                self_prompt=True,
            )
        )
        data = json.loads(state.read_text(encoding="utf-8"))
        self.assertEqual(result, 1)
        self.assertEqual(len(data["iterations"]), 1)
        self.assertEqual(data["final_status"], "BLOCKED")
        self.assertIn("LOOP_STATUS", data["stop_reason"])

    def test_runner_rejects_multiple_status_markers(self) -> None:
        self.assertEqual(
            status_from("LOOP_STATUS: PASS\nLOOP_STATUS: FAIL\n", 0),
            "NOT_RUN",
        )


if __name__ == "__main__":
    unittest.main()
