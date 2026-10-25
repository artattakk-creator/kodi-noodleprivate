"""Small shared startup snapshots and priority short guides; worker only."""
import json
import os
import tempfile
import time

_next={}
_offsets={}


def path(pid):
    import hashlib
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'startup_'+hashlib.sha256(str(pid).encode()).hexdigest()[:24]+'.json')


def read(pid,sid):
    try:
        with open(path(pid),encoding='utf-8') as stream: raw=stream.read(262145)
        data=json.loads(raw) if len(raw)<=262144 else {}
        if not isinstance(data,dict) or time.time()-float(data.get('at',0))>86400: return {}
        rows=data.get('rows',[])
        if not isinstance(rows,list): return {}
        return next((r for r in rows[:16] if isinstance(r,dict) and r.get('sid')==str(sid)),{})
    except (OSError,ValueError,TypeError): return {}


def prepare(cancel=lambda:False):
    from portals import get_active
    from library_index import Reader,initial_group
    from xtream import XtreamClient
    from epg import load_cache
    from epg_sources import configuration
    from epg_views import resolve_guide,_start_short_guides
    from media_art import request,local_art
    for portal in get_active():
        pid=portal['id']
        if portal.get('type')!='xtream' or time.monotonic()<_next.get(pid,0): continue
        _next[pid]=time.monotonic()+30
        reader=Reader(pid);groups=reader.groups('live')
        start=reader.get('live',str(portal.get('start_stream_id') or ''))
        cid=initial_group(portal,groups,start)
        if not cid: continue
        visible,total=reader.page('live',category=cid,limit=16,pin=start['sid'] if start else None)
        client=XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
        mappings=configuration(pid)['mappings']
        from guide_viewport import cache as viewport_cache
        from types import SimpleNamespace
        channels=[SimpleNamespace(tvg_id=r.get('epg_channel_id',''),extra={'stream_id':r['sid']}) for r in visible]
        cache=viewport_cache(pid,channels,mappings,time.time())
        if cache is None:cache=load_cache(pid)
        rows=[];missing=[]
        for row in visible:
            if cancel(): return
            guide=resolve_guide(cache,row.get('epg_channel_id',''),row['sid'],client=client,mappings=mappings)
            rows.append(dict(sid=row['sid'],name=row['name'],logo=local_art(row).get('thumb',''),guide=guide))
            if not guide.get('now'): missing.append(row['sid'])
        request(visible)
        # Start + visible first, then one small rotating page of the start
        # group, then other active groups. No XMLTV bulk feed to fill a tile.
        if missing: _start_short_guides(portal,missing[:16])
        else:
            offset=_offsets.get(pid,16)
            rest,count=reader.page('live',category=cid,offset=offset,limit=16)
            if rest:
                _start_short_guides(portal,[r['sid'] for r in rest]);_offsets[pid]=offset+16
            else:
                others=[g for g in groups if g['cid']!=cid]
                if others:
                    page,_=reader.page('live',category=others[(offset//16)%len(others)]['cid'],limit=16)
                    _start_short_guides(portal,[r['sid'] for r in page])
                _offsets[pid]=16
        filename=path(pid);fd,temp=tempfile.mkstemp(prefix='.startup-',dir=os.path.dirname(filename))
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as stream:
                json.dump(dict(at=time.time(),category=cid,rows=rows),stream,ensure_ascii=False)
            os.replace(temp,filename)
        finally:
            if os.path.exists(temp): os.unlink(temp)
