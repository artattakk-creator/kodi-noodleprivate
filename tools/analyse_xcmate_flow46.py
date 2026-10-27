"""Read local Kodi logs, emit only aggregate FLOW46 timings (never raw lines)."""
import argparse,json,math,re
from collections import defaultdict
PATTERN=re.compile(r'\[XCMate\]\[FLOW46\] id=([a-f0-9]{32}) kind=(live|media) phase=([A-Z_]+) ms=(\d+)\b')
ALLOWED={'ROUTE_ENTRY','DETAIL_SELECTED','DETAIL_READY','DETAIL_METADATA_READY','RESOLVE_BEGIN','PLAYBACK_REQUEST','FIRST_VIDEO','MINI_EPG_VISIBLE','GROUPS_READY'}


def analyse(lines):
    sessions={};values=defaultdict(list)
    for line in lines:
        m=PATTERN.search(line)
        if not m or m[3] not in ALLOWED or int(m[4])>300000:continue
        ident,kind,phase,ms=m[1],m[2],m[3],int(m[4])
        if len(sessions)>=4096 and ident not in sessions:continue
        session=sessions.setdefault(ident,dict(kind=kind,phases={}))
        if session['kind']!=kind:continue
        session['phases'].setdefault(phase,ms)
    for session in sessions.values():
        for phase,ms in session['phases'].items():
            if phase!='ROUTE_ENTRY':values[(session['kind'],phase)].append(ms)
    def percentile(v,p):return sorted(v)[max(0,math.ceil(len(v)*p)-1)]
    return dict(measurement='Python route to owned Player/UI evidence; no decoded-frame or physical-IR assertion',samples=[dict(kind=k[0],phase=k[1],n=len(v),p50_ms=percentile(v,.5),p95_ms=percentile(v,.95)) for k,v in sorted(values.items())])


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('log');args=p.parse_args()
    with open(args.log,encoding='utf-8',errors='replace') as f:print(json.dumps(analyse(f),indent=2))
