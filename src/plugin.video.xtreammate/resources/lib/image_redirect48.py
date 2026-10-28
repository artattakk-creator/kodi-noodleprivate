"""At most three credentialless public image redirects with pinned DNS/TLS.

API/bearer requests never enter here. Rebuild every request from fixed image
headers, no Cookie/Authorization/Referer forwarding, no HTTPS downgrade, no
URL credentials or private/local hosts. Existing download policy is untouched.
"""
from urllib.parse import urlsplit,urljoin
import time


def open_image(url,headers,connect,addresses,cancel=lambda:False,deadline=None):
    from media_sources43 import SourceError
    from artwork_visible import syntactic
    deadline=time.monotonic()+12 if deadline is None else deadline
    seen=set();initial=urlsplit(url)
    for hop in range(4):
        if cancel():raise SourceError('CANCELLED')
        if time.monotonic()>=deadline:raise SourceError('TIMEOUT')
        parsed=urlsplit(url)
        if url in seen or not syntactic(url):raise SourceError('REDIRECT_BLOCKED')
        seen.add(url)
        response=connect(url,addresses(url),{k:v for k,v in headers.items() if k in ('User-Agent','Accept','Accept-Encoding')})
        if time.monotonic()>=deadline:
            response.close();raise SourceError('TIMEOUT')
        if response.status not in (301,302,303,307,308):return response
        location=response.headers.get('Location','');response.close()
        if hop==3 or not location or len(location)>2048 or any(ord(c)<32 for c in location):raise SourceError('REDIRECT_BLOCKED')
        destination=urljoin(url,location);target=urlsplit(destination)
        if (target.scheme not in ('http','https') or parsed.scheme=='https' and target.scheme!='https'
                or target.fragment or target.username is not None or target.password is not None
                or target.port not in (None,80,443) and (target.hostname,target.port)!=(initial.hostname,initial.port)):
            raise SourceError('REDIRECT_BLOCKED')
        if not syntactic(destination):raise SourceError('UNSAFE_SOURCE')
        url=destination
    raise SourceError('REDIRECT_BLOCKED')
