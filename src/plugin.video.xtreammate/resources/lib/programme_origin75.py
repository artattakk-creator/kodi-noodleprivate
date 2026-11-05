"""Exact configured event-origin admission, never a host wildcard.

Only the worker may grant a short lease AFTER pinned public-DNS/TLS/image
preflight. Renderer reads hashed evidence; redirects stay disabled. No token,
query, literal IP, local network or credential path is admissible.
"""
import hashlib,ipaddress,json,re,time
from urllib.parse import urlsplit,unquote

def candidate(event,url,source):
    field={'xmltv_event':'xmltv_image','provider_event':'provider_image'}.get(source)
    if not field or not event.get('key') or event.get(field)!=url:return False
    if not event.get('canonical') or not event.get('pid') or not event.get('sid'):return False
    try:
        if not isinstance(url,str) or not 1<len(url)<=2048 or any(ord(c)<33 or ord(c)>126 for c in url):return False
        p=urlsplit(url);decoded=unquote(p.path)
        if p.scheme!='https' or p.port not in (None,443) or not p.hostname or p.query or p.fragment or p.username is not None or p.password is not None:return False
        if not re.fullmatch(r'[a-zA-Z0-9.-]+',p.hostname) or '.' not in p.hostname or p.hostname.endswith(('.local','.localhost','.internal','.invalid','.test')):return False
        try:ipaddress.ip_address(p.hostname);return False
        except ValueError:pass
        if not p.path or p.path=='/' or any(c in url+decoded for c in ('\\','|','@')) or any(ord(c)<32 for c in decoded):return False
        if any(part in ('.','..') for part in decoded.split('/')):return False
        from portals import get_by_id
        portal=get_by_id(str(event['pid'])) or {}
        if not portal:return False
        for key in ('xc_user','xc_pass'):
            secret=str(portal.get(key) or '')
            if secret and (secret in decoded.split('/') or len(secret)>=4 and secret in decoded):return False
        return True
    except (ValueError,TypeError,KeyError):return False

def _key(url):return 'XCMate.EventOrigin75.'+hashlib.sha256(url.encode()).hexdigest()[:32]

def grant(url):
    import xbmcgui
    from epg_handoff63 import profile_scope
    # Fixed slots prevent unbounded Home properties; collision is a miss.
    key=_key(url);slot='XCMate.EventOrigin75.'+str(int(key.rsplit('.',1)[1][:8],16)%128)
    xbmcgui.Window(10000).setProperty(slot,json.dumps(dict(key=key,profile=profile_scope(),until=time.time()+300)))

def approved(url):
    import xbmcgui
    from epg_handoff63 import profile_scope
    try:
        key=_key(url);slot='XCMate.EventOrigin75.'+str(int(key.rsplit('.',1)[1][:8],16)%128)
        raw=xbmcgui.Window(10000).getProperty(slot);value=json.loads(raw) if raw and len(raw)<512 else {}
        return value.get('key')==key and value.get('profile')==profile_scope() and 0<value.get('until',0)-time.time()<=300
    except (AttributeError,RuntimeError,TypeError,ValueError):return False
