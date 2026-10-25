"""Backup safety must hold before any overwrite or backup write starts."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

from scripts.sync_skills import sync

REPO=Path(__file__).resolve().parents[1]


class BackupPreflightTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name).resolve()
        self.target,self.backup=self.root/'skills',self.root/'backup'
        self.old={'loop-write':b'original write customization',
                  'loop-summarize':b'original summary customization'}
        for name,value in self.old.items():
            path=self.target/name/'SKILL.md';path.parent.mkdir(parents=True);path.write_bytes(value)

    def alias(self,link,real):
        self.assertTrue(link.absolute().is_relative_to(self.root))
        self.assertTrue(real.resolve().is_relative_to(self.root))
        if os.name=='nt':
            made=subprocess.run(['cmd','/c','mklink','/J',str(link),str(real)],capture_output=True)
            self.assertEqual(made.returncode,0,made.stderr)
        else:link.symlink_to(real,target_is_directory=True)

    def assert_originals(self):
        for name,value in self.old.items():self.assertEqual((self.target/name/'SKILL.md').read_bytes(),value)

    def test_internal_backup_alias_is_rejected_before_any_copy(self):
        for check in (False,True):
            with self.subTest(check=check):
                real=self.backup/('read-only'if check else'write')
                (real/'loop-write').mkdir(parents=True)
                self.alias(real/'loop-summarize',real/'loop-write')
                with mock.patch('scripts.sync_skills.shutil.copy2',wraps=shutil.copy2)as copy:
                    with self.assertRaises(ValueError):
                        sync(self.target,real,check=check,selected=list(self.old))
                    copy.assert_not_called()
                self.assert_originals()
                self.assertFalse((real/'loop-write/SKILL.md').exists())

    def test_backup_parent_file_is_rejected_before_earlier_backups_are_written(self):
        self.backup.mkdir();(self.backup/'loop-summarize').write_bytes(b'not a directory')
        with mock.patch('scripts.sync_skills.shutil.copy2',wraps=shutil.copy2)as copy:
            with self.assertRaises(ValueError):sync(self.target,self.backup,selected=list(self.old))
            copy.assert_not_called()
        self.assert_originals()
        self.assertFalse((self.backup/'loop-write').exists())

    def test_safe_distinct_backup_paths_preserve_every_original(self):
        self.assertTrue(sync(self.target,self.backup,selected=list(self.old)))
        for name,value in self.old.items():
            self.assertEqual((self.backup/name/'SKILL.md').read_bytes(),value)
            self.assertNotEqual((self.target/name/'SKILL.md').read_bytes(),value)

    def test_installer_cli_rejects_internal_backup_alias_without_overwriting(self):
        (self.backup/'loop-write').mkdir(parents=True)
        self.alias(self.backup/'loop-summarize',self.backup/'loop-write')
        result=subprocess.run([sys.executable,str(REPO/'scripts/install_skills.py'),
            '--bundle','writing','--target',str(self.target),'--backup',str(self.backup)],
            capture_output=True,text=True,encoding='utf-8',timeout=20)
        self.assertNotEqual(result.returncode,0,result.stdout)
        self.assert_originals()
        self.assertFalse((self.backup/'loop-write/SKILL.md').exists())


if __name__=='__main__':unittest.main()
