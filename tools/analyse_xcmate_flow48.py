"""Local .48 startup/wizard/dataflow summary. No raw lines, paths or identities."""
import argparse,json,math,re
from collections import Counter,defaultdict
from analyse_xcmate_flow47 import analyse as analyse47
PHASES={'SERVICE','DUPLICATE','LOCAL','NETWORK','WIDGET','EXIT','BACKGROUND','IMAGE','MAPPING'}
STAGES={'SOURCE','MATCH','LOCAL_EVENT','IMAGE','CACHE','LISTITEM','FOCUS','MINI'}
CODES={'READY','BUSY','DEFERRED','FAILED','NO_PORTAL','SETUP_ACTIVE','BUDGET','UNAVAILABLE','SKIPPED','NO_EPG','NO_SOURCE_FACTS','NO_IMAGE','PENDING','READY_STALE','IMAGE_DECODER_MISSING','LOCAL_IMAGE_MISSING','SOURCE_UNAVAILABLE'}

def analyse(lines):
    # Keep only whitelisted numeric samples, never retain a private raw log.
    timings=defaultdict(list);counts=Counter();wizard={};samples=defaultdict(list)
    oldlines=[]
    for line in lines:
        if len(line)>65536:continue
        if '[XCMate][FLOW46]' in line or '[XCMate][PREPARE47]' in line or '[XCMate][WIDGET47]' in line:
            # Old parser whitelists fields. Store only the matching bounded
            # diagnostic suffix; never usernames/provider paths from prefixes.
            if len(oldlines)<10000:oldlines.append(line[line.index('[XCMate]'):])
        match=re.search(r'\[START48\] phase=([A-Z_]+) code=([A-Z_]+) duration_ms=([0-9.]+)',line)
        if match and match[1] in PHASES:
            code=match[2] if match[2] in CODES else 'OTHER'
            counts[('START',match[1],code)]+=1
            value=float(match[3])
            if 0<=value<=300000 and len(timings[match[1]])<4096:timings[match[1]].append(value)
        match=re.search(r'\[PROGRAMME48\] stage=([A-Z_]+) event=[a-f0-9]{12} source=(XMLTV|PROVIDER|UNKNOWN) code=([A-Z_]+)',line)
        if match and match[1] in STAGES:counts[('PROGRAMME',match[1],match[3] if match[3] in CODES else 'OTHER')]+=1
        match=re.search(r'\[SETUP37\] stage=(DISCOVER_BEGIN|DISCOVER_DONE|DISCOVER_FAILED|ENTRY48|QUEUED48|NATIVE_INIT_TIMEOUT48|HANDOFF_TIMEOUT48) session=([a-f0-9]{12}|NONE) mono_ms=(\d+)',line)
        if match:
            phase,ident,ms=match[1],match[2],int(match[3]);counts[('WIZARD',phase,'OBSERVED')]+=1
            if phase=='DISCOVER_BEGIN' and len(wizard)<256:wizard[ident]=ms
            elif phase in ('DISCOVER_DONE','DISCOVER_FAILED') and ident in wizard:
                elapsed=ms-wizard.pop(ident)
                if 0<=elapsed<=300000:samples['DISCOVERY'].append(elapsed)
        match=re.search(r'\[RETURN48\] session=[a-f0-9]{12} phase=(requested|stopping|home|complete|failed) job=(pending|running|complete|failed|timeout|NONE) posted=([01]) ack=([01])',line)
        if match:counts[('RETURN',match[1].upper(),'ACK_'+match[4])]+=1
    timings.update(samples)
    def pct(values,p):return sorted(values)[max(0,math.ceil(len(values)*p)-1)]
    return dict(measurement='Host/Android log observations only; GUI pixels/crash root cause require device evidence',legacy=analyse47(oldlines),
        phases=[dict(phase=k,n=len(v),p50_ms=pct(v,.5),p95_ms=pct(v,.95)) for k,v in sorted(timings.items()) if v],
        counts=[dict(area=k[0],stage=k[1],code=k[2],n=v) for k,v in sorted(counts.items())])

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('log');parser.add_argument('--run-kind',choices=('cold','warm','unspecified'),default='unspecified');args=parser.parse_args()
    with open(args.log,encoding='utf-8',errors='replace') as stream:value=analyse(stream)
    print(json.dumps(dict(value,run_kind=args.run_kind),indent=2))
