"""Separate Codex office pilot: 12 serial calls, frozen before execution; no Copilot retries."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time
import uuid

if not __package__:sys.path.insert(0,str(Path(__file__).resolve().parent))
if __package__:
    from .empirical_audit import read,write,sha
    from .empirical_cases import fixtures,oracle,grade,controls
    from .empirical_pilot import prompt,exclusive,now,snapshot
    from .workflow_cost import inspect_call
    from .codex_office_analysis import item_summary,no_tools,unexpected_error
    from .campaign_coordination import stop_file,fault,record_marker,classify_failure
else:
    from empirical_audit import read,write,sha
    from empirical_cases import fixtures,oracle,grade,controls
    from empirical_pilot import prompt,exclusive,now,snapshot
    from workflow_cost import inspect_call
    from codex_office_analysis import item_summary,no_tools,unexpected_error
    from campaign_coordination import stop_file,fault,record_marker,classify_failure

ROOT=Path(__file__).resolve().parents[1]
SOURCES=('codex_office_pilot.py','codex_office_analysis.py','empirical_cases.py','empirical_audit.py','empirical_pilot.py','workflow_cost.py','workflow_cost_cases.py','campaign_coordination.py')
OVERRIDES=['--enable','skip_host_skill_discovery','--disable','plugins','--disable','apps',
           '--disable','shell_tool','--disable','unified_exec','-c','project_doc_max_bytes=0',
           '-c','skills.bundled.enabled=false','-c','skills.include_instructions=false','-c','developer_instructions=""']


def isolation_checks(text):
    return {word:word not in text for word in ('loop-work','workflow-setup','agent-attention','AgentRepo','<skills_instructions>')}


def freeze(folder,cli):
    folder=folder.resolve();folder.mkdir(parents=True,exist_ok=False)
    old=read(ROOT/'docs/evidence/copilot-integrity-20261103/pilot-protocol.json')
    checks=controls()
    if not all(c['pass'] for c in checks):raise ValueError('oracle controls failed')
    work=folder/'preflight-workspace';work.mkdir()
    pre=subprocess.run([cli,'-C',str(work),*OVERRIDES,'debug','prompt-input','PREFLIGHT_ONLY_NO_MODEL'],capture_output=True,timeout=30)
    (folder/'preflight.json').write_bytes(pre.stdout);(folder/'preflight-stderr.log').write_bytes(pre.stderr)
    value=json.loads(pre.stdout);leaks=isolation_checks(json.dumps(value))
    if pre.returncode or not all(leaks.values()):raise ValueError('preflight leakage or startup failure')
    version=subprocess.check_output([cli,'--version'],text=True).strip()
    protocol={'campaign':'codex-office-'+uuid.uuid4().hex[:12],'frozen_at':now(),'provider':'Codex CLI configured OpenAI service',
              'cli_version':version,'cli_sha256':sha(Path(cli)),'model_requested':'gpt-6.1-sol','reasoning':'low',
              'max_cli':12,'schedule':old['schedule'],'seed':old['seed'],'fixtures':old['fixtures'],
              'skill_text':old['skill_text'],'skill_sha256':old['skill_sha256'],'controls':checks,
              'source_hashes':{n:sha(ROOT/'scripts'/n) for n in SOURCES},'config_overrides':OVERRIDES,
              'timeout_seconds':150,'preflight':{'leak_checks':leaks,'prompt_sha256':sha(folder/'preflight.json'),
              'scope':'Model-visible debug input only; generic Codex skill boilerplate remains. No candidate catalog, source or ancestor instructions observed. Not an OS trace.'},
              'method':'New provider campaign, single-shot fresh ephemeral workspaces, auth retained with --ignore-user-config. No changes to home or global skills; no Copilot marker cleared.',
              'hypothesis':old['hypothesis'],'primary':old['primary'],'secondary':old['secondary'],
              'analysis':'Report each case/arm and all attempts. Tokens=input+output, cache subset. No general superiority from n=2. Do not pool with Copilot.',
              'coordination_contract_version':1,
              'stop':'Serial max12, reserve before call. Campaign-local marker by default; contract1 faults distinguish local environment and provider/account quota. Unknown global domain pauses same-provider calls only when marker exchange is explicit. Never retry uncertain attempts or switch identity to evade a stop.',
              'actual_model':'Only if emitted by CLI events; otherwise NOT_REPORTED, never infer it from requested model.'}
    write(folder/'protocol.json',protocol);write(folder/'seal.json',{'protocol_sha256':sha(folder/'protocol.json')})
    return protocol


def pin(folder,cli):
    p=read(folder/'protocol.json')
    if sha(folder/'protocol.json')!=read(folder/'seal.json')['protocol_sha256']:raise ValueError('STALE protocol')
    if sha(Path(cli))!=p['cli_sha256']:raise ValueError('STALE CLI')
    if any(sha(ROOT/'scripts'/n)!=h for n,h in p['source_hashes'].items()):raise ValueError('STALE source')
    if sha(ROOT/'.github/skills/loop-work/SKILL.md')!=p['skill_sha256']:raise ValueError('STALE skill')
    return p


def run(folder,cli):
    folder=folder.resolve();p=pin(folder,cli);rows=[];marker=folder/'STOP-MODEL-CALLS.json'
    if p.get('max_cli',12)!=12 or len(p['schedule'])!=12 or len({r['id'] for r in p['schedule']})!=12:
        raise ValueError('schedule must contain exactly12 unique slots within the hard CLI budget')
    lock=folder/'active.lock';exclusive(lock,{'pid':'controller','at':now()})
    try:
        for item in p['schedule']:
            attempt=folder/'attempts'/item['id']
            if (attempt/'result.json').exists():
                row=read(attempt/'result.json');rows.append(row)
                if row['status']=='BLOCKED_ENVIRONMENT':break
                continue
            if attempt.exists():
                rows.append({'cohort':'NEW_CODEX','campaign':p['campaign'],**item,'status':'BLOCKED_ENVIRONMENT',
                             'cli_count':1,'seconds':None,'usage':None,'reason':'incomplete_reservation'})
                observation=fault('codex',None,p['campaign'],'process',['attempts/'+item['id']+'/reserved.json'])
                record_marker(folder/'faults',observation)
                if not marker.exists():exclusive(marker,observation)
                break
            if stop_file(marker,provider='codex',account_domain=None,campaign=p['campaign'])['blocked']:break
            attempt.mkdir(parents=True);exclusive(attempt/'reserved.json',{'at':now(),**item})
            work=attempt/'workspace';work.mkdir();before=snapshot(work)
            request=prompt(p['fixtures'][item['case']],item['arm'],p['skill_text'])
            (attempt/'prompt.txt').write_bytes(request.encode())
            command=[cli,'exec','--ephemeral','--ignore-user-config','--sandbox','read-only','--skip-git-repo-check',
                     '-m',p['model_requested'],'-c','model_reasoning_effort="low"',*OVERRIDES,
                     '-C',str(work),'--json','-o',str(attempt/'answer.json'),'-']
            started=now();clock=time.perf_counter();code=None
            with (attempt/'events.jsonl').open('wb') as out,(attempt/'stderr.log').open('wb') as err:
                try:code=subprocess.run(command,input=request.encode(),stdout=out,stderr=err,timeout=p['timeout_seconds']).returncode
                except (OSError,subprocess.TimeoutExpired) as exc:err.write(str(exc).encode())
            seconds=time.perf_counter()-clock
            observed,answer=inspect_call(attempt,oracle(item['case'],p['fixtures'][item['case']]['source']),code,seconds)
            business=grade(item['case'],p['fixtures'][item['case']]['source'],answer)
            integrity=before==snapshot(work)
            events=[];stream_parse_failure=False
            for line in (attempt/'events.jsonl').read_text(encoding='utf-8').splitlines():
                try:
                    event=json.loads(line)
                    if not isinstance(event,dict):raise ValueError('event must be an object')
                    events.append(event)
                except ValueError:stream_parse_failure=True
            models=sorted({e['model'] for e in events if isinstance(e.get('model'),str)})
            # CLI startup diagnostics are not tool invocations. Unknown errors still fail.
            observed['checks']['no_tools']=no_tools(item_summary(events))
            if unexpected_error(events):observed['status']='BLOCKED'
            if observed['status']!='BLOCKED':observed['status']='PASS' if all(observed['checks'].values()) else 'FAIL'
            status='BLOCKED_ENVIRONMENT' if observed['status']=='BLOCKED' else 'PASS' if observed['status']=='PASS' and all(business.values()) and integrity else 'FAIL'
            row={'cohort':'NEW_CODEX','campaign':p['campaign'],**item,'status':status,'started_at':started,'finished_at':now(),
                 'seconds':seconds,'cli_count':1,'completed_turns':sum(e.get('type')=='turn.completed' for e in events),
                 'internal_model_requests':None,'actual_models':models or 'NOT_REPORTED','requested_model':p['model_requested'],
                 'usage':observed['usage'],'checks':{**observed['checks'],**business,'file_integrity':integrity},
                 'raw_hashes':observed['raw_hashes'],'candidate':answer}
            exclusive(attempt/'result.json',row);rows.append(row);write(folder/'observations.json',rows)
            print(json.dumps({k:row[k] for k in ('id','status','seconds','usage')}),flush=True)
            if status=='BLOCKED_ENVIRONMENT':
                error_text=(attempt/'stderr.log').read_text(encoding='utf-8',errors='replace')+' '+json.dumps([e for e in events if e.get('type') in ('error','turn.failed') or e.get('item',{}).get('type')=='error'])
                observation=fault('codex',None,p['campaign'],classify_failure('event_parse' if stream_parse_failure else 'missing_or_invalid_accounting',error_text),['attempts/'+item['id']+'/stderr.log'])
                record_marker(folder/'faults',observation)
                if not marker.exists():exclusive(marker,observation)
                break
        done={r['id'] for r in rows}
        for item in p['schedule']:
            if item['id'] not in done:rows.append({'cohort':'NEW_CODEX','campaign':p['campaign'],**item,'status':'NOT_RUN','cli_count':0,'seconds':None,'usage':None})
        write(folder/'observations.json',rows)
        return rows
    finally:lock.unlink()


def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('mode',choices=('freeze','run'));a.add_argument('--output',type=Path,required=True)
    a.add_argument('--execute',action='store_true');args=a.parse_args();cli=shutil.which('codex')
    if not cli:a.error('Codex CLI unavailable')
    if args.mode=='freeze':freeze(args.output,cli)
    elif args.execute:run(args.output,cli)
    else:a.error('run requires --execute')


if __name__=='__main__':main()
