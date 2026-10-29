import copy
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from unittest.mock import patch

from scripts import workflow_cost as cost
from scripts.workflow_cost_cases import cases


class WorkflowCostTests(unittest.TestCase):
    def call(self, folder, answer, usage=None, events=None, code=0):
        usage = usage if usage is not None else {'input_tokens': 100, 'cached_input_tokens': 40, 'output_tokens': 10}
        cost.write(folder / 'answer.json', answer)
        (folder / 'events.jsonl').write_text(json.dumps({'type': 'turn.completed', 'usage': usage}) + '\n'
                                            if events is None else events, encoding='utf-8')
        (folder / 'stderr.log').write_text('', encoding='utf-8')
        return cost.inspect_call(folder, {'value': 1}, code, 2)[0]

    def test_oracle_controls_and_source_numbers(self):
        fixtures = cases()
        self.assertTrue(all(c['passed'] for c in cost.controls(fixtures)))
        self.assertEqual(fixtures['finance']['expected']['totals'], {
            'all': {'EUR': '195.00', 'USD': '180.00'},
            'approved': {'EUR': '120.00', 'USD': '120.00'}})
        self.assertEqual(fixtures['revision']['expected']['after']['total_hours'], 11)
        self.assertEqual(fixtures['dependencies']['expected']['schedule']['selected_ids'], ['A', 'B', 'C'])

    def test_wrong_answer_is_fail_not_a_transport_block(self):
        with tempfile.TemporaryDirectory() as name:
            row = self.call(Path(name), {'value': 2})
            self.assertEqual(row['status'], 'FAIL')
            self.assertEqual(row['usage']['input_tokens'], 100)
            self.assertFalse(cost.exact({'value': True}, {'value': 1}))

    def test_candidate_blocked_word_does_not_block_transport(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            self.call(folder, {'overall': 'BLOCKED'})
            row, _ = cost.inspect_call(folder, {'overall': 'BLOCKED'}, 0, 2)
            self.assertEqual(row['status'], 'PASS')

    def test_bad_usage_cannot_become_a_cheap_success(self):
        variants = ({}, {'input_tokens': True, 'cached_input_tokens': 0, 'output_tokens': 1},
                    {'input_tokens': 10, 'cached_input_tokens': 11, 'output_tokens': 1},
                    {'input_tokens': 10, 'cached_input_tokens': 0, 'output_tokens': 1, 'reasoning_output_tokens': 2})
        with tempfile.TemporaryDirectory() as name:
            for usage in variants:
                self.assertEqual(self.call(Path(name), {'value': 1}, usage)['status'], 'BLOCKED')

    def test_duplicate_or_malformed_events_block(self):
        with tempfile.TemporaryDirectory() as name:
            for events in ('not-json\n', '{"type":"turn.completed","type":"error"}\n', '[]\n'):
                self.assertEqual(self.call(Path(name), {'value': 1}, events=events)['status'], 'BLOCKED')

    def test_duplicate_final_json_fails_and_tool_use_fails(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name)
            self.call(folder, {'value': 1})
            (folder / 'answer.json').write_text('{"value":1,"value":1}', encoding='utf-8')
            self.assertEqual(cost.inspect_call(folder, {'value': 1}, 0, 1)[0]['status'], 'FAIL')
            cost.write(folder / 'answer.json', {'value': 1})
            with (folder / 'events.jsonl').open('a', encoding='utf-8') as stream:
                stream.write(json.dumps({'type': 'item.completed', 'item': {'type': 'command_execution'}}) + '\n')
            self.assertEqual(cost.inspect_call(folder, {'value': 1}, 0, 1)[0]['status'], 'FAIL')

    def test_authorization_is_required_before_process_or_files(self):
        with patch.object(cost.subprocess, 'run') as execute:
            with self.assertRaisesRegex(ValueError, 'allow-model'):
                cost.run(Path('absent'), allow=False)
            execute.assert_not_called()

    def test_plan_freezes_and_refuses_overwrite_or_drift(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name) / 'campaign'
            protocol = cost.plan(folder)
            self.assertEqual(protocol['planned_calls'], 36)
            self.assertNotIn(b'\r\n', (folder / 'protocol.json').read_bytes())
            with self.assertRaises(FileExistsError):
                cost.plan(folder)
            with (folder / 'protocol.json').open('a', encoding='utf-8') as stream:
                stream.write(' ')
            with self.assertRaisesRegex(ValueError, 'STALE'):
                cost.check_pin(folder, protocol)

    def packages(self):
        protocol = {'fixtures': {'case': {}}, 'repetitions': 2}
        rows = []
        for rep in (1, 2):
            for arm in cost.ARMS:
                rows.append({'id': str(len(rows)), 'case': 'case', 'rep': rep, 'arm': arm, 'status': 'PASS',
                             'calls': [{'usage': {'input_tokens': 100, 'cached_input_tokens': 40, 'output_tokens': 10}, 'seconds': 2}]})
        return protocol, rows

    def test_failure_is_retained_and_disables_efficiency_claim(self):
        protocol, rows = self.packages()
        rows[0]['status'] = 'FAIL'
        rows[0]['calls'][0]['usage']['input_tokens'] = 1
        rows[0]['calls'][0]['usage']['cached_input_tokens'] = 0
        summary = cost.aggregate(protocol, rows)
        self.assertEqual(summary['measurement_status'], 'FAIL')
        self.assertEqual(summary['case_means']['case']['workflow']['statuses'], {'FAIL': 1, 'PASS': 1})
        self.assertEqual(summary['eligible_cases'], [])
        self.assertIsNone(summary['pooled_reductions_percent']['manual']['total_tokens'])

    def test_cache_is_subset_and_averages_recompute(self):
        protocol, rows = self.packages()
        summary = cost.aggregate(protocol, rows)
        row = summary['packages'][0]
        self.assertEqual(row['total_tokens'], 110)
        self.assertEqual(row['uncached_input_tokens'], 60)
        self.assertEqual(summary['pooled_reductions_percent']['manual']['total_tokens'], 0)
        changed = copy.deepcopy(rows)
        for row in changed:
            if row['arm'] == 'manual':
                row['calls'] *= 3
        summary = cost.aggregate(protocol, changed)
        self.assertAlmostEqual(summary['pooled_reductions_percent']['manual']['total_tokens'], 100 * 2/3)

    def test_missing_baseline_does_not_crash_or_claim_savings(self):
        protocol, rows = self.packages()
        rows[0]['arm'] = 'manual'
        self.assertEqual(cost.aggregate(protocol, rows)['eligible_cases'], [])

    def test_offline_regrade_from_fresh_inputs_detects_tampered_answer(self):
        with tempfile.TemporaryDirectory() as name:
            folder = Path(name) / 'campaign'
            cost.plan(folder, repetitions=1)

            def fake_invoke(call, prompt, expected, protocol, codex):
                call.mkdir(parents=True)
                cost.write(call / 'answer.json', expected)
                cost.write(call / 'prompt.txt', {'synthetic': True})
                event = {'type': 'turn.completed', 'usage': {'input_tokens': 100, 'cached_input_tokens': 40, 'output_tokens': 10}}
                (call / 'events.jsonl').write_text(json.dumps(event) + '\n', encoding='utf-8')
                (call / 'stderr.log').write_text('', encoding='utf-8')
                return cost.inspect_call(call, expected, 0, 2)

            with patch.object(cost, 'invoke', side_effect=fake_invoke):
                self.assertEqual(cost.run(folder, allow=True, codex='fake')['measurement_status'], 'PASS')
            with self.assertRaises(FileExistsError):
                cost.run(folder, allow=True, codex='fake')
            fresh = Path(name) / 'fresh'
            shutil.copytree(folder, fresh)
            (fresh / 'summary.json').unlink()
            self.assertEqual(cost.analyze(fresh)['measurement_status'], 'PASS')
            answer = next((fresh / 'calls').rglob('answer.json'))
            cost.write(answer, {'wrong': True})
            with self.assertRaisesRegex(ValueError, 'STALE'):
                cost.analyze(fresh)


if __name__ == '__main__':
    unittest.main()
