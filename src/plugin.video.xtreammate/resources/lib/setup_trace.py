"""Fixed wizard phases, monotonic milliseconds and anonymous correlation only."""
import hashlib
import time

STAGES=frozenset(('SAVE_BEGIN','COPY_CATALOG','COPY_GUIDE','CONFIG_PUBLISH','VERIFY','SAVE_DONE','SAVE_FAILED','GUI_CLOSE_BEGIN','GUI_CLOSE_DONE','NATIVE_RELEASED','HOME_REQUESTED'))


def mark(stage,session=''):
    if stage not in STAGES:return
    import xbmc
    code=hashlib.sha256(str(session).encode()).hexdigest()[:12] if session else 'NONE'
    try:xbmc.log('[XCMate][SETUP37] stage='+stage+' session='+code+' mono_ms='+str(int(time.monotonic()*1000)),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass
