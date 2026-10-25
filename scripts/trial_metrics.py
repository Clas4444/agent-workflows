#!/usr/bin/env python3
"""Score declared repeated-trial outcomes without running models or tools."""
import argparse
from collections import Counter
import json
from pathlib import Path

if __package__:
    from .validation.json_data import loads_json
else:
    from validation.json_data import loads_json

STATUSES=('PASS','FAIL','BLOCKED','NOT_RUN')


def score_trials(data):
    if not isinstance(data,dict) or set(data)!= {'expected_cases','trials_per_case','trials'}:
        raise ValueError('expected expected_cases, trials_per_case and trials')
    ids=data['expected_cases']; k=data['trials_per_case']; trials=data['trials']
    if (not isinstance(ids,list) or not ids or not all(isinstance(v,str) and v.strip() for v in ids)
            or len(ids)!=len(set(ids))):
        raise ValueError('expected_cases must be unique nonempty strings')
    if type(k) is not int or k<1:
        raise ValueError('trials_per_case must be a positive integer')
    if not isinstance(trials,dict) or set(trials)!=set(ids):
        raise ValueError('trials must cover exactly the declared cases')
    rows=[]; counts=Counter({status:0 for status in STATUSES})
    for name in ids:
        outcomes=trials[name]
        if (not isinstance(outcomes,list) or len(outcomes)!=k
                or any(not isinstance(v,str) or v not in STATUSES for v in outcomes)):
            raise ValueError(f'{name} needs exactly {k} recognized outcomes; retain missing trials as NOT_RUN')
        counts.update(outcomes)
        rows.append({'id':name,'outcomes':outcomes,'any_pass': 'PASS' in outcomes,
                     'all_pass':all(v=='PASS' for v in outcomes)})
    any_count=sum(row['any_pass'] for row in rows)
    all_count=sum(row['all_pass'] for row in rows)
    return {'scope':'Observed finite trial counts only; not a pass^k estimator or an independence claim.',
            'cases':len(ids),'trials_per_case':k,'declared_attempts':len(ids)*k,
            'status_counts':dict(counts),'any_pass_cases':any_count,'all_pass_cases':all_count,
            'observed_any_pass_fraction':any_count/len(ids),'observed_all_pass_fraction':all_count/len(ids),
            'per_case':rows}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    args=parser.parse_args()
    try:
        result=score_trials(loads_json(args.input.read_text(encoding='utf-8')))
    except (OSError,ValueError) as exc:
        print(json.dumps({'status':'FAIL','error':str(exc)},ensure_ascii=True))
        return 1
    print(json.dumps(result,ensure_ascii=True,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
