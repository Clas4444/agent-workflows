"""Reproduce COORD-02 historical and FUNCTION-03 blocked-attempt charts; no models."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import sys

if not __package__:sys.path.insert(0,str(Path(__file__).resolve().parent.parent))
from scripts.empirical_cases import oracle
from scripts.empirical_figures import SVG,COLORS

ROOT=Path(__file__).resolve().parents[1]
PACKET=ROOT/'docs/evidence/coordination-function-20261103'
OUTPUT=ROOT/'docs/evidence/coordination-function-charts-20261103'
ARMS=('plain','workflow','matched')
STATES={'BLOCKED_ENVIRONMENT':'#bc7b24','CANCELLED_UNKNOWN':'#9b3f4b','NOT_RUN':'#657783'}


def schema(value,expected):
    if type(value) is not type(expected):return False
    if isinstance(expected,dict):return set(value)==set(expected) and all(schema(value[k],expected[k]) for k in expected)
    if isinstance(expected,list):return all(isinstance(v,str) for v in value)
    return True


def derive(packet=PACKET):
    read=lambda p:json.loads(p.read_text(encoding='utf-8'))
    old=read(packet/'coord02-regrade-v2.json');model=read(packet/'function03-model.json')
    protocol=read(packet.parent/'codex-office-20261103/protocol.json')
    historical=[]
    for row in old['observations']:
        u=row['usage'];expected=oracle(row['case'],protocol['fixtures'][row['case']]['source'])
        historical.append({'id':row['id'],'case':row['case'],'arm':row['arm'],'rep':row['rep'],
          'original_pass':row['status']=='PASS','strict_pass':row['status_regraded']=='PASS',
          'schema_pass':schema(row['candidate'],expected),'required_fields_pass':row['required_fields_semantic'],
          'input_tokens':u['input_tokens'],'cached_input_tokens':u['cached_input_tokens'],'output_tokens':u['output_tokens'],
          'total_tokens':u['input_tokens']+u['output_tokens'],'seconds':row['seconds']})
    quality=[]
    for arm in ARMS:
        rows=[r for r in historical if r['arm']==arm]
        quality.append({'arm':arm,'n':len(rows),**{k:sum(r[k] for r in rows) for k in ('original_pass','strict_pass','schema_pass','required_fields_pass')}})
    new=[]
    for row in model['observations']:
        measured=row['total_tokens'] is not None
        fields=('id','case','arm','rep','original_status','regrade_status','cli_count','seconds','input_tokens',
                'cached_input_tokens','cache_write_input_tokens','output_tokens','reasoning_output_tokens','total_tokens')
        entry={k:row[k] for k in fields};entry['measured']=measured
        if measured:
            if (entry['total_tokens']!=entry['input_tokens']+entry['output_tokens']
                    or not 0<=entry['cached_input_tokens']<=entry['input_tokens']):raise ValueError('invalid measured counters')
        elif any(entry[k] is not None for k in ('input_tokens','output_tokens','cached_input_tokens','seconds')):
            raise ValueError('unmeasured slots cannot carry zero-filled counters')
        new.append(entry)
    return {'historical':historical,'quality':quality,'function03':new,
      'source_sha256':{name:hashlib.sha256((packet/name).read_bytes()).hexdigest() for name in ('coord02-regrade-v2.json','function03-model.json')},
      'scope':'Historical12 office calls; separate six FUNCTION-03 planned slots. Missing is not zero; no model effectiveness/cost A/B claim for failed prerequisites.'}


def ticks(chart,left,top,width,height,maximum,step,label):
    chart.text(left,top-17,label,15,weight='bold')
    for value in range(0,maximum+1,step):
        y=top+height-height*value/maximum
        chart.line(left,y,left+width,y);chart.text(left-12,y+5,f'{value:,}',13,anchor='end')
    chart.line(left,top,left,top+height,color='#657783')


def legend(chart,items,y=865):
    for i,(label,color) in enumerate(items):
        x=72+i*420;chart.rect(x,y-12,14,14,color);chart.text(x+22,y,label,14)


def render(data,output):
    output.mkdir(parents=True,exist_ok=True)
    write=lambda name,value:(output/name).write_bytes((json.dumps(value,indent=2,ensure_ascii=True)+'\n').encode())
    write('chart-data.json',data)
    for name,rows in (('historical-runs.csv',data['historical']),('historical-quality.csv',data['quality']),('function03-slots.csv',data['function03'])):
        stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=list(rows[0]),lineterminator='\n');writer.writeheader();writer.writerows(rows)
        (output/name).write_bytes(stream.getvalue().encode())
    s=SVG('COORD-02 / HISTORICAL: office acceptance layers',
          '12 saved Codex CLI calls; n=4 per arm (2 cases x 2 repeats). Original FAIL12 remains unchanged.')
    left,top,width,height=110,180,1180,470;ticks(s,left,top,width,height,4,1,'Accepted outputs (count / 4)')
    layers=[('strict_pass','Strict after diagnostic correction','#127d79'),('schema_pass','Recursive key/type schema','#4554a0'),('required_fields_pass','Required-field semantics','#bc7b24')]
    for i,row in enumerate(data['quality']):
        center=left+width*(i+.5)/3
        for j,(field,_,color) in enumerate(layers):
            x=center+(j-1)*76-28;h=row[field]/4*height;s.rect(x,top+height-h,56,h,color)
            s.text(x+28,top+height-h+27,str(row[field]),18,anchor='middle',weight='bold',color='#ffffff')
        s.text(center,top+height+36,row['arm'],18,anchor='middle')
    s.text(72,735,'Strict includes all corrected acceptance checks; schema checks keys/types, not expected values.',16)
    s.text(72,767,'One matched authority output has an extra field: strict/schema fail; required fields still correct.',16)
    s.text(72,802,'Source: historical-runs.csv / historical-quality.csv; not new execution or a reliability estimate.',15)
    legend(s,[(label,color) for _,label,color in layers]);s.save(output/'historical-quality.svg')

    s=SVG('COORD-02 / HISTORICAL: tokens and wall time by repeat',
          '12 saved calls; n=2 per case/arm. Points are observations, not a learning curve or confidence interval.')
    for panel,(case,field,maximum,step,label) in enumerate((('revision','total_tokens',16000,4000,'Revision: input + output tokens'),('authority','total_tokens',16000,4000,'Authority: input + output tokens'),('revision','seconds',16,4,'Revision: CLI wall seconds'),('authority','seconds',16,4,'Authority: CLI wall seconds'))):
        left=115+(panel%2)*690;top=155+(panel//2)*315;width=500;height=205
        ticks(s,left,top,width,height,maximum,step,label)
        for rep in (1,2):s.text(left+110+(rep-1)*270,top+height+27,rep,14,anchor='middle')
        s.text(left+width/2,top+height+55,'Repeat index',14,anchor='middle')
        for row in data['historical']:
            if row['case']!=case:continue
            x=left+110+(row['rep']-1)*270+(ARMS.index(row['arm'])-1)*17
            y=top+height-row[field]/maximum*height
            s.dot(x,y,COLORS[row['arm']],r=7)
    s.text(72,800,'Source: historical-runs.csv. Cache is a subset of input; total = input + output only.',15)
    legend(s,[(arm,COLORS[arm]) for arm in ARMS]);s.save(output/'historical-cost.svg')

    s=SVG('FUNCTION-03: all six planned slots, prerequisite-v2 status',
          '3 reservations consumed: 2 completed, 1 cancelled/unknown; 3 slots NOT_RUN. No delivered model work.')
    left,top,width,height=110,170,1180,320;ticks(s,left,top,width,height,6,1,'Planned slots (count)')
    for i,(status,color) in enumerate(STATES.items()):
        count=sum(r['regrade_status']==status for r in data['function03']);center=left+width*(i+.5)/3;h=count/6*height
        s.rect(center-65,top+height-h,130,h,color);s.text(center,top+height-h-14,count,20,anchor='middle',weight='bold')
        s.text(center,top+height+32,status,16,anchor='middle')
    for i,row in enumerate(data['function03']):
        y=580+i*35;s.rect(85,y-12,14,14,STATES[row['regrade_status']]);s.text(112,y,row['id'],15)
        s.text(600,y,row['regrade_status'],15)
    s.text(72,817,'Source: function03-slots.csv; original two FAIL labels retained separately from prerequisite-v2.',15)
    legend(s,list(STATES.items()));s.save(output/'function03-status.svg')

    s=SVG('FUNCTION-03: observed usage and wall time, with missing slots',
          'Only two completed attempts have counters. Both failed prerequisites; these are costs, not an efficacy A/B.')
    for panel,(maximum,step,label) in enumerate(((80000,20000,'Input + output tokens'),(25,5,'CLI wall seconds'))):
        left=110+panel*700;top=180;width=535;height=420;ticks(s,left,top,width,height,maximum,step,label)
        for i,row in enumerate(data['function03']):
            x=left+width*(i+.5)/6
            s.text(x,top+height+29,i+1,14,anchor='middle')
            if row['measured']:
                if panel==0:
                    values=[(row['cached_input_tokens'],'#657783'),(row['input_tokens']-row['cached_input_tokens'],'#127d79'),(row['output_tokens'],'#bc7b24')]
                    y=top+height
                    for value,color in values:
                        h=value/maximum*height;y-=h;s.rect(x-25,y,50,h,color)
                    s.text(x,y-12,f"{row['total_tokens']:,}",13,anchor='middle')
                else:
                    y=top+height-row['seconds']/maximum*height;s.dot(x,y,'#127d79',r=7);s.text(x,y-15,f"{row['seconds']:.3f}",13,anchor='middle')
            else:
                y=top+55;s.line(x-7,y-7,x+7,y+7,'#9b3f4b');s.line(x-7,y+7,x+7,y-7,'#9b3f4b')
                s.text(x,y+25,'unknown' if row['cli_count'] else 'not run',12,anchor='middle',color='#9b3f4b')
        s.text(left+width/2,top+height+60,'Planned slot index (1 workflow repair; 2 baseline repair; 3-6 missing)',13,anchor='middle')
    outputs='; '.join(f"slot{i+1}: output{r['output_tokens']} tokens" for i,r in enumerate(data['function03']) if r['measured'])
    s.text(72,687,'Thin gold segments: '+outputs+'. Exact component counters are in the CSV.',14)
    s.text(72,720,'Crosses mark missing values at an annotation height, not zero or a measured coordinate.',16)
    s.text(72,748,'Cached input is included in input. Output includes reasoning; do not add either subset again.',16)
    s.text(72,781,'Source: function03-slots.csv / function03-model.json. n=1 completed attempt per arm in repair only.',15)
    legend(s,[('Cached input','#657783'),('Uncached input / seconds','#127d79'),('Output','#bc7b24')]);s.save(output/'function03-observed-cost.svg')


def generated_bytes(data):
    import tempfile
    with tempfile.TemporaryDirectory() as directory:
        folder=Path(directory);render(data,folder)
        return {p.name:p.read_bytes() for p in folder.iterdir()}


def main():
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--packet',type=Path,default=PACKET);parser.add_argument('--output',type=Path,default=OUTPUT);parser.add_argument('--write',action='store_true');a=parser.parse_args()
    data=derive(a.packet)
    if a.write:render(data,a.output)
    else:
        expected=generated_bytes(data)
        failures=[name for name,value in expected.items() if not (a.output/name).is_file() or (a.output/name).read_bytes()!=value]
        if failures:parser.exit(1,'STALE chart data/SVG: '+', '.join(failures)+'\n')
    print('PASS: historical and blocked-attempt chart tables/SVG; no model calls')


if __name__=='__main__':main()
