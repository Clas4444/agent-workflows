"""Separate Codex office pilot: 12 serial calls, frozen before execution; no Copilot retries."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import time

if not __package__:sys.path.insert(0,str(Path(__file__).resolve().parent))
if __package__:
    from .empirical_audit import read,write,sha
    from .empirical_cases import fixtures,oracle,grade,controls
    from .empirical_pilot import prompt,exclusive,now,snapshot
    from .workflow_cost import inspect_call
else:
    from empirical_audit import read,write,sha
    from empirical_cases import fixtures,oracle,grade,controls
    from empirical_pilot import prompt,exclusive,now,snapshot
    from workflow_cost import inspect_call

ROOT=Path(__file__).resolve().parents[1]
SOURCES=('codex_office_pilot.py','empirical_cases.py','empirical_audit.py','empirical_pilot.py','workflow_cost.py','workflow_cost_cases.py')
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
    protocol={'campaign':'codex-office-20261103','frozen_at':now(),'provider':'Codex CLI configured OpenAI service',
              'cli_version':version,'cli_sha256':sha(Path(cli)),'model_requested':'gpt-6.1-sol','reasoning':'low',
              'max_cli':12,'schedule':old['schedule'],'seed':old['seed'],'fixtures':old['fixtures'],
              'skill_text':old['skill_text'],'skill_sha256':old['skill_sha256'],'controls':checks,
              'source_hashes':{n:sha(ROOT/'scripts'/n) for n in SOURCES},'config_overrides':OVERRIDES,
              'timeout_seconds':150,'preflight':{'leak_checks':leaks,'prompt_sha256':sha(folder/'preflight.json'),
              'scope':'Model-visible debug input only; generic Codex skill boilerplate remains. No candidate catalog, source or ancestor instructions observed. Not an OS trace.'},
              'method':'New provider campaign, single-shot fresh ephemeral workspaces, auth retained with --ignore-user-config. No changes to home or global skills; no Copilot marker cleared.',
              'hypothesis':old['hypothesis'],'primary':old['primary'],'secondary':old['secondary'],
              'analysis':'Report each case/arm and all attempts. Tokens=input+output, cache subset. No general superiority from n=2. Do not pool with Copilot.',
              'stop':'Serial max12, reserve before call. Stop on transport/auth/quota/accounting failure using campaign-local marker; never retry uncertain attempts.',
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
                if not marker.exists():exclusive(marker,{'reason':'incomplete_reservation','attempt':item['id']})
                break
            if marker.exists():break
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
            events=[]
            for line in (attempt/'events.jsonl').read_text(encoding='utf-8').splitlines():
                try:events.append(json.loads(line))
                except ValueError:pass
            models=sorted({e['model'] for e in events if isinstance(e.get('model'),str)})
            status='BLOCKED_ENVIRONMENT' if observed['status']=='BLOCKED' else 'PASS' if observed['status']=='PASS' and all(business.values()) and integrity else 'FAIL'
            row={'cohort':'NEW_CODEX','campaign':p['campaign'],**item,'status':status,'started_at':started,'finished_at':now(),
                 'seconds':seconds,'cli_count':1,'completed_turns':sum(e.get('type')=='turn.completed' for e in events),
                 'internal_model_requests':None,'actual_models':models or 'NOT_REPORTED','requested_model':p['model_requested'],
                 'usage':observed['usage'],'checks':{**observed['checks'],**business,'file_integrity':integrity},
                 'raw_hashes':observed['raw_hashes'],'candidate':answer}
            exclusive(attempt/'result.json',row);rows.append(row);write(folder/'observations.json',rows)
            print(json.dumps({k:row[k] for k in ('id','status','seconds','usage')}),flush=True)
            if status=='BLOCKED_ENVIRONMENT':
                exclusive(marker,{'reason':'transport_auth_quota_or_accounting_failure','attempt':item['id']});break
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
