"""Disposable acceptance fixtures for the 1.2 workflow additions."""
import json
import shutil
import re
import subprocess
import sys
from pathlib import Path

NEW_SKILLS = ('loop-plan', 'loop-dependencies', 'loop-migrate', 'loop-test-e2e', 'loop-evaluate')
REGRESSION_SKILLS = ('loop-review','loop-code','loop-prompt')
SMOKE_SKILLS = NEW_SKILLS + REGRESSION_SKILLS
CALC = 'def add(a, b):\n    return a + b\n'
RECORDS = {'schema': 1, 'records': [{'id': 1, 'name': 'Ada'}, {'id': 2, 'name': 'Lin'}]}
RUBRIC = [{'id': name, 'expected': status} for name, status in
          [('p1','PASS'),('p2','PASS'),('n1','FAIL'),('n2','FAIL'),('b1','BLOCKED'),('u1','NOT_RUN')]]
BASELINE = {'p1':'PASS','p2':'FAIL','n1':'PASS','n2':'FAIL','b1':'BLOCKED','u1':'NOT_RUN'}
CANDIDATE = {case['id']:case['expected'] for case in RUBRIC}
TASKS = {
    'loop-review': 'Review calc.py and run test_calc.py. Identify the concrete off-by-one defect, exact expected/actual values and source location in evidence.md. Do not edit source or assertions. No explicit duration is required beyond completing this bounded review.',
    'loop-code': 'Repair calc.add to return the mathematical sum. Run the unchanged test_calc.py baseline first, then minimally fix calc.py and verify passing tests. User already authorizes this exact behavior change; do not ask for permission again. Do not alter the tests.',
    'loop-prompt': 'Explicit /loop-prompt 1: verify local protocol steps. Use the installed skill bundled scripts/run_loop.py with --follow-up-count 1 --self-prompt --timeout-seconds 5, --state-file state.json and --report-file report.md. The explicitly authorized child command is the provided Python executable followed by fake_agent.py in this fixture. No more model calls. Verify two invocations, distinct NEXT_PROMPT values and a terminal iteration limit.',
    'loop-plan': 'Inspect calc.py. Plan adding a JSON-export CLI; do not implement it. Write plan.md with acceptance criteria, out-of-scope items, dependency-ordered batches, verification commands and rollback. Source must remain unchanged.',
    'loop-dependencies': 'In this synthetic local JSON lockfile format, manifest.json dependencies and lock.json packages both map names to exact version strings (no resolver hashes). Approved change: fixture-lib 1.0.0 to 1.1.0; metadata.json records MIT/Python 3.11 compatibility. Update only this dependency in both files, save original manifest bytes in manifest.before.json, run check_dependency.py. Do not install or contact registries. Record rollback and that live advisory checks were NOT_RUN.',
    'loop-migrate': 'Implement migrate.py with CLI: python migrate.py records.json [--dry-run | --rollback]. Migrate schema 1 records id/name to schema 2 id/label, preserving ids/values/order. Validate before writes. --dry-run never writes. Actual migration creates byte-identical records.json.bak only once, repeated migration is idempotent, --rollback restores backup. Reject malformed records without changing input/backup. Demonstrate dry-run, migration, repeated run and rollback on these local disposable fixtures. Leave records.json restored after your demonstration.',
    'loop-test-e2e': 'Use actual app.py entry point for the complete CLI journey. Create test_e2e.py using unittest and subprocess with timeouts. Cover sum success, negative/zero inputs, bad integer and missing argument; verify JSON/exit/error and no sentinel changes. Run the suite. Do not modify app.py or sentinel.txt.',
    'loop-evaluate': 'Read fixed cases.json, baseline.json and candidate.json. Do not edit these inputs or run new models. Implement evaluate.py runnable with no arguments, reading these files and writing metrics.json. It must work in a fresh directory containing only the script and these three inputs; no pre-existing evidence.md/report may be required. For baseline and candidate output total, correct, false_positive (unexpected PASS), false_negative (expected PASS but other status), blocked and not_run counts from actual outputs. Write the rubric before grading and preserve per-case outcomes in evidence.md. Include blocked/not-run cases in the 6-case denominator; do not discard them.',
}

def prepare(folder: Path, skill: str) -> None:
    """Require a fresh directory; never overwrite another attempt."""
    if skill not in SMOKE_SKILLS:
        raise ValueError(f'unknown smoke case: {skill}')
    folder.mkdir(parents=True, exist_ok=False)
    (folder/'calc.py').write_text(CALC, encoding='utf-8')
    if skill in ('loop-review','loop-code'):
        (folder/'calc.py').write_text('def add(a, b):\n    return a + b + 1\n', encoding='utf-8')
        (folder/'test_calc.py').write_text("import unittest\nfrom calc import add\nclass Tests(unittest.TestCase):\n    def test_positive(self): self.assertEqual(add(2,3),5)\n    def test_zero(self): self.assertEqual(add(0,0),0)\n    def test_negative(self): self.assertEqual(add(-2,-3),-5)\n", encoding='utf-8')
    if skill == 'loop-prompt':
        (folder/'fake_agent.py').write_text("import sys\nfrom pathlib import Path\nsys.stdin.read(); p=Path('counter.txt'); n=int(p.read_text())+1 if p.exists() else 1; p.write_text(str(n)); print(f'local step {n}'); print(f'NEXT_PROMPT: verify local step {n+1}'); print('LOOP_STATUS: PASS')\n", encoding='utf-8')
    if skill == 'loop-dependencies':
        for name, value in {'manifest.json':{'dependencies':{'fixture-lib':'1.0.0','keep-lib':'2.0.0'}},
                            'lock.json':{'packages':{'fixture-lib':'1.0.0','keep-lib':'2.0.0'}},
                            'metadata.json':{'fixture-lib':{'approved':'1.1.0','license':'MIT','python':'3.11'}}}.items():
            (folder/name).write_text(json.dumps(value,indent=2)+'\n', encoding='utf-8')
        (folder/'check_dependency.py').write_text("import json\nfrom pathlib import Path\na=json.loads(Path('manifest.json').read_text())['dependencies']; b=json.loads(Path('lock.json').read_text())['packages']; assert a == b == {'fixture-lib':'1.1.0','keep-lib':'2.0.0'}; print('DEPENDENCIES_PASS')\n", encoding='utf-8')
    if skill == 'loop-migrate':
        (folder/'records.json').write_text(json.dumps(RECORDS,indent=2)+'\n', encoding='utf-8')
    if skill == 'loop-test-e2e':
        (folder/'app.py').write_text("import argparse,json\np=argparse.ArgumentParser(); p.add_argument('a',type=int); p.add_argument('b',type=int); a=p.parse_args(); print(json.dumps({'sum':a.a+a.b}))\n", encoding='utf-8')
        (folder/'sentinel.txt').write_text('must remain unchanged\n', encoding='utf-8')
    if skill == 'loop-evaluate':
        for name,value in [('cases.json',RUBRIC),('baseline.json',BASELINE),('candidate.json',CANDIDATE)]:
            (folder/name).write_text(json.dumps(value,indent=2)+'\n', encoding='utf-8')

def command(folder: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable,'-B',*args],cwd=folder,capture_output=True,text=True,
                          encoding='utf-8',errors='replace',timeout=15)

def snapshot(folder: Path) -> dict[str, bytes]:
    return {path.name:path.read_bytes() for path in folder.iterdir() if path.is_file()}

def verification_directory(folder: Path, label: str) -> Path:
    number=1
    while True:
        path=folder/(label if number==1 else f'{label}-{number}')
        try:
            path.mkdir()
            return path
        except FileExistsError:
            number+=1

def grade(folder: Path, skill: str, original: dict[str, bytes]) -> dict[str, bool]:
    checks={'source_preserved':(folder/'calc.py').read_bytes()==original['calc.py']}
    try:
        if skill == 'loop-code':
            checks.pop('source_preserved')
            checks['source_changed']=(folder/'calc.py').read_bytes()!=original['calc.py']
            checks['tests_preserved']=(folder/'test_calc.py').read_bytes()==original['test_calc.py']
            checks['regression_tests_pass']=command(folder,'-m','unittest','-v').returncode==0
        elif skill == 'loop-review':
            text=(folder/'evidence.md').read_text(encoding='utf-8').lower()
            checks['finding_evidence']=all(term in text for term in ('calc.py','6','5'))
            checks['failing_baseline']=command(folder,'-m','unittest','-v').returncode!=0
            checks['tests_preserved']=(folder/'test_calc.py').read_bytes()==original['test_calc.py']
        elif skill == 'loop-prompt':
            state=json.loads((folder/'state.json').read_text(encoding='utf-8'))
            iterations=state.get('iterations',[])
            prompts=[re.search(r'^NEXT_PROMPT:\s*(.+)$',item.get('output',''),re.M) for item in iterations]
            checks['two_invocations']=state.get('prompt_count')==2 and len(iterations)==2
            checks['successful_children']=state.get('final_status')=='PASS' and all(item.get('returncode')==0 and item.get('status')=='PASS' for item in iterations)
            checks['distinct_next_prompts']=all(prompts) and len({p.group(1) for p in prompts if p})==2
            checks['child_fixture_preserved']=(folder/'fake_agent.py').read_bytes()==original['fake_agent.py']
        elif skill == 'loop-plan':
            text=(folder/'plan.md').read_text(encoding='utf-8').lower()
            checks['plan_contract']=(all(term in text for term in ('acceptance','batch','verif','rollback'))
                                     and bool(re.search(r'\bout[-\s]+of[-\s]+scope\b',text)))
            checks['no_implementation']=not (folder/'app.py').exists()
        elif skill == 'loop-dependencies':
            checks['checker_preserved']=(folder/'check_dependency.py').read_bytes()==original['check_dependency.py']
            expected_manifest=json.loads(original['manifest.json'])
            expected_lock=json.loads(original['lock.json'])
            approved=json.loads(original['metadata.json'])['fixture-lib']['approved']
            expected_manifest['dependencies']['fixture-lib']=approved
            expected_lock['packages']['fixture-lib']=approved
            checks['independent_approved_versions']=(json.loads((folder/'manifest.json').read_text(encoding='utf-8'))==expected_manifest
                and json.loads((folder/'lock.json').read_text(encoding='utf-8'))==expected_lock)
            checks['consistent_approved_versions']=(checks['checker_preserved']
                and command(folder,'check_dependency.py').returncode==0)
            checks['backup_exact']=(folder/'manifest.before.json').read_bytes()==original['manifest.json']
            checks['metadata_preserved']=(folder/'metadata.json').read_bytes()==original['metadata.json']
        elif skill == 'loop-migrate':
            checks['demonstration_restored_source']=(folder/'records.json').read_bytes()==original['records.json']
            # Exercise independently on new inputs, not the agent's self-report.
            verify=verification_directory(folder,'independent-migration')
            target=verify/'input.json'; target.write_bytes(original['records.json'])
            script=str((folder/'migrate.py').resolve()); path=str(target.resolve())
            checks['dry_run']=command(folder,script,path,'--dry-run').returncode==0 and target.read_bytes()==original['records.json'] and not target.with_suffix('.json.bak').exists()
            migrated=command(folder,script,path)
            expected={'schema':2,'records':[{'id':r['id'],'label':r['name']} for r in RECORDS['records']]}
            checks['migration_invariants']=migrated.returncode==0 and json.loads(target.read_text(encoding='utf-8'))==expected
            first=target.read_bytes(); backup=target.with_suffix('.json.bak')
            checks['backup_exact']=backup.read_bytes()==original['records.json']
            checks['idempotence']=command(folder,script,path).returncode==0 and target.read_bytes()==first and backup.read_bytes()==original['records.json']
            checks['rollback']=command(folder,script,path,'--rollback').returncode==0 and target.read_bytes()==original['records.json']
            target.write_text('{"schema":1,"records":[{"id":1}]}', encoding='utf-8')
            invalid=target.read_bytes(); old_backup=backup.read_bytes()
            checks['invalid_input_no_write']=command(folder,script,path).returncode!=0 and target.read_bytes()==invalid and backup.read_bytes()==old_backup
        elif skill == 'loop-test-e2e':
            checks['entrypoint_preserved']=(folder/'app.py').read_bytes()==original['app.py']
            suite=command(folder,'-m','unittest','discover','-p','test_e2e.py','-v')
            count=re.search(r'(?m)^Ran ([0-9]+) tests?\b',suite.stdout+'\n'+suite.stderr)
            checks['agent_suite']=(suite.returncode==0 and (folder/'test_e2e.py').exists()
                                   and count is not None and int(count.group(1))>0)
            # A passing suite can still contain only assertTrue(True). Challenge
            # the submitted tests on isolated mutants, without changing its inputs.
            mutants={
                'wrong_sum':"import argparse,json\np=argparse.ArgumentParser(); p.add_argument('a',type=int); p.add_argument('b',type=int); a=p.parse_args(); print(json.dumps({'sum':a.a+a.b+1}))\n",
                'accepts_invalid':"import json,sys\ntry:\n    a,b=map(int,sys.argv[1:]); total=a+b\nexcept ValueError:\n    total=0\nprint(json.dumps({'sum':total}))\n",
            }
            for label,mutant in mutants.items():
                rejected=False
                if checks['agent_suite']:
                    challenge=verification_directory(folder,'independent-e2e-'+label)
                    shutil.copy2(folder/'test_e2e.py',challenge/'test_e2e.py')
                    (challenge/'app.py').write_text(mutant,encoding='utf-8')
                    (challenge/'calc.py').write_bytes(original['calc.py'])
                    (challenge/'sentinel.txt').write_bytes(original['sentinel.txt'])
                    challenged=command(challenge,'-m','unittest','discover','-p','test_e2e.py','-v')
                    (challenge/'suite-execution.log').write_text(challenged.stdout+challenged.stderr,encoding='utf-8')
                    rejected=challenged.returncode!=0 and 'AssertionError' in challenged.stdout+challenged.stderr
                checks['suite_rejects_'+label]=rejected
            for a,b in [(2,3),(0,0),(-2,-3)]:
                result=command(folder,'app.py',str(a),str(b))
                checks[f'journey_{a}_{b}']=result.returncode==0 and json.loads(result.stdout)=={'sum':a+b}
            for args in [('oops','3'),('2',)]:
                result=command(folder,'app.py',*args)
                checks['invalid_'+'_'.join(args)]=result.returncode==2 and bool(result.stderr) and not result.stdout.strip()
            checks['no_side_effect']=(folder/'sentinel.txt').read_bytes()==original['sentinel.txt']
        elif skill == 'loop-evaluate':
            checks['inputs_preserved']=all((folder/name).read_bytes()==original[name] for name in ('cases.json','baseline.json','candidate.json'))
            checks['scorer_runs']=command(folder,'evaluate.py').returncode==0
            metrics=json.loads((folder/'metrics.json').read_text(encoding='utf-8'))
            expected={'baseline':{'total':6,'correct':4,'false_positive':1,'false_negative':1,'blocked':1,'not_run':1},
                      'candidate':{'total':6,'correct':6,'false_positive':0,'false_negative':0,'blocked':1,'not_run':1}}
            checks['fixed_rubric_metrics']=all(all(metrics[group].get(key)==value for key,value in expected[group].items()) for group in expected)
            # Perturb outputs in a separate directory to reject a scorer that
            # merely hardcodes the published example totals.
            challenge=verification_directory(folder,'independent-evaluation')
            shutil.copy2(folder/'evaluate.py',challenge/'evaluate.py')
            (challenge/'cases.json').write_text(json.dumps(RUBRIC), encoding='utf-8')
            (challenge/'baseline.json').write_text(json.dumps({case['id']:'FAIL' for case in RUBRIC}), encoding='utf-8')
            (challenge/'candidate.json').write_text(json.dumps({case['id']:'PASS' for case in RUBRIC}), encoding='utf-8')
            run=command(challenge,'evaluate.py')
            (challenge/'scorer-execution.log').write_text(run.stdout+run.stderr,encoding='utf-8')
            varied=json.loads((challenge/'metrics.json').read_text(encoding='utf-8'))
            checks['perturbed_outputs_scored']=run.returncode==0 and varied['baseline']['correct']==2 and varied['baseline']['false_negative']==2 and varied['candidate']['correct']==2 and varied['candidate']['false_positive']==4
    except (OSError,ValueError,KeyError,TypeError,subprocess.TimeoutExpired):
        checks['artifact_verification']=False
    return checks
