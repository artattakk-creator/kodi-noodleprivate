"""Bounded, secret-free transfer reasons; no recorder dependency for downloads."""
import re
import socket
import ssl
from urllib.error import HTTPError,URLError


def _token(value,default='UNKNOWN'):
    return value if isinstance(value,str) and re.fullmatch('[A-Z][A-Z0-9_]{0,63}',value) else default


def encode(value,fallback=''):
    if isinstance(value,dict):code=value.get('code','');step=value.get('step','');number=value.get('errno',0)
    elif isinstance(value,str):
        match=re.fullmatch(r'([A-Z][A-Z0-9_]{0,63})(?:@([A-Z][A-Z0-9_]{0,31}):([0-9]{1,4}))?',value)
        return value if match else '' if not value else 'UNKNOWN'
    else:
        code=getattr(value,'code','');step=getattr(value,'step','');number=getattr(value,'number',getattr(value,'errno',0)) or 0
        if not isinstance(code,str) or not code:
            if isinstance(value,HTTPError):code='HTTP_AUTH' if value.code in (401,403) else 'HTTP_LIMIT' if value.code==429 else 'HTTP_ERROR'
            elif isinstance(value,URLError):return encode(value.reason,fallback)
            elif isinstance(value,ssl.SSLError):code='TLS_ERROR'
            elif isinstance(value,socket.gaierror):code='DNS_ERROR'
            elif isinstance(value,(TimeoutError,socket.timeout)):code='TIMEOUT'
            elif isinstance(value,ValueError) and str(value) in ('RECORDING_BUSY','INVALID_DURATION','UNSUPPORTED_TARGET'):code=str(value)
            else:code=fallback or 'ACTION_FAILED'
    if not code:return ''
    code=_token(code);step=_token(step,'')
    number=number if isinstance(number,int) and 0<=number<=4095 else 0
    if number and not step:step='IO'
    return code+('@'+step+':'+str(number) if step else '')


def describe(value,component='capture'):
    from localization import tr
    encoded=encode(value)
    if not encoded:return ''
    code=encoded.split('@')[0]
    if code.startswith('REDIRECT_'):ident=34610
    elif code.startswith('TARGET_') or code in ('UNSUPPORTED_TARGET','DISK_FULL','NO_SPACE'):ident=34400
    elif code.startswith('HTTP_'):ident=34402
    elif code in ('TIMEOUT','DNS_ERROR','TLS_ERROR','CONNECTION_ERROR','NETWORK_ERROR'):ident=34405
    elif code in ('CANCELLED','INTERRUPTED','SERVICE_INTERRUPTED'):ident=34406
    elif code.startswith('SOURCE_') or code in ('UNSUPPORTED_MANIFEST','NOT_DIRECT_TS','ENCRYPTED_TS','UNSUPPORTED_HEADERS','UNSUPPORTED_PORTAL','PORTAL_UNAVAILABLE','CHANNEL_UNAVAILABLE','INVALID_SOURCE','TS_PROBE_LIMIT','PROTECTED_SOURCE','UNSUPPORTED_SOURCE','INVALID_MEDIA','LENGTH_REQUIRED'):
        ident=34404 if component=='download' else 34401
    else:ident=34404 if component=='download' else 34403
    return tr(ident)+'\n'+encoded


def mark(component,stage,value=''):
    if component not in ('CAPTURE','DOWNLOAD') or stage not in ('TARGET_READY','SOURCE_RESOLVE','STATE','FAILED'):return
    try:
        import xbmc
        count=value.get('bytes',0) if isinstance(value,dict) else 0
        status=value.get('status','') if isinstance(value,dict) else ''
        status=status if status in ('pending','starting','recording','complete','partial','failed') else ''
        xbmc.log('[XCMate][{}] stage={} reason={} status={} bytes={}'.format(component,stage,encode(value),status,count if isinstance(count,int) and count>=0 else 0),xbmc.LOGINFO)
    except (ImportError,AttributeError,RuntimeError):pass
