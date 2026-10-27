"""Publish changed local pages into already bound XCMate Home containers.

No skin writes, shortcut rebinding, global refresh, library scan or focus IO.
Worker writes a bounded atomic DTO; the service GUI pump handles native lists.
Only a completely identified own row may be updated. Unsupported native
controls remain untouched and produce an explicit capability code.
"""
import hashlib,json,os,tempfile,time
MAX_BYTES=768*1024
_next=0;_scan_at=0;_ids=[];_seen={};_last_code={};_cursor=0


def trace(code,kind='',rows=0):
    if code not in ('PUBLISHED','UPDATED','UNCHANGED','NO_BINDING','UNSUPPORTED_CONTROL','READ_ERROR','DEFERRED','BAD_FRAME'):return
    state=(code,kind,rows)
    if _last_code.get(kind)==state:return
    _last_code[kind]=state
    try:
        import xbmc
        xbmc.log('[XCMate][WIDGET45] code='+code+' kind='+(kind if kind in ('live','vod','series') else 'all')+' rows='+str(min(24,max(0,rows))),xbmc.LOGINFO)
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
        values=frame.get('items')
        if not isinstance(values,list) or not 0<len(values)<= (12 if kind=='live' else 24):return None
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
    except (OSError,ValueError,TypeError):return None


def publish(portal,kind,rows,code='READY'):
    if code not in ('READY','CACHE') or not rows:return False
    from widget_items45 import describe
    from widget_art44 import read as approved
    from widget_data41 import policy
    values=approved(portal['id']);epg={}
    if kind=='live':
        from local_epg import now_next
        from epg_sources import configuration
        epg=now_next(portal['id'],rows,configuration(portal['id'])['mappings'])
    items=[describe(portal,kind,row,values,epg.get(row['sid'])) for row in rows[:12 if kind=='live' else 24]]
    frame=dict(pid=str(portal['id']),kind=kind,policy=policy(portal,kind),at=time.time(),items=items)
    frame['signature']=hashlib.sha256(json.dumps(items,sort_keys=True).encode()).hexdigest()
    data=json.dumps(frame).encode()
    if len(data)>MAX_BYTES:trace('BAD_FRAME',kind);return False
    fd,temp=tempfile.mkstemp(prefix='.widget45-',dir=os.path.dirname(path(portal['id'],kind)))
    try:
        with os.fdopen(fd,'wb') as f:f.write(data)
        os.replace(temp,path(portal['id'],kind))
    finally:
        if os.path.exists(temp):os.unlink(temp)
    trace('PUBLISHED',kind,len(items));return True


def container_ids():
    """Read installed generated layout IDs; never write or evaluate skin code."""
    import xbmcvfs,xml.etree.ElementTree as ET
    found=set()
    for path_ in ('special://skin/xml/script-skinshortcuts-includes.xml','special://skin/1080i/script-skinshortcuts-includes.xml','special://skin/720p/script-skinshortcuts-includes.xml'):
        if not xbmcvfs.exists(path_):continue
        f=xbmcvfs.File(path_)
        try:raw=bytes(f.readBytes(4*1024*1024+1))
        finally:f.close()
        if len(raw)>4*1024*1024 or b'<!DOCTYPE' in raw or b'<!ENTITY' in raw:continue
        try:tree=ET.fromstring(raw)
        except ET.ParseError:continue
        for node in tree.iter():
            value=node.get('id') if node.tag=='control' and node.get('type') in ('list','panel','wraplist','fixedlist') else node.get('value') if node.tag=='param' and node.get('name')=='widgetid' else ''
            if str(value).isdigit() and 0<int(value)<2147483647:found.add(int(value))
            if len(found)>256:return []
    return sorted(found)


def binding(control):
    """Require every displayed item to prove its own PID/kind and route."""
    from urllib.parse import urlsplit,parse_qs
    size=control.size()
    if not 0<size<=25:return None
    pid=kind=None;identities=[]
    for i in range(size):
        li=control.getListItem(i);k=li.getProperty('XCMate.WidgetKind41');p=li.getProperty('XCMate.PortalId')
        if k not in ('live','vod','series') or not p:
            # Older media rows contain one final "all titles" directory tile.
            # Verify its actual URL before removing it from a poster-only row.
            if i==size-1 and kind in ('vod','series'):
                try:
                    parsed=urlsplit(li.getPath());q=parse_qs(parsed.query)
                    if parsed.scheme=='plugin' and parsed.netloc=='plugin.video.xtreammate' and q.get('pid')==[pid] and q.get('action')==['movies_home' if kind=='vod' else 'series_home']:
                        identities.append('__legacy_directory45');continue
                except (AttributeError,ValueError):pass
            return None
        if pid is None:pid,kind=p,k
        if (p,k)!=(pid,kind):return None
        sid=li.getProperty('XCMate.MediaId');url=li.getProperty('XCMate.ClickTarget44')
        parsed=urlsplit(url);q=parse_qs(parsed.query)
        action='play_live' if k=='live' else 'media_detail'
        if parsed.scheme!='plugin' or parsed.netloc!='plugin.video.xtreammate' or q.get('pid')!=[p] or q.get('sid')!=[sid]:return None
        if q.get('action') not in ([action],['source_play'] if k=='live' else [action]):return None
        if k!='live' and q.get('kind')!=[k]:return None
        identities.append(sid)
    return pid,kind,identities


def apply(control,frame,identities,previous=None):
    from widget_items45 import item
    values=frame['items'];new=[v['props']['XCMate.MediaId'] for v in values]
    selected=control.getSelectedPosition();sid=identities[selected] if 0<=selected<len(identities) else None
    if identities==new:
        for i,value in enumerate(values):
            if previous and previous['items'][i]==value:continue
            li=control.getListItem(i);li.setLabel(value['label']);li.setInfo('video',value['info']);li.setArt(value['art'])
            for key,text in value['props'].items():li.setProperty(key,str(text))
    else:
        # Selection by stable title ID, never focus a different control/window.
        native=[item(value) for value in values]
        control.reset();control.addItems(native)
        control.selectItem(new.index(sid) if sid in new else min(max(0,selected),len(new)-1))


def poll():
    global _next,_scan_at,_ids,_cursor
    import xbmc,xbmcgui
    now=time.monotonic()
    if now<_next:return
    _next=now+2
    try:
        if xbmcgui.getCurrentWindowId()!=10000 or xbmcgui.getCurrentWindowDialogId() not in (0,-1):return
        if xbmc.getCondVisibility('Player.HasMedia'):return
        if xbmc.getSkinDir()!='skin.titan.bingie.mod':return
        window=xbmcgui.Window(10000)
        if now>=_scan_at:_ids=container_ids();_scan_at=now+60
        focused=window.getFocusId()
        scan=(_ids+_ids)[_cursor:_cursor+16] if _ids else []
        _cursor=(_cursor+16)%len(_ids) if _ids else 0
        ids=list(dict.fromkeys([focused]+list(_seen)+scan))[:32]
        found=False
        from portals import get_by_id
        from widget_data41 import policy
        for cid in ids:
            try:
                control=window.getControl(cid);own=binding(control)
                if not own:continue
                found=True;pid,kind,identities=own;frame=read(pid,kind)
                if not frame:continue
                portal=get_by_id(pid)
                if not portal or not portal.get('enabled',True) or frame.get('policy')!=policy(portal,kind):continue
                prior=_seen.get(cid)
                if prior and prior['signature']==frame['signature'] and identities==[v['props']['XCMate.MediaId'] for v in frame['items']]:continue
                apply(control,frame,identities,prior if prior and prior.get('pid')==pid and prior.get('kind')==kind and len(prior['items'])==len(frame['items']) else None)
                _seen[cid]=frame
                while len(_seen)>8:_seen.pop(next(iter(_seen)))
                trace('UPDATED',kind,len(frame['items']))
            except (AttributeError,RuntimeError,TypeError,ValueError,KeyError):continue
        if not found:trace('NO_BINDING')
    except (AttributeError,RuntimeError,OSError,ValueError,ImportError):trace('READ_ERROR')
