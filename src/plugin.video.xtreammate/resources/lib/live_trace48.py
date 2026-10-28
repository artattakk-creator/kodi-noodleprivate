"""Session-correlated exit observations; no Player calls, URLs or titles."""
import hashlib
import json
import time
_last={}


def observe(value,job=None):
    if not value:return
    session=value.get('session',{})
    token=hashlib.sha256(json.dumps(['live',session.get('nonce')]).encode()).hexdigest()[:12]
    phase=value.get('phase','')
    if phase not in ('requested','stopping','home','complete','failed'):return
    job=job or {}
    stage=job.get('phase','NONE')
    if stage not in ('pending','running','complete','failed','timeout'):stage='NONE'
    signature=(phase,stage,bool(job.get('native_posted')),bool(job.get('worker_done')))
    if _last.get(token)==signature:return
    _last[token]=signature
    if len(_last)>16:_last.pop(next(iter(_last)))
    try:
        import xbmc,xbmcgui
        age=max(0,min(86400,int(time.time()-float(session.get('at',time.time())))))
        window=int(xbmcgui.getCurrentWindowId());dialog=int(xbmcgui.getCurrentWindowDialogId())
        origin='HOME' if value.get('origin_window48')==10000 else 'APP'
        xbmc.log('[XCMate][RETURN48] session='+token+' phase='+phase+' job='+stage+' posted='+str(int(bool(job.get('native_posted'))))+' ack='+str(int(bool(job.get('worker_done'))))+' age_seconds='+str(age)+' origin='+origin+' window='+str(window)+' dialog='+str(dialog),xbmc.LOGINFO)
    except (ImportError,AttributeError,RuntimeError,ValueError,TypeError):pass


def return_home(value):
    """Home widget returns to Home; preserve its native focus and bindings.

    Called only after positively completed own Stop and normal modal checks.
    Never re-enter the plugin root (which can start another background route).
    """
    if value.get('origin_window48')!=10000:return False
    import xbmc,xbmcgui
    from window_lifecycle import lease
    if lease() or int(xbmcgui.getCurrentWindowId()) not in (10000,10025,12005):return None
    if int(xbmcgui.getCurrentWindowId())!=10000:xbmc.executebuiltin('ActivateWindow(Home)',wait=False)
    return True
