import json
import tempfile
import unittest
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from scripts.validate import validate, frontmatter_value, DEFAULT_ROOTS

class ContractValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.root=Path(self.temp.name)
        self.text=(Path(__file__).resolve().parents[1]/'.github/skills/loop-review/SKILL.md').read_text(encoding='utf-8')
        self.write(self.text)
        (self.root/'skills-manifest.json').write_text(json.dumps({'version':'1.0.0','skills':['loop-review'],'project_skill_roots':list(DEFAULT_ROOTS)}), encoding='utf-8')

    def tearDown(self): self.temp.cleanup()

    def write(self,text):
        for root in DEFAULT_ROOTS:
            path=self.root/root/'loop-review/SKILL.md'
            path.parent.mkdir(parents=True,exist_ok=True)
            path.write_text(text,encoding='utf-8')

    def test_valid_contract_passes(self): self.assertEqual(validate(self.root),[])

    def test_missing_contract_fails_even_when_all_copies_match(self):
        self.write(self.text.replace('## Inputs','## Other'))
        self.assertTrue(any('Inputs section' in error for error in validate(self.root)))

    def test_wrong_order_fails(self):
        self.write(self.text.replace('## Inputs','## TEMP').replace('## Output','## Inputs').replace('## TEMP','## Output'))
        self.assertTrue(any('out-of-order' in error for error in validate(self.root)))

    def test_invalid_metadata_boolean_fails(self):
        self.write(self.text.replace('user-invocable: true','user-invocable: yes'))
        self.assertTrue(any('invalid boolean' in error for error in validate(self.root)))

    def test_quoted_boolean_string_is_not_a_literal_boolean(self):
        self.write(self.text.replace('user-invocable: true','user-invocable: "true"'))
        self.assertTrue(any('invalid boolean' in error for error in validate(self.root)))

    def test_empty_description_does_not_consume_next_field(self):
        self.assertIsNone(frontmatter_value('description:\nname: next','description'))
        self.write(self.text.replace(next(line for line in self.text.splitlines() if line.startswith('description:')),'description:'))
        self.assertTrue(any('no description' in error for error in validate(self.root)))

    def test_duplicate_metadata_fails(self):
        self.write(self.text.replace('name: loop-review','name: loop-review\nname: loop-review'))
        self.assertTrue(any('duplicate metadata' in error for error in validate(self.root)))

    def test_missing_never_sleep_policy_fails(self):
        self.write(self.text.replace('Never sleep','Do not wait'))
        self.assertTrue(any('never-sleep' in error for error in validate(self.root)))

    def test_overlong_description_fails(self):
        line=next(line for line in self.text.splitlines() if line.startswith('description:'))
        self.write(self.text.replace(line,'description: "'+'x'*1025+'"'))
        self.assertTrue(any('1024' in error for error in validate(self.root)))
