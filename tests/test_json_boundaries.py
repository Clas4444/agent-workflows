"""Portable control-plane JSON must not silently choose duplicate last values."""
import json
from pathlib import Path
import shutil
import tempfile
import unittest

from scripts.validation.manifest import load_manifest
from scripts.routing_check import check_routes
from scripts.catalog import check_catalog
from scripts.validation.json_data import loads_json, MAX_JSON_DEPTH
from scripts.sync_skills import sync
from unittest import mock

ROOT=Path(__file__).resolve().parents[1]


class JSONBoundaryTests(unittest.TestCase):
    def test_excessive_nesting_has_a_controlled_validation_error(self):
        raw='['*10000+'0'+']'*10000
        with self.assertRaisesRegex(ValueError,'nesting'):
            loads_json(raw)

    def test_depth_bound_is_explicit_for_strings_and_encoded_inputs(self):
        valid = '['*MAX_JSON_DEPTH+'0'+']'*MAX_JSON_DEPTH
        invalid = '['*(MAX_JSON_DEPTH+1)+'0'+']'*(MAX_JSON_DEPTH+1)
        for encode in (lambda s:s, lambda s:s.encode('utf-8'),
                       lambda s:bytearray(s.encode('utf-16'))):
            with self.subTest(encode=encode):
                self.assertIsInstance(loads_json(encode(valid)), list)
                with self.assertRaisesRegex(ValueError, 'nesting'):
                    loads_json(encode(invalid))

    def test_quoted_brackets_and_escaped_quotes_do_not_count_as_nesting(self):
        value = {'text':'['*2000+' escaped quote: " and slash: \\ '+']'*2000}
        self.assertEqual(loads_json(json.dumps(value)), value)

    def test_unique_keys_apply_after_escape_decoding_and_at_every_depth(self):
        for raw in ('{"status":"FAIL","\\u0073tatus":"PASS"}',
                    '{"outer":{"same":1,"same":2}}','{"list":[{"x":1,"x":2}]}'):
            with self.subTest(raw=raw), self.assertRaisesRegex(ValueError,'duplicate JSON key'):
                loads_json(raw)

    def test_normal_nested_values_and_quoted_constant_names_remain_valid(self):
        raw='{"nested":[true,false,null,0,1.5,"NaN","Infinity"],"other":{"k":"value"}}'
        self.assertEqual(loads_json(raw),json.loads(raw))

    def test_sync_rejects_duplicate_manifest_before_any_install_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory); repo=root/'source';repo.mkdir()
            (repo/'skills-manifest.json').write_text('{"skills":["../escape"],"skills":["loop-code"]}',encoding='utf-8')
            with mock.patch('scripts.sync_skills.REPO',repo), self.assertRaisesRegex(ValueError,'duplicate JSON key'):
                sync(root/'installed',root/'backup')
            self.assertFalse((root/'installed').exists())
            self.assertFalse((root/'backup').exists())

    def test_duplicate_manifest_key_is_rejected_not_last_value_wins(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            original=(ROOT/'skills-manifest.json').read_text(encoding='utf-8')
            (root/'skills-manifest.json').write_text('{"version":"invalid",'+original.lstrip()[1:],encoding='utf-8')
            self.assertTrue(load_manifest(root)[1])

    def test_nonfinite_json_extensions_are_rejected_in_manifest(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            original=(ROOT/'skills-manifest.json').read_text(encoding='utf-8').rstrip()
            for value in ('NaN','Infinity','-Infinity'):
                with self.subTest(value=value):
                    (root/'skills-manifest.json').write_text(original[:-1]+',"extra":'+value+'}',encoding='utf-8')
                    self.assertTrue(load_manifest(root)[1])

    def test_duplicate_routing_cases_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            shutil.copy2(ROOT/'skills-manifest.json',root/'skills-manifest.json')
            original=(ROOT/'skill-routing.json').read_text(encoding='utf-8')
            (root/'skill-routing.json').write_text('{"cases":[],'+original.lstrip()[1:],encoding='utf-8')
            self.assertTrue(check_routes(root))

    def test_duplicate_catalog_group_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory)
            for name in ('skills-manifest.json','README.md'):
                shutil.copy2(ROOT/name,root/name)
            shutil.copytree(ROOT/'.github/skills',root/'.github/skills')
            original=(ROOT/'skill-groups.json').read_text(encoding='utf-8')
            key=next(iter(json.loads(original)))
            (root/'skill-groups.json').write_text('{'+json.dumps(key)+':null,'+original.lstrip()[1:],encoding='utf-8')
            self.assertTrue(check_catalog(root))
