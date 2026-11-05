"""Bounded property-only evidence for native Stop; never retries a stuck Stop.

Python cannot repair CVideoPlayer/MediaCodec/AudioSink deadlocks. Preserve the
explicit .42 compatibility choice and native FIFO completion requirement.
"""
import hashlib,time
_seen={}

def observe(value):
    if not value or value.get('token',[None])[0]!='live' or not value.get('native_posted'):return
    from native_stop41 import returned
    from live_stop42 import ACK
    import xbmc,xbmcgui
    key=hashlib.sha256(str(value['token'][1].get('nonce','')).encode()).hexdigest()[:12]
    posted=value.get('posted_at75')
    if type(posted) not in (int,float):return
    age=time.monotonic()-posted
    ack=returned(value);stage='ACK' if ack else 'WAIT_10S' if age>=10 else 'WAIT_5S' if age>=5 else 'POSTED'
    signature=(key,stage)
    if signature in _seen:return
    _seen[signature]=time.monotonic()
    while len(_seen)>64:_seen.pop(next(iter(_seen)))
    # Window properties do not take the native player lock. No isPlaying,
    # InfoTag, getPlayingFile, ActivateWindow or Stop while the ACK is absent.
    fields=' native_ack='+str(int(ack))+' elapsed_ms='+str(max(0,int(age*1000)))
    fields+=' strategy='+('fullscreen42' if value.get('strategy42')=='fullscreen42' else 'direct41')
    fields+=' prepare_ack='+str(int(bool(value.get('prepare_ack42') and xbmcgui.Window(10000).getProperty(ACK)==value['prepare_ack42'])))
    try:xbmc.log('[XCMate][STOP75] session='+key+' stage='+stage+fields,xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass
