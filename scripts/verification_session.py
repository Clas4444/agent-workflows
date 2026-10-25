#!/usr/bin/env python3
"""Run repository gates with a session ID and before/after verification-input pin."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys

if __package__:
    from .validation.json_data import loads_json
else:
    from validation.json_data import loads_json

COMMANDS = (
    ('unit', ('-m','unittest','discover','-s','tests','-v')),
    ('full', ('scripts/validate.py',)),
    ('format', ('-m','scripts.validate','--profile','format')),
    ('catalog', ('scripts/catalog.py',)),
    ('routing', ('scripts/routing_check.py',)),
    ('workflows', ('scripts/workflows.py',)),
    ('bundles', ('scripts/install_skills.py','--list')),
    ('install-diagnosis', ('scripts/doctor_skills.py','--all','--target','.github/skills')),
    ('resources', ('scripts/skill_resources.py',)),
    ('published-evidence', ('scripts/evidence_indexes.py',)),
    ('sync', ('scripts/sync_skills.py','--target','.github/skills','--check')),
    ('smoke-interface', ('scripts/runtime_smoke.py','--help')),
    ('compile', ('-m','compileall','-q','scripts','tests')),
)
ROOTS = ('.github/skills','.agents/skills','.claude/skills','scripts','tests','schemas',
         '.github/workflows','docs/evidence','docs/guides','docs/assets')
FILES = ('skills-manifest.json','skill-groups.json','skill-routing.json','workflow-presets.json',
         'skill-bundles.json','README.md','AGENTS.md','CONTRIBUTING.md','.gitattributes',
         'skill-resources.json',
         'docs/SKILL-USAGE.md','docs/RUNTIME-TEST-MATRIX.md','docs/PROCESS-LIFECYCLE.md')


def utc_now():
    return datetime.now(timezone.utc).isoformat()


def input_snapshot(repo):
    paths = {repo/name for name in FILES if (repo/name).is_file()}
    for name in ROOTS:
        paths.update(path for path in (repo/name).rglob('*') if path.is_file()
                     and '__pycache__' not in path.relative_to(repo).parts
                     and path.suffix != '.pyc')
    return {path.relative_to(repo).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
            for path in sorted(paths)}


def fingerprint(snapshot):
    raw = json.dumps(snapshot,sort_keys=True,separators=(',',':')).encode('utf-8')
    return hashlib.sha256(raw).hexdigest()


def git_context(repo):
    try:
        top = subprocess.run(['git','-C',str(repo),'rev-parse','--show-toplevel'],capture_output=True,
                             text=True,encoding='utf-8',errors='replace',timeout=15)
        if top.returncode!=0 or Path(top.stdout.strip()).resolve()!=repo.resolve():
            return {'head_at_start':None,'dirty_at_start':None}
        head = subprocess.run(['git','-C',str(repo),'rev-parse','HEAD'],capture_output=True,
                              text=True,encoding='utf-8',errors='replace',timeout=15)
        dirty = subprocess.run(['git','-C',str(repo),'status','--porcelain'],capture_output=True,
                               text=True,encoding='utf-8',errors='replace',timeout=15)
        return {'head_at_start':head.stdout.strip() if head.returncode==0 else None,
                'dirty_at_start':bool(dirty.stdout.strip()) if dirty.returncode==0 else None}
    except (OSError,subprocess.TimeoutExpired):
        return {'head_at_start':None,'dirty_at_start':None}


def run_session(repo, output, session_id, execute=None):
    execute = execute or subprocess.run
    # A new directory preserves failed runs and prevents accidental result reuse.
    output.mkdir(parents=True,exist_ok=False)
    before = input_snapshot(repo)
    report = {'session_id':session_id,'started_at':utc_now(),'python':sys.version.split()[0],
              'platform':sys.platform,'git':git_context(repo),
              'input_scope':{'roots':list(ROOTS),'files':list(FILES)},
              'inputs':before,'input_fingerprint':fingerprint(before),'checks':[]}
    for key, args in COMMANDS:
        started = utc_now()
        try:
            result = execute([sys.executable,*args],cwd=repo,capture_output=True,text=True,
                             encoding='utf-8',errors='replace',timeout=240)
            text = result.stdout+result.stderr
            code = result.returncode
        except (OSError,subprocess.TimeoutExpired) as exc:
            text = str(exc)
            code = None
        log = output/(key+'.log')
        log.write_text(text,encoding='utf-8')
        row = {'id':key,'command':['python',*args],'started_at':started,'finished_at':utc_now(),
               'exit_code':code,'status':'PASS' if code==0 else 'FAIL',
               'log_sha256':hashlib.sha256(log.read_bytes()).hexdigest()}
        if key=='unit':
            counts = re.findall(r'^Ran (\d+) tests? in ',text,re.MULTILINE)
            summaries = re.findall(r'^(?:OK|FAILED)(?: \([^\n]*\))?\s*$',text,re.MULTILINE)
            summary = summaries[-1] if summaries else ''
            skip = re.search(r'skipped=(\d+)',summary)
            row['discovered'] = int(counts[-1]) if counts else None
            row['skipped'] = int(skip.group(1)) if skip else 0
            if not row['discovered'] or not summary.startswith('OK'):
                row['status'] = 'FAIL'
        report['checks'].append(row)
    after = input_snapshot(repo)
    report.update({'finished_at':utc_now(),'inputs_unchanged':before==after,
                   'after_fingerprint':fingerprint(after)})
    report['status'] = ('STALE' if before!=after else
                        'PASS' if all(row['status']=='PASS' for row in report['checks']) else 'FAIL')
    (output/'verification.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    return report


def verify_report(repo, path, session_id):
    report = loads_json(path.read_text(encoding='utf-8'))
    errors = []
    if report.get('session_id') != session_id:
        errors.append('session ID does not match the requested session')
    current = input_snapshot(repo)
    if report.get('inputs') != current or report.get('input_fingerprint') != fingerprint(current):
        errors.append('verification inputs changed; the result is stale for this checkout')
    if report.get('input_scope') != {'roots':list(ROOTS),'files':list(FILES)}:
        errors.append('verification input scope differs')
    if report.get('after_fingerprint') != fingerprint(current):
        errors.append('post-run input pin differs')
    checks = report.get('checks')
    if (not isinstance(checks,list) or len(checks)!=len(COMMANDS)
            or any(not isinstance(row,dict) or row.get('id')!=key
                   or row.get('command')!=['python',*args] or row.get('exit_code')!=0
                   or row.get('status')!='PASS'
                   for row,(key,args) in zip(checks or [],COMMANDS))):
        errors.append('all fixed gates must have successful recorded outcomes')
    if isinstance(checks,list) and checks and isinstance(checks[0],dict):
        unit = checks[0]
        count, skipped = unit.get('discovered'), unit.get('skipped')
        if (type(count) is not int or count<=0 or type(skipped) is not int
                or not 0<=skipped<=count):
            errors.append('unit test counts must include a real non-empty discovery')
    if report.get('status')!='PASS' or report.get('inputs_unchanged') is not True:
        errors.append('the campaign did not finish PASS with unchanged inputs')
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[1])
    parser.add_argument('--session',required=True)
    modes = parser.add_mutually_exclusive_group(required=True)
    modes.add_argument('--output',type=Path,help='New raw-evidence directory, normally under .loop')
    modes.add_argument('--verify',type=Path,help='Verify session identity, input pin and gate coverage')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._-]{0,99}',args.session):
        parser.error('--session must be an identifier of at most 100 letters, digits, dots, underscores or hyphens')
    try:
        if args.verify:
            errors = verify_report(args.repo.resolve(),args.verify,args.session)
            print('\n'.join(errors) if errors else 'PASS: session and verification inputs match')
            return int(bool(errors))
        report = run_session(args.repo.resolve(),args.output.resolve(),args.session)
        print(json.dumps({k:report[k] for k in ('session_id','status','input_fingerprint','inputs_unchanged')}))
        return int(report['status']!='PASS')
    except (OSError,ValueError,KeyError,TypeError,AttributeError) as exc:
        parser.exit(1,f'FAIL: {exc}\n')


if __name__ == '__main__':
    raise SystemExit(main())
