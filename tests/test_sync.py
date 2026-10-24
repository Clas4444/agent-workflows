import tempfile
import unittest
from pathlib import Path
import sys
import json
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from scripts.sync_skills import sync, REPO


class SyncTests(unittest.TestCase):
    def test_backup_conflict_is_detected_before_any_target_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target, backup = root / 'skills', root / 'backup'
            for name in ('loop-review', 'loop-code'):
                path = target / name / 'SKILL.md'
                path.parent.mkdir(parents=True)
                path.write_text('old', encoding='utf-8')
            collision = backup / 'loop-code' / 'SKILL.md'
            collision.parent.mkdir(parents=True)
            collision.write_text('previous backup', encoding='utf-8')
            with self.assertRaises(ValueError):
                sync(target, backup)
            self.assertEqual((target / 'loop-review' / 'SKILL.md').read_text(encoding='utf-8'), 'old')

    def test_missing_source_is_detected_before_creating_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / 'repo'
            source = repo / '.github' / 'skills' / 'loop-review' / 'SKILL.md'
            source.parent.mkdir(parents=True)
            source.write_text('valid first source', encoding='utf-8')
            (repo / 'skills-manifest.json').write_text(json.dumps({'skills': ['loop-review', 'loop-missing']}), encoding='utf-8')
            target = root / 'target'
            with mock.patch('scripts.sync_skills.REPO', repo):
                with self.assertRaises((ValueError, OSError)):
                    sync(target, root / 'backup')
            self.assertFalse(target.exists())

    def test_manifest_rejects_path_traversal_before_creating_target(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            repo = root / 'repo'
            repo.mkdir()
            (repo / 'skills-manifest.json').write_text(json.dumps({'skills': ['../outside']}), encoding='utf-8')
            with mock.patch('scripts.sync_skills.REPO', repo):
                with self.assertRaises(ValueError):
                    sync(root / 'target', root / 'backup', check=True)

    def test_check_backup_sync_and_idempotence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target, backup = root / 'skills', root / 'backup'
            old = target / 'loop-code' / 'SKILL.md'
            old.parent.mkdir(parents=True)
            old.write_text('old custom instructions', encoding='utf-8')
            unrelated = target / 'unrelated' / 'SKILL.md'
            unrelated.parent.mkdir()
            unrelated.write_text('keep', encoding='utf-8')
            self.assertTrue(sync(target, backup, check=True))
            self.assertEqual(old.read_text(encoding='utf-8'), 'old custom instructions')
            sync(target, backup)
            self.assertEqual((backup / 'loop-code' / 'SKILL.md').read_text(encoding='utf-8'), 'old custom instructions')
            self.assertEqual(unrelated.read_text(encoding='utf-8'), 'keep')
            self.assertEqual(sync(target, backup, check=True), [])
            self.assertEqual(sync(target, backup), [])
            self.assertEqual((target / 'loop-prompt' / 'scripts' / 'run_loop.py').read_bytes(),
                             (REPO / 'scripts' / 'run_loop.py').read_bytes())

    def test_rejects_backup_inside_target(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory)
            with self.assertRaises(ValueError):
                sync(target, target / 'backup')
