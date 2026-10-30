"""Property-only timeout evidence; cannot repair a wedged Kodi native queue."""
import hashlib,json
_last={}


def observe(value):
    if not value or value.get('token',[None])[0]!='live':return
    if value.get('phase')!='timeout':return
    posted=bool(value.get('native_posted'))
    from native_stop41 import returned
    try:ack=bool(posted and returned(value))
    except (AttributeError,RuntimeError,ValueError,TypeError):return
    code=('NATIVE_QUEUE_UNRETURNED' if posted and not ack else
          'PREPARE_QUEUE_UNRETURNED' if value.get('prepare_posted42') and not value.get('prepare_done42') else
          'STOP_RETURNED_LATE' if posted and ack else 'STOP_NOT_POSTED')
    strategy=value.get('strategy42','UNSELECTED')
    if strategy not in ('direct41','fullscreen42'):strategy='UNSELECTED'
    token=hashlib.sha256(json.dumps(['live',value['token'][1].get('nonce')]).encode()).hexdigest()[:12]
    signature=(code,strategy)
    if _last.get(token)==signature:return
    _last[token]=signature
    if len(_last)>16:_last.pop(next(iter(_last)))
    import xbmc
    try:xbmc.log('[XCMate][STOP58] session='+token+' code='+code+' strategy='+strategy+
             ' native_posted='+str(int(posted))+' native_ack='+str(int(ack)),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass
