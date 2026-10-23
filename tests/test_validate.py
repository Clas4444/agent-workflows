import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.validate import validate
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

    def test_runner_rejects_multiple_status_markers(self) -> None:
        self.assertEqual(
            status_from("LOOP_STATUS: PASS\nLOOP_STATUS: FAIL\n", 0),
            "NOT_RUN",
        )


if __name__ == "__main__":
    unittest.main()
