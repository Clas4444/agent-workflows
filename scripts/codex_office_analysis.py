"""Offline regrade of a Codex office pilot. Original labels are never overwritten."""
from collections import defaultdict
import argparse
import csv
import io
import json
from pathlib import Path
import statistics
import math
import sys
if not __package__:sys.path.insert(0,str(Path(__file__).resolve().parent))
if __package__:
    from .empirical_cases import oracle,same,grade
    from .empirical_audit import read,write
    from .empirical_figures import SVG,COLORS
else:
    from empirical_cases import oracle,same,grade
    from empirical_audit import read,write
    from empirical_figures import SVG,COLORS

WARNING='Under-development features enabled: skip_host_skill_discovery. Under-development features are incomplete and may behave unpredictably.'


def item_summary(events):
    result=[]
    for event in events:
        if event.get('type') not in ('item.started','item.completed'):continue
        item=event.get('item',{});kind=item.get('type')
        diagnostic=kind=='error' and item.get('message','').startswith(WARNING+' To suppress this warning, set `suppress_unstable_features_warning = true` in ')
        result.append({'type':kind,'recognized_feature_warning':diagnostic})
    return result


def no_tools(items):
    return all(i['type'] in ('agent_message','reasoning') or (i['type']=='error' and i.get('recognized_feature_warning') is True) for i in items)


def unexpected_error(events):
    return any(e.get('type') in ('error','turn.failed') for e in events) or any(i['type']=='error' and not i['recognized_feature_warning'] for i in item_summary(events))


def analyze(rows,protocol):
    if len(rows)!=12 or len({r['id'] for r in rows})!=12:raise ValueError('missing or duplicate planned slots')
    results=[]
    for row in rows:
        r=dict(row);checks=dict(r.get('checks',{}));checks['no_tools']=no_tools(r.get('items',[]))
        if r['status'] not in ('PASS','FAIL','BLOCKED_ENVIRONMENT','NOT_RUN'):raise ValueError('invalid status')
        expected=oracle(r['case'],protocol['fixtures'][r['case']]['source']);candidate=r.get('candidate')
        checks.update(grade(r['case'],protocol['fixtures'][r['case']]['source'],candidate));checks['expected_output']=same(candidate,expected)
        r['status_original']=r['status']
        r['checks_regraded']=checks
        r['status_regraded']=r['status'] if r['status'] in ('BLOCKED_ENVIRONMENT','NOT_RUN') else 'PASS' if checks and all(checks.values()) else 'FAIL'
        r['required_fields_semantic']=isinstance(candidate,dict) and all(k in candidate and same(candidate[k],v) for k,v in expected.items())
        r['extra_fields']=sorted(set(candidate or {})-set(expected)) if isinstance(candidate,dict) else []
        results.append(r)
    summary=[]
    for case in ('revision','authority'):
        for arm in ('plain','workflow','matched'):
            group=[r for r in results if r['case']==case and r['arm']==arm]
            if len(group)!=2:raise ValueError('missing case/arm repetition')
            measured=[r for r in group if r.get('usage')]
            summary.append({'case':case,'arm':arm,'planned':2,'cli_count':sum(r['cli_count'] for r in group),
                'original_pass':sum(r['status_original']=='PASS' for r in group),'regraded_pass':sum(r['status_regraded']=='PASS' for r in group),
                'required_fields_pass':sum(r['required_fields_semantic'] for r in group),
                'measured_n':len(measured),'mean_seconds':statistics.mean(r['seconds'] for r in measured) if measured else None,
                'mean_total_tokens':statistics.mean(r['usage']['input_tokens']+r['usage']['output_tokens'] for r in measured) if measured else None})
    comparisons=[]
    for case in ('revision','authority'):
        work=next(r for r in summary if r['case']==case and r['arm']=='workflow')
        for arm in ('plain','matched'):
            base=next(r for r in summary if r['case']==case and r['arm']==arm)
            eligible=work['regraded_pass']==base['regraded_pass']==2
            comparisons.append({'case':case,'baseline':arm,'eligible_equal_quality':eligible,
                'token_change_percent':100*(work['mean_total_tokens']/base['mean_total_tokens']-1) if eligible else None,
                'time_change_percent':100*(work['mean_seconds']/base['mean_seconds']-1) if eligible else None})
    work=[r for r in summary if r['arm']=='workflow'];base=[r for r in summary if r['arm']=='plain']
    eligible=all(r['regraded_pass']==2 for r in work+base)
    pooled={'method':'Ratio of means across two cases, two repeats each; no statistical superiority claim.',
            'baseline':'plain','eligible_equal_quality':eligible,
            'token_change_percent':100*(statistics.mean(r['mean_total_tokens'] for r in work)/statistics.mean(r['mean_total_tokens'] for r in base)-1) if eligible else None,
            'time_change_percent':100*(statistics.mean(r['mean_seconds'] for r in work)/statistics.mean(r['mean_seconds'] for r in base)-1) if eligible else None}
    return {'observations':results,'summary':summary,'comparisons':comparisons,'pooled_workflow_vs_plain':pooled,'scope':'Original FAIL labels preserved. Posthoc diagnostic repair changes no_tools only; extra-field schema failure retained. Required-fields semantics separate.'}


def analyze_versioned(rows,protocol,version=2):
    """v1 reproduces retained artifacts. v2 rejects missing telemetry/evidence.

    Sanitized telemetry is not an attestation; COORD-02 separately matches raw
    hashes and events. Never promote absent records into successful model runs.
    """
    if type(version) is not int or version not in (1,2):raise ValueError('unsupported regrade version')
    if version==1:return analyze(rows,protocol)
    expected={(r['id'],r['case'],r['arm'],r['rep']) for r in protocol['schedule']}
    actual={(r['id'],r['case'],r['arm'],r['rep']) for r in rows}
    if len(rows)!=12 or expected!=actual or len(actual)!=12:raise ValueError('records do not match frozen schedule')
    required={'exit_zero','expected_output','file_integrity','functional','jsonl_valid','no_tools','one_usage_event','policy','usage_valid'}
    for row in rows:
        if type(row['rep']) is not int or type(row['cli_count']) is not int:raise ValueError('repetition/CLI counters must be integers, not booleans')
        if row['status']=='NOT_RUN':
            if row['cli_count']!=0 or row['usage'] is not None or row['seconds'] is not None:raise ValueError('NOT_RUN cannot contain measured usage/time')
            continue
        if row['status']=='BLOCKED_ENVIRONMENT':continue
        if row['cli_count']!=1 or type(row['seconds']) not in (int,float) or not math.isfinite(row['seconds']) or row['seconds']<0:raise ValueError('invalid CLI/time counter')
        checks=row.get('checks',{})
        if not required<=set(checks) or any(type(checks[k]) is not bool for k in required):raise ValueError('missing typed acceptance checks')
        usage=row.get('usage')
        if not isinstance(usage,dict) or any(type(usage.get(k)) is not int or usage[k]<0 for k in ('input_tokens','output_tokens','cached_input_tokens')):raise ValueError('missing or malformed usage')
        if usage['cached_input_tokens']>usage['input_tokens']:raise ValueError('cache exceeds input')
        if 'cache_write_input_tokens' in usage and (type(usage['cache_write_input_tokens']) is not int or usage['cache_write_input_tokens']<0 or usage['cached_input_tokens']+usage['cache_write_input_tokens']>usage['input_tokens']):raise ValueError('invalid cache-write subset')
        if 'reasoning_output_tokens' in usage and (type(usage['reasoning_output_tokens']) is not int or not 0<=usage['reasoning_output_tokens']<=usage['output_tokens']):raise ValueError('invalid reasoning subset')
        items=row.get('items')
        if not isinstance(items,list) or any(not isinstance(i,dict) for i in items) or not any(i.get('type')=='agent_message' for i in items):raise ValueError('missing final assistant evidence')
        if any(i.get('type')=='error' and not i.get('recognized_feature_warning') for i in items):raise ValueError('unclassified runtime error needs review')
    result=analyze(rows,protocol)
    result['regrade_version']='codex-office-v2-coord02'
    result['input_validation']='PASS: frozen roster, typed counters/checks, assistant evidence; raw provenance checked separately'
    return result


def render(data,output):
    output.mkdir(parents=True,exist_ok=True);write(output/'analysis.json',data)
    stream=io.StringIO(newline='');w=csv.DictWriter(stream,fieldnames=list(data['summary'][0]),lineterminator='\n');w.writeheader();w.writerows(data['summary'])
    (output/'summary.csv').write_bytes(stream.getvalue().encode())
    for field,title,limit in [('seconds','Elapsed wall seconds per package',16),('total_tokens','Total input + output tokens per package',16000)]:
        chart=SVG('New Codex pilot: '+title,'Two independent repetitions per case/arm; 12 CLI. Separate from historical Copilot. Descriptive only, not a learning curve.')
        for panel,case in enumerate(('revision','authority')):
            left=110+panel*710;top=180;width=470;height=400
            chart.text(left,125,case,22,weight='bold')
            for t in range(5):
                y=top+height-height*t/4;chart.line(left,y,left+width,y);chart.text(left-15,y+5,f'{limit*t/4:,.0f}',14,anchor='end')
            for rep in (1,2):chart.text(left+(rep-1)*width,top+height+32,rep,16,anchor='middle')
            for arm in ('plain','workflow','matched'):
                group=sorted([r for r in data['observations'] if r['case']==case and r['arm']==arm],key=lambda r:r['rep'])
                pts=[]
                for r in group:
                    if not r.get('usage'):continue
                    value=r['seconds'] if field=='seconds' else r['usage']['input_tokens']+r['usage']['output_tokens']
                    pts.append((left+(r['rep']-1)*width,top+height-value/limit*height))
                chart.parts.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in pts)+f'" fill="none" stroke="{COLORS[arm]}" stroke-width="3"/>')
                for x,y in pts:chart.dot(x,y,COLORS[arm],5)
            chart.text(left+width/2,top+height+75,'Independent repetition',17,anchor='middle')
        for i,arm in enumerate(('plain','workflow','matched')):
            x=100+i*440;chart.rect(x,749,30,4,COLORS[arm]);chart.text(x+42,760,{'plain':'Idea-complete plain prompt','workflow':'Agent Workflows','matched':'Information-matched prompt'}[arm],17)
        quality='; '.join(f"{arm}: {sum(r['regraded_pass'] for r in data['summary'] if r['arm']==arm)}/4" for arm in ('plain','workflow','matched'))
        chart.text(52,840,'Strict quality after diagnostic correction: '+quality+'.',15)
        chart.text(52,875,f"Original FAIL labels retained: {sum(r['status_original']=='FAIL' for r in data['observations'])}/12; diagnostic correction is separate. See analysis.json.",14)
        chart.save(output/('codex-office-seconds.svg' if field=='seconds' else 'codex-office-tokens.svg'))
    chart=SVG('New Codex pilot: quality and cost by case/arm','n=2 per arm/case. Strict schema and required-fields semantics remain separate; original labels retained.')
    for panel,case in enumerate(('revision','authority')):
        left=70+panel*710;top=160;chart.text(left,top,case,22,weight='bold')
        for i,row in enumerate([r for r in data['summary'] if r['case']==case]):
            y=top+70+i*155;chart.text(left,y,row['arm'],18)
            chart.rect(left,y+20,490,25,'#e3e9e7');chart.rect(left,y+20,490*row['regraded_pass']/2,25,COLORS[row['arm']])
            chart.text(left+505,y+40,f"{row['regraded_pass']}/2",16)
            tokens=f"{row['mean_total_tokens']:,.1f}" if row['mean_total_tokens'] is not None else 'NOT_RUN'
            seconds=f"{row['mean_seconds']:.3f}" if row['mean_seconds'] is not None else 'NOT_RUN'
            chart.text(left,y+80,f"Required fields: {row['required_fields_pass']}/2; mean tokens {tokens}; mean seconds {seconds}",15)
    extras=sum(bool(r['extra_fields']) for r in data['observations'])
    chart.text(52,800,f'Answers with extra output fields: {extras}. Strict schema and required-field semantics are shown separately.',15)
    chart.text(52,840,'No average savings claim across unequal-quality arms. Cache is a subset of input, and backend request count is not reported.',15)
    chart.save(output/'codex-office-quality.svg')
    chart=SVG('New Codex pilot: coverage and scoring layers','All planned slots retained. Completed CLI turns are not an independently reported backend model-request count.')
    n=len(data['observations'])
    for i,(label,passed) in enumerate((('Original strict checker',sum(r['status_original']=='PASS' for r in data['observations'])),
                                     ('Diagnostic-corrected strict checker',sum(r['status_regraded']=='PASS' for r in data['observations'])),
                                     ('Required business fields only',sum(r['required_fields_semantic'] for r in data['observations'])))):
        y=165+i*190;chart.text(70,y,label,22,weight='bold');chart.rect(70,y+30,1200,60,'#9b3f4b')
        if passed:chart.rect(70,y+30,1200*passed/n,60,'#127d79')
        chart.text(70,y+125,f'PASS {passed}/{n}; non-PASS {n-passed}/{n}',18)
    completed=sum(r.get('completed_turns',0) for r in data['observations']);calls=sum(r['cli_count'] for r in data['observations'])
    chart.text(70,790,f'CLI attempts: {calls}/12. Completed turns: {completed}. Remaining authorized calls: {12-calls}.',20)
    chart.text(70,835,'Original failures remain visible. Diagnostic correction does not hide extra-field schema violations.',16)
    chart.save(output/'codex-office-coverage.svg')


def main():
    a=argparse.ArgumentParser(description=__doc__);a.add_argument('--packet',type=Path,required=True);a.add_argument('--output',type=Path,required=True)
    a.add_argument('--regrade-version',type=int,choices=(1,2),default=1,help='v1 retains published reproduction; v2 validates the full frozen roster and telemetry')
    args=a.parse_args()
    if args.regrade_version==1:
        print('NOTE: legacy v1 reproduces retained artifacts; use --regrade-version 2 for strict telemetry validation.',file=sys.stderr)
    render(analyze_versioned(read(args.packet/'observations.json'),read(args.packet/'protocol.json'),args.regrade_version),args.output)


if __name__=='__main__':main()
