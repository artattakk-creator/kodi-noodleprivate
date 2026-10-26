"""Optional BINGIE adapter: focus EPG from a bounded published RAM bank only.

Disabled unless the user explicitly enables the separate skin adapter. No
provider/SQLite/disk access, popup or tune when a widget item gains focus.
"""
import hashlib,json,time
BANK='XCMate.Widget41.Bank'
PREFIX='XCMate.Widget41.'
_next=0
_last=None

def publish(portal,rows,snapshot):
    import xbmcgui
    bank={}
    for row in rows[:12]:
        token=hashlib.sha256((str(portal['id'])+'|'+str(row['sid'])).encode()).hexdigest()[:32]
        info=snapshot.get(row['sid'],{})
        events=[dict(title=str(e.get('title',''))[:256],start=e.get('start',0),stop=e.get('stop',0)) for e in info.get('events',[])[:8]]
        bank[token]=events
    data=json.dumps(dict(at=time.time(),events=bank))
    if len(data.encode())<=65536:xbmcgui.Window(10000).setProperty(BANK,data)

def token(portal,row):return hashlib.sha256((str(portal['id'])+'|'+str(row['sid'])).encode()).hexdigest()[:32]

def poll():
    global _next,_last
    import xbmc,xbmcgui
    if time.monotonic()<_next:return
    _next=time.monotonic()+1
    if not xbmc.getCondVisibility('Skin.HasSetting(xcmate41.adapter.enabled)'):return
    marker=xbmcgui.Window(10000)
    current=xbmc.getInfoLabel('Container(90241).ListItem.Property(XCMate.WidgetToken41)') if xbmc.getCondVisibility('Control.HasFocus(90241)') else ''
    try:
        raw=marker.getProperty(BANK);bank=json.loads(raw) if raw and len(raw)<=65536 else {}
        events=bank.get('events',{}).get(current,[]) if 0<=time.time()-bank.get('at',0)<3600 else []
    except (ValueError,TypeError,AttributeError):events=[]
    from epg_views import guide_for_channel
    info=guide_for_channel({'focused':events},'focused')
    from localization import tr
    values=dict(Now=info['now'] or tr(35611),Next=info['next'],Times=(info['now_time']+'–'+info['now_end_time']) if info['now'] else '',NextTime=info['next_time'],Progress=str(round(info['progress']*100)) if info['progress'] is not None else '0')
    signature=(current,tuple(values.items()))
    if signature==_last:return
    _last=signature
    for key,value in values.items():marker.setProperty(PREFIX+key,value)
