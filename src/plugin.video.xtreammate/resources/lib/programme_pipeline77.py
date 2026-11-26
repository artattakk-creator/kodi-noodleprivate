"""Correlated, bounded pipeline evidence. Never claims Android visual PASS."""
import hashlib,json,threading,time
_seen={}
_agent_seen={};_agent_lock=threading.Lock()
STAGES={'EPG_EVENT','MATCHED_EVENT_FACTS','IMAGE_SOURCE_SELECTION','MATCH_CONFIDENCE','URL_SECURITY','HTTP_RESPONSE','LOCAL_CACHE','EVENT_REVISION','IMAGE_LEASE','BINGIE_SKIN_PROPERTY','RENDER_CONTROL','ACTUAL_TEXTURE'}
CODES={'IDENTIFIED','SOURCE_READY','SOURCE_MISSING','EXACT_MATCH','SOURCE_SELECTED','APPROVED','BLOCKED','IMAGE_DECODED','REFERENCE_VERIFIED','PERSISTED','RAM_ONLY','LOCAL_READY','BOUND','CONTROL_MISSING','IMAGE_REQUESTED','TEXTURE_CACHED','TEXTURE_PENDING','TEXTURE_UNAVAILABLE'}
AGENT_STAGES={'FACTS','URL','FETCH','DECODE','CACHE'}
AGENT_CODES={'READY','APPROVED','IMAGE_DECODED','AGENT_IMAGE_SHAPE','AGENT_CACHE_UNAVAILABLE',
             'AGENT_REFERENCE_MISSING','AGENT_REFERENCE_REJECTED','AGENT_REFERENCE_UNAVAILABLE','AGENT_ROLE_MISSING','AGENT_ART_DISABLED',
             'BLOCKED_IMAGE_HOST_OR_URL','BLOCKED_CREDENTIAL_URL','UNSAFE_SOURCE','DNS_ERROR','TLS_ERROR','CONNECTION_ERROR',
             'REDIRECT_PRIVATE_ADDRESS','REDIRECT_UNSAFE_HOST',
             'REDIRECT_BLOCKED','HTTP_AUTH','HTTP_NOT_FOUND','HTTP_RATE_LIMIT','HTTP_SERVER','HTTP_CLIENT',
             'CONTENT_TYPE','CONTENT_ENCODING','IMAGE_LIMIT','INVALID_IMAGE','IMAGE_DECODER_MISSING',
             'CANCELLED','TIMEOUT','IMAGE_PREFLIGHT_FAILED','REQUEST_QUEUE_FULL','FETCH_FAILED'}


def agent_stage(event,stage,code,candidate=None,uri=''):
    """Log only fixed role/host classes and redacted event correlation."""
    from urllib.parse import urlsplit
    from agent_programme100 import PERSON_ROLES, ROLE_ORDER, SOURCES
    if stage not in AGENT_STAGES:return
    code=code if code in AGENT_CODES else 'FETCH_FAILED'
    candidate=candidate or {}
    source=candidate.get('source')
    source=source if source in SOURCES else 'agent'
    role=candidate.get('role81')
    role=role if role in ROLE_ORDER+PERSON_ROLES else 'none'
    try:host=urlsplit(uri).hostname
    except (ValueError,TypeError):host=None
    host_class={'image.tmdb.org':'TMDB_CDN','static.tvmaze.com':'TVMAZE_CDN'}.get(host,'OTHER' if host else 'NONE')
    tag=__import__('hero_timing87').correlation(event)[:12]
    signature=(tag,stage,code,source,role,host_class)
    now=time.monotonic()
    with _agent_lock:
        if now-_agent_seen.get(signature,-1e9)<30:return
        _agent_seen[signature]=now
        if len(_agent_seen)>256:_agent_seen.pop(next(iter(_agent_seen)))
    import xbmc
    try:xbmc.log(f'[XCMate][AGENT104] event={tag} stage={stage} code={code} source={source} role={role} host={host_class}',xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass
def note(event,stage,code,**facts):
    if stage not in STAGES or code not in CODES:return
    __import__('hero_timing87').pipeline(event,stage,code)
    tag=__import__('hero_timing87').correlation(event)[:12];now=time.monotonic();key=(tag,stage,code)
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
        value=None
        # Kodi can canonicalize transport-only | options before indexing a
        # texture. Inspect only the exact verified URL and its base form.
        for exact in dict.fromkeys((url,url.partition('|')[0])):
            request=dict(jsonrpc='2.0',id=77,method='Textures.GetTextures',params=dict(filter=dict(field='url',operator='is',value=exact),properties=['url','cachedurl','sizes']))
            response=json.loads(xbmc.executeJSONRPC(json.dumps(request)))
            if response.get('error'):return dict(code='TEXTURE_UNAVAILABLE')
            rows=response.get('result',{}).get('textures',[])
            value=next((size for row in rows if row.get('url')==exact and row.get('cachedurl') for size in row.get('sizes',[]) if type(size.get('width')) is int and type(size.get('height')) is int and size['width']>0 and size['height']>0),None)
            if value:break
        result=dict(code='TEXTURE_CACHED',width=value['width'],height=value['height']) if value else dict(code='TEXTURE_PENDING')
    except (AttributeError,RuntimeError,ValueError,TypeError):result=dict(code='TEXTURE_UNAVAILABLE')
    note(event,'ACTUAL_TEXTURE',result['code'],**{k:v for k,v in result.items() if k!='code'})
    return result
