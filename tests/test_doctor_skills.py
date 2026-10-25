"""Installed payload diagnosis: correctness, no writes and alias rejection."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts.doctor_skills import diagnose


class DoctorSkillsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo,self.target = self.root/'repo',self.root/'installed'
        self.repo.mkdir()
        (self.repo/'skills-manifest.json').write_text(json.dumps({
            'version':'1.0.0','skills':['loop-demo','loop-other'],
            'project_skill_roots':['.github/skills','.agents/skills','.claude/skills'],
            'resource_manifest':'skill-resources.json'}),encoding='utf-8')
        (self.repo/'skill-resources.json').write_text(json.dumps({'version':1,'resources':{
            'loop-demo':['references/facts.txt']}}),encoding='utf-8')
        self.source = self.repo/'.github/skills/loop-demo'
        (self.source/'references').mkdir(parents=True)
        (self.source/'SKILL.md').write_text('source instructions',encoding='utf-8')
        (self.source/'references/facts.txt').write_text('source facts',encoding='utf-8')
        other = self.repo/'.github/skills/loop-other';other.mkdir()
        (other/'SKILL.md').write_text('unselected instructions',encoding='utf-8')

    def install(self):
        shutil.copytree(self.source,self.target/'loop-demo')

    def check(self,selected=None):
        return diagnose(self.repo,self.target,['loop-demo'] if selected is None else selected)

    def test_missing_root_is_not_installed_and_no_directory_is_created(self):
        result = self.check()
        self.assertEqual(result['status'],'FAIL')
        self.assertEqual(result['skills'][0]['status'],'NOT_INSTALLED')
        self.assertFalse(self.target.exists())
        self.assertEqual(result['writes'],'NONE')

    def test_current_complete_payload_does_not_claim_native_or_runtime_success(self):
        self.install()
        extra = self.target/'loop-demo/personal.txt';extra.write_bytes(b'keep this')
        result = self.check()
        self.assertEqual(result['status'],'PASS')
        self.assertEqual(result['counts']['CURRENT'],1)
        self.assertEqual(result['native_discovery'],'NOT_RUN')
        self.assertEqual(result['runtime_validation'],'NOT_RUN')
        self.assertEqual(result['unmanaged_payloads'],'NOT_INSPECTED')
        self.assertEqual(extra.read_bytes(),b'keep this')
        self.assertEqual(result['selected_skills'],['loop-demo'])

    def test_missing_resource_differs_from_absent_skill(self):
        self.install();(self.target/'loop-demo/references/facts.txt').unlink()
        result = self.check()
        self.assertEqual(result['skills'][0]['status'],'INCOMPLETE')
        self.assertEqual([row['path'] for row in result['skills'][0]['payloads']
                          if row['status']=='MISSING'],['references/facts.txt'])

    def test_stale_instructions_report_hashes_without_overwriting(self):
        self.install();path=self.target/'loop-demo/SKILL.md';path.write_bytes(b'personal version')
        result = self.check()
        self.assertEqual(result['skills'][0]['status'],'DRIFTED')
        row=next(row for row in result['skills'][0]['payloads'] if row['path']=='SKILL.md')
        self.assertEqual(row['observed_sha256'],hashlib.sha256(b'personal version').hexdigest())
        self.assertNotEqual(row['expected_sha256'],row['observed_sha256'])
        self.assertEqual(path.read_bytes(),b'personal version')

    def assert_source_change_detected(self):
        self.install()
        source=self.source/'SKILL.md'
        destination=(self.target/'loop-demo/SKILL.md').resolve()
        original=Path.read_bytes
        observed=[]
        def change_after_comparison(p):
            data=original(p)
            if p.resolve()==destination:
                source.write_bytes(b'changed during diagnosis')
                observed.append(True)
            return data
        with mock.patch.object(Path,'read_bytes',change_after_comparison):result=self.check()
        self.assertEqual(observed,[True],'the source-drift injection must actually execute')
        self.assertEqual(result['status'],'BLOCKED')
        self.assertFalse(result['reference_unchanged'])
        self.assertTrue(result['reference_errors'])

    def test_source_change_during_diagnosis_cannot_finish_pass(self):
        self.assert_source_change_detected()

    def test_source_drift_with_equivalent_target_spelling_is_still_injected(self):
        anchor=self.root/'alias-anchor';anchor.mkdir()
        self.target=anchor/'..'/'installed'
        self.assert_source_change_detected()

    def test_hardlinked_payload_is_blocked_without_reading_its_bytes(self):
        self.install();path=self.target/'loop-demo/SKILL.md';path.unlink()
        outside=self.root/'outside.txt';outside.write_bytes(b'private outside')
        os.link(outside,path)
        original=Path.read_bytes
        def guarded_read(p):
            if p.resolve()==path.resolve():raise AssertionError('must not read the aliased target')
            return original(p)
        with mock.patch.object(Path,'read_bytes',guarded_read):result=self.check()
        self.assertEqual(result['status'],'BLOCKED')
        self.assertEqual(outside.read_bytes(),b'private outside')

    def test_directory_in_payload_position_and_file_parent_are_blocked(self):
        self.install();path=self.target/'loop-demo/SKILL.md';path.unlink();path.mkdir()
        self.assertEqual(self.check()['status'],'BLOCKED')
        shutil.rmtree(self.target/'loop-demo/references')
        (self.target/'loop-demo/references').write_bytes(b'file parent')
        rows=self.check()['skills'][0]['payloads']
        self.assertEqual(next(row for row in rows if row['path']=='references/facts.txt')['status'],'BLOCKED')

    def test_invalid_selection_never_falls_back_to_all(self):
        for selected in ([],['loop-demo','loop-demo'],['../outside'],'loop-demo'):
            with self.subTest(selected=selected),self.assertRaises(ValueError):self.check(selected)
        self.assertFalse(self.target.exists())

    def test_missing_or_unregistered_source_resource_cannot_look_current(self):
        self.install();(self.source/'references/facts.txt').unlink()
        with self.assertRaises(ValueError):self.check()
        (self.source/'references/facts.txt').write_bytes(b'restored')
        (self.source/'unregistered.txt').write_bytes(b'unregistered')
        with self.assertRaises(ValueError):self.check()

    def test_invalid_manifest_is_rejected_before_constructing_destination_paths(self):
        p=self.repo/'skills-manifest.json';data=json.loads(p.read_text());data['skills']=['../outside']
        p.write_text(json.dumps(data))
        with self.assertRaises(ValueError):self.check()
        self.assertFalse(self.target.exists())

    def test_cli_requires_explicit_selection_and_never_writes_missing_target(self):
        script=Path(__file__).resolve().parents[1]/'scripts/doctor_skills.py'
        for flags in ([],['--bundle','typo'],['--all','--skill','loop-debug']):
            result=subprocess.run([sys.executable,str(script),'--target',str(self.target),*flags],
                                  capture_output=True,text=True,timeout=20)
            self.assertNotEqual(result.returncode,0,result.stderr)
            self.assertFalse(self.target.exists())


if __name__=='__main__':unittest.main()
