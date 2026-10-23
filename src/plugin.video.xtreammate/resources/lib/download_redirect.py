"""Finite GET-only redirects, portal trust, per-hop DNS checks and IP pinning.

No cookie jar, automatic authentication, proxy credentials or redirected headers.
DNS results are connected directly; HTTPS verifies the original hostname/SNI.
"""
import hashlib,http.client,ipaddress,re,socket,ssl
from urllib.parse import urljoin,urlsplit
from urllib.error import HTTPError
from download_sources import DownloadFailure,validate

MAX_HOPS=5
SAFE_HEADERS={'accept','accept-encoding','range','if-range'}
LAN_NETWORKS=tuple(ipaddress.ip_network(n) for n in ('10.0.0.0/8','172.16.0.0/12','192.168.0.0/16','fc00::/7'))


def origin(url):
    validate(url)
    try:
        p=urlsplit(url);host=p.hostname.encode('idna').decode('ascii').lower();port=p.port or (443 if p.scheme=='https' else 80)
        if not 1<=port<=65535 or '%' in host or not re.fullmatch(r'[a-z0-9.:-]+',host):raise ValueError()
        if ':' not in host and (host.endswith('.') or any(not label or len(label)>63 or label.startswith('-') or label.endswith('-') for label in host.split('.'))):raise ValueError()
    except (ValueError,UnicodeError):raise DownloadFailure('REDIRECT_UNSAFE_HOST') from None
    return p.scheme+'://'+('['+host+']' if ':' in host else host)+((':'+str(port)) if port!=(443 if p.scheme=='https' else 80) else '')


def addresses(url,lan=False):
    p=urlsplit(origin(url));values=[]
    for entry in socket.getaddrinfo(p.hostname,p.port or (443 if p.scheme=='https' else 80),type=socket.SOCK_STREAM):
        ip=ipaddress.ip_address(entry[4][0])
        if ip.version==6 and (ip.sixtofour or ip.teredo or ip in ipaddress.ip_network('64:ff9b::/96') or ip in ipaddress.ip_network('64:ff9b:1::/48')):
            raise DownloadFailure('REDIRECT_PRIVATE_ADDRESS')
        if getattr(ip,'ipv4_mapped',None):ip=ip.ipv4_mapped
        permitted=ip.is_global and not (ip.is_multicast or ip.is_reserved)
        if lan and any(ip.version==net.version and ip in net for net in LAN_NETWORKS):permitted=True
        if not permitted:raise DownloadFailure('REDIRECT_PRIVATE_ADDRESS')
        if str(ip) not in values:values.append(str(ip))
    if not values:raise DownloadFailure('DNS_ERROR')
    return values


def mark(status,hop,cross,scheme,reason):
    if reason not in ('ALLOWED','REDIRECT_UNTRUSTED_TARGET','REDIRECT_PRIVATE_ADDRESS','REDIRECT_DOWNGRADE','REDIRECT_HOP_LIMIT','REDIRECT_LOOP','REDIRECT_UNSAFE_HOST','REDIRECT_INVALID_LOCATION','UNSUPPORTED_SOURCE'):reason='REDIRECT_BLOCKED'
    try:
        import xbmc
        xbmc.log('[XCMate][DOWNLOAD_REDIRECT] status_class={} hop={} cross={} scheme={} reason={}'.format(
            '3xx' if 300<=status<400 else 'source',min(MAX_HOPS+1,max(0,hop)),int(bool(cross)),scheme if scheme in ('http','https') else 'OTHER',reason),xbmc.LOGINFO)
    except (ImportError,AttributeError,RuntimeError):pass


def _connect(url,ips,headers):
    p=urlsplit(url);port=p.port or (443 if p.scheme=='https' else 80);connection=None
    try:
        raw=socket.create_connection((ips[0],port),timeout=10)
        if p.scheme=='https':
            try:raw=ssl.create_default_context().wrap_socket(raw,server_hostname=p.hostname)
            except BaseException:raw.close();raise
        connection=http.client.HTTPConnection(p.hostname,port,timeout=10);connection.sock=raw
        path=p.path or '/'
        if p.query:path+='?'+p.query
        connection.request('GET',path,headers=headers)
        response=connection.getresponse()
        return Response(response,connection,url)
    except BaseException:
        if connection:connection.close()
        raise


class Response:
    def __init__(self,response,connection,url):
        self.response=response;self.connection=connection;self.status=response.status;self.headers=response.headers
        self.source_fingerprint=hashlib.sha256(url.encode()).hexdigest()
    def read(self,count):return self.response.read(count)
    def close(self):
        try:self.response.close()
        finally:self.connection.close()


def open_source(url,headers,pid='',job_id='',transport=None):
    from download_trust import allowed,remember
    source=origin(url);seen=set();hop=0;crossed=False;current=url;redirect_status=0
    clean={str(k):str(v) for k,v in headers.items() if re.fullmatch('[A-Za-z0-9-]{1,64}',str(k)) and not any(c in str(v) for c in ('\r','\n','\0')) and str(k).lower() not in ('host','connection','proxy-authorization','proxy-connection','transfer-encoding','content-length')}
    clean['Accept-Encoding']='identity'
    while True:
        target=origin(current);cross=target!=source;p=urlsplit(current)
        if current in seen:mark(302,hop,cross,p.scheme,'REDIRECT_LOOP');raise DownloadFailure('REDIRECT_LOOP')
        seen.add(current)
        if hop>MAX_HOPS:mark(302,hop,cross,p.scheme,'REDIRECT_HOP_LIMIT');raise DownloadFailure('REDIRECT_HOP_LIMIT')
        try:
            ips=addresses(current,lan=allowed(pid,source,target,lan=True))
        except DownloadFailure as exc:
            if exc.code=='REDIRECT_PRIVATE_ADDRESS':remember(job_id,pid,source,target)
            mark(302 if hop else 0,hop,cross,p.scheme,exc.code);raise
        if cross and not allowed(pid,source,target):
            remember(job_id,pid,source,target);mark(302,hop,cross,p.scheme,'REDIRECT_UNTRUSTED_TARGET')
            raise DownloadFailure('REDIRECT_UNTRUSTED_TARGET')
        if hop:mark(redirect_status,hop,cross,p.scheme,'ALLOWED')
        if crossed:clean={k:v for k,v in clean.items() if k.lower() in SAFE_HEADERS}
        response=(transport or _connect)(current,ips,clean)
        if response.status not in (301,302,303,307,308):
            if response.status>=400:
                status=response.status;response.close();raise HTTPError('',status,'HTTP_ERROR',{},None)
            return response
        status=response.status;location=response.headers.get('Location','');response.close()
        if not isinstance(location,str) or not location or len(location)>16384 or any(ord(c)<32 for c in location):
            mark(status,hop+1,cross,p.scheme,'REDIRECT_INVALID_LOCATION');raise DownloadFailure('REDIRECT_INVALID_LOCATION')
        new=urljoin(current,location)
        try:next_origin=origin(new)
        except DownloadFailure as exc:mark(status,hop+1,True,'OTHER',exc.code);raise
        if p.scheme=='https' and urlsplit(new).scheme!='https':
            mark(status,hop+1,next_origin!=target,'http','REDIRECT_DOWNGRADE');raise DownloadFailure('REDIRECT_DOWNGRADE')
        hop+=1;crossed=crossed or next_origin!=target
        redirect_status=status;current=new
