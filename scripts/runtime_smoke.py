#!/usr/bin/env python3
"""Run explicitly authorized Codex fixture workflows; never invoked by CI."""
import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

if __package__:
    from .smoke_cases import NEW_SKILLS, SMOKE_SKILLS, TASKS, prepare, snapshot, grade
else:
    from smoke_cases import NEW_SKILLS, SMOKE_SKILLS, TASKS, prepare, snapshot, grade

def classify(returncode: int, log: str, response: dict) -> str:
    if 'usage limit' in log.lower() or 'rate limit' in log.lower():
        return 'BLOCKED'
    if returncode:
        return 'BLOCKED' if response.get('status')=='BLOCKED' else 'FAIL'
    status=response.get('status')
    return status if status in ('PASS','FAIL','BLOCKED','NOT_RUN') else 'FAIL'

def parse_response(text: str) -> dict:
    text=text.strip()
    if text.startswith('```'):
        text='\n'.join(text.splitlines()[1:-1])
    try:
        value=json.loads(text)
        return value if isinstance(value,dict) else {}
    except ValueError:
        return {}

def run_case(folder: Path, skill: str, skill_root: Path, codex: str, timeout: int) -> dict:
    instruction=(skill_root/skill/'SKILL.md').resolve()
    if not instruction.is_file():
        return {'skill':skill,'status':'BLOCKED','reason':'installed instruction missing','checks':{}}
    instruction_before=hashlib.sha256(instruction.read_bytes()).hexdigest()
    prepare(folder,skill); original=snapshot(folder)
    (folder/'input-hashes.json').write_text(json.dumps({name:hashlib.sha256(value).hexdigest() for name,value in original.items()},indent=2)+'\n', encoding='utf-8')
    prompt=f'''${skill}
Use the installed skill at {instruction}; read it explicitly if not already loaded.
Task: {TASKS[skill]}
This is an authorized disposable fixture. You may edit only inside this directory,
run local Python and write evidence.md. Do not edit global skills, change ACLs,
install dependencies, access network, authenticate, spawn agents/models, or commit/push.
Use ordinary retained directories, not tempfile, so external verification can read artifacts.
Python executable: {sys.executable}. Complete one useful batch within 120 seconds.
Record commands and actual results in evidence.md, not just a plan. Preserve failures.
Return only JSON: skill (exactly "{skill}"), status, loaded_skill_path, commands,
findings, limitations. A workflow PASS does not imply every external check ran.
'''
    (folder/'request.txt').write_text(prompt,encoding='utf-8')
    final=folder/'response.json'; log_path=folder/'execution.log'
    try:
        with log_path.open('wb') as log:
            result=subprocess.run([codex,'exec','--ephemeral','--sandbox','workspace-write','--skip-git-repo-check',
                                   '-C',str(folder),'-o',str(final),'-'],input=prompt.encode(),stdout=log,stderr=subprocess.STDOUT,timeout=timeout)
        returncode=result.returncode
    except subprocess.TimeoutExpired:
        return {'skill':skill,'status':'BLOCKED','reason':'outer timeout','folder':str(folder),'checks':{}}
    log=log_path.read_text(encoding='utf-8',errors='replace')
    response=parse_response(final.read_text(encoding='utf-8')) if final.exists() else {}
    status=classify(returncode,log,response)
    try:
        instruction_after=hashlib.sha256(instruction.read_bytes()).hexdigest()
    except OSError:
        instruction_after=None
    checks={'instruction_unchanged':instruction_before==instruction_after}
    if status=='PASS' and not checks['instruction_unchanged']:
        status='BLOCKED'
    elif status=='PASS':
        checks.update({'response_identity':response.get('skill')==skill,
                'installed_path':str(response.get('loaded_skill_path','')).replace('\\','/').lower()==str(instruction).replace('\\','/').lower(),
                'evidence_written':(folder/'evidence.md').is_file()})
        checks.update(grade(folder,skill,original))
        if not all(checks.values()):status='FAIL'
    row={'skill':skill,'status':status,'returncode':returncode,'folder':str(folder),'checks':checks,
         'quota_limited':'usage limit' in log.lower() or 'rate limit' in log.lower(),
         'instruction_sha256':instruction_before,
         'instruction_sha256_after':instruction_after,
         'response':response}
    if not checks['instruction_unchanged']:
        row['reason']='installed instruction changed or became unavailable during execution'
    (folder/'verified.json').write_text(json.dumps(row,indent=2)+'\n',encoding='utf-8')
    return row

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--allow-model-invocations',action='store_true',help='explicitly authorize account usage for these fixture tasks')
    parser.add_argument('--skill-root',type=Path,required=True)
    parser.add_argument('--output-dir',type=Path,required=True)
    parser.add_argument('--codex',default=shutil.which('codex'))
    parser.add_argument('--skills',nargs='+',choices=SMOKE_SKILLS,default=list(NEW_SKILLS))
    parser.add_argument('--timeout',type=int,default=180)
    args=parser.parse_args()
    if not args.allow_model_invocations:parser.error('model invocation authorization is required')
    if not args.codex:parser.error('Codex executable not found')
    if args.timeout<=0:parser.error('timeout must be positive')
    if len(set(args.skills))!=len(args.skills):parser.error('duplicate skill selection')
    output=args.output_dir.resolve()
    # Every run gets a fresh directory; never overwrite old evidence.
    try:output.mkdir(parents=True,exist_ok=False)
    except OSError as exc:parser.error(str(exc))
    rows=[];quota=False
    for skill in args.skills:
        if quota:
            row={'skill':skill,'status':'NOT_RUN','reason':'stopped after account usage limit','checks':{}}
        else:
            try:row=run_case(output/skill,skill,args.skill_root.resolve(),args.codex,args.timeout)
            except (OSError,ValueError) as exc:row={'skill':skill,'status':'BLOCKED','reason':str(exc),'checks':{}}
            quota=row.get('quota_limited',False)
        rows.append(row)
        summary={'recorded_at':datetime.now(timezone.utc).isoformat(),'results':rows}
        (output/'results.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
        print(json.dumps({'skill':skill,'status':row['status'],'failed':[key for key,value in row['checks'].items() if not value]}),flush=True)
    return 0 if rows and all(row['status']=='PASS' for row in rows) else 1

if __name__=='__main__':raise SystemExit(main())
