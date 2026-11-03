"""User CLI journeys with real files/check processes; no model calls."""
import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HELPER=Path(__file__).resolve().parents[1]/'scripts/workflow_setup.py'


def graph():
    def edges(passed,failed):
        return [{'status':'PASS','next':passed},{'status':'FAIL','next':failed},
                {'status':'BLOCKED','next':'STOP'},{'status':'NOT_RUN','next':'STOP'}]
    steps=[]
    for name,sources,skill,passed,failed in (
        ('intake',['authority.txt'],'loop-intake','repair','STOP'),
        ('repair',['request.txt','calc.py'],'loop-debug','verify','repair'),
        ('verify',['request.txt','calc.py','check.py'],'loop-test','DONE','repair')):
        transitions=edges(passed,failed)
        if name=='verify':transitions.insert(0,{'status':'PASS','when':{'more':True},'next':'intake'})
        steps.append({'id':name,'title':name,'sources':sources,'acceptance':['Authorized criteria checked'],
                      'bindings':[{'when':{},'skills':[skill]}],'transitions':transitions,
                      'cycle_end':name=='verify'})
    return {'schema_version':1,'id':'repair-demo','goal':'Repair the requested calculation within scope',
            'entry':'intake','limits':{'max_steps':8,'max_cycles':2},'fact_keys':['more'],
            'boundaries':['Only approved fixture files may change'],'steps':steps}


class ResumeCliTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.project=Path(self.temp.name)
        for name,contents in {'authority.txt':'Only local calc.py may change',
            'request.txt':'Return x+1','calc.py':'def calc(x): return x-1\n',
            'check.py':'from calc import calc\nassert calc(2)==3\n'}.items():
            (self.project/name).write_text(contents)
        self.document=graph();self.save('graph.json',self.document)

    def save(self,name,value):
        (self.project/name).write_text(json.dumps(value),encoding='utf-8')

    def cli(self,command,state=None,ok=True,**kwargs):
        args=[sys.executable,'-I','-B',str(HELPER),command,'--file',str(self.project/'graph.json')]
        if state is not None:self.save('state.json',state);args+=['--state',str(self.project/'state.json')]
        for key,value in kwargs.items():args+=['--'+key.replace('_','-'),str(value)]
        result=subprocess.run(args,cwd=self.project,capture_output=True,text=True,timeout=15)
        if ok:self.assertEqual(result.returncode,0,result.stderr)
        else:self.assertNotEqual(result.returncode,0)
        return json.loads(result.stdout) if ok else result

    def tracked(self):
        return self.cli('start',project=self.project,facts='{"more":false}')

    def record(self,state,status='PASS'):
        return self.cli('record',state,project=self.project,status=status,evidence='Observed fixture check')

    def test_real_failing_check_repair_verify_stop(self):
        state=self.record(self.tracked())
        self.assertEqual(self.cli('select',state)['skills'],['loop-debug'])
        before=subprocess.run([sys.executable,'-B','check.py'],cwd=self.project,capture_output=True)
        self.assertNotEqual(before.returncode,0)
        state=self.record(state,'FAIL');self.assertEqual(state['step'],'repair')
        (self.project/'calc.py').write_text('def calc(x): return x+1\n')
        state=self.record(state)
        checked=subprocess.run([sys.executable,'-B','check.py'],cwd=self.project,capture_output=True)
        self.assertEqual(checked.returncode,0,checked.stderr)
        done=self.record(state);self.assertEqual(done['status'],'DONE')
        self.assertEqual(done['steps_completed'],4)
        self.cli('select',done,ok=False)

    def test_changed_requirement_rewinds_affected_suffix_without_budget_refund(self):
        state=self.record(self.record(self.tracked()))
        self.assertEqual(state['step'],'verify')
        same=self.cli('resume',state,project=self.project)
        self.assertEqual(same['step'],'verify');self.assertEqual(same['records'],state['records'])
        (self.project/'request.txt').write_text('Return x+2')
        self.cli('record',state,project=self.project,status='PASS',evidence='stale',ok=False)
        resumed=self.cli('resume',state,project=self.project)
        self.assertEqual(resumed['step'],'repair')
        self.assertEqual(resumed['steps_completed'],2)
        self.assertEqual(len(resumed['records']),1)
        self.assertEqual(resumed['invalidations'][-1]['records'],state['records'][1:])
        self.assertEqual(resumed['resume']['changed_sources'],['request.txt'])

    def test_legacy_cannot_claim_source_freshness_and_resume_requires_tracking(self):
        legacy=self.cli('start',facts='{"more":false}')
        legacy=self.cli('advance',legacy,status='PASS',evidence='intake observed')
        (self.project/'authority.txt').write_text('Changed scope')
        # Legacy selection still works: deliberately preserved compatibility, not evidence freshness.
        self.assertEqual(self.cli('select',legacy)['step'],'repair')
        error=self.cli('resume',legacy,project=self.project,ok=False)
        self.assertIn('tracked',error.stderr)

    def test_conflict_stops_and_bounds_are_not_refunded(self):
        state=self.tracked();before=(self.project/'calc.py').read_bytes()
        stopped=self.record(state,'BLOCKED');self.assertEqual(stopped['status'],'STOP')
        self.assertEqual(before,(self.project/'calc.py').read_bytes())
        state=self.record(self.tracked())
        for _ in range(7):
            state=self.record(state,'FAIL')
            if state['status']=='STOP':break
        self.assertEqual(state['last']['reason'],'MAX_STEPS')
        self.assertEqual(state['steps_completed'],8)

    def test_changed_graph_missing_source_and_corrupt_records_fail_closed(self):
        state=self.record(self.tracked())
        changed=copy.deepcopy(self.document);changed['goal']='Changed goal';self.save('graph.json',changed)
        self.cli('resume',state,project=self.project,ok=False)
        self.save('graph.json',self.document)
        (self.project/'authority.txt').unlink()
        self.cli('resume',state,project=self.project,ok=False)
        (self.project/'authority.txt').write_text('restored')
        state['records'][0]['source_sha256']={}
        self.cli('resume',state,project=self.project,ok=False)

    def test_stopped_checkpoint_cannot_reopen_after_source_change(self):
        state=self.record(self.record(self.tracked()),'BLOCKED')
        (self.project/'authority.txt').write_text('Changed authority; needs human review')
        resumed=self.cli('resume',state,project=self.project)
        self.assertEqual(resumed['status'],'STOP')
        self.assertEqual(resumed['steps_completed'],2)
        self.assertEqual(len(resumed['invalidations'][-1]['records']),2)

    def test_unknown_tracking_and_advance_bypass_are_rejected(self):
        state=self.tracked();state['tracking_version']=True
        self.cli('resume',state,project=self.project,ok=False)
        self.cli('advance',self.tracked(),status='PASS',evidence='bypass',ok=False)

    def test_record_observation_is_not_aliased_by_current_fact_or_last_mutation(self):
        from scripts.workflow_setup import tracked_start,record
        state=record(self.document,tracked_start(self.document,{'more':False}),self.project,'PASS','observed')
        state['facts']['more']=True
        state['last']['evidence']='caller edited current display'
        self.assertEqual(state['records'][-1]['after']['facts'],{'more':False})
        self.assertEqual(state['records'][-1]['after']['last']['evidence'],'observed')

    def test_malformed_tracking_and_refunded_invalidated_budget_are_rejected(self):
        state=self.record(self.record(self.tracked()))
        (self.project/'request.txt').write_text('Return x+2')
        resumed=self.cli('resume',state,project=self.project)
        for damaged in ({**resumed,'steps_completed':1}, {**resumed,'extra':True},
                        {**resumed,'status':'ACTIVE','step':'DONE'},
                        {**resumed,'invalidations':[{'reason':'unknown','records':[]}]}):
            self.cli('resume',damaged,project=self.project,ok=False)


if __name__=='__main__':unittest.main()
