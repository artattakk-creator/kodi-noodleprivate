"""Publish local pages and notify existing native skin directory reload hooks.

No skin writes, shortcut rebinding, global refresh, library scan or focus IO.
Worker writes a bounded atomic DTO; the service GUI pump changes only runtime
reload properties already referenced by verified own widget source URLs. Kodi
retains its DirectoryProvider and exact native click behavior. Missing hooks
are explicitly blocked until an optional separately confirmed adapter is used.
"""
import hashlib,json,os,tempfile,time
MAX_BYTES=16*1024*1024
_next=0;_seen={};_last_code={};_art_cursor46={}


def trace(code,kind='',rows=0):
    if code not in ('PUBLISHED','UPDATED','UNCHANGED','NO_BINDING','UNSUPPORTED_CONTROL','READ_ERROR','DEFERRED','BAD_FRAME','BLOCKED_NO_RELOAD_HOOK'):return
    state=(code,kind,rows)
    if _last_code.get(kind)==state:return
    _last_code[kind]=state
    try:
        import xbmc
        xbmc.log('[XCMate][WIDGET45] code='+code+' kind='+(kind if kind in ('live','vod','series') else 'all')+' rows='+str(max(0,rows)),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


def path(pid,kind):
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'widget45_'+hashlib.sha256((str(pid)+'|'+kind).encode()).hexdigest()[:24]+'.json')


def read(pid,kind):
    try:
        with open(path(pid,kind),encoding='utf-8') as f:raw=f.read(MAX_BYTES+1)
        if len(raw)>MAX_BYTES:return None
        frame=json.loads(raw)
        if not isinstance(frame,dict) or frame.get('pid')!=str(pid) or frame.get('kind')!=kind:return None
        if not isinstance(frame.get('at'),(int,float)) or not 0<=time.time()-frame['at']<600:return None
        if kind=='live' and isinstance(frame.get('pages46'),list):
            from widget_pages46 import Items
            pages=frame['pages46']
            if (not isinstance(frame.get('count46'),int) or frame['count46']<=0
                    or not pages or any(not isinstance(p,dict) or not isinstance(p.get('count'),int) or not 0<p['count']<=16 for p in pages)
                    or sum(p['count'] for p in pages)!=frame['count46']):return None
            values=frame['items']=Items(path(pid,kind),frame)
        else:
            values=frame.get('items')
            if not isinstance(values,list) or not values or kind!='live' and len(values)>24:return None
        from urllib.parse import urlsplit,parse_qs
        for value in values:
            if not isinstance(value,dict) or not all(isinstance(value.get(k),dict) for k in ('props','art','info')) or not isinstance(value.get('label'),str):return None
            props=value['props'];q=parse_qs(urlsplit(value.get('url','')).query)
            if props.get('XCMate.PortalId')!=str(pid) or props.get('XCMate.WidgetKind41')!=kind:return None
            if q.get('pid')!=[str(pid)] or q.get('sid')!=[props.get('XCMate.MediaId')]:return None
            parsed=urlsplit(value['url'])
            if parsed.scheme!='plugin' or parsed.netloc!='plugin.video.xtreammate':return None
            allowed=('play_live','source_play') if kind=='live' else ('media_detail',)
            if q.get('action',[''])[0] not in allowed or (kind!='live' and q.get('kind')!=[kind]):return None
        return frame
    except (OSError,ValueError,TypeError,KeyError,AttributeError):return None


def publish(portal,kind,rows,code='READY'):
    if code not in ('READY','CACHE') or not rows:return False
    from widget_items45 import describe
    from widget_art44 import read as approved
    from widget_data41 import policy
    values=approved(portal['id']);epg={}
    if kind=='live' and len(rows)>64:
        from widget_pages46 import publish as publish_pages46
        return publish_pages46(portal,rows,values)
    if kind in ('live','vod'):
        from widget_render47 import values as render47
        items=render47(portal,kind,rows if kind=='live' else rows[:24],values)
    else:items=[describe(portal,kind,row,values) for row in rows[:24]]
    from widget_diagnostics47 import describe as describe47,save as save47
    save47(portal['id'],kind,'ITEMS',describe47(portal['id'],kind,items))
    if kind=='live':
        from programme_urls55 import enqueue
        cursor=_art_cursor46.get(str(portal['id']),0)%max(1,len(items))
        positions={(cursor+i)%len(items) for i in range(min(16,len(items)))}
        _art_cursor46[str(portal['id'])]=(cursor+16)%max(1,len(items))
        records46=[]
        for pos,value in enumerate(items):
            event=value.pop('_programme46',None)
            if event and pos in positions:enqueue(event)
            if event:records46.append(event)
        from programme_index46 import publish as publish_records46
        publish_records46(records46)
        from programme_assets47 import channels as channels47
        channels47(portal,records46)
    frame=dict(pid=str(portal['id']),kind=kind,policy=policy(portal,kind),at=time.time(),items=items)
    signature_items=[]
    for value in items:
        clone=dict(value,props={k:v for k,v in value['props'].items() if k not in ('XtreamMate.Progress','XCMate.EpgPercent41')})
        signature_items.append(clone)
    # Progress is a real value; refresh no faster than once per minute.
    minute=int(time.time()//60) if kind=='live' and any(v['props'].get('XtreamMate.Now') for v in items) else 0
    frame['signature']=hashlib.sha256(json.dumps([signature_items,minute],sort_keys=True).encode()).hexdigest()
    data=json.dumps(frame).encode()
    if len(data)>MAX_BYTES:trace('BAD_FRAME',kind);return False
    fd,temp=tempfile.mkstemp(prefix='.widget45-',dir=os.path.dirname(path(portal['id'],kind)))
    try:
        with os.fdopen(fd,'wb') as f:f.write(data)
        os.replace(temp,path(portal['id'],kind))
    finally:
        if os.path.exists(temp):os.unlink(temp)
    from widget_notice46 import prepare as prepare_notice46
    prepare_notice46(portal,kind,frame['signature'],len(items))
    trace('PUBLISHED',kind,len(items));return True


def poll():
    global _next
    import xbmc,xbmcgui
    now=time.monotonic()
    if now<_next:return
    _next=now+2
    try:
        if xbmcgui.getCurrentWindowId()!=10000 or xbmcgui.getCurrentWindowDialogId() not in (0,-1):return
        if xbmc.getCondVisibility('Player.HasMedia') or xbmc.getSkinDir()!='skin.titan.bingie.mod':return
        from widget_hooks45 import read as bindings
        from portals import get_by_id
        from widget_data41 import policy
        state=bindings();window=xbmcgui.Window(10000);pending={}
        for binding in state.get('bindings',[])[:96]:
            pid,kind=binding['pid'],binding['kind'];hooks=binding.get('hooks',[])
            if kind not in ('live','vod','series'):continue
            if not hooks:trace('BLOCKED_NO_RELOAD_HOOK',kind);continue
            frame=read(pid,kind)
            if not frame:continue
            portal=get_by_id(pid)
            if not portal or not portal.get('enabled',True) or frame.get('policy')!=policy(portal,kind):continue
            for hook in hooks:
                if not (hook.startswith('XCMate.Widget45.Reload.') or hook in ('widgetreload','widgetreload2','widgetreloadmovies','widgetreloadtvshows')):continue
                pending.setdefault(hook,[]).append((kind,frame['signature'],len(frame['items'])))
        # Shared pre-existing skin hooks are coalesced to one native update.
        for hook,changes in pending.items():
            signature=hashlib.sha256(json.dumps(sorted(changes)).encode()).hexdigest();prior=_seen.get(hook)
            if prior and (prior[0]==signature or now-prior[1]<60):continue
            window.setProperty(hook,signature);_seen[hook]=(signature,now)
            for kind,_,count in changes:trace('UPDATED',kind,count)
            if len(_seen)>96:_seen.pop(next(iter(_seen)))
        if not state.get('bindings'):trace('NO_BINDING')
    except (AttributeError,RuntimeError,OSError,ValueError,ImportError,KeyError,TypeError):trace('READ_ERROR')
