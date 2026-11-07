"""Canonical exact-source image references; never follows plaintext HTTP.

HTTP metadata may be upgraded to the same origin's HTTPS endpoint; only its
fully verified HTTPS response can be published. No host discovery/wildcards.
"""
import html,ipaddress,re
from urllib.parse import urlsplit,urlunsplit,quote

def canonical(raw):
    if not isinstance(raw,str) or not 1<len(raw)<=2048 or any(ord(c)<32 for c in raw) or any(c in raw for c in ('\\','|')):return ''
    try:
        value=html.unescape(raw.strip());p=urlsplit(value)
        if p.scheme not in ('http','https') or p.username is not None or p.password is not None or p.fragment or p.port not in (None,80 if p.scheme=='http' else 443):return ''
        host=(p.hostname or '').encode('idna').decode().lower()
        if not re.fullmatch('[a-z0-9.-]+',host) or '.' not in host or host.endswith(('.local','.localhost','.internal','.invalid','.test')):return ''
        try:ipaddress.ip_address(host);return ''
        except ValueError:pass
        from programme_url77 import public_query
        if not public_query(p.query) or not p.path or p.path=='/':return ''
        path=quote(p.path,safe="/%-._~!$&'()*+,;=:")
        from urllib.parse import unquote
        decoded=unquote(path)
        if any(part in ('.','..') for part in decoded.split('/')) or '@' in decoded or '\\' in decoded or any(ord(c)<32 for c in decoded):return ''
        return urlunsplit(('https',host,path,p.query,''))
    except (ValueError,UnicodeError,TypeError):return ''
