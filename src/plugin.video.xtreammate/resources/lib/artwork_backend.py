"""Image-file boundary; job SQLite always remains in internal userdata.

.36 enables only the existing local directories. VFS targets, selection and
copy/verify/resume migration are .37 work; URI paths fail closed here. No
adapter deletes originals or changes settings. Workers own writes/inventory.
"""
from abc import ABC, abstractmethod
import hashlib
import os
import shutil
import tempfile


class ArtworkStorageBackend(ABC):
    kind = 'UNKNOWN'

    @abstractmethod
    def resolve_target(self, ident=None):pass
    @abstractmethod
    def stat(self, ident=None):pass
    @abstractmethod
    def free_or_unknown(self):pass
    @abstractmethod
    def exists(self, ident):pass
    @abstractmethod
    def read(self, ident, limit):pass
    @abstractmethod
    def write_verified(self, ident, data, validate):pass
    @abstractmethod
    def make_display_uri(self, ident):pass
    @abstractmethod
    def availability(self):pass
    @abstractmethod
    def enumerate_for_migration(self):pass


class LocalArtworkStorage(ArtworkStorageBackend):
    kind = 'LOCAL'

    def __init__(self, root):
        root=os.fspath(root)
        if '://' in root or not os.path.isabs(root):
            raise ValueError('UNSUPPORTED_ARTWORK_BACKEND')
        self.root=root

    def resolve_target(self, ident=None):
        if ident is None:return self.root
        if len(ident)!=64 or any(c not in '0123456789abcdef' for c in ident):
            raise ValueError('INVALID_ARTWORK_KEY')
        return os.path.join(self.root,ident+'.img')

    def stat(self, ident=None):
        value=os.stat(self.resolve_target(ident))
        return dict(bytes=value.st_size,revision=value.st_mtime_ns)

    def free_or_unknown(self):
        target=self.root
        # Probe this mount; a future SMB adapter must report None for unknown
        # capacity instead of consulting internal userdata or inventing bytes.
        while not os.path.isdir(target):
            parent=os.path.dirname(target)
            if parent==target:break
            target=parent
        value=shutil.disk_usage(target)
        return dict(free=value.free,total=value.total)

    def exists(self, ident):
        return os.path.isfile(self.resolve_target(ident))

    def read(self, ident, limit):
        with open(self.resolve_target(ident),'rb') as stream:return stream.read(limit)

    def write_verified(self, ident, data, validate):
        """Bounded image, same-directory atomic publish after verified readback."""
        if len(data)>3*1024*1024 or not validate(data):raise ValueError('INVALID_IMAGE')
        target=self.resolve_target(ident);os.makedirs(self.root,exist_ok=True)
        temporary=''
        try:
            fd,temporary=tempfile.mkstemp(prefix='.art-',dir=self.root)
            with os.fdopen(fd,'wb') as stream:
                stream.write(data);stream.flush();os.fsync(stream.fileno())
            with open(temporary,'rb') as stream:readback=stream.read(len(data)+1)
            if len(readback)!=len(data) or hashlib.sha256(readback).digest()!=hashlib.sha256(data).digest() or not validate(readback):
                raise OSError('ARTWORK_VERIFY_FAILED')
            os.replace(temporary,target);temporary=''
            return self.make_display_uri(ident)
        finally:
            if temporary:
                try:os.unlink(temporary)
                except OSError:pass

    def make_display_uri(self, ident):
        return self.resolve_target(ident)

    def availability(self):
        try:self.free_or_unknown();return 'AVAILABLE'
        except OSError:return 'UNAVAILABLE'

    def enumerate_for_migration(self):
        """Worker-only lazy, read-only inventory; no migration or removal."""
        if not os.path.isdir(self.root):return
        with os.scandir(self.root) as entries:
            for entry in entries:
                ident=entry.name[:-4]
                if entry.name.endswith('.img') and len(ident)==64 and all(c in '0123456789abcdef' for c in ident) and entry.is_file(follow_symlinks=False):
                    yield dict(ident=ident,bytes=entry.stat(follow_symlinks=False).st_size)


def active_backend(kind='media'):
    """Compatible .35 roots; no external setting or silent target fallback."""
    from utils import addon_data_dir
    if kind not in ('media','logos'):raise ValueError('INVALID_ARTWORK_KIND')
    return LocalArtworkStorage(os.path.join(addon_data_dir(),'media_art_v1' if kind=='media' else 'tv_logos'))
