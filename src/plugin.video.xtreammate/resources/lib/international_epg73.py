"""Opt-in extension of the existing EPG source manager, never a new importer.

Only reviewed HTTPS registry endpoints, full bounded XML/gzip verification,
public DNS, same-origin redirects, explicit activation, no mass downloads.
"""
import gzip
import hashlib
import ipaddress
import json
import os
import socket
import tempfile
import time
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, build_opener, Request
from vodsync_api72 import SyncError

MAX_BYTES=256*1024*1024
DOWNLOAD_BYTES=64*1024*1024


def registry():
    with open(os.path.join(os.path.dirname(__file__),'..','international_sources73.json'),encoding='utf-8') as stream:
        return json.load(stream)


def countries(continent=None):
    from utils import setting
    language=setting('xcmate_ui_language','kodi')
    if language=='kodi':
        import xbmc
        try:language=xbmc.getLanguage(xbmc.ISO_639_1)
        except (AttributeError,RuntimeError):language='en_gb'
    language=language.lower()
    result=[]
    for row in registry()['entries']:
        if continent and row['continent']!=continent:continue
        names=row['names'];name=names.get(language) or next((v for k,v in names.items() if k.split('_')[0].lower()==language.split('_')[0]),names['en_gb'])
        result.append(dict(row,label=name))
    return sorted(result,key=lambda r:r['label'].casefold())


def endpoint(source):
    url=source.get('url','');parsed=urlsplit(url)
    registered=[s for row in registry()['entries'] for s in row['sources'] if s['url']==url]
    if not registered or parsed.scheme!='https' or parsed.username or parsed.password or parsed.port not in (None,443):raise SyncError('EPG_UNTRUSTED_ENDPOINT')
    if parsed.hostname not in ('iptv-epg.org','www.free-epg.de'):raise SyncError('EPG_UNTRUSTED_ENDPOINT')
    return parsed


def public_dns(host):
    addresses=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(row[4][0]).is_global for row in addresses):raise SyncError('EPG_UNSAFE_HOST')


class Redirect(HTTPRedirectHandler):
    def __init__(self,origin):self.origin=origin;self.count=0
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        self.count+=1;target=urlsplit(newurl)
        if self.count>3 or target.scheme!='https' or target.hostname!=self.origin.hostname or target.port not in (None,443) or target.username or target.password:
            raise SyncError('EPG_REDIRECT_BLOCKED')
        public_dns(target.hostname)
        return super().redirect_request(req,fp,code,msg,headers,newurl)


def inspect_xml(stream,cancel=lambda:False):
    """Use the existing bounded SAX parser, including its inert DTD policy.

    No ElementTree document and no worker-thread _strptime initialization.
    Internal/external entities remain rejected by the production XMLTV parser.
    """
    class Bounded:
        def __init__(self):self.bytes=0;self.until=time.monotonic()+30
        def read(self,n=-1):
            if cancel():raise SyncError('CANCELLED')
            if time.monotonic()>self.until:raise SyncError('TIMEOUT')
            data=stream.read(min(n if n>=0 else 65536,65536));self.bytes+=len(data)
            if self.bytes>MAX_BYTES:raise SyncError('EPG_PROBE_BUDGET')
            return data
    channels=set();count=0;first=None;last=None
    def channel(cid,name):
        if cid:channels.add(cid)
    def programme(row):
        nonlocal count,first,last
        if not row.get('name'):return
        start,stop=row['start_timestamp'],row['stop_timestamp']
        count+=1;first=start if first is None else min(first,start);last=stop if last is None else max(last,stop)
    from xmltv_stream import parse
    parse(Bounded(),channel,programme,cancel,max_seconds=30)
    if not channels or not count:raise SyncError('EPG_EMPTY_SAMPLE')
    if last < time.time()-86400:raise SyncError('EPG_STALE_FEED')
    return dict(channels=len(channels),programmes=count,first=first,last=last,verified=time.time())


def verify(source,cancel=lambda:False):
    parsed=endpoint(source);public_dns(parsed.hostname)
    opener=build_opener(Redirect(parsed))
    req=Request(source['url'],headers={'User-Agent':'XCMate/0.1.29.73','Accept-Encoding':'identity'})
    from utils import addon_data_dir
    from wizard_resume53 import private_folder,write_file
    from import_budget import check_space
    folder=os.path.join(addon_data_dir(),'international73');private_folder(folder)
    until=time.monotonic()+30
    with opener.open(req,timeout=8) as response, tempfile.TemporaryFile(dir=folder) as raw:
        downloaded=0
        while True:
            if cancel():raise SyncError('CANCELLED')
            if time.monotonic()>until:raise SyncError('TIMEOUT')
            chunk=response.read(65536)
            if not chunk:break
            downloaded+=len(chunk)
            if downloaded>DOWNLOAD_BYTES:raise SyncError('EPG_PROBE_BUDGET')
            check_space(folder,len(chunk)*3);raw.write(chunk)
        raw.seek(0);magic=raw.read(2);raw.seek(0)
        if magic==b'\x1f\x8b':
            with gzip.GzipFile(fileobj=raw) as xml:proof=inspect_xml(xml,cancel)
        else:proof=inspect_xml(raw,cancel)
    proof['url_hash']=hashlib.sha256(source['url'].encode()).hexdigest()
    write_file(os.path.join(folder,proof['url_hash']+'.json'),proof)
    return proof


def activate(portal,row,source,confirmed=False):
    if not confirmed:raise SyncError('EPG_CONSENT_REQUIRED')
    endpoint(source)
    policy=registry()['provider_policy'][source['provider']]
    if not policy['personal_player_use']:raise SyncError('EPG_TERMS_PENDING')
    from utils import addon_data_dir
    filename=os.path.join(addon_data_dir(),'international73',hashlib.sha256(source['url'].encode()).hexdigest()+'.json')
    try:
        with open(filename) as stream:proof=json.load(stream)
    except (OSError,ValueError):raise SyncError('EPG_VERIFICATION_REQUIRED') from None
    if not 0<=time.time()-proof.get('verified',0)<86400 or proof.get('url_hash')!=hashlib.sha256(source['url'].encode()).hexdigest():raise SyncError('EPG_VERIFICATION_REQUIRED')
    from profile_transaction import writing
    from epg_sources import configuration,_save
    with writing():
        config=configuration(portal['id'])
        existing=next((s for s in config['sources'] if s['uri']==source['url']),None)
        if existing:existing['enabled']=True
        else:
            sid='intl73-'+hashlib.sha256((row['code']+'|'+source['url']).encode()).hexdigest()[:24]
            config['sources'].append(dict(id=sid,name=row['label']+' · '+source['provider'],uri=source['url'],local=False,enabled=True,international73=row['code']))
        _save(portal['id'],config)
    # Existing schedule/import gates own downloading and source-qualified mapping.
    from epg import request_refresh
    return request_refresh(portal['id'],portal,force=True)
