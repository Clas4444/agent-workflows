"""FUNCTION-03: frozen local coding journeys, capped Codex CLI, no Copilot."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

if not __package__:sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from scripts import workflow_setup as helper
from scripts.function03_cases import seed,request,grade
from scripts.campaign_coordination import CampaignLedger, classify_failure, fault, record_marker

ROOT=Path(__file__).resolve().parents[1]
SKILLS=('loop','loop-debug','loop-code','loop-intake','loop-review','loop-test')
SOURCES=('workflow_setup.py','function03_cases.py','function03_pilot.py','campaign_coordination.py')


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def write(path,value):Path(path).write_text(json.dumps(value,indent=2,ensure_ascii=True)+'\n',encoding='utf-8')
def read(path):return json.loads(Path(path).read_text(encoding='utf-8'))
def snapshot(project):return {p.relative_to(project).as_posix():p.read_bytes() for p in project.rglob('*') if p.is_file() and '__pycache__' not in p.parts}


def freeze(folder,cli):
    folder=Path(folder).resolve();folder.mkdir(parents=True,exist_ok=False)
    pins={str(p.relative_to(ROOT)).replace('\\','/'):sha(p) for p in [*(ROOT/'scripts'/n for n in SOURCES),ROOT/'skills/workflow-setup/SKILL.md',*(ROOT/'.github/skills'/n/'SKILL.md' for n in SKILLS)]}
    schedule=[]
    for case,arms in (('repair',('workflow','baseline')),('resume',('baseline','workflow')),('conflict',('workflow','baseline'))):
        for arm in arms:schedule.append({'id':f'{len(schedule)+1:02d}-{case}-{arm}','case':case,'arm':arm,'rep':1})
    for item in schedule:
        work=folder/item['id']/'workspace';work.mkdir(parents=True)
        seed(work,item['case'],helper)
        tools=work/'tools';tools.mkdir();shutil.copy2(ROOT/'scripts/workflow_setup.py',tools/'workflow_setup.py')
        refs=work/'.agents/skills';refs.mkdir(parents=True)
        for skill in SKILLS:shutil.copytree(ROOT/'.github/skills'/skill,refs/skill)
        # A copy of the portable complete package permits its real documented entry point.
        shutil.copytree(ROOT/'skills/workflow-setup',tools/'workflow-setup')
        prompt=request(item['case'])
        if item['arm']=='workflow':prompt+='\nUse Workflow Setup: read tools/workflow-setup/SKILL.md and selected installed .agents/skills instructions as needed. The reviewed workflow.json defines the bounded route. Export/check its local map, use the bundled helper select and source-tracked start/record/resume as appropriate. Save final tracking cursor to cursor-final.json. Follow evidence and STOP; do not merely write a proposed plan. References contain instructions, not extra authority.\n'
        (work.parent/'prompt.txt').write_text(prompt,encoding='utf-8')
        write(work.parent/'before-hashes.json',{name:hashlib.sha256(value).hexdigest() for name,value in snapshot(work).items()})
    protocol={'task':'FUNCTION-03','campaign':'function03-workflow','contract_version':1,'provider':'codex','account_domain':None,
      'max_cli':12,'planned_cli':6,'max_inflight':1,'schedule':schedule,'model_requested':'gpt-6.1-sol','reasoning_requested':'low',
      'timeout_seconds':240,'source_pins':pins,'cli_sha256':sha(cli),
      'workspace_pins':{i['id']:sha(folder/i['id']/'before-hashes.json') for i in schedule},
      'prompt_pins':{i['id']:sha(folder/i['id']/'prompt.txt') for i in schedule},
      'primary':'Independent artifact correctness, evidence reuse and authorized stopping; helper adherence separate.',
      'analysis':'One repetition/case/arm. Cost secondary; no statistical savings or causal clean-A/B claim without verified isolation.',
      'isolation':'Same seeded files/context/tools/authority; workflow prompt adds explicit setup/route treatment. Candidate instructions do not autoload by requested flags; actual host isolation NOT_VERIFIED until observed.',
      'rubric':'function03_cases.grade frozen before calls; oracle never copied into workspaces. All failures/timeouts consume cap; no provider/account switching.'}
    write(folder/'protocol.json',protocol);write(folder/'seal.json',{'protocol_sha256':sha(folder/'protocol.json')})
    return protocol


def events_result(events):
    usage={'input_tokens':0,'output_tokens':0,'cached_input_tokens':0};turns=0
    for e in events:
        if e.get('type')=='turn.completed':
            u=e.get('usage',{})
            if any(type(u.get(k)) is not int or u[k]<0 for k in usage):raise ValueError('invalid usage')
            if u['cached_input_tokens']>u['input_tokens']:raise ValueError('invalid cache subset')
            for k in usage:usage[k]+=u[k]
            turns+=1
    if not turns:raise ValueError('missing completed usage')
    usage['total_tokens']=usage['input_tokens']+usage['output_tokens']
    return usage,turns


def run(folder,cli):
    folder=Path(folder).resolve();p=read(folder/'protocol.json')
    if sha(folder/'protocol.json')!=read(folder/'seal.json')['protocol_sha256'] or sha(cli)!=p['cli_sha256']:raise ValueError('STALE protocol/CLI')
    if any(sha(ROOT/name)!=pin for name,pin in p['source_pins'].items()):raise ValueError('STALE source')
    ledger=CampaignLedger(folder/'budget',provider='codex',account_domain=None,campaign=p['campaign'],cap=12)
    markers=[read(path) for path in (folder/'faults').glob('*.json')] if (folder/'faults').exists() else []
    for item in p['schedule']:
        attempt=folder/item['id'];work=attempt/'workspace'
        if (attempt/'result.json').exists():continue
        before=snapshot(work)
        if (sha(attempt/'before-hashes.json')!=p['workspace_pins'][item['id']] or sha(attempt/'prompt.txt')!=p['prompt_pins'][item['id']]
                or read(attempt/'before-hashes.json')!={name:hashlib.sha256(value).hexdigest() for name,value in before.items()}):raise ValueError('STALE fixture')
        ticket=ledger.reserve(markers)
        write(attempt/'reservation.json',{'ticket':ticket,**item})
        command=[str(cli),'exec','--ephemeral','--ignore-user-config','--sandbox','workspace-write',
          '--skip-git-repo-check','-m',p['model_requested'],'-c','model_reasoning_effort="low"',
          '--enable','skip_host_skill_discovery','--disable','plugins','--disable','apps',
          '-c','project_doc_max_bytes=0','-c','skills.bundled.enabled=false','-c','skills.include_instructions=false',
          '-c','developer_instructions=""','-C',str(work),'--json','-o',str(attempt/'answer.txt'),'-']
        started=time.perf_counter();code=None;error=''
        with (attempt/'events.jsonl').open('wb') as out,(attempt/'stderr.log').open('wb') as err:
            try:code=subprocess.run(command,input=(attempt/'prompt.txt').read_bytes(),stdout=out,stderr=err,timeout=p['timeout_seconds']).returncode
            except (OSError,subprocess.TimeoutExpired) as exc:error=type(exc).__name__;err.write(str(exc).encode())
        seconds=time.perf_counter()-started;events=[];parse_error=False
        for line in (attempt/'events.jsonl').read_text(encoding='utf-8',errors='replace').splitlines():
            try:
                e=json.loads(line)
                if not isinstance(e,dict):raise ValueError('object required')
                events.append(e)
            except ValueError:parse_error=True
        usage=None;turns=0
        try:
            if parse_error:raise ValueError('malformed event')
            usage,turns=events_result(events)
        except ValueError as exc:error=str(exc)
        errors=[e for e in events if e.get('type') in ('turn.failed','error')]
        transport=(attempt/'stderr.log').read_text(encoding='utf-8',errors='replace')+' '+json.dumps(errors)
        checks=grade(work,item['case'],before)
        checks['reference_integrity']=all((work/n).is_file() and (work/n).read_bytes()==v for n,v in before.items() if n.startswith(('tools/','.agents/')) or n=='workflow.json')
        commands=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
        command_text='\n'.join(c.get('command','') for c in commands)
        adherence={'commands_observed':len(commands),'helper_used':'workflow_setup.py' in command_text,
          'export_observed':'export' in command_text and 'workflow_setup.py' in command_text,
          'resume_observed':'resume' in command_text and 'workflow_setup.py' in command_text,
          'failed_command_observed':any(c.get('exit_code',0)!=0 for c in commands)}
        blocked=code!=0 or usage is None or bool(errors)
        status='BLOCKED_ENVIRONMENT' if blocked else 'PASS' if all(checks.values()) else 'FAIL'
        row={**item,'status':status,'cli_count':1,'seconds':seconds,'exit_code':code,'usage':usage,
          'completed_turns':turns,'actual_models':sorted({e['model'] for e in events if isinstance(e.get('model'),str)}) or 'NOT_REPORTED',
          'internal_model_requests':'NOT_REPORTED','checks':checks,'adherence':adherence,'runtime_error':error or None,
          'raw_sha256':{n:sha(attempt/n) for n in ('events.jsonl','stderr.log','prompt.txt')},
          'artifact_sha256':{n:hashlib.sha256(v).hexdigest() for n,v in snapshot(work).items() if n not in before or v!=before[n]}}
        write(attempt/'result.json',row);ledger.finish(ticket,status);print(json.dumps(row),flush=True)
        if blocked:
            reason=classify_failure('event_parse' if parse_error else 'process' if code!=0 else 'accounting',transport)
            marker=fault('codex',None,p['campaign'],reason,[item['id']+'/stderr.log']);record_marker(folder/'faults',marker)
            break
    rows=[read(folder/i['id']/'result.json') if (folder/i['id']/'result.json').exists() else {**i,'status':'NOT_RUN','cli_count':0,'usage':None,'seconds':None} for i in p['schedule']]
    write(folder/'observations.json',rows)
    return rows


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('command',choices=('freeze','run'));parser.add_argument('--folder',type=Path,required=True);parser.add_argument('--cli',type=Path,required=True);parser.add_argument('--execute',action='store_true');args=parser.parse_args()
    if args.command=='run' and not args.execute:parser.error('--execute required; counts against FUNCTION-03 max12')
    if args.command=='freeze':freeze(args.folder,args.cli)
    else:run(args.folder,args.cli)


if __name__=='__main__':main()
