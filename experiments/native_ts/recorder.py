"""Unintegrated Direct-TS prototype. No Kodi/player or external process imports.

POSIX target only. No timer/UI/provider resolver, reconnect or VFS promises.
The caller must authorize a separate connection; unsupported targets fail shut.
"""
import json
import math
import os
from pathlib import Path
import socket
import ssl
import threading
import time
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener, ProxyHandler, HTTPSHandler
import uuid

PACKET=188
RESERVE=64*1024*1024
MAX_PROBE=2*1024*1024


class Failure(Exception):
    def __init__(self,code):self.code=code;super().__init__(code)


def crc(data):
    value=0xffffffff
    for byte in data:
        value^=byte<<24
        for _ in range(8):value=((value<<1)^0x04c11db7 if value&0x80000000 else value<<1)&0xffffffff
    return value


class Transport:
    """188-byte alignment, packet headers, PAT/PMT CRC and clear media streams."""
    def __init__(self):
        self.tail=b'';self.packets=0;self.pmt_pids=set();self.media=False;self.sections={}

    @property
    def ready(self):return self.packets>=20 and bool(self.pmt_pids) and self.media

    def feed(self,data):
        data=self.tail+data;end=len(data)//PACKET*PACKET
        for offset in range(0,end,PACKET):self._packet(data[offset:offset+PACKET])
        self.tail=data[end:]
        return data[:end]

    def _packet(self,p):
        if p[0]!=0x47:raise Failure('NOT_DIRECT_TS')
        if p[1]&0x80:raise Failure('TS_TRANSPORT_ERROR')
        if p[3]&0xc0:raise Failure('ENCRYPTED_TS')
        mode=(p[3]>>4)&3
        if not mode:raise Failure('INVALID_TS_HEADER')
        start=4
        if mode&2:
            start=5+p[4]
            if start>PACKET:raise Failure('INVALID_TS_HEADER')
        self.packets+=1
        pid=((p[1]&31)<<8)|p[2]
        if not mode&1 or start>=PACKET or pid not in {0,*self.pmt_pids}:return
        payload=p[start:]
        if p[1]&0x40:
            pointer=payload[0]
            if pointer>=len(payload):raise Failure('INVALID_PSI')
            self.sections[pid]=b'';payload=payload[1+pointer:]
        elif pid not in self.sections:return
        buf=self.sections.get(pid,b'')+payload
        while len(buf)>=3 and buf[0]!=255:
            length=3+(((buf[1]&15)<<8)|buf[2])
            if not 12<=length<=1024:raise Failure('INVALID_PSI')
            if len(buf)<length:break
            section,buf=buf[:length],buf[length:]
            if crc(section):raise Failure('INVALID_PSI_CRC')
            if not section[5]&1:continue
            if pid==0 and section[0]==0:
                for pos in range(8,length-4,4):
                    if pos+4>length-4:raise Failure('INVALID_PAT')
                    program=int.from_bytes(section[pos:pos+2],'big')
                    pmt=((section[pos+2]&31)<<8)|section[pos+3]
                    if program and 16<=pmt<8191:self.pmt_pids.add(pmt)
            elif pid in self.pmt_pids and section[0]==2:self._pmt(section)
        self.sections[pid]=b'' if buf and buf[0]==255 else buf

    def _descriptors(self,data):
        pos=0
        while pos<len(data):
            if pos+2>len(data) or pos+2+data[pos+1]>len(data):raise Failure('INVALID_PMT')
            if data[pos]==9:raise Failure('ENCRYPTED_TS')
            pos+=2+data[pos+1]

    def _pmt(self,s):
        if len(s)<16:raise Failure('INVALID_PMT')
        info=((s[10]&15)<<8)|s[11];pos=12+info
        if pos>len(s)-4:raise Failure('INVALID_PMT')
        self._descriptors(s[12:pos])
        while pos<len(s)-4:
            if pos+5>len(s)-4:raise Failure('INVALID_PMT')
            size=((s[pos+3]&15)<<8)|s[pos+4];end=pos+5+size
            if end>len(s)-4:raise Failure('INVALID_PMT')
            self._descriptors(s[pos+5:end])
            if s[pos] in (1,2,3,4,15,16,27,36,129,135):self.media=True
            pos=end


def validate_url(value):
    try:
        p=urlsplit(value)
        if p.scheme not in ('http','https') or not p.hostname or p.username or p.password or p.fragment or p.port==0:raise ValueError()
        if len(value)>8192 or any(ord(c)<33 or ord(c)==127 for c in value):raise ValueError()
        if p.path.lower().endswith(('.m3u','.m3u8','.mpd')):raise Failure('UNSUPPORTED_MANIFEST')
    except ValueError:raise Failure('INVALID_SOURCE') from None
    return value


class Redirects(HTTPRedirectHandler):
    def redirect_request(self,req,fp,code,msg,headers,newurl):
        validate_url(newurl)
        if urlsplit(req.full_url).scheme=='https' and urlsplit(newurl).scheme!='https':raise Failure('INSECURE_REDIRECT')
        # No private request headers exist in this prototype. Integration must
        # explicitly validate Kodi suffix headers/cookies and provider limits.
        return super().redirect_request(req,fp,code,msg,headers,newurl)


def error_code(error):
    if isinstance(error,Failure):return error.code
    if isinstance(error,HTTPError):
        return 'HTTP_AUTH' if error.code in (401,403) else 'HTTP_MISSING' if error.code in (404,410) else 'HTTP_LIMIT' if error.code==429 else 'HTTP_ERROR'
    if isinstance(error,URLError):return error_code(error.reason)
    if isinstance(error,ssl.SSLError):return 'TLS_ERROR'
    if isinstance(error,socket.gaierror):return 'DNS_ERROR'
    if isinstance(error,(TimeoutError,socket.timeout)):return 'TIMEOUT'
    if isinstance(error,OSError):return 'DISK_FULL' if error.errno==28 else 'IO_ERROR'
    return 'SOURCE_ERROR'


class Recorder:
    """Call run() on its own worker; stop() affects only this recording.

    .ts.part and a safe JSON state survive failures. complete requires reaching
    the requested wall duration, valid clear PAT/PMT, full packets and fsync.
    A final filename is created with an exclusive hard link, never overwritten.
    """
    def __init__(self,source,directory,duration,*,separate_connection=False,max_bytes=2*1024**3):
        self.source=source;self.directory=directory;self.duration=duration
        self.authorized=separate_connection;self.max_bytes=max_bytes
        self.cancel=threading.Event();self.ident=uuid.uuid4().hex
        self.state=dict(id=self.ident,status='pending',code='',bytes=0,seconds=0)
        self._guard=threading.Lock();self._started=False

    def stop(self):self.cancel.set()

    def _space(self,fd,incoming=0):
        capacity=os.fstatvfs(fd)
        if capacity.f_bavail*capacity.f_frsize<RESERVE+incoming:raise Failure('DISK_FULL')
        if self.state['bytes']+incoming>self.max_bytes:raise Failure('FILE_LIMIT')

    def _save(self,fd):
        tmp=self.ident+'.json.tmp';name=self.ident+'.json'
        output=os.open(tmp,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600,dir_fd=fd)
        with os.fdopen(output,'w',encoding='utf-8') as stream:
            json.dump(self.state,stream);stream.flush();os.fsync(stream.fileno())
        os.replace(tmp,name,src_dir_fd=fd,dst_dir_fd=fd);os.fsync(fd)

    def run(self):
        with self._guard:
            if self._started:raise Failure('ALREADY_STARTED')
            self._started=True
        fd=None;output=None;part=self.ident+'.ts.part';final=self.ident+'.ts'
        began=None;written=False;promoted=False;next_status=0
        try:
            if not self.authorized:raise Failure('CONNECTION_CONFIRMATION_REQUIRED')
            if not isinstance(self.duration,(int,float)) or isinstance(self.duration,bool) or not math.isfinite(self.duration) or not 0<self.duration<=21600:raise Failure('INVALID_DURATION')
            if not isinstance(self.max_bytes,int) or not PACKET*20<=self.max_bytes<=2*1024**3:raise Failure('INVALID_LIMIT')
            validate_url(self.source)
            if not isinstance(self.directory,(str,os.PathLike)) or '://' in str(self.directory):raise Failure('UNSUPPORTED_TARGET')
            directory=Path(self.directory)
            if not directory.is_absolute() or directory.is_symlink():raise Failure('UNSUPPORTED_TARGET')
            fd=os.open(directory,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
            self._space(fd)
            self._save(fd)
            if self.cancel.is_set():raise Failure('CANCELLED')
            transport=Transport();pending=bytearray();probe_start=time.monotonic()
            # Keep system HTTPS CA trust. There is no implicit reconnect or
            # second source connection; redirects obey urllib's finite bound.
            opener=build_opener(ProxyHandler(),Redirects(),HTTPSHandler())
            request=Request(self.source,headers={'User-Agent':'XCMate-native-ts-prototype','Accept':'video/mp2t','Accept-Encoding':'identity'})
            with opener.open(request,timeout=2) as response:
                content=response.headers.get('Content-Type','').split(';',1)[0].lower()
                if content in ('application/vnd.apple.mpegurl','application/x-mpegurl','application/dash+xml','text/html','application/json'):raise Failure('NOT_DIRECT_TS')
                if response.status!=200 or response.headers.get('Content-Encoding','identity').lower()!='identity':raise Failure('UNSUPPORTED_RESPONSE')
                while True:
                    if self.cancel.is_set():raise Failure('CANCELLED')
                    if began is not None and time.monotonic()-began>=self.duration:break
                    chunk=response.read(PACKET*200)
                    if not chunk:raise Failure('SOURCE_EOF')
                    complete=transport.feed(chunk)
                    if began is None:
                        pending.extend(complete)
                        if len(pending)>MAX_PROBE or time.monotonic()-probe_start>10:raise Failure('TS_PROBE_LIMIT')
                        if not transport.ready:continue
                        output=os.fdopen(os.open(part,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600,dir_fd=fd),'wb')
                        began=time.monotonic();self.state.update(status='recording',code='')
                        complete=bytes(pending);pending.clear();self._save(fd)
                    self._space(fd,len(complete))
                    if self.cancel.is_set():raise Failure('CANCELLED')
                    output.write(complete);self.state['bytes']+=len(complete);written=written or bool(complete)
                    self.state['seconds']=round(time.monotonic()-began,3)
                    if self.state['seconds']>=next_status:
                        self._save(fd);next_status=self.state['seconds']+5
                # At a timed boundary, an incomplete last packet is retained
                # only in memory and never written to disk. No resync/guessing.
                output.flush();os.fsync(output.fileno());output.close();output=None
                if self.cancel.is_set():raise Failure('CANCELLED')
                os.link(part,final,src_dir_fd=fd,dst_dir_fd=fd,follow_symlinks=False)
                promoted=True;os.fsync(fd)
                self.state.update(status='complete',code='',file=final)
                self._save(fd)
                # Remove only our extra link after durable publication. The
                # actual data remains at final; unrelated files are untouched.
                try:os.unlink(part,dir_fd=fd);os.fsync(fd)
                except OSError:
                    self.state['code']='PART_CLEANUP_PENDING';self._save(fd)
        except Exception as error:
            self.state.update(status='partial' if written or promoted else 'failed',code=error_code(error))
            if fd is not None:
                try:self._save(fd)
                except OSError:pass
        finally:
            if output is not None:
                try:output.flush();os.fsync(output.fileno())
                except OSError:pass
                output.close()
            if fd is not None:os.close(fd)
        return dict(self.state)
