"""Bounded numeric phase timings; native visibility is not a decoded frame."""
import time,uuid
_last={}
PHASES=frozenset(('IR_RECEIVED','OWNER_BEGIN','OWNER_READY','CATALOG_SCHEDULED','CATALOG_READY',
                 'RAM_SNAPSHOT','BUILD_BEGIN','BUILD_END','SHOW_BEGIN','SHOW_RETURN','GUI_APPLIED'))


def begin(view,key=0):
    view._timing39=dict(id=uuid.uuid4().hex,start=time.monotonic_ns(),key=int(key),marks=[],finished=False)
    mark(view,'IR_RECEIVED')


def mark(view,phase):
    value=getattr(view,'_timing39',None)
    if value and not value['finished'] and phase in PHASES and len(value['marks'])<16:
        value['marks'].append((phase,max(0,(time.monotonic_ns()-value['start'])//1000000)))


def finish(view):
    value=getattr(view,'_timing39',None)
    if not value or value['finished']:return
    value['finished']=True;now=time.monotonic();elapsed=(time.monotonic_ns()-value['start'])//1000000
    # First/slow sample retained; fast IR repeats do not flood the Kodi log.
    if now-_last.get('IR',-100)<1 and elapsed<200:return
    _last['IR']=now
    import xbmc,xbmcgui
    try:
        dialog=int(xbmcgui.getCurrentWindowDialogId())
        phases=' '.join(name+'='+str(ms) for name,ms in value['marks'])
        xbmc.log('[XCMate][UI39] generation='+value['id']+' action='+str(value['key'])+' dialog='+str(dialog)+' '+phases,xbmc.LOGINFO)
    except (AttributeError,RuntimeError,TypeError,ValueError):pass


def service_poll(function):
    started=time.monotonic_ns()
    try:return function()
    finally:
        ms=(time.monotonic_ns()-started)//1000000
        if ms>=250:
            import xbmc
            try:xbmc.log('[XCMate][UI39] phase=APP_SERVICE_POLL duration_ms='+str(ms),xbmc.LOGINFO)
            except (AttributeError,RuntimeError):pass
