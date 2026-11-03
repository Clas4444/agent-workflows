"""COORD-02 read-only audit of the existing12 Codex traces. Never invokes a model."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time
if not __package__:sys.path.insert(0,str(Path(__file__).resolve().parent))
if __package__:
    from .empirical_audit import read,write,sha
    from .empirical_cases import oracle,same,grade
    from .empirical_pilot import prompt,snapshot
    from .codex_office_analysis import analyze_versioned,item_summary
    from .workflow_cost import inspect_call
else:
    from empirical_audit import read,write,sha
    from empirical_cases import oracle,same,grade
    from empirical_pilot import prompt,snapshot
    from codex_office_analysis import analyze_versioned,item_summary
    from workflow_cost import inspect_call

ROOT=Path(__file__).resolve().parents[1]


def audit(raw,packet,output):
    before=time.perf_counter();output.mkdir(parents=True,exist_ok=False)
    protocol=read(packet/'protocol.json');rows=read(packet/'observations.json')
    if sha(packet/'protocol.json')!=read(packet/'seal.json')['protocol_sha256']:raise ValueError('frozen protocol hash mismatch')
    if sha(packet/'measured-controller.py')!=protocol['source_hashes']['codex_office_pilot.py']:raise ValueError('measured controller hash mismatch')
    source_pins=[]
    for name,digest in protocol['source_hashes'].items():
        if name=='codex_office_pilot.py':source='measured-controller.py';matched=sha(packet/source)==digest
        else:
            source='base-git-object'
            blob=subprocess.check_output(['git','show','0b038de:scripts/'+name],cwd=ROOT)
            matched=hashlib.sha256(blob).hexdigest()==digest
        if not matched:raise ValueError('measured source pin mismatch: '+name)
        source_pins.append({'name':name,'measured_source':source,'measured_pin_matches':matched,
                            'current_canonical_matches':sha(ROOT/'scripts'/name)==digest})
    reports=[];threads=set()
    for row in rows:
        folder=raw/'attempts'/row['id']
        hashes={name:sha(folder/name)==digest for name,digest in row['raw_hashes'].items()}
        if not all(hashes.values()):raise ValueError('retained trace hash changed: '+row['id'])
        source=protocol['fixtures'][row['case']]
        expected_prompt=prompt(source,row['arm'],protocol['skill_text']).encode()
        if (folder/'prompt.txt').read_bytes()!=expected_prompt:raise ValueError('prompt differs from frozen fixture/arm')
        recorded_exit=0 if row['checks']['exit_zero'] else 1
        outcome,answer=inspect_call(folder,oracle(row['case'],source['source']),recorded_exit,row['seconds'])
        original='BLOCKED_ENVIRONMENT' if outcome['status']=='BLOCKED' else outcome['status']
        if original!=row['status'] or not same(answer,row['candidate']) or outcome['usage']!=row['usage']:
            raise ValueError('original output/usage/status differs: '+row['id'])
        for key,value in outcome['checks'].items():
            if row['checks'][key] is not value:raise ValueError('original check differs: '+key)
        events=[json.loads(line) for line in (folder/'events.jsonl').read_text(encoding='utf-8').splitlines()]
        messages=[e['item']['text'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message']
        if not messages or not same(json.loads(messages[-1]),answer):raise ValueError('candidate does not match final assistant message')
        if item_summary(events)!=row['items']:raise ValueError('sanitized item summary differs from raw events')
        completed=sum(e.get('type')=='turn.completed' for e in events)
        for event in events:
            if event.get('type')=='thread.started':threads.add(event['thread_id'])
        reports.append({'id':row['id'],'raw_hashes_match':True,'prompt_matches_frozen_fixture':True,
                        'original_status_reproduced':original,'candidate_matches_final_message':True,
                        'usage_matches':True,'completed_turns':completed,'workspace_still_empty':not snapshot(folder/'workspace'),
                        'exit_code_provenance':'recorded checks.exit_zero; integer process return code was not separately persisted'})
    result=analyze_versioned(rows,protocol,2)
    write(output/'regrade-v2.json',result)
    receipt={'repo':'agent-workflows','task':'COORD-02','delivery_policy':'NO_PUSH',
             'new_model_sessions':0,'historical_cli_checked':len(rows),'historical_distinct_threads':len(threads),
             'regrade_version':result['regrade_version'],'original_labels_immutable':True,
             'original_fail':sum(r['status']=='FAIL' for r in rows),
             'regraded_pass':sum(r['status_regraded']=='PASS' for r in result['observations']),
             'required_fields_pass':sum(r['required_fields_semantic'] for r in result['observations']),
             'source_pins':source_pins,'traces':reports,'pooled_workflow_vs_plain':result['pooled_workflow_vs_plain'],
             'offline_audit_seconds':time.perf_counter()-before,
             'scope':'Read-only historical trace reconciliation and versioned regrade; not a new experiment or proof of live combined semantics.'}
    write(output/'receipt.json',receipt);return receipt


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--raw',type=Path,required=True);p.add_argument('--packet',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();r=audit(a.raw,a.packet,a.output);print(json.dumps({k:r[k] for k in ('new_model_sessions','historical_cli_checked','original_fail','regraded_pass','required_fields_pass','pooled_workflow_vs_plain')}))


if __name__=='__main__':main()
