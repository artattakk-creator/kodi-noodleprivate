"""Worker-only Kodi-VFS image adapter. No POSIX access to VFS URLs.

A final image is readable only after verified copy and a matching size/hash
commit marker. No atomic SMB rename is assumed. Partial writes remain private
and bounded; no original/user file is deleted or replaced on collision.
"""
import hashlib
import json
import os
from urllib.parse import urlsplit,unquote
import uuid
from artwork_backend import ArtworkStorageBackend,LocalArtworkStorage

MAX_BYTES=3*1024*1024


class StorageFailure(OSError):
    def __init__(self,code):self.code=code;super().__init__(code)


def target_root(value):
    if not isinstance(value,str) or not value or any(ord(c)<32 for c in value) or '|' in value or '\\' in value:
        raise StorageFailure('INVALID_TARGET')
    parsed=urlsplit(value)
    if parsed.username is not None or parsed.password is not None or parsed.query or parsed.fragment:
        raise StorageFailure('TARGET_CREDENTIALS_NOT_ALLOWED')
    if any(part in ('.','..') for part in unquote(parsed.path).split('/')):raise StorageFailure('INVALID_TARGET')
    if parsed.scheme:
        if parsed.scheme!='smb' or not parsed.hostname or not parsed.path.strip('/'):
            raise StorageFailure('UNSUPPORTED_TARGET')
    elif not os.path.isabs(value):raise StorageFailure('INVALID_TARGET')
    return value.rstrip('/')


def image_valid(data):
    from media_art import dimensions,MAX_PIXELS
    try:
        w,h=dimensions(data)
        return 0<len(data)<=MAX_BYTES and 0<w<=4096 and 0<h<=4096 and w*h<=MAX_PIXELS
    except (ValueError,TypeError):return False


class VFSArtworkStorage(ArtworkStorageBackend):
    kind='KODI_VFS';is_external=True

    def __init__(self,root,owner_marker):
        self.root=target_root(root);self.owner_marker=owner_marker

    def resolve_target(self,ident=None):
        if ident is None:return self.root
        if len(ident)!=64 or any(c not in '0123456789abcdef' for c in ident):raise StorageFailure('INVALID_ARTWORK_KEY')
        return self.root+'/'+ident+'.img'

    def _read(self,path,limit):
        import xbmcvfs
        try:
            stream=xbmcvfs.File(path,'r')
            try:return bytes(stream.readBytes(limit))
            finally:stream.close()
        except Exception:raise StorageFailure('STORAGE_OFFLINE') from None

    def _write(self,path,data):
        import xbmcvfs
        stream=None
        try:
            stream=xbmcvfs.File(path,'w')
            if not stream.write(bytearray(data)):raise StorageFailure('TARGET_WRITE_FAILED')
        except StorageFailure:raise
        except Exception:raise StorageFailure('TARGET_WRITE_FAILED') from None
        finally:
            if stream is not None:stream.close()

    def availability(self):
        try:return 'AVAILABLE' if self._read(self.owner_marker,128)==b'XCMATE_ARTWORK_V1' else 'STORAGE_OFFLINE'
        except OSError:return 'STORAGE_OFFLINE'

    def free_or_unknown(self):return dict(free=None,total=None)

    def _record(self,ident):
        try:
            value=json.loads(self._read(self.resolve_target(ident)+'.ok',512))
            if value.get('version')!=1 or not 0<value['bytes']<=MAX_BYTES or len(value['sha256'])!=64:raise ValueError()
            return value
        except (ValueError,KeyError,TypeError):raise StorageFailure('UNVERIFIED_IMAGE') from None

    def exists(self,ident):
        import xbmcvfs
        return xbmcvfs.exists(self.resolve_target(ident)) and xbmcvfs.exists(self.resolve_target(ident)+'.ok')

    def read(self,ident,limit):
        if self.availability()!='AVAILABLE':raise StorageFailure('STORAGE_OFFLINE')
        record=self._record(ident);data=self._read(self.resolve_target(ident),MAX_BYTES+1)
        if len(data)!=record['bytes'] or hashlib.sha256(data).hexdigest()!=record['sha256'] or not image_valid(data):
            raise StorageFailure('IMAGE_VERIFY_FAILED')
        return data[:limit]

    def stat(self,ident=None):
        if ident is None:return dict(bytes=0,revision=0)
        record=self._record(ident);return dict(bytes=record['bytes'],revision=0)

    def make_display_uri(self,ident):return self.resolve_target(ident)

    def write_verified(self,ident,data,validate):
        import xbmcvfs
        if self.availability()!='AVAILABLE':raise StorageFailure('STORAGE_OFFLINE')
        if len(data)>MAX_BYTES or not validate(data):raise StorageFailure('INVALID_IMAGE')
        filename=self.resolve_target(ident);digest=hashlib.sha256(data).hexdigest();temporary=filename+'.part.'+uuid.uuid4().hex
        try:
            # Shared target files are immutable. Never overwrite another box's
            # image: isolated per-profile namespace + compare on collision.
            if xbmcvfs.exists(filename):
                existing=self._read(filename,MAX_BYTES+1)
                if existing!=data:raise StorageFailure('TARGET_COLLISION')
            else:
                self._write(temporary,data)
                if self._read(temporary,MAX_BYTES+1)!=data:raise StorageFailure('IMAGE_VERIFY_FAILED')
                if not xbmcvfs.copy(temporary,filename):raise StorageFailure('TARGET_WRITE_FAILED')
            final=self._read(filename,MAX_BYTES+1)
            if final!=data or not validate(final):raise StorageFailure('IMAGE_VERIFY_FAILED')
            self._write(filename+'.ok',json.dumps(dict(version=1,bytes=len(data),sha256=digest)).encode())
            if self.read(ident,MAX_BYTES+1)!=data:raise StorageFailure('IMAGE_VERIFY_FAILED')
            return self.make_display_uri(ident)
        finally:
            # Only this invocation's newly created partial, never an original.
            try:
                if xbmcvfs.exists(temporary):xbmcvfs.delete(temporary)
            except Exception:pass

    def enumerate_for_migration(self):
        import xbmcvfs
        if self.availability()!='AVAILABLE':raise StorageFailure('STORAGE_OFFLINE')
        try:directories,files=xbmcvfs.listdir(self.root)
        except Exception:raise StorageFailure('STORAGE_OFFLINE') from None
        for name in files:
            if len(name)==68 and name.endswith('.img') and all(c in '0123456789abcdef' for c in name[:-4]):
                ident=name[:-4]
                if self.exists(ident):yield dict(ident=ident,bytes=self.stat(ident)['bytes'])


class ExternalLocalStorage(LocalArtworkStorage):
    is_external=True

    def __init__(self,root,marker):super().__init__(root);self.owner_marker=marker

    def availability(self):
        try:
            with open(self.owner_marker,'rb') as stream:return 'AVAILABLE' if stream.read(128)==b'XCMATE_ARTWORK_V1' else 'STORAGE_OFFLINE'
        except OSError:return 'STORAGE_OFFLINE'

    def _available(self):
        if self.availability()!='AVAILABLE':raise StorageFailure('STORAGE_OFFLINE')

    def free_or_unknown(self):
        self._available();value=super().free_or_unknown()
        from utils import addon_data_dir
        value['same_as_internal']=os.stat(self.root).st_dev==os.stat(addon_data_dir()).st_dev
        return value
    def read(self,ident,limit):self._available();return super().read(ident,limit)
    def enumerate_for_migration(self):self._available();yield from super().enumerate_for_migration()

    def write_verified(self,ident,data,validate):
        self._available()
        if len(data)>MAX_BYTES or not validate(data):raise StorageFailure('INVALID_IMAGE')
        if os.path.lexists(self.resolve_target(ident)):
            if os.path.islink(self.resolve_target(ident)) or self.read(ident,MAX_BYTES+1)!=data:raise StorageFailure('TARGET_COLLISION')
            return self.make_display_uri(ident)
        return super().write_verified(ident,data,validate)


def backend_for(target,profile,kind='media'):
    target=target_root(target)
    if len(profile)!=32 or any(c not in '0123456789abcdef' for c in profile):raise StorageFailure('INVALID_PROFILE_NAMESPACE')
    if kind not in ('media','logos','fanart'):raise StorageFailure('INVALID_ARTWORK_KIND')
    base=target+'/XCMate/Artwork';marker=base+'/'+profile+'.owner'
    root=base+'/'+kind+'/'+profile
    return VFSArtworkStorage(root,marker) if target.startswith('smb://') else ExternalLocalStorage(root,marker)


def prepare_target(target,profile):
    """Explicit user target-probe only. No call from normal image reads."""
    import xbmcvfs
    target=target_root(target);storage=backend_for(target,profile)
    base=target+'/XCMate/Artwork'
    if target.startswith('smb://'):
        for kind in ('media','logos','fanart'):
            path=backend_for(target,profile,kind).resolve_target()
            if not xbmcvfs.mkdirs(path+'/') and not xbmcvfs.exists(path+'/'):raise StorageFailure('TARGET_WRITE_FAILED')
        if xbmcvfs.exists(storage.owner_marker):
            if storage.availability()!='AVAILABLE':raise StorageFailure('TARGET_COLLISION')
        else:storage._write(storage.owner_marker,b'XCMATE_ARTWORK_V1')
    else:
        # Never create an absent mount: require the user-selected root to exist.
        if not os.path.isdir(target) or os.path.islink(target):raise StorageFailure('STORAGE_OFFLINE')
        for kind in ('media','logos','fanart'):
            path=backend_for(target,profile,kind).root
            current=path
            while current and current!='/':
                if os.path.islink(current):raise StorageFailure('TARGET_SYMLINK')
                current=os.path.dirname(current)
            os.makedirs(path,exist_ok=True)
        if os.path.lexists(storage.owner_marker):
            if os.path.islink(storage.owner_marker) or storage.availability()!='AVAILABLE':raise StorageFailure('TARGET_COLLISION')
        else:
            with open(storage.owner_marker,'xb') as stream:stream.write(b'XCMATE_ARTWORK_V1');stream.flush();os.fsync(stream.fileno())
    return storage
