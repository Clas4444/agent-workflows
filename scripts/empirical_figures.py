"""Reproduce chart tables and standalone SVGs from sanitized observations only.

No plotting dependencies. Optional PNG rendering: node scripts/empirical_render.cjs DIR
with the standard sharp package available to Node. No source-report numbers hardcoded.
"""
import argparse
import csv
import io
import math
from pathlib import Path
import statistics
import sys
from xml.sax.saxutils import escape

if __package__:
    from .empirical_audit import aggregate, read, write, number
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from empirical_audit import aggregate, read, write, number

COLORS = {'workflow':'#127d79', 'manual':'#9b3f4b', 'idea':'#bc7b24', 'exhaustive':'#4554a0',
          'attention':'#2672a0', 'combined':'#734c94', 'plain':'#657783', 'matched':'#4554a0'}


def tables(historical, pilot):
    summary = aggregate(historical, expected_count=80)
    if len(pilot) != 12 or len({r['id'] for r in pilot}) != 12: raise ValueError('missing or duplicated pilot slots')
    runs = []
    for r in historical:
        calls = r['calls']
        for c in calls:
            if not number(c['seconds']): raise ValueError('invalid elapsed')
            u = c['usage']
            if any(type(u.get(k)) is not int or u[k] < 0 for k in ('input_tokens','output_tokens','total_tokens','cached_input_tokens')):
                raise ValueError('invalid chart usage')
            if u['total_tokens'] != u['input_tokens']+u['output_tokens']: raise ValueError('double-counted chart tokens')
        runs.append({k:r.get(k) for k in ('cohort','campaign','case','arm','rep','original_status','saved_functional_status','order_relaxed_revision','semantic_revision')} | {
            'cli_count':len(calls), 'seconds':math.fsum(c['seconds'] for c in calls),
            'input_tokens':sum(c['usage']['input_tokens'] for c in calls),
            'output_tokens':sum(c['usage']['output_tokens'] for c in calls),
            'total_tokens':sum(c['usage']['total_tokens'] for c in calls),
            'cached_input_tokens':sum(c['usage']['cached_input_tokens'] for c in calls),
            'cache_write_tokens':sum(c['usage']['cache_write_tokens'] for c in calls),
            'model_requests':sum(c['usage']['model_requests'] for c in calls)})
    return {'summary': summary, 'historical_runs': runs, 'pilot_slots': pilot,
            'units':'Tokens=input+output; cache is a subset, not additive. Time=CLI wall seconds. Historical packages are not new executions.'}


class SVG:
    def __init__(self, title, subtitle, width=1440, height=920):
        self.width=width; self.height=height
        self.parts=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
                    '<rect width="100%" height="100%" fill="#fafbf9"/>', '<g font-family="Arial, sans-serif" fill="#182a35">']
        self.text(52,48,title,26,weight='bold'); self.text(52,78,subtitle,15)
    def text(self,x,y,text,size=14,weight='normal',color='#182a35',anchor='start'):
        self.parts.append(f'<text x="{x}" y="{y}" font-size="{size}" font-weight="{weight}" fill="{color}" text-anchor="{anchor}">{escape(str(text))}</text>')
    def rect(self,x,y,w,h,color): self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{color}"/>')
    def line(self,x1,y1,x2,y2,color='#ced7da'):
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}"/>')
    def dot(self,x,y,color,r=5,kind='circle'):
        if kind=='circle': self.parts.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')
        else: self.parts.append(f'<path d="M {x} {y-r} L {x+r} {y+r} L {x-r} {y+r} Z" fill="{color}"/>')
    def save(self,path): path.write_bytes(('\n'.join(self.parts+['</g></svg>'])+'\n').encode())


def render(data, output):
    output.mkdir(parents=True,exist_ok=True); write(output/'chart-data.json', data)
    runs=data['historical_runs']; summary=data['summary']
    s=SVG('Historical acceptance: original labels and separate sensitivity layers',
          'Saved Copilot campaigns, n=5 per arm/case. These are descriptive records, not a clean causal A/B.')
    for panel,(campaign,case) in enumerate((('workflow','revision'),('combined','revision'),('combined','cents'))):
        top=125+panel*235; s.text(52,top,f'{campaign} / {case}',19,weight='bold')
        group=[r for r in summary if r['campaign']==campaign and r['case']==case]
        for i,r in enumerate(group):
            x=160+i*195; s.text(x,top+27,r['arm'],14)
            layers=[('original',r['original_pass'],'#364b60')]
            if campaign=='combined': layers.append(('saved functional',r['saved_functional_pass'],'#127d79'))
            if case=='revision': layers.append(('order sensitivity',r['order_relaxed_pass'],'#bc7b24'))
            if case=='revision': layers.append(('order + wrapper',r['semantic_pass'],'#734c94'))
            for j,(label,n,color) in enumerate(layers):
                y=top+45+j*40; s.rect(x,y,140,18,'#e3e9e7'); s.rect(x,y,140*n/r['n'],18,color)
                s.text(x+146,y+14,f"{n}/{r['n']}",13); s.text(x,y+33,label,11,color=color)
    s.text(52,875,'Separate sensitivities: ID order only; ID order + split-response wrapper. Saved cents functional is not a new regrade.',14)
    s.save(output/'acceptance.svg')

    s=SVG('Historical per-package resource use, all five repeats retained',
          'Workflow-only revision campaign. One package may contain multiple restarted CLI calls; cache is not added to total tokens.')
    groups=sorted({r['arm'] for r in runs if r['campaign']=='workflow'})
    rows=[r for r in runs if r['campaign']=='workflow']
    for panel,(field,title,limit) in enumerate((('total_tokens','Total tokens (input + output)',60000),('seconds','Elapsed wall seconds',40),('cached_input_tokens','Cache-read tokens (input subset)',30000))):
        top=135+panel*230; s.text(52,top,title,18,weight='bold')
        for tick in range(5):
            y=top+160-tick*35; s.line(145,y,1320,y); s.text(135,y+5,f'{limit*tick/4:,.0f}',12,anchor='end')
        for n,arm in enumerate(groups):
            x=300+n*290; group=[r for r in rows if r['arm']==arm]
            for r in group:
                xx=x+(r['rep']-3)*24; yy=top+160-r[field]/limit*140
                s.dot(xx,yy,COLORS[arm]); s.text(xx,yy-9,r['rep'],11,anchor='middle')
            s.text(x,top+185,arm,14,anchor='middle')
            if panel==0:s.text(x,top+205,f"{group[0]['cli_count']} CLI/package",12,anchor='middle')
    s.text(52,875,'Labels identify repeat 1–5. Per-run input/output/cache-write/CLI/internal-request counters are in historical-runs.csv.',14)
    s.save(output/'per-run.svg')

    s=SVG('Historical cost–quality: read each case and scoring layer separately',
          'Points are arm/case means, n=5. No billing currency conversion, uncertainty interval or general superiority claim.')
    for panel,(campaign,case,max_tokens) in enumerate((('workflow','revision',60000),('combined','revision',60000),('combined','cents',450000))):
        left=85+panel*470;top=185;width=350;height=470
        s.text(left,130,f'{campaign} / {case}',18,weight='bold')
        for t in range(6):
            x=left+t/5*width;s.line(x,top,x,top+height);s.text(x,top+height+28,f'{max_tokens*t/5/1000:.0f}k',12,anchor='middle')
            y=top+height-t/5*height;s.line(left,y,left+width,y);s.text(left-10,y+5,f'{t*20}%',12,anchor='end')
        group=[r for r in summary if r['campaign']==campaign and r['case']==case]
        for i,r in enumerate(group):
            x=left+r['mean_total_tokens']/max_tokens*width;y=top+height-r['original_pass']/r['n']*height
            color=COLORS[r['arm']];s.dot(x,y,color,6);s.text(x+6,y-12-(i%2)*16,i+1,12,color=color)
            s.text(left,750+i*22,f"{i+1}: {r['arm']}",13,color=color)
        s.text(left,top-25,'Original PASS rate',14);s.text(left+width/2,top+height+65,'Mean total tokens/package',14,anchor='middle')
    s.save(output/'cost-quality.svg')

    s=SVG('Coverage and missingness: historical records versus new pilot',
          'NOT_RUN is missing evidence, never zero measured cost. Historical and new planned denominators remain separate.')
    original_pass=sum(r['original_status']=='PASS' for r in runs)
    layers=[('Historical original labels, 80 packages',[(original_pass,'PASS','#127d79'),(len(runs)-original_pass,'FAIL','#9b3f4b')]),
            ('Historical combined saved functional, 60 packages',[(sum(r['saved_functional_pass'] for r in summary if r['campaign']=='combined'),'PASS','#127d79'),(60-sum(r['saved_functional_pass'] for r in summary if r['campaign']=='combined'),'FAIL','#9b3f4b')])]
    statuses={}
    for r in data['pilot_slots']:statuses[r['status']]=statuses.get(r['status'],0)+1
    layers.append(('New pilot, 12 planned slots',[(v,k,'#657783' if k=='NOT_RUN' else '#bc7b24') for k,v in sorted(statuses.items())]))
    for i,(title,parts) in enumerate(layers):
        y=170+i*180; s.text(52,y,title,20,weight='bold'); x=52; denominator=sum(p[0] for p in parts)
        for n,label,color in parts:
            w=1240*n/denominator; s.rect(x,y+28,w,58,color);s.text(x+12,y+64,f'{label}: {n}/{denominator}',18,color='white');x+=w
    s.text(52,770,f"Historical: {sum(r['cli_count'] for r in runs)} CLI invocations; {sum(r['model_requests'] for r in runs)} internal model requests.",18)
    s.text(52,807,f"New pilot: {sum(r['cli_count'] for r in data['pilot_slots'])} CLI invocations. Planned slots retained; missing time/usage is not zero cost.",18)
    s.text(52,865,'Cohorts stay separate. Blocked sibling attempts belong to the other repository and are not workflow pilot observations.',14)
    s.save(output/'coverage.svg')
    for name, rows in [('historical-runs', runs), ('summary', summary), ('pilot-slots', data['pilot_slots'])]:
        stream=io.StringIO(newline=''); writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n'); writer.writeheader();writer.writerows(rows)
        (output/(name+'.csv')).write_bytes(stream.getvalue().encode())


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--historical',type=Path,required=True);p.add_argument('--pilot',type=Path,required=True);p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();render(tables(read(a.historical),read(a.pilot)),a.output)


if __name__=='__main__':main()
