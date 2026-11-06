"""Correlated, bounded pipeline evidence. Never claims Android visual PASS."""
import hashlib,json,time
_seen={}
STAGES={'EPG_EVENT','MATCHED_EVENT_FACTS','IMAGE_SOURCE_SELECTION','MATCH_CONFIDENCE','URL_SECURITY','HTTP_RESPONSE','LOCAL_CACHE','EVENT_REVISION','IMAGE_LEASE','BINGIE_SKIN_PROPERTY','RENDER_CONTROL','ACTUAL_TEXTURE'}
CODES={'IDENTIFIED','SOURCE_READY','SOURCE_MISSING','EXACT_MATCH','SOURCE_SELECTED','APPROVED','BLOCKED','IMAGE_DECODED','REFERENCE_VERIFIED','PERSISTED','RAM_ONLY','LOCAL_READY','BOUND','CONTROL_MISSING','IMAGE_REQUESTED','TEXTURE_CACHED','TEXTURE_PENDING','TEXTURE_UNAVAILABLE'}
def note(event,stage,code,**facts):
    if stage not in STAGES or code not in CODES:return
    from programme_requests68 import identity
    tag=identity(event)[:12];now=time.monotonic();key=(tag,stage,code)
    if now-_seen.get(key,-1e9)<30:return
    _seen[key]=now
    while len(_seen)>256:_seen.pop(next(iter(_seen)))
    clean={k:v for k,v in facts.items() if k in ('control','width','height','count','visible') and type(v) in (int,bool)}
    import xbmc
    try:xbmc.log('[XCMate][IMAGE77] event='+tag+' stage='+stage+' code='+code+' '+json.dumps(clean,separators=(',',':')),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass

def texture(event,art):
    """Explicit diagnostic worker only: actual Kodi texture-cache evidence.

    A cached texture plus a requested control is not a substitute for the
    required Android screenshot. No URLs, paths or hashes are returned.
    """
    import xbmc
    from programme_image69 import eligible
    if not eligible(art,event):return dict(code='TEXTURE_PENDING')
    url=art.get('image','')
    try:
        request=dict(jsonrpc='2.0',id=77,method='Textures.GetTextures',params=dict(filter=dict(field='url',operator='is',value=url),properties=['url','cachedurl','sizes']))
        response=json.loads(xbmc.executeJSONRPC(json.dumps(request)))
        rows=response.get('result',{}).get('textures',[])
        value=next((size for row in rows if row.get('url')==url and row.get('cachedurl') for size in row.get('sizes',[]) if type(size.get('width')) is int and type(size.get('height')) is int and size['width']>0 and size['height']>0),None)
        result=dict(code='TEXTURE_CACHED',width=value['width'],height=value['height']) if value else dict(code='TEXTURE_PENDING')
    except (AttributeError,RuntimeError,ValueError,TypeError):result=dict(code='TEXTURE_UNAVAILABLE')
    note(event,'ACTUAL_TEXTURE',result['code'],**{k:v for k,v in result.items() if k!='code'})
    return result
