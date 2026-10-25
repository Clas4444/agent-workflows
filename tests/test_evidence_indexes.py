"""Published byte references must not silently accept drift, aliases or bad paths."""
import hashlib
import json
import os
from pathlib import Path
import tempfile
import unittest

from scripts.evidence_indexes import check_indexes


class EvidenceIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.artifact=self.root/'artifact.txt';self.artifact.write_bytes(b'known bytes\n')
        self.index=self.root/'published-hashes.json'
        self.rows={'artifact.txt':hashlib.sha256(self.artifact.read_bytes()).hexdigest()}
        self.write(self.rows)

    def write(self,rows,structured=False):
        data={'algorithm':'sha256','scope':'test declared bytes','files':rows}if structured else rows
        self.index.write_text(json.dumps(data),encoding='utf-8')

    def test_flat_and_structured_indexes_accept_actual_bytes_without_writes(self):
        for structured in [False,True]:
            self.write(self.rows,structured);before=self.index.read_bytes()
            result=check_indexes(self.root)
            self.assertEqual(result['status'],'PASS',result)
            self.assertEqual(result['indexes'],1);self.assertEqual(result['indexed_artifacts'],1)
            self.assertEqual(result['runtime_validation'],'NOT_RUN')
            self.assertEqual(self.index.read_bytes(),before)

    def test_changed_missing_and_wrong_content_artifacts_are_rejected(self):
        self.artifact.write_bytes(b'different bytes\n')
        self.assertEqual(check_indexes(self.root)['status'],'FAIL')
        self.artifact.unlink();self.assertEqual(check_indexes(self.root)['status'],'FAIL')

    def test_unsafe_and_case_colliding_paths_fail_closed(self):
        for name in ['../outside','/absolute','C:/outside','nested\\file','a/../artifact.txt','./artifact.txt','a//b',
                     'artifact.txt ','artifact.txt.','CON','NUL.txt','x?file']:
            with self.subTest(name=name):
                self.write({name:self.rows['artifact.txt']});self.assertEqual(check_indexes(self.root)['status'],'FAIL')
        self.write({'artifact.txt':self.rows['artifact.txt'],'ARTIFACT.TXT':self.rows['artifact.txt']})
        self.assertEqual(check_indexes(self.root)['status'],'FAIL')

    def test_bad_digest_algorithm_empty_and_self_reference_are_rejected(self):
        for data in [{},{'artifact.txt':'bad'},{'files':self.rows,'algorithm':'md5'},
                     {'published-hashes.json':'0'*64},{'files':{},'algorithm':'sha256'}]:
            with self.subTest(data=data):
                self.index.write_text(json.dumps(data),encoding='utf-8')
                self.assertEqual(check_indexes(self.root)['status'],'FAIL')

    def test_duplicate_keys_and_nonfinite_json_are_rejected(self):
        digest=self.rows['artifact.txt']
        for text in ['{"artifact.txt":"'+digest+'","artifact.txt":"'+digest+'"}',
                     '{"artifact.txt":NaN}']:
            self.index.write_text(text,encoding='utf-8')
            self.assertEqual(check_indexes(self.root)['status'],'FAIL')

    def test_unindexed_content_is_explicitly_outside_the_guarantee(self):
        (self.root/'personal.txt').write_bytes(b'not an indexed claim')
        result=check_indexes(self.root)
        self.assertEqual(result['status'],'PASS')
        self.assertIn('Unindexed files',result['scope'])

    def test_hardlinked_artifact_and_index_are_rejected(self):
        outside=self.root.parent/(self.root.name+'-outside')
        outside.write_bytes(b'known bytes\n');self.addCleanup(lambda:outside.unlink(missing_ok=True))
        self.artifact.unlink();os.link(outside,self.artifact)
        self.assertEqual(check_indexes(self.root)['status'],'FAIL')
        self.artifact.unlink();self.artifact.write_bytes(b'known bytes\n')
        alias=self.root/'index-alias.json';os.link(self.index,alias)
        self.assertEqual(check_indexes(self.root)['status'],'FAIL')

    def test_no_indexes_is_not_a_pass_and_parent_cache_name_does_not_hide_it(self):
        cache=self.root/'__pycache__';cache.mkdir();nested=cache/'evidence';nested.mkdir()
        self.assertEqual(check_indexes(nested)['status'],'FAIL')
        (nested/'artifact.txt').write_bytes(b'known bytes\n')
        (nested/'published-hashes.json').write_text(json.dumps(self.rows),encoding='utf-8')
        self.assertEqual(check_indexes(nested)['status'],'PASS')


if __name__=='__main__':unittest.main()
