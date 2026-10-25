"""Synthetic inputs and task definitions; does not execute submissions."""
import json
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

def snapshot(folder: Path) -> dict[str, bytes]:
    return {path.name:path.read_bytes() for path in folder.iterdir() if path.is_file()}
