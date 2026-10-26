"""Installed-version notice: persistent own marker, GUI presentation in plugin.

Service only detects/schedules. No dialog or player method on its thread.
Existing pre-.41 service build is a one-time, read-only upgrade witness; a truly
new/unknown installation gets a baseline, never a fictitious update notice.
"""
import contextlib,json,os,re,tempfile,time
PENDING='XCMate.UpdateNotice41.Pending'
ACK='XCMate.UpdateNotice41.Ack'
_next=0

def version(value):
    if not isinstance(value,str) or not re.fullmatch(r'\d+(?:\.\d+){1,5}',value):return None
    return tuple(int(p) for p in value.split('.'))

def installed():
    import xbmcaddon
    value=xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('version')
    return value if version(value) else ''

def root():
    from utils import addon_data_dir
    return addon_data_dir()

def read():
    try:
        with open(os.path.join(root(),'xcmate_update_notice.json'),encoding='utf-8') as f:raw=f.read(8193)
        value=json.loads(raw) if len(raw)<=8192 else None
        if not isinstance(value,dict) or not version(value.get('current')) or not isinstance(value.get('seen',[]),list):return None
        value['seen']=[v for v in value.get('seen',[]) if version(v)][-16:]
        if not version(value.get('pending')):value['pending']=''
        if not isinstance(value.get('retry_at',0),(int,float)):value['retry_at']=0
        return value
    except (OSError,ValueError,TypeError):return None

def save(value):
    temporary=None
    try:
        fd,temporary=tempfile.mkstemp(prefix='.update-notice-',dir=root())
        with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(value,f);f.flush();os.fsync(f.fileno())
        os.replace(temporary,os.path.join(root(),'xcmate_update_notice.json'));return True
    except (OSError,ValueError,TypeError):return False
    finally:
        if temporary and os.path.exists(temporary):os.unlink(temporary)

@contextlib.contextmanager
def lease():
    stream=None;acquired=False
    try:
        import fcntl
        stream=open(os.path.join(root(),'xcmate_update_notice.lock'),'a')
        fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB);acquired=True
    except (OSError,ImportError):pass
    try:yield acquired
    finally:
        if stream:stream.close()

def legacy():
    try:
        from live_diagnostics import _disk
        builds=[int(e['build']) for e in _disk('service') if e.get('code') in ('STARTED','RUNNING','STOPPED') and isinstance(e.get('build'),int) and 1<=e['build']<=40]
        return '0.1.29.'+str(builds[-1]) if builds else ''
    except (OSError,ValueError,TypeError,ImportError):return ''

def detect():
    import xbmcgui
    try:current=installed()
    except (AttributeError,RuntimeError,TypeError):return False
    if not current:return False
    with lease() as acquired:
        if not acquired:return False
        value=read()
        if value is None:
            old=legacy()
            value=dict(current=current,seen=[],pending=current if version(old) and version(old)<version(current) else '',previous=old)
        elif value['current']!=current:
            old=value['current'];value.update(current=current,previous=old,pending=current if version(old)<version(current) and current not in value.get('seen',[]) else '')
        if not save(value):return False
        xbmcgui.Window(10000).setProperty(PENDING,value.get('pending',''));return bool(value.get('pending'))

def safe():
    import xbmc,xbmcgui
    from exit_jobs import blocked
    from window_lifecycle import lease as nav_lease
    if blocked() or nav_lease():return False
    try:
        return (int(xbmcgui.getCurrentWindowId()) in (10000,10025) and
                int(xbmcgui.getCurrentWindowDialogId()) in (0,9999) and
                not any(xbmc.getCondVisibility(c) for c in ('Player.HasMedia','System.HasActiveModalDialog','Container.IsUpdating')))
    except (AttributeError,RuntimeError,ValueError,TypeError):return False

def schedule():
    global _next
    import xbmc,xbmcgui
    if time.monotonic()<_next:return
    marker=xbmcgui.Window(10000);pending=marker.getProperty(PENDING)
    if not pending or marker.getProperty(ACK)==pending:return
    _next=time.monotonic()+30
    if safe():xbmc.executebuiltin('RunPlugin(plugin://plugin.video.xtreammate/?action=update_notice)',wait=False)

def show():
    import xbmcgui
    from localization import tr
    if not safe():return False
    with lease() as acquired:
        if not acquired:return False
        value=read();current=installed();marker=xbmcgui.Window(10000)
        if not value or not current or value.get('pending')!=current or marker.getProperty(ACK)==current:return False
        if time.time()<value.get('retry_at',0):return False
        try:
            # This is the explicitly dispatched plugin/GUI interpreter, never service.run.
            xbmcgui.Dialog().ok(tr(35850),tr(35851,current))
        except (AttributeError,RuntimeError):
            value['retry_at']=time.time()+60;save(value);return False
        marker.setProperty(ACK,current);marker.clearProperty(PENDING)
        value.update(pending='',seen=(value.get('seen',[])+[current])[-16:],retry_at=0)
        return save(value)  # Both OK and Back acknowledge the displayed version.
