"""Owned media destinations; VFS URIs are never passed to POSIX open()."""
import hashlib
import os
import shutil
import uuid
from urllib.parse import urlsplit,urlunsplit

RESERVE=64*1024*1024


class FileFailure(OSError):
    def __init__(self,code):self.code=code;super().__init__(code)


def local(uri):
    return '://' not in uri or uri.startswith('special://')


def native(uri):
    if uri.startswith('special://'):
        import xbmcvfs
        return xbmcvfs.translatePath(uri)
    return uri


def join(root,*parts):
    if any(not p or p in ('.','..') or '/' in p or '\\' in p or '\0' in p for p in parts):raise FileFailure('UNSAFE_TARGET')
    return root.rstrip('/')+'/'+ '/'.join(parts)


def display(uri):
    p=urlsplit(uri)
    return urlunsplit((p.scheme,p.hostname or '',p.path,'','')) if p.scheme else uri


def safe_name(value,default='XCMate'):
    value=str(value or '')
    if '://' in value:value=default
    return ''.join(c if c.isalnum() or c in ' _-' else '_' for c in value)[:48].strip(' _-') or default


def exists(uri):
    if local(uri):return os.path.exists(native(uri))
    import xbmcvfs
    return xbmcvfs.exists(uri)


def size(uri):
    if local(uri):return os.path.getsize(native(uri))
    import xbmcvfs
    return xbmcvfs.Stat(uri).st_size()


def mkdir(uri):
    if local(uri):os.makedirs(native(uri),exist_ok=True)
    else:
        import xbmcvfs
        if not xbmcvfs.exists(uri) and not xbmcvfs.mkdirs(uri):raise FileFailure('TARGET_UNAVAILABLE')


def remove(uri):
    if local(uri):os.unlink(native(uri))
    else:
        import xbmcvfs
        if not xbmcvfs.delete(uri):raise FileFailure('TARGET_WRITE')


def rename(source,target):
    if exists(target):raise FileFailure('TARGET_EXISTS')
    if local(source):
        # The destination has an unpredictable, job-owned suffix. Link first
        # gives a strict non-overwrite publish on capable local filesystems.
        try:os.link(native(source),native(target),follow_symlinks=False)
        except FileExistsError:raise FileFailure('TARGET_EXISTS') from None
        else:os.unlink(native(source))
    else:
        import xbmcvfs
        if not xbmcvfs.rename(source,target):raise FileFailure('TARGET_RENAME')


def capacity(uri,additional=0):
    if local(uri):
        path=native(uri)
        while not os.path.isdir(path):
            parent=os.path.dirname(path)
            if parent==path:raise FileFailure('TARGET_UNAVAILABLE')
            path=parent
        free=shutil.disk_usage(path).free
        if free<RESERVE+max(0,additional):raise FileFailure('NO_SPACE')
        return free
    # Kodi VFS has no reliable free-space API. Never invent a capacity.
    return None


def file_limit(uri):
    from utils import setting_int
    configured=max(1,min(512,setting_int('downloads_max_gib',64)))*1024**3
    if not local(uri):return min(configured,4*1024**3-1)
    # Linux/Android VFAT is limited to 4 GiB-1; unknown VFS targets use that
    # conservative policy too. Other local FS errors remain real failures.
    try:
        path=os.path.realpath(native(uri));mounts=[]
        with open('/proc/mounts') as stream:
            for line in stream:
                fields=line.split()
                if len(fields)>2:
                    mount=fields[1].replace('\\040',' ')
                    if path==mount or path.startswith(mount.rstrip('/')+'/'):mounts.append((len(mount),fields[2]))
        if mounts and max(mounts)[1] in ('vfat','msdos'):return min(configured,4*1024**3-1)
    except OSError:pass
    return configured


def reader(uri):
    if local(uri):return open(native(uri),'rb')
    import xbmcvfs
    source=xbmcvfs.File(uri)
    class Reader:
        def read(self,n):return bytes(source.readBytes(n))
        def close(self):source.close()
        def __enter__(self):return self
        def __exit__(self,*args):self.close()
    return Reader()


def writer(uri):
    if local(uri):
        path=native(uri);parent=os.path.dirname(path)
        os.makedirs(parent,exist_ok=True)
        # Never follow a replaced owned temporary file.
        fd=os.open(path,os.O_WRONLY|os.O_CREAT|os.O_EXCL|getattr(os,'O_NOFOLLOW',0),0o600)
        return os.fdopen(fd,'wb')
    import xbmcvfs
    if xbmcvfs.exists(uri):raise FileFailure('TARGET_EXISTS')
    target=xbmcvfs.File(uri,'w')
    class Writer:
        def write(self,data):
            result=target.write(bytearray(data))
            if result is False or (type(result) is int and result!=len(data)):raise FileFailure('TARGET_WRITE')
            return len(data)
        def flush(self):pass
        def close(self):target.close()
        def __enter__(self):return self
        def __exit__(self,*args):self.close()
    return Writer()


def flush(stream):
    stream.flush()
    if hasattr(stream,'fileno'):os.fsync(stream.fileno())


def probe(root):
    from capture_target import probe as native_probe
    result=native_probe(native(root),create=True)
    return dict(writable=True,free=result['free'],max_bytes=file_limit(root),vfs=False)


def owned_part(uri,ident):
    return uri.rsplit('/',1)[-1].startswith('.xcmate-'+ident+'-') and uri.endswith('.part')
