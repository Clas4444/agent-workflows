import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.skill_bundles import load_bundles, select_skills
from scripts.sync_skills import sync

ROOT = Path(__file__).resolve().parents[1]


class NeedBasedInstallTests(unittest.TestCase):
    def cli(self, *args):
        return subprocess.run([sys.executable, str(ROOT/'scripts/install_skills.py'), *map(str,args)],
                              capture_output=True, text=True, timeout=30)

    def test_writing_bundle_is_small_and_union_is_manifest_ordered(self):
        self.assertEqual(set(load_bundles(ROOT)['writing']['skills']), {'loop-write','loop-summarize'})
        chosen = select_skills(ROOT, ['writing','office','writing'], ['loop-write'])
        self.assertEqual(set(chosen), {'loop-write','loop-summarize','loop-meeting','loop-organize'})
        manifest = json.loads((ROOT/'skills-manifest.json').read_text(encoding='utf-8'))['skills']
        self.assertEqual(chosen, [name for name in manifest if name in chosen])

    def test_invalid_or_empty_selection_never_creates_destination(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for flags in ([], ['--bundle','typo'], ['--skill','../escape']):
                target, backup = root/'skills', root/'backup'
                result = self.cli('--target',target,'--backup',backup,*flags)
                self.assertNotEqual(result.returncode, 0)
                self.assertFalse(target.exists())
                self.assertFalse(backup.exists())
            for selection in ([], ['loop-write','loop-write'], ['not-a-skill'], 'loop-write'):
                with self.subTest(selection=selection), self.assertRaises(ValueError):
                    sync(root/'skills',root/'backup',selected=selection)
                self.assertFalse((root/'skills').exists())

    def test_read_only_check_then_real_install_does_not_install_unselected_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); target=root/'space Ω'/'skills'; backup=root/'backup'
            result = self.cli('--bundle','writing','--target',target,'--backup',backup,'--check')
            self.assertEqual(result.returncode, 1, result.stderr)
            self.assertFalse(target.exists())
            self.assertFalse(backup.exists())
            self.assertEqual(set(json.loads(result.stdout)['selected_skills']), {'loop-write','loop-summarize'})
            result = self.cli('--bundle','writing','--target',target,'--backup',backup)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual({p.name for p in target.iterdir()}, {'loop-write','loop-summarize'})
            for name in ('loop-write','loop-summarize'):
                self.assertEqual((target/name/'SKILL.md').read_bytes(),
                                 (ROOT/'.github/skills'/name/'SKILL.md').read_bytes())
            self.assertEqual(self.cli('--bundle','writing','--target',target,'--check').returncode, 0)

    def test_selected_overwrite_is_backed_up_and_unselected_files_are_preserved(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);target=root/'skills';backup=root/'backup'
            for name, data in [('loop-write',b'custom draft skill'),('loop-code',b'keep customized code')]:
                path=target/name/'SKILL.md';path.parent.mkdir(parents=True);path.write_bytes(data)
            sync(target,backup,selected=['loop-write'])
            self.assertEqual((backup/'loop-write/SKILL.md').read_bytes(), b'custom draft skill')
            self.assertEqual((target/'loop-code/SKILL.md').read_bytes(), b'keep customized code')
            self.assertFalse((backup/'loop-code').exists())

    def test_selected_runner_is_self_contained_without_installing_other_skills(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);target=root/'skills'
            sync(target,root/'backup',selected=['loop-prompt'])
            self.assertEqual({p.name for p in target.iterdir()}, {'loop-prompt'})
            result=subprocess.run([sys.executable,str(target/'loop-prompt/scripts/run_loop.py'),'--help'],
                                  capture_output=True,text=True,timeout=20)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_list_is_read_only_and_rejects_conflicting_options(self):
        listed=self.cli('--list')
        self.assertEqual(listed.returncode,0,listed.stderr)
        self.assertIn('office',json.loads(listed.stdout))
        self.assertNotEqual(self.cli('--list','--bundle','office').returncode,0)

    def test_unknown_bundle_members_fail_before_selection(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            (root/'skills-manifest.json').write_bytes((ROOT/'skills-manifest.json').read_bytes())
            (root/'skill-bundles.json').write_text(json.dumps({'version':1,'bundles':{
                'writing':{'purpose':'Writing','skills':['loop-write','unknown']}}}),encoding='utf-8')
            with self.assertRaises(ValueError):
                select_skills(root,['writing'],[])
