"""Exact event-image preflight: finite trusted redirects and complete decode.

No API/bearer request, cookies, query credentials or network work on GUI. A
cross-origin hop requires a separately configured/known image host, never '*'.
"""
import time
from urllib.parse import urlsplit

def verified(url,cancel=lambda:False,connect=None,resolver=None,keep_data81=False):
    from programme_urls55 import safe,hosts
    from download_redirect import addresses,_connect
    from image_redirect48 import open_image
    from media_sources43 import SourceError,validate_image,MAX_IMAGE
    initial=urlsplit(url).hostname;final=[url];deadline=time.monotonic()+12
    def guarded(target,ips,headers):
        parsed=urlsplit(target)
        if parsed.scheme!='https' or parsed.port not in (None,443) or not __import__('programme_url77').public_query(parsed.query) or parsed.fragment or parsed.username is not None or parsed.password is not None:raise SourceError('REDIRECT_BLOCKED')
        # safe() requires a lease for event origins. Validate syntax against
        # that exact origin without expanding the global hostname allowlist.
        from programme_urls55 import hosts
        if parsed.hostname!=initial and parsed.hostname not in hosts():raise SourceError('REDIRECT_BLOCKED')
        if any(c in target for c in ('\\','|')) or any(ord(c)<33 or ord(c)>126 for c in target):raise SourceError('UNSAFE_SOURCE')
        from urllib.parse import unquote
        decoded=unquote(parsed.path)
        if any(p in ('.','..') for p in decoded.split('/')) or any(c in decoded for c in ('\\','|','@')) or any(ord(c)<32 for c in decoded):raise SourceError('UNSAFE_SOURCE')
        from portals import get_active
        for portal in get_active()[:16]:
            for field in ('xc_user','xc_pass'):
                secret=str(portal.get(field) or '')
                if secret and (secret in decoded.split('/') or len(secret)>=4 and secret in decoded):raise SourceError('BLOCKED_CREDENTIAL_URL')
        if parsed.hostname in hosts() and not safe(target):raise SourceError('UNSAFE_SOURCE')
        final[0]=target
        return (connect or _connect)(target,ips,headers)
    response=None
    try:
        response=open_image(url,{'User-Agent':'XCMate event image','Accept':'image/jpeg,image/png','Accept-Encoding':'identity'},guarded,resolver or addresses,cancel,deadline)
        status=response.status
        if status in (401,403):raise SourceError('HTTP_AUTH')
        if status in (404,410):raise SourceError('HTTP_NOT_FOUND')
        if status==429:raise SourceError('HTTP_RATE_LIMIT')
        if status!=200:raise SourceError('HTTP_SERVER' if status>=500 else 'HTTP_CLIENT')
        if response.headers.get('Content-Type','').partition(';')[0].strip().lower() not in ('image/jpeg','image/png'):raise SourceError('CONTENT_TYPE')
        if response.headers.get('Content-Encoding','identity').lower() not in ('','identity'):raise SourceError('CONTENT_ENCODING')
        data=bytearray()
        while True:
            if cancel():raise SourceError('CANCELLED')
            if time.monotonic()>deadline:raise SourceError('TIMEOUT')
            part=response.read(min(65536,MAX_IMAGE-len(data)+1))
            if not part:break
            data.extend(part)
            if len(data)>MAX_IMAGE:raise SourceError('IMAGE_LIMIT')
        width,height=validate_image(bytes(data))
        result=dict(url=final[0],width=width,height=height,bytes=len(data),decoded77=True)
        if keep_data81:result['_body81']=bytes(data)
        return result
    except SourceError:raise
    except Exception:
        raise SourceError('IMAGE_PREFLIGHT_FAILED') from None
    finally:
        if response is not None:response.close()
