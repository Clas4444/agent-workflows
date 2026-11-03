from concurrent.futures import ThreadPoolExecutor,ProcessPoolExecutor
from datetime import datetime,timezone,timedelta
import json
from pathlib import Path
import tempfile
import time
import unittest
from scripts.campaign_coordination import (CampaignLedger,CoordinationBlocked,ReservationBusy,
                                          LOCAL_REASONS,decision,fault,record_marker,validate_marker)
from scripts.campaign_coordination import stop_file,classify_failure

ROOT=Path(__file__).resolve().parents[1]


def process_reservation(directory):
    ledger=CampaignLedger(directory,provider='codex',account_domain='a',campaign='own',cap=2,max_inflight=2)
    for retry in range(200):
        try:return ledger.reserve()
        except ReservationBusy:time.sleep(.002)
        except CoordinationBlocked:return None
    raise RuntimeError('reservation lock unavailable')


class CampaignCoordinationTests(unittest.TestCase):
    def test_contract_fixture_v1(self):
        fixture=json.loads((ROOT/'tests/fixtures/coordination-v1.json').read_text(encoding='utf-8'))
        for c in fixture['cases']:
            with self.subTest(c['id']):
                marker=fault(c['marker_provider'],c['marker_domain'],c['marker_campaign'],c['reason'],['sanitized/startup.json'],fixture['marker_time'])
                result=decision(marker,provider=c['provider'],account_domain=c['account_domain'],campaign=c['campaign'],now=datetime.fromisoformat(fixture['now']))
                self.assertEqual(result['blocked'],c['blocked'])

    def test_every_local_fault_is_local_and_other_provider_never_blocked(self):
        for reason in LOCAL_REASONS:
            marker=fault('copilot',None,'own',reason,['evidence.json'])
            self.assertFalse(decision(marker,provider='copilot',account_domain=None,campaign='peer')['blocked'])
            self.assertFalse(decision(marker,provider='codex',account_domain=None,campaign='own')['blocked'])

    def test_stale_global_requires_review_but_does_not_cross_provider(self):
        when=datetime(2026,11,1,tzinfo=timezone.utc)
        marker=fault('copilot',None,'own','quota',['evidence.json'],when.isoformat())
        result=decision(marker,provider='copilot',account_domain='a',campaign='peer',now=when+timedelta(days=3))
        self.assertEqual(result,{'blocked':True,'diagnostic':'STALE_MARKER_REVIEW_REQUIRED'})
        self.assertFalse(decision(marker,provider='codex',account_domain=None,campaign='peer')['blocked'])

    def test_invalid_legacy_or_conflicting_marker_has_explicit_diagnostic(self):
        with self.assertRaisesRegex(ValueError,'unsupported marker format'):validate_marker({'reason':'MALFORMED_USAGE'})
        marker=fault('codex','account-a','own','cwd',['evidence.json']);marker['scope']='provider_account'
        with self.assertRaisesRegex(ValueError,'scope conflict'):validate_marker(marker)
        with self.assertRaises(ValueError):fault('codex','email@example.com','own','quota',['evidence.json'])
        with self.assertRaises(ValueError):fault('codex',None,'own','quota',['C:/private/log'])

    def test_markers_append_never_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            marker=fault('codex',None,'own','parse',['evidence.json'])
            one=record_marker(directory,marker);before=one.read_bytes();two=record_marker(directory,marker)
            self.assertNotEqual(one,two);self.assertEqual(one.read_bytes(),before)

    def test_failure_classification_uses_local_auth_home_and_real_service_limits(self):
        self.assertEqual(classify_failure('missing_or_invalid_accounting','no authentication information'),'auth_home')
        self.assertEqual(classify_failure('missing_or_invalid_accounting','usage limit reached'),'quota')
        self.assertEqual(classify_failure('event_parse',''),'parse')
        self.assertEqual(classify_failure('cli_failure','file not found'),'process')
        self.assertEqual(classify_failure('missing_or_invalid_accounting',''),'accounting')

    def test_legacy_stop_is_explicit_local_prerequisite_not_global_scope(self):
        with tempfile.TemporaryDirectory() as directory:
            path=Path(directory)/'stop.json';path.write_text('{"reason":"MALFORMED_USAGE"}')
            self.assertEqual(stop_file(path,provider='codex',account_domain=None,campaign='own')['diagnostic'],'LEGACY_OR_INVALID_LOCAL_MARKER_REVIEW_REQUIRED')
            marker=fault('copilot',None,'peer','quota',['quota.json']);path.write_text(json.dumps(marker))
            self.assertFalse(stop_file(path,provider='codex',account_domain=None,campaign='own')['blocked'])

    def test_concurrent_reservations_cannot_exceed_cap(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger=CampaignLedger(directory,provider='codex',account_domain='a',campaign='own',cap=4,max_inflight=4)
            def worker(_):
                for retry in range(100):
                    try:return ledger.reserve()
                    except ReservationBusy:time.sleep(.001)
                    except CoordinationBlocked:return None
                self.fail('reservation lock did not become available')
            with ThreadPoolExecutor(max_workers=12) as pool:ids=list(pool.map(worker,range(12)))
            self.assertEqual(len([x for x in ids if x]),4);self.assertEqual(len(set(x for x in ids if x)),4)
            with self.assertRaisesRegex(CoordinationBlocked,'CAP_EXHAUSTED'):ledger.reserve()

    def test_process_race_uses_the_same_file_lock_and_cap(self):
        with tempfile.TemporaryDirectory() as directory:
            with ProcessPoolExecutor(max_workers=4) as pool:ids=list(pool.map(process_reservation,[directory]*8))
            self.assertEqual(len([x for x in ids if x]),2)
            self.assertEqual(len(set(x for x in ids if x)),2)

    def test_inflight_unknown_and_failed_attempts_never_refund_or_auto_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger=CampaignLedger(directory,provider='codex',account_domain=None,campaign='own',cap=2)
            first=ledger.reserve()
            with self.assertRaises(ReservationBusy):ledger.reserve()
            ledger.finish(first,'BLOCKED_ENVIRONMENT')
            second=ledger.reserve();ledger.finish(second,'FAIL')
            with self.assertRaises(CoordinationBlocked):ledger.reserve()
            with self.assertRaises(FileExistsError):ledger.finish(first,'PASS')

    def test_identity_cannot_switch_on_resume_and_lock_is_not_auto_deleted(self):
        with tempfile.TemporaryDirectory() as directory:
            one=CampaignLedger(directory,provider='codex',account_domain='a',campaign='own',cap=2);one.reserve()
            two=CampaignLedger(directory,provider='copilot',account_domain='a',campaign='own',cap=2)
            with self.assertRaisesRegex(CoordinationBlocked,'IDENTITY_OR_BUDGET_CHANGED'):two.reserve()
            lock=Path(directory)/'reservation.lock';lock.write_text('old unknown owner')
            with self.assertRaises(ReservationBusy):one.reserve()
            self.assertTrue(lock.exists())

    def test_global_guard_blocks_only_matching_domain(self):
        with tempfile.TemporaryDirectory() as directory:
            ledger=CampaignLedger(directory,provider='codex',account_domain='a',campaign='own',cap=2)
            local=fault('codex',None,'peer','auth_home',['auth.json'])
            self.assertTrue(ledger.reserve([local]))
            global_marker=fault('codex',None,'peer','auth_account',['account.json'])
            with self.assertRaisesRegex(CoordinationBlocked,'UNKNOWN_ACCOUNT'):ledger.reserve([global_marker])
