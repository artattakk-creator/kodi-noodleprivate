"""Sanitised artwork transport classes. No URL or exception text escapes."""
import socket
import ssl
from urllib.error import HTTPError,URLError

CODES=('HTTP_AUTH','HTTP_NOT_FOUND','HTTP_RATE_LIMIT','HTTP_SERVER','HTTP_CLIENT','DNS_ERROR','TLS_ERROR','TIMEOUT','CONNECTION_ERROR')
PERMANENT=frozenset(('HTTP_AUTH','HTTP_NOT_FOUND','HTTP_CLIENT','TLS_ERROR','INVALID_SOURCE','INVALID_IMAGE'))


def classify(error):
    seen=set();current=error
    for _ in range(6):
        if id(current) in seen:break
        seen.add(id(current))
        if type(current).__name__ in ('InvalidURL','InvalidSchema','MissingSchema','URLRequired'):return 'INVALID_SOURCE'
        status=getattr(current,'code',None)
        response=getattr(current,'response',None)
        if not isinstance(status,int):status=getattr(response,'status_code',None)
        if isinstance(status,int):
            if status in (401,403):return 'HTTP_AUTH'
            if status in (404,410):return 'HTTP_NOT_FOUND'
            if status==429:return 'HTTP_RATE_LIMIT'
            if status>=500:return 'HTTP_SERVER'
            if 400<=status<500:return 'HTTP_CLIENT'
        if isinstance(current,socket.gaierror):return 'DNS_ERROR'
        if isinstance(current,ssl.SSLError):return 'TLS_ERROR'
        if isinstance(current,(TimeoutError,socket.timeout)) or type(current).__name__ in ('ConnectTimeout','ReadTimeout','WriteTimeout','PoolTimeout'):return 'TIMEOUT'
        reason=getattr(current,'reason',None)
        following=reason if isinstance(reason,BaseException) else current.__cause__ or current.__context__
        if following is None:break
        current=following
    if isinstance(error,ConnectionError) or type(error).__name__ in ('ConnectError','ReadError','RemoteProtocolError'):return 'CONNECTION_ERROR'
    return 'NETWORK_ERROR'


def retry_after(error):
    headers=getattr(error,'headers',None) or getattr(getattr(error,'response',None),'headers',None) or {}
    try:
        text=str(headers.get('Retry-After',''))
        if text.isdigit():return min(86400,max(60,int(text)))
        from email.utils import parsedate_to_datetime
        import time
        return min(86400,max(60,int(parsedate_to_datetime(text).timestamp()-time.time())))
    except (ValueError,TypeError,OverflowError,AttributeError):return 300
