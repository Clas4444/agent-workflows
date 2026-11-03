import copy
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from scripts.workflow_setup import (advance,agent_map,attach_attention,attention_scope,check_map,
                                    fingerprint,select,start,template)

ROOT=Path(__file__).resolve().parents[1]


class WorkflowAttentionContractTests(unittest.TestCase):
    def test_self_contained_product_contract_fixture_v1(self):
        fixture=json.loads((ROOT/'tests/fixtures/workflow-attention-v1.json').read_text(encoding='utf-8'))
        graph=attach_attention(fixture['graph'],fixture['patch']);base=dict(fixture['base_profile'])
        state=start(graph,{'kind':'table','done':True})
        with attention_scope(graph,state,base) as choice:
            self.assertEqual(choice['skills'],['loop-table']);self.assertEqual(base['focus'],fixture['expected']['work_focus'])
        self.assertEqual(base,fixture['base_profile'])
        state=advance(graph,state,'PASS','mandatory checks observed')
        with attention_scope(graph,state,base):self.assertEqual(base['verify'],fixture['expected']['check_verify'])
        self.assertEqual(advance(graph,state,'PASS','mandatory checks observed')['status'],'DONE')
        self.assertEqual(base,fixture['base_profile'])
    def test_versioned_opt_in_and_legacy_patch_have_identical_intent(self):
        graph=template('skills');before=copy.deepcopy(graph)
        patch={'attention':{'focus':2},'steps':{'verify':[{'binding':0,'attention':{'verify':5}}]}}
        legacy=attach_attention(graph,patch);versioned=attach_attention(graph,dict(patch,contract_version=1))
        self.assertEqual(legacy,versioned);self.assertEqual(graph,before)
        stripped=copy.deepcopy(versioned);stripped.pop('attention')
        for step in stripped['steps']:
            for binding in step['bindings']:binding.pop('attention',None)
        self.assertEqual(stripped,graph)

    def test_patch_cannot_add_routes_permissions_or_remove_mandatory_checks(self):
        graph=template('skills');before=copy.deepcopy(graph)
        for patch in ({'contract_version':2,'attention':{'verify':1}}, {'contract_version':True,'attention':{}},
                      {'contract_version':1}, {'contract_version':1,'attention':None},
                      {'contract_version':1,'attention':{'verify':0}}, {'contract_version':1,'attention':{'verify':True}},
                      {'contract_version':1,'boundaries':[]}, {'contract_version':1,'steps':{'verify':[{'binding':0,'acceptance':[],'attention':{}}]}},
                      {'contract_version':1,'steps':{'work':[{'binding':0,'skills':[],'attention':{}}]}}):
            with self.subTest(patch=patch):
                with self.assertRaises(ValueError):attach_attention(graph,patch)
                self.assertEqual(graph,before)

    def test_selection_view_cannot_mutate_owned_checks_paths_or_selected_skills(self):
        graph=template('skills');before=copy.deepcopy(graph);state=start(graph,{'kind':'bug'})
        selected=select(graph,state)
        selected['acceptance'].clear();selected['sources'].append('unapproved.md')
        selected['skills'].clear();selected['boundaries'].clear()
        self.assertEqual(graph,before)

    def test_standalone_has_no_attention_effect_and_no_profile_is_required(self):
        graph=template('skills');state=start(graph,{'kind':'bug'});current={'focus':5,'verify':4}
        with attention_scope(graph,state,current) as chosen:
            self.assertFalse(chosen['attention_requested']);self.assertEqual(current,{'focus':5,'verify':4})
        self.assertEqual(current,{'focus':5,'verify':4})
        with attention_scope(graph,state,current):current['focus']=1
        self.assertEqual(current['focus'],1)  # Independent attention changes are not owned by workflow.

    def test_scope_restores_base_on_exception_early_stop_and_nested_exit(self):
        graph=attach_attention(template('skills'),{'contract_version':1,'attention':{'focus':2}})
        state=start(graph,{'kind':'bug'});current={'focus':5,'verify':4};original=dict(current)
        with self.assertRaisesRegex(RuntimeError,'step failed'):
            with attention_scope(graph,state,current) as chosen:
                self.assertEqual(current['focus'],2);self.assertEqual(current['verify'],4)
                self.assertEqual(chosen['attention'],current)
                with attention_scope(graph,state,current):current['focus']=1
                self.assertEqual(current['focus'],2)
                raise RuntimeError('step failed')
        self.assertEqual(current,original)
        def early_stop():
            with attention_scope(graph,state,current):return advance(graph,state,'BLOCKED','missing input')
        self.assertEqual(early_stop()['status'],'STOP');self.assertEqual(current,original)

    def test_low_verify_does_not_change_checks_or_routes_and_next_step_reselects(self):
        original=template('skills');graph=attach_attention(original,{'contract_version':1,'steps':{'work':[{'binding':0,'attention':{'verify':1}}]}})
        state=start(graph,{'kind':'bug'});base={'verify':5}
        with attention_scope(graph,state,base) as chosen:
            self.assertEqual(chosen['attention']['verify'],1)
            self.assertEqual(chosen['acceptance'],original['steps'][0]['acceptance'])
        self.assertEqual(base,{'verify':5})
        nxt=advance(graph,state,'PASS','caller checks passed',{'risk':'high'})
        with attention_scope(graph,nxt,base):self.assertEqual(base['verify'],5)
        self.assertEqual(base,{'verify':5})

    def test_isolated_copy_without_peer_can_attach_select_and_export_no_cross_write(self):
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);project=root/'project';project.mkdir();sentinel=root/'outside.txt';sentinel.write_text('untouched')
            helper=root/'helper.py';shutil.copyfile(ROOT/'scripts/workflow_setup.py',helper)
            graph=project/'graph.json';graph.write_text(json.dumps(template('skills')))
            patch=project/'patch.json';patch.write_text(json.dumps({'contract_version':1,'attention':{'focus':2}}))
            command=[sys.executable,'-I','-S','-B',str(helper)]
            result=subprocess.run(command+['attach','--file',str(graph),'--patch',str(patch)],cwd=root,capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            updated=json.loads(result.stdout);graph.write_text(json.dumps(updated))
            result=subprocess.run(command+['export','--file',str(graph),'--project',str(project)],cwd=root,capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)
            output=Path(json.loads(result.stdout)['directory']);contents=(output/'AGENT-MAP.md').read_text()
            self.assertEqual(check_map(updated,contents,project)['status'],'PASS')
            self.assertEqual(sentinel.read_text(),'untouched')
            self.assertEqual(sorted(p.name for p in root.iterdir()),['helper.py','outside.txt','project'])
            self.assertNotIn('agent-attention/',contents)

    def test_legacy_attention_layer_is_explicit_compatibility_not_setup_takeover(self):
        result=subprocess.run([sys.executable,'-I','-S','-B',str(ROOT/'scripts/workflow_setup.py'),
            'template','--layer','attention'],capture_output=True,text=True,timeout=10)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertEqual(json.loads(result.stdout)['schema_version'],1)
        self.assertIn('not standalone Attention Setup',result.stderr)
