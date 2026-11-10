"""Separate cached rows / publication / native controls; never invent pixels."""
import json,time
_seen={}

def note(stage,kind,**facts):
    allowed={'CACHED_ITEMS_READY','LISTITEM_PUBLISHED','SKIN_CONTROL_ACTIVE','IMAGE_DECODE_REQUESTED','IMAGE_PENDING'}
    if stage not in allowed or kind not in ('live','vod','series'):return
    import xbmc,xbmcgui
    window=xbmcgui.Window(10000)
    try:
        raw=window.getProperty('XCMate.Home75.Schedule');state=json.loads(raw) if raw and len(raw)<8192 else {}
    except (ValueError,TypeError):state={}
    context=state.get('context','UNCONFIGURED');now=time.monotonic();tag=(context,kind,stage)
    semantic=tuple(sorted((k,v) for k,v in facts.items() if k in ('count','local_images','approved_refs','control','generation')))
    old86=_seen.get(tag)
    if isinstance(old86,tuple) and (stage=='CACHED_ITEMS_READY' and old86[1]==semantic or now-old86[0]<30 and old86[1]==semantic):return
    _seen[tag]=(now,semantic)
    while len(_seen)>128:_seen.pop(next(iter(_seen)))
    clean={k:v for k,v in facts.items() if k in ('count','local_images','approved_refs','control') and type(v) is int}
    if isinstance(facts.get('generation'),str) and len(facts['generation'])==64:clean['generation']=facts['generation'][:16]
    value=dict(stage=stage,kind=kind,elapsed_ms=max(0,int((now-state.get('at',now))*1000)),android_render_verified=False,**clean)
    window.setProperty('XCMate.Home82.'+kind+'.'+stage,json.dumps(value,separators=(',',':')))
    try:xbmc.log('[XCMate][HOME82] '+json.dumps(value,separators=(',',':')),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass
