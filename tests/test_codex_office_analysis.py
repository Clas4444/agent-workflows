import copy
import unittest
import tempfile
from pathlib import Path
from scripts.empirical_audit import read
from scripts.codex_office_analysis import render
from scripts.codex_office_analysis import WARNING,item_summary,no_tools,analyze,unexpected_error
from scripts.empirical_cases import fixtures,oracle


class OfficeAnalysisTests(unittest.TestCase):
    def test_only_recognized_cli_warning_is_non_tool(self):
        warning={'type':'item.completed','item':{'type':'error','message':WARNING+' To suppress this warning, set `suppress_unstable_features_warning = true` in config.toml.'}}
        self.assertTrue(no_tools(item_summary([warning])))
        self.assertFalse(unexpected_error([warning]))
        bad=copy.deepcopy(warning);bad['item']['message']='quota error'
        self.assertFalse(no_tools(item_summary([bad])))
        self.assertTrue(unexpected_error([bad]))
        self.assertFalse(no_tools([{'type':'command_execution'}]))
        self.assertFalse(no_tools(item_summary([{'type':'item.started','item':{'type':'command_execution'}}])))

    def rows(self):
        result=[]
        for case in fixtures():
            for arm in ('plain','workflow','matched'):
                for rep in (1,2):
                    result.append({'id':f'{case}-{arm}-{rep}','case':case,'arm':arm,'rep':rep,'status':'FAIL','cli_count':1,'seconds':1,
                        'usage':{'input_tokens':10,'output_tokens':2},'items':[{'type':'error','recognized_feature_warning':True}],
                        'checks':{'expected_output':True,'functional':True,'no_tools':False},'candidate':oracle(case,fixtures()[case]['source'])})
        return result

    def test_regrade_never_overwrites_original_or_hides_wrong_answers(self):
        rows=self.rows();result=analyze(rows,{'fixtures':fixtures()})
        self.assertTrue(all(r['status_original']=='FAIL' and r['status_regraded']=='PASS' for r in result['observations']))
        rows[-1]['candidate']['extra']='unexpected'
        last=analyze(rows,{'fixtures':fixtures()})['observations'][-1]
        self.assertEqual(last['status_regraded'],'FAIL');self.assertTrue(last['required_fields_semantic'])
        rows[-1]['candidate']['sent']=True
        self.assertFalse(analyze(rows,{'fixtures':fixtures()})['observations'][-1]['checks_regraded']['policy'])

    def test_missing_duplicate_and_not_run_cannot_pass(self):
        rows=self.rows()
        with self.assertRaises(ValueError):analyze(rows[:-1],{'fixtures':fixtures()})
        with self.assertRaises(ValueError):analyze(rows[:-1]+[rows[0]],{'fixtures':fixtures()})
        rows[-1].update(status='NOT_RUN',usage=None,seconds=None,cli_count=0,candidate=None)
        self.assertEqual(analyze(rows,{'fixtures':fixtures()})['observations'][-1]['status_regraded'],'NOT_RUN')

    def test_public_regrade_and_figures_are_reproducible_without_traces(self):
        packet=Path(__file__).resolve().parents[1]/'docs/evidence/codex-office-20261103'
        result=analyze(read(packet/'observations.json'),read(packet/'protocol.json'))
        self.assertEqual(sum(r['status_regraded']=='PASS' for r in result['observations']),11)
        with tempfile.TemporaryDirectory() as directory:
            render(result,Path(directory))
            self.assertEqual(read(Path(directory)/'analysis.json'),read(packet/'figures/analysis.json'))
            self.assertEqual((Path(directory)/'codex-office-tokens.svg').read_bytes(),(packet/'figures/codex-office-tokens.svg').read_bytes())
