"""Aggregate local .47 timings/counts; never output raw lines or identities."""
import argparse,json,math,re
from collections import defaultdict

FLOW=re.compile(r'\[XCMate\]\[FLOW46\] id=([a-f0-9]{32}) kind=(live|media) phase=([A-Z_]+) ms=(\d+)\b')
PREPARE=re.compile(r'\[XCMate\]\[PREPARE47\] id=([a-f0-9]{32}) code=(LOCAL_READ_BEGIN|START_GROUP_MODEL_READY|FULL_MODEL_READY) rows=\d+ ms=(\d+)\b')
WIDGET=re.compile(r'\[XCMate\]\[WIDGET47\] flow=[a-f0-9]{12} portal=[a-f0-9]{12} kind=(live|vod|series) stage=([A-Z0-9_]+) code=([A-Z0-9_]+)\b(.*)')
PHASES={'ROUTE_ENTRY','DETAIL_SELECTED','DETAIL_READY','DETAIL_METADATA_READY','RESOLVE_BEGIN','PLAYBACK_REQUEST','FIRST_VIDEO','MINI_EPG_VISIBLE','GROUPS_READY'}
FIELDS={'provider_received','sync_stored','indexed','groups','selected','items','poster_sources','logo_sources',
        'local_images','dynamic_images','placeholders','event_count','matched_images','directory_ok','queries','query_ms'}
STAGES={'INDEX','SELECT','ASSETS','ITEMS','DIRECTORY','SKIN','SQL_STATE','SQL_GROUPS','SQL_HEADS',
        'SQL_LEGACY_PRESENCE','SQL_V2_KEYS','SQL_LEGACY_KEYS','SQL_PAYLOAD'}
CODES={'READY','CACHE','BUDGET','SQLITE_BUSY','SQLITE_LOCKED','SQLITE_INTERRUPT','SQLITE_CORRUPT',
       'SQLITE_NOTADB','SQLITE_CANTOPEN','SQLITE_IOERR','INDEX_MISSING','LOCKED','UNAVAILABLE','DISABLED',
       'PREPARE_UNAVAILABLE','WORKER_UNAVAILABLE','CHOICE_REFERENCE_UNAVAILABLE','REFERENCES_READY','NO_RENDERABLE_REFERENCE'}


def analyse(lines):
    sessions={};stages=defaultdict(list)
    for line in lines:
        f=FLOW.search(line);p=PREPARE.search(line)
        if f and f[3] in PHASES:
            ident,kind,phase,ms=f[1],f[2],f[3],int(f[4])
        elif p:
            ident,kind,phase,ms=p[1],'live','PREPARE_'+p[2],int(p[3])
        else:
            w=WIDGET.search(line)
            if w and w[2] in STAGES and len(stages)<512:
                code=w[3] if w[3] in CODES else 'OTHER_CODE'
                bucket=stages[(w[1],w[2],code)]
                if len(bucket)>=4096:continue
                values={k:int(v) for k,v in re.findall(r'\b([a-z_]+)=(-?\d+)\b',w[4])
                        if k in FIELDS and -1<=int(v)<=10000000}
                bucket.append(values)
            continue
        if ms>300000 or len(sessions)>=4096 and ident not in sessions:continue
        session=sessions.setdefault(ident,dict(kind=kind,phases={}))
        if session['kind']==kind:session['phases'].setdefault(phase,ms)
    samples=defaultdict(list)
    for session in sessions.values():
        phases=session['phases'];kind=session['kind']
        for phase,ms in phases.items():
            if phase!='ROUTE_ENTRY':samples[(kind,phase)].append(ms)
        for left,right in (('PLAYBACK_REQUEST','FIRST_VIDEO'),('FIRST_VIDEO','GROUPS_READY'),
                           ('FIRST_VIDEO','MINI_EPG_VISIBLE'),('DETAIL_SELECTED','FIRST_VIDEO')):
            if left in phases and right in phases and phases[right]>=phases[left]:
                samples[(kind,left+'_TO_'+right)].append(phases[right]-phases[left])
    def percentile(values,p):return sorted(values)[max(0,math.ceil(len(values)*p)-1)]
    counts=[]
    for (kind,stage,code),values in sorted(stages.items()):
        fields={}
        for field in FIELDS:
            present=[v[field] for v in values if field in v]
            if present:fields[field]=dict(min=min(present),max=max(present),unknown=sum(v==-1 for v in present))
        counts.append(dict(kind=kind,stage=stage,code=code,n=len(values),counts=fields))
    return dict(measurement='Add-on route/player/UI evidence; no physical IR or decoded-display-frame proof',
        timings=[dict(kind=k[0],phase=k[1],n=len(v),p50_ms=percentile(v,.5),p95_ms=percentile(v,.95)) for k,v in sorted(samples.items())],
        widgets=counts)


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('log');parser.add_argument('--run-kind',choices=('cold','warm','unspecified'),default='unspecified')
    args=parser.parse_args()
    with open(args.log,encoding='utf-8',errors='replace') as stream:result=analyse(stream)
    print(json.dumps(dict(result,run_kind=args.run_kind),indent=2))
