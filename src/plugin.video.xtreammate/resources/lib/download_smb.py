"""Private signed SMB2 adapter: exclusive create, no-replace rename, readback.

Kodi VFS is used for destination browsing/playback, never as an atomic writer.
No SMB1, guest/unsigned fallback, remote shell, terminal logging or live recorder.
"""
import hashlib,hmac,io,os,re,socket,sqlite3,sys
from contextlib import contextmanager
from urllib.parse import quote,unquote,urlsplit,urlunsplit
from xcmate_smb_vendor.smb.SMBConnection import SMBConnection


class Failure(OSError):
    def __init__(self,code,step='SMB',number=0):
        self.code=code;self.step=step;self.number=number;super().__init__(code)


def parse(uri):
    try:
        p=urlsplit(uri);port=p.port or 445;host=p.hostname or ''
        if p.scheme!='smb' or not host or not 1<=port<=65535 or p.query or p.fragment or '%' in host:raise ValueError()
        components=[unquote(v) for v in p.path.strip('/').split('/')]
        if not components or any(not c or c in ('.','..') or any(x in c for x in ('\\','/',':','\0','*','?')) for c in components):raise ValueError()
        if not re.fullmatch(r'[A-Za-z0-9._:-]+',host):raise ValueError()
        return p,host,port,components[0],'/'.join(components[1:])
    except (ValueError,UnicodeError):raise Failure('TARGET_UNSAFE_PATH','SMB_PATH') from None


def normalized(uri):
    p,host,port,share,path=parse(uri)
    authority=('['+host+']' if ':' in host else host)+(':'+str(port) if port!=445 else '')
    return 'smb://'+authority+'/'+quote(share,safe='')+('/'+quote(path,safe='/') if path else '')


def _key(uri):
    p,host,port,share,path=parse(uri)
    return hashlib.sha256((host.lower()+':'+str(port)+'/'+share).encode()).hexdigest()


def credentials(uri,value=None):
    from utils import addon_data_dir
    path=os.path.join(addon_data_dir(),'download_smb_credentials.sqlite')
    db=sqlite3.connect(path,timeout=.25);os.chmod(path,0o600)
    try:
        db.execute('CREATE TABLE IF NOT EXISTS accounts(scope TEXT PRIMARY KEY,user TEXT,password TEXT,domain TEXT)')
        if value is not None:
            with db:db.execute('INSERT OR REPLACE INTO accounts VALUES(?,?,?,?)',(_key(uri),*value))
        row=db.execute('SELECT user,password,domain FROM accounts WHERE scope=?',(_key(uri),)).fetchone()
        return row or ('','','')
    finally:db.close()


def configure(uri):
    p,*_=parse(uri)
    if p.username is not None:credentials(uri,(unquote(p.username),unquote(p.password or ''),''))
    return normalized(uri)


class SignedConnection(SMBConnection):
    def write(self,data):
        runtime=sys.modules.get('service_runtime')
        if runtime and self.sock:runtime.track_socket(self.sock)
        return super().write(data)
    def _updateState_SMB1(self,message):raise Failure('SMB2_REQUIRED','SMB_NEGOTIATE')
    def _updateState_SMB2(self,message):
        if message.command==0 and message.status==0:
            if message.payload.dialect_revision not in (0x202,0x210):raise Failure('SMB_DIALECT_UNSUPPORTED','SMB_NEGOTIATE')
            if not message.payload.security_mode&3:raise Failure('SMB_SIGNING_REQUIRED','SMB_NEGOTIATE')
        if self.has_authenticated:
            if not self.is_signing_active or not self.signing_session_key:raise Failure('SMB_SIGNING_REQUIRED','SMB_SIGNATURE')
            raw=message.raw_data
            signature=hmac.new(self.signing_session_key,raw[:48]+b'\0'*16+raw[64:],hashlib.sha256).digest()[:16]
            if not message.flags&8 or not hmac.compare_digest(signature,message.signature):raise Failure('SMB_BAD_SIGNATURE','SMB_SIGNATURE')
        result=super()._updateState_SMB2(message)
        if self.has_authenticated and not self.is_signing_active:raise Failure('SMB_SIGNING_REQUIRED','SMB_AUTH')
        return result


def safe_error(exc,step):
    if isinstance(exc,(Failure,InterruptedError)):return exc
    statuses=[getattr(m,'status',0) for m in getattr(exc,'smb_messages',())]
    code='SMB_DNS_FAILED' if isinstance(exc,socket.gaierror) else 'SMB_AUTH_FAILED' if 0xc000006d in statuses else 'TARGET_EXISTS' if 0xc0000035 in statuses else 'TARGET_PERMISSION' if 0xc0000022 in statuses else 'TARGET_NOT_FOUND' if any(n in statuses for n in (0xc000000f,0xc0000034,0xc000003a,0x80000006)) else 'NO_SPACE' if 0xc000007f in statuses else 'SMB_CONNECTION_FAILED'
    status=next((n for n in reversed(statuses) if n),0)
    if status:step=step+'_'+format(status,'08X')
    return Failure(code,step,getattr(exc,'errno',0) or 0)


@contextmanager
def session(uri):
    _,host,port,share,path=parse(uri);user,password,domain=credentials(uri)
    if not user:raise Failure('SMB_AUTH_REQUIRED','SMB_AUTH')
    connection=SignedConnection(user,password,'XCMATE',host,domain=domain,use_ntlm_v2=True,
                                sign_options=SMBConnection.SIGN_WHEN_SUPPORTED,is_direct_tcp=True)
    try:
        if not connection.connect(host,port=port,timeout=10):raise Failure('SMB_AUTH_FAILED','SMB_AUTH')
        if not connection.isUsingSMB2 or not connection.is_signing_active:raise Failure('SMB_SIGNING_REQUIRED','SMB_AUTH')
        yield connection,share,path
    except BaseException as exc:
        if isinstance(exc,(KeyboardInterrupt,SystemExit)):raise
        raise safe_error(exc,'SMB_IO') from None
    finally:connection.close()


def size(uri):
    with session(uri) as (connection,share,path):
        value=connection.getAttributes(share,path,timeout=10)
        if value.isDirectory:raise Failure('TARGET_NOT_REGULAR','SMB_STAT')
        return value.file_size


def exists(uri):
    try:size(uri);return True
    except Failure as exc:
        if exc.code=='TARGET_NOT_FOUND':return False
        raise


def digest(uri,expected,cancel=lambda:False):
    class Sink:
        def __init__(self):self.count=0;self.hash=hashlib.sha256()
        def write(self,data):
            if cancel():raise InterruptedError()
            self.count+=len(data)
            if self.count>expected:raise Failure('TARGET_VERIFY_FAILED','SMB_HASH')
            self.hash.update(data)
    sink=Sink()
    with session(uri) as (connection,share,path):connection.retrieveFile(share,path,sink,timeout=10)
    if sink.count!=expected:raise Failure('TARGET_VERIFY_FAILED','SMB_HASH')
    return sink.hash.hexdigest()


def upload_exclusive(source,target,cancel=lambda:False,progress=lambda n:None):
    class Source:
        def __init__(self,stream):self.stream=stream;self.count=0
        def read(self,count):
            if cancel():raise InterruptedError()
            data=self.stream.read(min(count,65536));self.count+=len(data);progress(self.count);return data
    with session(target) as (connection,share,path):
        with open(source,'rb') as stream:return connection.storeFile(share,path,Source(stream),timeout=10)


def rename(source,target):
    if _key(source)!=_key(target):raise Failure('TARGET_DIRECTORY_MISMATCH','SMB_RENAME')
    _,_,_,_,destination=parse(target)
    with session(source) as (connection,share,path):connection.rename(share,path,destination,timeout=10)


def remove(uri):
    with session(uri) as (connection,share,path):connection.deleteFiles(share,path,timeout=10)


class Reader:
    def __init__(self,uri):self.uri=uri;self.offset=0
    def read(self,count):
        if not 0<count<=65536:raise Failure('TARGET_READ_LIMIT','SMB_READ')
        output=io.BytesIO()
        with session(self.uri) as (connection,share,path):connection.retrieveFileFromOffset(share,path,output,self.offset,count,timeout=10)
        data=output.getvalue();self.offset+=len(data);return data
    def close(self):pass
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
