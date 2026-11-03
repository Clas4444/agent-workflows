import json
from pathlib import Path
import shutil
import tempfile
import unittest
from scripts.coordination_evidence import verify,ROOT


class PublishedCoordinationTests(unittest.TestCase):
    def fixture(self,directory):
        root=Path(directory)
        for folder in ('coordination-function-20261103','codex-office-20261103'):
            target=root/'docs/evidence'/folder;target.mkdir(parents=True)
            names=('observations.json','protocol.json') if folder=='codex-office-20261103' else tuple(p.name for p in (ROOT/'docs/evidence'/folder).iterdir() if p.is_file())
            for name in names:shutil.copyfile(ROOT/'docs/evidence'/folder/name,target/name)
        return root

    def test_public_consistency_reproduces_from_only_documented_inputs(self):
        with tempfile.TemporaryDirectory() as directory:
            result=verify(self.fixture(directory))
            self.assertEqual(result['status'],'PASS')
            self.assertEqual(result['new_reserved_cli'],3)
            self.assertEqual(result['live_adherence'],'NOT_VERIFIED')

    def test_changed_counter_cannot_rely_on_human_report(self):
        with tempfile.TemporaryDirectory() as directory:
            root=self.fixture(directory);path=root/'docs/evidence/coordination-function-20261103/function03-model.json'
            data=json.loads(path.read_text());data['observations'][0]['input_tokens']+=1
            path.write_text(json.dumps(data))
            with self.assertRaisesRegex(ValueError,'CSV differs'):verify(root)

    def test_changed_measured_archive_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=self.fixture(directory)
            (root/'docs/evidence/coordination-function-20261103/function03-measured-helper.py').write_text('changed')
            with self.assertRaisesRegex(ValueError,'helper archive differs'):verify(root)
