import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
from scripts.install_plan import plan_install

ROOT=Path(__file__).resolve().parents[1]


class InstallPlanTests(unittest.TestCase):
    def cli(self,*args):
        return subprocess.run([sys.executable,str(ROOT/'scripts/install_skills.py'),*map(str,args)],
                              capture_output=True,text=True,timeout=30)

    def test_missing_target_plan_is_stable_and_never_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'skills'
            first=plan_install(ROOT,target,['loop-write'])
            second=plan_install(ROOT,target,['loop-write'])
            self.assertEqual(first['plan_id'],second['plan_id'])
            self.assertEqual(first['status'],'READY')
            self.assertGreater(first['counts']['CREATE'],0)
            self.assertFalse(first['backup_required'])
            self.assertFalse(target.exists())

    def test_review_apply_and_stale_target_rejection_preserve_custom_files(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'skills';backup=Path(directory)/'backup'
            args=('--skill','loop-write','--target',target)
            planned=self.cli(*args,'--plan')
            self.assertEqual(planned.returncode,0,planned.stderr)
            token=json.loads(planned.stdout)['plan_id']
            applied=self.cli(*args,'--expect-plan',token,'--backup',backup)
            self.assertEqual(applied.returncode,0,applied.stderr)
            current=plan_install(ROOT,target,['loop-write'])
            self.assertEqual(current['counts']['CREATE'],0)
            self.assertEqual(current['counts']['REPLACE'],0)
            payload=target/'loop-write/SKILL.md';payload.write_text('my custom version')
            stale=self.cli(*args,'--expect-plan',current['plan_id'],'--backup',Path(directory)/'unused')
            self.assertNotEqual(stale.returncode,0)
            self.assertIn('stale',stale.stderr)
            self.assertEqual(payload.read_text(),'my custom version')
            self.assertFalse((Path(directory)/'unused').exists())
            replacement=plan_install(ROOT,target,['loop-write'])
            self.assertEqual(replacement['counts']['REPLACE'],1)
            self.assertTrue(replacement['backup_required'])

    def test_reference_change_invalidates_plan_id(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'skills'
            from scripts.doctor_skills import diagnose
            report=diagnose(ROOT,target,['loop-write'])
            with mock.patch('scripts.install_plan.diagnose',return_value=report):
                first=plan_install(ROOT,target,['loop-write'])
                report['reference_inputs']['skills-manifest.json']='changed'
                second=plan_install(ROOT,target,['loop-write'])
            self.assertNotEqual(first['plan_id'],second['plan_id'])

    def test_hardlinked_destination_is_blocked_without_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);target=base/'skills'
            payload=target/'loop-write/SKILL.md';payload.parent.mkdir(parents=True)
            original=base/'original';original.write_text('preserve')
            os.link(original,payload)
            result=plan_install(ROOT,target,['loop-write'])
            self.assertEqual(result['status'],'BLOCKED')
            self.assertEqual(result['counts']['BLOCKED'],1)
            self.assertEqual(original.read_text(),'preserve')

    def test_incompatible_modes_fail_without_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            target=Path(directory)/'skills'
            for flags in (('--plan','--check'),('--plan','--expect-plan','a'*64),('--expect-plan','bad')):
                result=self.cli('--skill','loop-write','--target',target,*flags)
                self.assertNotEqual(result.returncode,0)
                self.assertFalse(target.exists())
