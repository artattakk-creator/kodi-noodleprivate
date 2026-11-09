"""Exact-event display-only leases for decoded images under storage pressure.

RAM_ONLY is not persistence or render proof. Existing pinned transport, match,
credential, source-consent and public-DNS checks remain mandatory. Only the
existing programme worker renews leases; GUI readers never resolve DNS/fetch.
"""
import hashlib
import json
import time
from urllib.parse import urlsplit
PREFIX='XCMate.EventDisplay84.'


def _account(pid):
    from portals import get_by_id
    portal=get_by_id(str(pid)) or {}
    return hashlib.sha256(json.dumps([portal.get(k) for k in ('id','type','xc_host','xc_user','xc_pass','enabled')],sort_keys=True).encode()).hexdigest()


def key(event):
    from programme_requests68 import identity
    from programme_art46 import fingerprint
    from programme_policy68 import negative_scope
    return hashlib.sha256((identity(event)+fingerprint(event)+negative_scope({})+_account(event.get('pid'))).encode()).hexdigest()


def _slot(tag):return PREFIX+str(int(tag[:8],16)%128)


def _load(tag):
    import xbmcgui
    try:
        raw=xbmcgui.Window(10000).getProperty(_slot(tag))
        value=json.loads(raw) if raw and len(raw)<16384 else {}
        return value if value.get('key84')==tag else {}
    except (ValueError,TypeError,AttributeError,RuntimeError):return {}


def verify(art,event=None):
    from programme_requests68 import scope,identity
    from programme_policy68 import negative_scope
    tag=art.get('display_key84','')
    if not isinstance(tag,str) or len(tag)!=64:return False
    value=_load(tag);old=value.get('art',{});now=time.time()
    if value.get('profile')!=scope() or old.get('policy69')!=negative_scope({}):return False
    if value.get('account84')!=_account(value.get('pid84')):return False
    if __import__('widget_refs74').revoked(old.get('source_url','')):return False
    until=old.get('until',0)
    if type(until) not in (int,float) or not 0<until-now<=30:return False
    if event is not None:
        from programme_art46 import fingerprint
        if key(event)!=tag or old.get('scope69')!=identity(event) or old.get('fingerprint')!=fingerprint(event):return False
    return all(art.get(k)==old.get(k) for k in ('key','image','source_url','scope69','profile69','fingerprint','source','match','until'))


def read(event):
    value=_load(key(event)).get('art',{})
    if not value:return {}
    from programme_image69 import eligible
    return dict(value) if eligible(value,event) else {}


def _publish(event,value,validated_until):
    from programme_requests68 import identity,scope
    from programme_art46 import fingerprint
    from programme_policy68 import negative_scope
    from programme_urls55 import safe,OPTIONS
    from widget_assets69 import safe as provider_safe
    from portals import get_by_id
    from artwork_visible import public_dns,_dns_cache,_lock
    from artwork_display84 import note
    url=value.get('source_url','');now=time.time()
    portal=get_by_id(str(event.get('pid',''))) or {}
    if not portal or not provider_safe(portal,url) or not safe(url):return None
    if not public_dns(url):
        if __import__('widget_refs74').revoked(url):
            import xbmcgui
            xbmcgui.Window(10000).clearProperty(_slot(key(event)))
        return None
    from programme_image69 import eligible
    admission=dict(value,until=now+1)
    admission.pop('display84',None);admission.pop('display_key84',None)
    if not eligible(admission,event):return None
    parts=urlsplit(url)
    with _lock:dns=_dns_cache.get((parts.hostname,443))
    remaining=min(30,max(0,dns[0]-time.monotonic())) if dns and dns[1] else 0
    until=min(now+remaining,validated_until,float(event.get('stop',now)))
    if until<=now:return None
    tag=key(event)
    art=dict(value,code='READY',key=event['key'],fingerprint=fingerprint(event),
             image=url+OPTIONS,thumbnail=url+OPTIONS,url_version55=1,url_verified69=True,
             scope69=identity(event),profile69=scope(),policy69=negative_scope({}),until=until,
             display84=True,display_key84=tag,persisted69=False,storage69='RAM_ONLY')
    # A body decoded for another event may never be rebound by this API.
    if value.get('scope69')!=identity(event) or value.get('fingerprint')!=fingerprint(event):return None
    import xbmcgui
    raw=json.dumps(dict(key84=tag,profile=scope(),pid84=str(event.get('pid','')),account84=_account(event.get('pid')),validated_until=validated_until,art=art),separators=(',',':'))
    if len(raw)>16384:return None
    xbmcgui.Window(10000).setProperty(_slot(tag),raw)
    note('event','RAM_ONLY',width=int(value.get('image_width77',0)),height=int(value.get('image_height77',0)))
    return art


def remember(event,value):
    """Producer only, called after genuine complete image decode."""
    if not value.get('decoded77') or value.get('code')!='READY' or value.get('url_verified69') is not True:return value
    from programme_image69 import eligible
    if not eligible(value,event):return value
    approved=_publish(event,value,min(time.time()+300,float(event.get('stop',0))))
    if approved:return approved
    from artwork_display84 import note
    note('event','SOURCE_BLOCKED')
    return dict(key=event['key'],fingerprint=value.get('fingerprint'),code='DISPLAY_URL_BLOCKED',
                image=event['placeholder'],source='placeholder',match='NONE',until=time.time()+30)


def renew(event):
    """Existing worker only: DNS renewal, no repeat image download for 5 min."""
    from programme_requests68 import scope
    value=_load(key(event))
    if value.get('profile')!=scope() or value.get('validated_until',0)<=time.time():return None
    return _publish(event,value.get('art',{}),value['validated_until'])


def recover(event):
    """Worker-only cold recovery of a decoded Kodi file for an exact feed URL.

    No guessed TMDB/title matching, HTTP, origin grant or new metadata file.
    A cached file is not evidence of current Android GUI visibility.
    """
    import xbmc
    from portals import get_by_id
    from widget_assets69 import safe
    from widget_cache82 import variants,decoded
    portal=get_by_id(str(event.get('pid',''))) or {};wanted={}
    if not portal:return None
    from image_reference78 import canonical
    for field,source in (('xmltv_image','xmltv_event'),('provider_image','provider_event')):
        url=canonical(event.get(field)) or ''
        if not url or not safe(portal,url):continue
        for variant in variants(url):wanted[variant]=(url,source)
    if not wanted:return None
    request=dict(jsonrpc='2.0',id=84,method='Textures.GetTextures',params=dict(filter={'or':[
        dict(field='url',operator='is',value=url) for url in wanted]},properties=['url','cachedurl','sizes']))
    try:
        raw=xbmc.executeJSONRPC(json.dumps(request))
        if not isinstance(raw,str) or len(raw)>262144:return None
        response=json.loads(raw);textures=response.get('result',{}).get('textures',[])
        if not isinstance(textures,list):return None
        for texture in textures[:32]:
            if not isinstance(texture,dict) or texture.get('url') not in wanted:continue
            url,source=wanted[texture['url']];record=decoded(texture,url)
            if not record:continue
            from programme_requests68 import identity,scope
            from programme_art46 import fingerprint
            from programme_policy68 import negative_scope
            return dict(code='READY',key=event['key'],fingerprint=fingerprint(event),
                        source=source,match='EXACT_EVENT',image=record['file'],thumbnail=record['file'],
                        sha256=record['sha256'],scope69=identity(event),profile69=scope(),policy69=negative_scope({}),
                        until=min(time.time()+86400,float(event.get('stop',0))),persisted69=False,
                        storage69='KODI_TEXTURE_CACHE',decoded77=True,image_width77=record['width'],image_height77=record['height'])
    except (OSError,ValueError,TypeError,AttributeError,RuntimeError):return None
    return None
