import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from scripts.validate import validate


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

    def test_skill_creation_workflow_contract_is_enforced(self) -> None:
        path = self.temp / ".github" / "skills" / "loop-skill-create" / "SKILL.md"
        path.write_text(
            path.read_text(encoding="utf-8").replace("sleep to consume duration", "pause", 1),
            encoding="utf-8",
        )
        errors = validate(self.temp)
        self.assertTrue(any("not identical" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
