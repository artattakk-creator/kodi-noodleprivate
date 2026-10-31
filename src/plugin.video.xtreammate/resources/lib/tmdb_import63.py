"""Explicit file-picker sources only. Private destination keeps descriptor guards.

VFS is deliberately separate from the private file reader. SMB/Android mounts
are read once with a byte/EOF budget; their addresses never become a setting.
One outstanding VFS read per interpreter, even if an OS call ignores cancellation.
"""
import os
import threading
import time
from urllib.parse import unquote, urlsplit
from tmdb_token61 import TokenError, MAX_BYTES

_busy=threading.Lock()


def source(path):
    if not isinstance(path,str) or not path or len(path)>8192 or any(ord(c)<32 for c in path):
        raise TokenError('TOKEN_PATH')
    try:
        parsed=urlsplit(path)
        decoded=unquote(parsed.path)
    except (ValueError,UnicodeError):
        raise TokenError('TOKEN_PATH') from None
    if any(ord(c)<32 for c in decoded) or '..' in decoded.split('/') or parsed.query or parsed.fragment:
        raise TokenError('TOKEN_PATH')
    if parsed.scheme=='smb':
        if not parsed.netloc or not parsed.hostname or not decoded.startswith('/') or decoded.endswith('/'):
            raise TokenError('TOKEN_PATH')
        # Kodi owns the explicitly selected SMB connection/authentication.
        return path,True
    if parsed.scheme=='special':
        if parsed.netloc not in ('profile','home','masterprofile','temp') or not decoded.startswith('/'):
            raise TokenError('TOKEN_PATH')
        import xbmcvfs
        translated=xbmcvfs.translatePath(path)
        if not isinstance(translated,str) or not os.path.isabs(translated) or '://' in translated:
            raise TokenError('TOKEN_PATH')
        return source(translated)
    if parsed.scheme=='file':
        if parsed.netloc:raise TokenError('TOKEN_PATH')
        path=decoded
    elif parsed.scheme or parsed.netloc:
        raise TokenError('TOKEN_PATH')
    if not os.path.isabs(path) or path.endswith('/') or '..' in path.split('/'):
        raise TokenError('TOKEN_PATH')
    # FUSE/USB mount aliases belong to Kodi VFS, never to the private writer.
    android=path.startswith(('/storage/','/sdcard/','/mnt/media_rw/','/mnt/runtime/'))
    return path,android


def _vfs(path):
    import xbmcvfs
    handle=None
    try:
        handle=xbmcvfs.File(path,'rb')
        try:size=handle.size()
        except Exception:size=-1
        if isinstance(size,int) and size>MAX_BYTES:raise TokenError('TOKEN_SIZE')
        raw=bytearray();request=MAX_BYTES+1
        while True:
            chunk=handle.readBytes(request)
            if not isinstance(chunk,(bytes,bytearray)):raise TokenError('TOKEN_UNREADABLE')
            if not chunk:return bytes(raw)
            raw.extend(chunk)
            if len(raw)>MAX_BYTES:raise TokenError('TOKEN_SIZE')
            # VFS/network reads may be short. Accumulate to the byte ceiling,
            # then demand EOF; never mistake a valid partial packet for size.
            request=1 if isinstance(size,int) and size>0 and len(raw)>=size else MAX_BYTES+1-len(raw)
    except TokenError:raise
    except Exception:raise TokenError('TOKEN_UNREADABLE') from None
    finally:
        if handle is not None:
            try:handle.close()
            except Exception:pass


def selected(path,cancel=lambda:False,budget=5.):
    """Call only after the user selected a concrete file. No writes here."""
    path,vfs=source(path)
    if cancel():raise TokenError('TOKEN_UNREADABLE')
    if not vfs:
        from tmdb_token61 import read
        raw=read(path)
        if cancel():raise TokenError('TOKEN_UNREADABLE')
        return raw
    if not _busy.acquire(False):raise TokenError('TOKEN_UNREADABLE')
    complete=threading.Event();box={}
    def run():
        try:box['raw']=_vfs(path)
        except TokenError as exc:box['code']=exc.code
        finally:_busy.release();complete.set()
    try:threading.Thread(target=run,name='XCMateTokenImport',daemon=True).start()
    except RuntimeError:
        _busy.release();raise TokenError('TOKEN_UNREADABLE') from None
    deadline=time.monotonic()+min(10.,max(.05,budget))
    while not complete.wait(.05):
        if cancel() or time.monotonic()>=deadline:
            # No global timeout setting, forced thread stop or unbounded retry.
            raise TokenError('TOKEN_UNREADABLE')
    if cancel():raise TokenError('TOKEN_UNREADABLE')
    if 'code' in box:raise TokenError(box['code'])
    return box.pop('raw')
