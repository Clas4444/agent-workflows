import json
import os
from pathlib import Path
import shutil
import tempfile
import subprocess
import unittest
from unittest import mock

from scripts.skill_resources import check_resources, load_resources
from scripts.sync_skills import sync
from scripts.validate import validate

ROOT=Path(__file__).resolve().parents[1]


class SkillResourceTests(unittest.TestCase):
    def fixture(self, root):
        repo=root/'repo';repo.mkdir()
        manifest={'version':'1.0.0','skills':['loop-review'],
                  'project_skill_roots':['.github/skills','.agents/skills','.claude/skills'],
                  'resource_manifest':'skill-resources.json'}
        (repo/'skills-manifest.json').write_text(json.dumps(manifest),encoding='utf-8')
        (repo/'skill-resources.json').write_text(json.dumps({'version':1,'resources':{
            'loop-review':['references/guide.md']}}),encoding='utf-8')
        for native in manifest['project_skill_roots']:
            folder=repo/native/'loop-review';(folder/'references').mkdir(parents=True)
            shutil.copy2(ROOT/'.github/skills/loop-review/SKILL.md',folder/'SKILL.md')
            (folder/'references/guide.md').write_text('Required supporting reference\n',encoding='utf-8')
        return repo

    def test_full_validator_rejects_mismatched_resource_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            repo=self.fixture(Path(directory))
            self.assertEqual(validate(repo),[])
            (repo/'.agents/skills/loop-review/references/guide.md').write_text('stale reference',encoding='utf-8')
            self.assertTrue(validate(repo))

    def test_install_copies_declared_resource_and_preserves_external_extras(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);repo=self.fixture(root);target=root/'installed'
            extra=target/'loop-review/notes.txt';extra.parent.mkdir(parents=True);extra.write_text('custom',encoding='utf-8')
            with mock.patch('scripts.sync_skills.REPO',repo):
                sync(target,root/'backup')
                self.assertTrue((target/'loop-review/references/guide.md').is_file())
                self.assertEqual(sync(target,root/'backup',check=True),[])
            self.assertEqual(extra.read_text(encoding='utf-8'),'custom')

    def test_missing_declared_registry_and_unregistered_source_files_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            repo=self.fixture(Path(directory))
            (repo/'skill-resources.json').unlink()
            self.assertTrue(check_resources(repo))
            with self.assertRaises(ValueError):load_resources(repo,['loop-review'])

    def test_unsafe_and_case_alias_paths_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo=self.fixture(Path(directory))
            for paths in (['../escape'],['/absolute'],['C:/escape'],['references\\file'],
                          ['assets/NUL.txt'],['assets/end./file'],['assets/Foo','assets/foo']):
                (repo/'skill-resources.json').write_text(json.dumps({'version':1,'resources':{'loop-review':paths}}),encoding='utf-8')
                with self.subTest(paths=paths),self.assertRaises(ValueError):load_resources(repo,['loop-review'])

    def test_implicit_instruction_and_parent_directory_case_aliases_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            repo=self.fixture(Path(directory))
            for paths in (['skill.md'],['references/a.md','References/b.md']):
                (repo/'skill-resources.json').write_text(json.dumps({'version':1,'resources':{'loop-review':paths}}),encoding='utf-8')
                with self.subTest(paths=paths),self.assertRaises(ValueError):load_resources(repo,['loop-review'])

    def test_hardlinked_source_resource_is_rejected_before_destination_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);repo=self.fixture(root)
            resource=repo/'.github/skills/loop-review/references/guide.md'
            resource.unlink();outside=root/'outside';outside.write_bytes(b'private fixture')
            os.link(outside,resource)
            with mock.patch('scripts.sync_skills.REPO',repo),self.assertRaises(ValueError):
                sync(root/'installed',root/'backup')
            self.assertFalse((root/'installed').exists())

    def test_repository_copies_are_strict_but_installer_does_not_delete_extras(self):
        with tempfile.TemporaryDirectory() as directory:
            repo=self.fixture(Path(directory))
            (repo/'.claude/skills/loop-review/extra.md').write_text('unexpected',encoding='utf-8')
            self.assertTrue(check_resources(repo))

    def test_source_directory_alias_is_rejected_before_any_payload_copy(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);repo=self.fixture(root);source=repo/'.github/skills'
            moved=root/'real-source';source.rename(moved)
            if os.name=='nt':
                subprocess.run(['cmd','/c','mklink','/J',str(source),str(moved)],
                               check=True,capture_output=True,timeout=20)
            else:
                source.symlink_to(moved,target_is_directory=True)
            with mock.patch('scripts.sync_skills.REPO',repo),self.assertRaises(ValueError):
                sync(root/'installed',root/'backup')
            self.assertFalse((root/'installed').exists())
            self.assertTrue(validate(repo))
