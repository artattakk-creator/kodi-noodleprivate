"""Fixed wizard phases, monotonic milliseconds and anonymous correlation only."""
import hashlib
import time

STAGES=frozenset(('WORK_TIMEOUT','SETUP_DISCOVER_DONE','GROUPS_RENDER_BEGIN','GROUPS_RENDER_END','GROUP_FOCUS','GROUP_TOGGLE','SETUP_SAVE_BEGIN','SETUP_SAVE_END','HANDOFF_TIMEOUT48','ENTRY48','QUEUED48','DISCOVER_BEGIN','DISCOVER_DONE','DISCOVER_FAILED','NATIVE_INIT_TIMEOUT48','SAVE_BEGIN','COPY_CATALOG','COPY_GUIDE','CONFIG_PUBLISH','VERIFY','SAVE_DONE','SAVE_FAILED','GUI_CLOSE_BEGIN','GUI_CLOSE_DONE','NATIVE_RELEASED','HOME_REQUESTED'))


def mark(stage,session='',**fields):
    if stage not in STAGES:return
    import xbmc
    code=hashlib.sha256(str(session).encode()).hexdigest()[:12] if session else 'NONE'
    safe=''
    if fields.get('kind') in ('live','vod','series'):safe+=' kind='+fields['kind']
    if type(fields.get('total')) is int:safe+=' total='+str(max(0,min(1000000,fields['total'])))
    try:xbmc.log('[XCMate][SETUP37] stage='+stage+' session='+code+' mono_ms='+str(int(time.monotonic()*1000))+safe,xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass
