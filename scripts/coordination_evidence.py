"""Reproduce published COORD-02/FUNCTION-03 consistency checks; no model calls."""
import csv
import hashlib
import json
from pathlib import Path
import sys

if not __package__:sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from scripts.codex_office_analysis import analyze_versioned
from scripts.function03_pilot import events_result,reported_policy_stop

ROOT=Path(__file__).resolve().parents[1]


def verify(root=ROOT):
    packet=root/'docs/evidence/coordination-function-20261103'
    old=root/'docs/evidence/codex-office-20261103'
    def read(path):return json.loads(path.read_text(encoding='utf-8'))
    observed=read(packet/'coord02-regrade-v2.json')
    actual=analyze_versioned(read(old/'observations.json'),read(old/'protocol.json'),2)
    if actual!=observed:raise ValueError('historical v2 reproduction differs')
    protocol=read(packet/'function03-protocol.json');model=read(packet/'function03-model.json')
    events=read(packet/'function03-events-sanitized.json')['attempts']
    if hashlib.sha256((packet/'function03-measured-controller.py').read_bytes()).hexdigest()!=protocol['source_pins']['scripts/function03_pilot.py']:
        raise ValueError('measured controller archive differs')
    if hashlib.sha256((packet/'function03-measured-helper.py').read_bytes()).hexdigest()!=protocol['source_pins']['scripts/workflow_setup.py']:
        raise ValueError('measured helper archive differs')
    with (packet/'function03-model.csv').open(encoding='utf-8',newline='') as stream:table=list(csv.DictReader(stream))
    if len(table)!=len(model['observations']) or len(table)!=len(protocol['schedule']):raise ValueError('schedule/table mismatch')
    for row,record,slot in zip(table,model['observations'],protocol['schedule']):
        if row['id']!=slot['id'] or record['id']!=slot['id']:raise ValueError('slot order mismatch')
        for key,value in row.items():
            expected=record[key]
            if value!=('' if expected is None else str(expected)):raise ValueError('CSV differs: '+key)
        stream=events.get(row['id'],[])
        commands=[e for e in stream if e.get('item',{}).get('type')=='command_execution']
        if len(commands)!=record['executed_commands']:raise ValueError('command count differs')
        completed=[e for e in stream if e['type']=='turn.completed']
        if record['total_tokens'] is not None:
            usage,_=events_result(stream)
            if any(usage[k]!=record[k] for k in usage):raise ValueError('usage differs')
            for key in ('cache_write_input_tokens','reasoning_output_tokens'):
                if sum(e['usage'][key] for e in completed)!=record[key]:raise ValueError('subset counter differs')
            if not reported_policy_stop(stream,commands) or record['regrade_status']!='BLOCKED_ENVIRONMENT':raise ValueError('policy regrade differs')
        elif completed:raise ValueError('completed usage is missing from table')
    budget=read(packet/'function03-budget.json')
    consumed=sum(r['cli_count'] for r in model['observations'])
    if consumed!=budget['consumed'] or consumed!=len(budget['tickets']) or consumed>budget['max_cli']:
        raise ValueError('budget mismatch')
    return {'status':'PASS','scope':'Published-input consistency only; no execution attestation','historical_cli':len(actual['observations']),
            'new_reserved_cli':consumed,'new_completed_cli':sum(r['total_tokens'] is not None for r in model['observations']),
            'live_adherence':'NOT_VERIFIED','cost_comparison':'NOT_ELIGIBLE_PREREQUISITE_FAILED'}


if __name__=='__main__':print(json.dumps(verify(),indent=2))
