"""Private bounded token file. Only explicit UI/workers read disk, never focus."""
import errno
import hashlib
import os
import re
import stat
import threading
import time
import uuid

NAME='tmdb_read_access_token.txt'
MAX_BYTES=4097
_lock=threading.RLock()
_cache=None
_cache_path=None
_checked=0.

class TokenError(ValueError):
    def __init__(self,code):
        self.code=code
        super().__init__(code)

def validate(raw):
    if not isinstance(raw,bytes) or len(raw)>MAX_BYTES:raise TokenError('TOKEN_SIZE')
    try:value=raw.decode('utf-8')
    except UnicodeError:raise TokenError('TOKEN_FORMAT') from None
    if value.endswith('\r\n'):value=value[:-2]
    elif value.endswith('\n'):value=value[:-1]
    if not 40<=len(value)<=4096 or not re.fullmatch(r'[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',value):raise TokenError('TOKEN_FORMAT')
    if any(k in value.casefold() for k in ('placeholder','synthetic','example','your_token')):raise TokenError('TOKEN_FORMAT')
    return value

def location():
    import xbmcvfs
    return xbmcvfs.translatePath('special://profile/addon_data/plugin.video.xtreammate/'+NAME)

def parent(path):
    """Walk with openat/O_NOFOLLOW: no symlink component, even during races."""
    if not isinstance(path,str) or not os.path.isabs(path) or '\x00' in path or '://' in path or '..' in path.split('/'):raise TokenError('TOKEN_PATH')
    parts=path.split('/')[1:]
    if not parts or not parts[-1]:raise TokenError('TOKEN_PATH')
    fd=os.open('/',os.O_RDONLY|os.O_DIRECTORY)
    try:
        for part in parts[:-1]:
            if not part:continue
            nxt=os.open(part,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=fd)
            os.close(fd);fd=nxt
        return fd,parts[-1]
    except OSError:
        os.close(fd);raise TokenError('TOKEN_PATH') from None

def read(path,missing=False):
    fd,name=parent(path)
    try:
        try:source=os.open(name,os.O_RDONLY|os.O_NOFOLLOW|os.O_NONBLOCK,dir_fd=fd)
        except FileNotFoundError:
            if missing:return None
            raise TokenError('TOKEN_UNREADABLE') from None
        except OSError:raise TokenError('TOKEN_PATH') from None
        try:
            if not stat.S_ISREG(os.fstat(source).st_mode):raise TokenError('TOKEN_PATH')
            raw=os.read(source,MAX_BYTES+1)
            # A bounded second read detects concurrent growth and short reads.
            if os.read(source,1):raise TokenError('TOKEN_SIZE')
            return raw
        finally:os.close(source)
    finally:os.close(fd)

def publish_revision(code,token=''):
    try:
        import xbmcgui
        value=hashlib.sha256((code+'\0'+token).encode()).hexdigest()
        xbmcgui.Window(10000).setProperty('XCMate.TMDB61.Revision',value)
    except (ImportError,AttributeError,RuntimeError):pass

def effective_tmdb_read_token(force=False):
    """File wins; invalid/unreadable file blocks legacy fallback. No HTTP."""
    global _cache,_cache_path,_checked
    from utils import setting
    path=location()
    with _lock:
        if force or _cache is None or _cache_path!=path or time.monotonic()-_checked>=30:
            try:
                raw=read(path,missing=True)
                _cache=('FILE_VALID',validate(raw)) if raw is not None else ('FILE_MISSING','')
            except (TokenError,OSError) as exc:
                _cache=(exc.code if isinstance(exc,TokenError) else 'TOKEN_UNREADABLE','')
            _checked=time.monotonic();_cache_path=path
        code,token=_cache
        if code=='FILE_MISSING':token=setting('tmdb_read_token43','').strip()
        publish_revision(code,token)
        if code not in ('FILE_VALID','FILE_MISSING'):raise TokenError(code)
        return token

def token_fingerprint():
    """RAM / Kodi-property lookup only; provider art never depends on token."""
    from utils import setting
    legacy=hashlib.sha256(setting('tmdb_read_token43','').encode()).hexdigest()
    try:
        import xbmcgui
        revision=xbmcgui.Window(10000).getProperty('XCMate.TMDB61.Revision')
    except (ImportError,AttributeError,RuntimeError):revision=''
    return hashlib.sha256((revision+'|'+legacy).encode()).hexdigest()

def status():
    try:effective_tmdb_read_token(force=True)
    except TokenError:return 'FILE_INVALID'
    with _lock:return _cache[0]

def import_file(source,expected):
    """expected raw digest comes from the explicit overwrite confirmation."""
    raw=read(source);value=validate(raw)
    path=location();fd,name=parent(path);temp='.tmdb61-'+uuid.uuid4().hex
    try:
        before=read(path,missing=True)
        digest=hashlib.sha256(before).hexdigest() if before is not None else None
        if digest!=expected:raise TokenError('TOKEN_CHANGED')
        out=os.open(temp,os.O_WRONLY|os.O_CREAT|os.O_EXCL|os.O_NOFOLLOW,0o600,dir_fd=fd)
        with os.fdopen(out,'wb') as stream:
            stream.write((value+'\n').encode());stream.flush();os.fsync(stream.fileno())
        current=read(path,missing=True)
        if (hashlib.sha256(current).hexdigest() if current is not None else None)!=expected:raise TokenError('TOKEN_CHANGED')
        os.replace(temp,name,src_dir_fd=fd,dst_dir_fd=fd);os.fsync(fd)
    except OSError:raise TokenError('TOKEN_WRITE') from None
    finally:
        try:os.unlink(temp,dir_fd=fd)
        except FileNotFoundError:pass
        os.close(fd)
    effective_tmdb_read_token(force=True)
    return 'IMPORTED'
