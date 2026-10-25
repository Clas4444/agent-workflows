"""Independent artifact checks and bounded subprocess probes."""
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path
from .fixtures import RECORDS,RUBRIC

if '.' in __package__:
    from ..validation.json_data import loads_json
else:
    from validation.json_data import loads_json

def command(folder: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable,'-B',*args],cwd=folder,capture_output=True,text=True,
                          encoding='utf-8',errors='replace',timeout=15)

def verification_directory(folder: Path, label: str) -> Path:
    number=1
    while True:
        path=folder/(label if number==1 else f'{label}-{number}')
        try:
            path.mkdir()
            return path
        except FileExistsError:
            number+=1

def metrics_match(actual, expected):
    return (isinstance(actual,dict) and all(isinstance(actual.get(group),dict)
        and all(type(actual[group].get(key)) is int and actual[group][key]==value
                for key,value in values.items()) for group,values in expected.items()))


def grade(folder: Path, skill: str, original: dict[str, bytes]) -> dict[str, bool]:
    checks={}
    submitted_names={'loop-code':('calc.py',),'loop-migrate':('migrate.py',),
                     'loop-test-e2e':('test_e2e.py',),'loop-evaluate':('evaluate.py',)}.get(skill,())
    submitted_before={}
    try:
        submitted_before={name:(folder/name).read_bytes() for name in submitted_names}
        checks['source_preserved']=(folder/'calc.py').read_bytes()==original['calc.py']
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
            state=loads_json((folder/'state.json').read_text(encoding='utf-8'))
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
            expected_manifest=loads_json(original['manifest.json'])
            expected_lock=loads_json(original['lock.json'])
            approved=loads_json(original['metadata.json'])['fixture-lib']['approved']
            expected_manifest['dependencies']['fixture-lib']=approved
            expected_lock['packages']['fixture-lib']=approved
            checks['independent_approved_versions']=(loads_json((folder/'manifest.json').read_text(encoding='utf-8'))==expected_manifest
                and loads_json((folder/'lock.json').read_text(encoding='utf-8'))==expected_lock)
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
            checks['migration_invariants']=migrated.returncode==0 and loads_json(target.read_text(encoding='utf-8'))==expected
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
                checks[f'journey_{a}_{b}']=result.returncode==0 and loads_json(result.stdout)=={'sum':a+b}
            for args in [('oops','3'),('2',)]:
                result=command(folder,'app.py',*args)
                checks['invalid_'+'_'.join(args)]=result.returncode==2 and bool(result.stderr) and not result.stdout.strip()
            checks['no_side_effect']=(folder/'sentinel.txt').read_bytes()==original['sentinel.txt']
        elif skill == 'loop-evaluate':
            checks['inputs_preserved']=all((folder/name).read_bytes()==original[name] for name in ('cases.json','baseline.json','candidate.json'))
            checks['scorer_runs']=command(folder,'evaluate.py').returncode==0
            metrics=loads_json((folder/'metrics.json').read_text(encoding='utf-8'))
            expected={'baseline':{'total':6,'correct':4,'false_positive':1,'false_negative':1,'blocked':1,'not_run':1},
                      'candidate':{'total':6,'correct':6,'false_positive':0,'false_negative':0,'blocked':1,'not_run':1}}
            checks['fixed_rubric_metrics']=metrics_match(metrics,expected)
            # Perturb outputs in a separate directory to reject a scorer that
            # merely hardcodes the published example totals.
            challenge=verification_directory(folder,'independent-evaluation')
            shutil.copy2(folder/'evaluate.py',challenge/'evaluate.py')
            (challenge/'cases.json').write_text(json.dumps(RUBRIC), encoding='utf-8')
            (challenge/'baseline.json').write_text(json.dumps({case['id']:'FAIL' for case in RUBRIC}), encoding='utf-8')
            (challenge/'candidate.json').write_text(json.dumps({case['id']:'PASS' for case in RUBRIC}), encoding='utf-8')
            run=command(challenge,'evaluate.py')
            (challenge/'scorer-execution.log').write_text(run.stdout+run.stderr,encoding='utf-8')
            varied=loads_json((challenge/'metrics.json').read_text(encoding='utf-8'))
            varied_expected={'baseline':{'total':6,'correct':2,'false_positive':0,'false_negative':2,'blocked':0,'not_run':0},
                             'candidate':{'total':6,'correct':2,'false_positive':4,'false_negative':0,'blocked':0,'not_run':0}}
            checks['perturbed_outputs_scored']=run.returncode==0 and metrics_match(varied,varied_expected)
    except (OSError,ValueError,KeyError,TypeError,subprocess.TimeoutExpired):
        checks['artifact_verification']=False
    # Submitted programs may modify protected inputs during their verification.
    allowed={'loop-code':{'calc.py'},'loop-dependencies':{'manifest.json','lock.json'}}.get(skill,set())
    try:
        checks['protected_inputs_preserved_after_verification']=all(
            (folder/name).read_bytes()==value for name,value in original.items() if name not in allowed)
    except OSError:
        checks['protected_inputs_preserved_after_verification']=False
    if submitted_names:
        try:
            checks['submitted_artifacts_unchanged_during_verification']=(set(submitted_before)==set(submitted_names)
                and all((folder/name).read_bytes()==value for name,value in submitted_before.items()))
        except OSError:
            checks['submitted_artifacts_unchanged_during_verification']=False
    return checks
