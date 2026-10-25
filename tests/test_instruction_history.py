import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from scripts.instruction_history import instruction_identity, check_history


class InstructionHistoryTests(unittest.TestCase):
    def fixture(self, root):
        current=root/'.github/skills/loop-write/SKILL.md';current.parent.mkdir(parents=True);current.write_bytes(b'new instructions')
        archive=root/'docs/evidence/instruction-history/test-1/loop-write/SKILL.md';archive.parent.mkdir(parents=True);archive.write_bytes(b'old instructions')
        old=hashlib.sha256(archive.read_bytes()).hexdigest()
        data={'test-1':{'loop-write':{'historical_sha256':old,'current_sha256':hashlib.sha256(current.read_bytes()).hexdigest(),
             'archive':archive.relative_to(root).as_posix(),'reason':'Contract changed','historical_reuse_status':'INVALIDATED','automatic_discovery_status':'NOT_RUN'}}}
        index=root/'docs/evidence/instruction-history.json';index.write_text(json.dumps(data),encoding='utf-8')
        return current,archive,index,old

    def test_archived_version_stays_verifiable_without_claiming_current_runtime(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);current,archive,index,old=self.fixture(root)
            self.assertEqual(instruction_identity(root,'test-1','loop-write',old),'HISTORICAL_ONLY_INVALIDATED')
            self.assertEqual(check_history(root),[])

    def test_current_drift_or_archived_tampering_cannot_reuse_pass(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);current,archive,index,old=self.fixture(root)
            current.write_bytes(b'changed again')
            with self.assertRaises(ValueError):instruction_identity(root,'test-1','loop-write',old)
            self.assertTrue(check_history(root))
            current.write_bytes(b'new instructions');archive.write_bytes(b'tampered')
            with self.assertRaises(ValueError):instruction_identity(root,'test-1','loop-write',old)

    def test_forged_digest_archive_escape_and_missing_invalidation_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);current,archive,index,old=self.fixture(root)
            data=json.loads(index.read_text(encoding='utf-8'))
            data['test-1']['loop-write']['archive']='../outside'
            index.write_text(json.dumps(data),encoding='utf-8')
            with self.assertRaises(ValueError):instruction_identity(root,'test-1','loop-write',old)
            with self.assertRaises(ValueError):instruction_identity(root,'test-1','../escape',old)
            index.unlink()
            with self.assertRaises(OSError):instruction_identity(root,'test-1','loop-write',old)

    def test_byte_identical_current_source_remains_a_separate_basis(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);current,archive,index,old=self.fixture(root)
            current.write_bytes(archive.read_bytes())
            self.assertEqual(instruction_identity(root,'test-1','loop-write',old),'CURRENT_BYTE_IDENTICAL')
            self.assertTrue(check_history(root))  # Stale invalidation registry must also be updated.
