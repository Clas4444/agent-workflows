"""Plot all six historical combined/cents arms across five independent repetitions."""
import argparse
import csv
import io
import math
from pathlib import Path
import sys

if __package__:
    from .empirical_figures import SVG, COLORS
    from .empirical_audit import write, sha
else:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from empirical_figures import SVG, COLORS
    from empirical_audit import write, sha

ARMS=('workflow','attention','combined','manual','idea','exhaustive')
LABELS={'workflow':'Agent Workflows','attention':'Agent Attention','combined':'Combined',
        'manual':'Split prompts','idea':'Idea + review','exhaustive':'Oracle-rich prompt'}


def select(rows):
    result=[];seen=set()
    for row in rows:
        if row['campaign']!='combined' or row['case']!='cents':continue
        if row['cohort']!='HISTORICAL':raise ValueError('historical cohort required')
        arm=row['arm'];rep=int(row['rep']);key=(arm,rep)
        if arm not in ARMS or rep not in range(1,6) or key in seen:raise ValueError('invalid or duplicate line point')
        value={k:row[k] for k in ('cohort','campaign','case','arm')}
        value.update(rep=rep,cli_count=int(row['cli_count']),seconds=float(row['seconds']),
                     input_tokens=int(row['input_tokens']),output_tokens=int(row['output_tokens']),
                     total_tokens=int(row['total_tokens']),cached_input_tokens=int(row['cached_input_tokens']),
                     cache_write_tokens=int(row['cache_write_tokens']))
        if not math.isfinite(value['seconds']) or value['seconds']<0:raise ValueError('invalid elapsed')
        if any(value[k]<0 for k in ('input_tokens','output_tokens','total_tokens','cached_input_tokens','cache_write_tokens')):raise ValueError('negative token counter')
        if value['total_tokens']!=value['input_tokens']+value['output_tokens']:raise ValueError('token double count')
        if value['cached_input_tokens']+value['cache_write_tokens']>value['input_tokens']:raise ValueError('cache exceeds input')
        if value['cli_count']!=(3 if arm=='manual' else 2 if arm=='idea' else 1):raise ValueError('unexpected package CLI count')
        seen.add(key);result.append(value)
    if seen!={(a,r) for a in ARMS for r in range(1,6)}:raise ValueError('missing line points: require 6 arms x 5 repeats')
    return sorted(result,key=lambda r:(ARMS.index(r['arm']),r['rep']))


def render(rows,output,source_hash):
    points=select(rows);output.mkdir(parents=True,exist_ok=True)
    write(output/'line-data.json',{'cohort':'HISTORICAL','source_table_sha256':source_hash,'n_per_arm':5,
          'interpretation':'Independent restarted packages, linked for readability; not a learning curve or native continued history.',
          'points':points})
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=list(points[0]),lineterminator='\n')
    writer.writeheader();writer.writerows(points);(output/'line-data.csv').write_bytes(stream.getvalue().encode())
    for field,title,unit,step in [('total_tokens','Token use across independent repetitions','Total tokens / package (input + output)',100000),
                                   ('seconds','Elapsed time across independent repetitions','Elapsed wall seconds / package',30)]:
        chart=SVG('Historical combined cents: '+title,
                  'Six arms, five packages per arm (n=30). Lines link independent repetitions; this is not a learning curve.')
        left=135;top=170;width=1030;height=500
        limit=max(step,math.ceil(max(p[field] for p in points)/step)*step)
        chart.text(left,135,unit,18,weight='bold')
        for tick in range(6):
            value=limit*tick/5;y=top+height-height*tick/5
            chart.line(left,y,left+width,y);chart.text(left-16,y+5,f'{value:,.0f}',14,anchor='end')
        for rep in range(1,6):
            x=left+(rep-1)/4*width;chart.line(x,top,x,top+height)
            chart.text(x,top+height+32,rep,16,anchor='middle')
        for arm in ARMS:
            group=[p for p in points if p['arm']==arm];color=COLORS[arm]
            xy=[(left+(p['rep']-1)/4*width,top+height-p[field]/limit*height) for p in group]
            chart.parts.append('<polyline points="'+' '.join(f'{x},{y}' for x,y in xy)+f'" fill="none" stroke="{color}" stroke-width="3"/>')
            for x,y in xy:chart.dot(x,y,color,5)
        chart.text(left+width/2,top+height+73,'Independent repetition index',18,anchor='middle')
        for i,arm in enumerate(ARMS):
            x=75+(i%3)*445;y=800+(i//3)*35
            chart.rect(x,y-11,30,4,COLORS[arm]);chart.dot(x+15,y-9,COLORS[arm],4)
            count=next(p['cli_count'] for p in points if p['arm']==arm)
            chart.text(x+42,y-3,f'{LABELS[arm]} ({count} CLI/package)',16)
        chart.text(52,894,'Source: sanitized saved Copilot combined/cents table. Cache is included within input; no billing-currency conversion.',14)
        chart.save(output/('combined-cents-tokens.svg' if field=='total_tokens' else 'combined-cents-seconds.svg'))


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-table',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    with args.source_table.open(encoding='utf-8',newline='') as stream:rows=list(csv.DictReader(stream))
    render(rows,args.output,sha(args.source_table))


if __name__=='__main__':main()
