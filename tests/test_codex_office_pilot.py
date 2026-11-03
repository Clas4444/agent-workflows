import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from scripts.codex_office_pilot import isolation_checks,run
from scripts.empirical_audit import sha,write
from scripts.empirical_cases import fixtures,oracle


class CodexOfficeTests(unittest.TestCase):
    def test_generic_boilerplate_is_not_a_candidate_catalog(self):
        self.assertTrue(all(isolation_checks('Generic Available skills boilerplate').values()))
        self.assertFalse(all(isolation_checks('<skills_instructions>loop-work</skills_instructions>').values()))

    def protocol(self,folder):
        return {'campaign':'test','schedule':[{'id':str(i),'case':'revision','arm':'plain','rep':i} for i in range(1,13)],
                'fixtures':fixtures(),'skill_text':'','model_requested':'test','timeout_seconds':10}

    def test_shared_scope_is_new_provider_and_local_stop_prevents_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);write(folder/'STOP-MODEL-CALLS.json',{'reason':'quota'})
            with patch('scripts.codex_office_pilot.pin',return_value=self.protocol(folder)),patch('scripts.codex_office_pilot.subprocess.run') as invoke:
                rows=run(folder,'none');invoke.assert_not_called()
            self.assertEqual(len(rows),12);self.assertEqual(sum(r['cli_count'] for r in rows),0)

    def test_uncertain_reservation_consumes_attempt_without_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);(folder/'attempts/1').mkdir(parents=True)
            with patch('scripts.codex_office_pilot.pin',return_value=self.protocol(folder)),patch('scripts.codex_office_pilot.subprocess.run') as invoke:
                rows=run(folder,'none');invoke.assert_not_called()
            self.assertEqual(rows[0]['status'],'BLOCKED_ENVIRONMENT');self.assertEqual(sum(r['cli_count'] for r in rows),1)

    def test_schedule_cannot_expand_the_hard_twelve_call_budget(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);protocol=self.protocol(folder)
            protocol['schedule'].append(dict(protocol['schedule'][0],id='13'))
            with patch('scripts.codex_office_pilot.pin',return_value=protocol),patch('scripts.codex_office_pilot.subprocess.run',side_effect=AssertionError('must not invoke')) as invoke:
                with self.assertRaises(ValueError):run(folder,'none')
                invoke.assert_not_called()

    def test_transport_failure_preserved_and_stops_after_one(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            with patch('scripts.codex_office_pilot.pin',return_value=self.protocol(folder)),patch('scripts.codex_office_pilot.subprocess.run',side_effect=OSError('startup')) as invoke:
                rows=run(folder,'none');self.assertEqual(invoke.call_count,1)
            self.assertEqual(rows[0]['status'],'BLOCKED_ENVIRONMENT')
            self.assertEqual(sum(r['cli_count'] for r in rows),1)
            self.assertEqual(sum(r['status']=='NOT_RUN' for r in rows),11)

    def test_candidate_correctness_cannot_hide_unexpected_workspace_writes(self):
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory);protocol=self.protocol(folder)
            def candidate(command,**kw):
                answer=Path(command[command.index('-o')+1]);value=oracle('revision',fixtures()['revision']['source'])
                write(answer,value)
                kw['stdout'].write((json.dumps({'type':'turn.completed','usage':{'input_tokens':10,'cached_input_tokens':0,'output_tokens':2}})+'\n').encode())
                (Path(command[command.index('-C')+1])/'unexpected').write_text('bad')
                class Result:returncode=0
                return Result()
            with patch('scripts.codex_office_pilot.pin',return_value=protocol),patch('scripts.codex_office_pilot.subprocess.run',side_effect=candidate) as invoke:
                rows=run(folder,'none');self.assertEqual(invoke.call_count,12)
            self.assertTrue(all(r['status']=='FAIL' and r['checks']['functional'] for r in rows))
