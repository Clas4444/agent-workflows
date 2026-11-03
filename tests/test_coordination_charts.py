import json
from pathlib import Path
import shutil
import struct
import re
import tempfile
import unittest
from scripts.coordination_charts import derive,generated_bytes,OUTPUT,PACKET,ROOT


class CoordinationChartTests(unittest.TestCase):
    def test_chart_sources_and_svgs_reproduce_without_human_report(self):
        data=derive()
        self.assertEqual(len(data['historical']),12)
        self.assertEqual([(r['strict_pass'],r['schema_pass'],r['required_fields_pass']) for r in data['quality']],[(4,4,4),(4,4,4),(3,3,4)])
        self.assertEqual(sum(r['measured'] for r in data['function03']),2)
        for name,value in generated_bytes(data).items():self.assertEqual((OUTPUT/name).read_bytes(),value,name)

    def test_unknown_usage_remains_null_and_zero_filling_is_rejected(self):
        data=derive();missing=[r for r in data['function03'] if not r['measured']]
        self.assertEqual(len(missing),4)
        self.assertTrue(all(r['total_tokens'] is None and r['seconds'] is None for r in missing))
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);packet=root/'coordination-function-20261103';packet.mkdir()
            previous=root/'codex-office-20261103';previous.mkdir()
            for name in ('coord02-regrade-v2.json','function03-model.json'):shutil.copyfile(PACKET/name,packet/name)
            shutil.copyfile(ROOT/'docs/evidence/codex-office-20261103/protocol.json',previous/'protocol.json')
            value=json.loads((packet/'function03-model.json').read_text());value['observations'][2]['seconds']=0
            (packet/'function03-model.json').write_text(json.dumps(value))
            with self.assertRaisesRegex(ValueError,'zero-filled'):derive(packet)

    def test_pngs_exist_and_both_public_reports_embed_them(self):
        for name in ('historical-quality','historical-cost','function03-status','function03-observed-cost'):
            raw=(OUTPUT/(name+'.png')).read_bytes()
            self.assertEqual(raw[:8],b'\x89PNG\r\n\x1a\n')
            self.assertEqual(struct.unpack('>II',raw[16:24]),(1440,920))
            report='2026-11-03-coordination.md' if name.startswith('historical') else '2026-11-03-functional-workflow.md'
            text=(ROOT/'docs/testing/experiments'/report).read_text(encoding='utf-8')
            self.assertRegex(text,r'!\[[^\]]+\]\([^\n)]*/'+re.escape(name)+r'\.png\)')
            self.assertIn(name+'.svg)',text)
