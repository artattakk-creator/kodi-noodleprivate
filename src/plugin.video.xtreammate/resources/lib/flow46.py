"""Bounded anonymous route-to-video/UI timings, no URLs or titles in logs.

Entry means the Python route boundary, not physical IR receipt. FIRST_VIDEO is
owned Player/getTime evidence, not a measurement of a decoded display frame.
Private Window state carries identity; logs contain only random correlation.
"""
import json,time,uuid
KEY='XCMate.Flow46'
PHASES=frozenset(('ROUTE_ENTRY','DETAIL_SELECTED','DETAIL_READY','DETAIL_METADATA_READY','RESOLVE_BEGIN',
                 'PLAYBACK_REQUEST','FIRST_VIDEO','MINI_EPG_VISIBLE','GROUPS_READY'))


def read():
    import xbmcgui
    try:
        raw=xbmcgui.Window(10000).getProperty(KEY)
        value=json.loads(raw) if raw and len(raw)<=4096 else None
        if (isinstance(value,dict) and value.get('kind') in ('live','media')
                and len(value.get('id',''))==32 and all(c in '0123456789abcdef' for c in value['id'])
                and isinstance(value.get('marks'),list) and 0<=time.monotonic_ns()-value['start']<300*10**9):return value
    except (AttributeError,RuntimeError,TypeError,ValueError,KeyError):pass


def save(value):
    import xbmcgui
    xbmcgui.Window(10000).setProperty(KEY,json.dumps(value))


def begin(kind,pid,sid='',force=False):
    if kind not in ('live','media'):return
    old=read()
    if not force and old and old.get('kind')==kind and old.get('pid')==str(pid) and (not sid or old.get('sid') in ('',str(sid))):return old
    value=dict(id=uuid.uuid4().hex,kind=kind,pid=str(pid),sid=str(sid),start=time.monotonic_ns(),marks=[])
    save(value);mark('ROUTE_ENTRY',value=value);return read()


def entry(argv):
    from urllib.parse import parse_qs
    try:q=parse_qs(argv[2].lstrip('?'))
    except (IndexError,TypeError,ValueError):return
    action=q.get('action',[''])[0]
    if action in ('play_live','source_play','play_start','play_start_direct','source_start','media_detail'):
        begin('media' if action=='media_detail' else 'live',q.get('pid',[''])[0],q.get('sid',[''])[0],force=True)


def selected(pid,sid):
    old=read();begin('media',pid,sid,force=bool(old and 'DETAIL_SELECTED' in old.get('marks',[])))
    mark('DETAIL_SELECTED',pid=pid,sid=sid)


def mark(phase,value=None,pid=None,sid=None):
    if phase not in PHASES:return
    value=value or read()
    if not value or phase in value.get('marks',[]):return
    if pid is not None and value.get('pid')!=str(pid):return
    if sid is not None and value.get('sid') not in ('',str(sid)):return
    elapsed=(time.monotonic_ns()-value['start'])//1000000
    value['marks'].append(phase);save(value)
    import xbmc
    try:xbmc.log('[XCMate][FLOW46] id='+value['id']+' kind='+value['kind']+' phase='+phase+' ms='+str(max(0,elapsed)),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


def bind(kind,session):
    value=read()
    if not value or value.get('kind')!=kind or value.get('pid')!=str(session['pid']):return
    target=str(session.get('series_id') or session.get('sid','')) if kind=='media' else str(session.get('sid',''))
    if value.get('sid') not in ('',target,str(session.get('sid',''))):return
    value['nonce']=session['nonce'];save(value);mark('PLAYBACK_REQUEST',value=value)


def observe():
    value=read()
    if not value or not value.get('nonce') or 'FIRST_VIDEO' in value['marks']:return
    import xbmc
    from playback_exit import identity
    player=xbmc.Player();token=identity(player)
    if token and token[0]==value['kind'] and token[1]['nonce']==value['nonce']:
        try:player.getTime()
        except (AttributeError,RuntimeError,ValueError):return
        mark('FIRST_VIDEO',value=value)
