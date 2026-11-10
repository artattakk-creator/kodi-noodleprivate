"""Migration adapter for exact owned programme image names, never databases."""
import os,re
from artwork_backend import LocalArtworkStorage
from artwork_vfs import StorageFailure
PATTERN=re.compile(r'(?:blob46-|user86-)[a-f0-9]{64}\.(?:jpg|png)')
class ProgrammeStorage(LocalArtworkStorage):
 def __init__(self,root,marker=None):super().__init__(root);self.marker=marker
 def _safe(self):
  current=self.root
  while current and current!='/':
   if os.path.islink(current):raise StorageFailure('TARGET_SYMLINK')
   current=os.path.dirname(current)
  if self.marker:
   if os.path.islink(self.marker):raise StorageFailure('TARGET_SYMLINK')
   try:
    with open(self.marker,'rb') as stream:owned=stream.read(128)==b'XCMATE_ARTWORK_V1'
   except OSError:owned=False
   if not owned:raise StorageFailure('STORAGE_OFFLINE')
 def read(self,ident,limit):
  self._safe();return super().read(ident,limit)
 def write_verified(self,ident,data,validate):
  self._safe()
  if self.exists(ident) and self.read(ident,len(data)+1)!=data:raise StorageFailure('TARGET_COLLISION')
  return super().write_verified(ident,data,validate)
 def resolve_target(self,ident=None):
  self._safe()
  if ident is None:return self.root
  if not PATTERN.fullmatch(ident):raise StorageFailure('INVALID_ARTWORK_KEY')
  path=os.path.join(self.root,ident)
  if os.path.islink(self.root) or os.path.islink(path):raise StorageFailure('TARGET_SYMLINK')
  return path
 def enumerate_for_migration(self):
  if os.path.islink(self.root):raise StorageFailure('TARGET_SYMLINK')
  if not os.path.isdir(self.root):return
  with os.scandir(self.root) as entries:
   for row in entries:
    if PATTERN.fullmatch(row.name) and row.is_file(follow_symlinks=False):yield dict(ident=row.name,bytes=row.stat(follow_symlinks=False).st_size)
def source(config):
 from android_artwork87 import programme_root
 if config.get('programme_target87') and config['mode']=='external':
  from artwork_vfs import backend_for
  backend=backend_for(config['programme_target87'],config['profile'],'logos');return ProgrammeStorage(programme_root(config),backend.owner_marker)
 return ProgrammeStorage(programme_root(config))
def target(path,profile):
 from artwork_vfs import backend_for
 if '://' in path:raise StorageFailure('UNSUPPORTED_TARGET')
 backend=backend_for(path,profile,'logos')
 return ProgrammeStorage(os.path.join(os.path.dirname(os.path.dirname(backend.root)),'programme_images87',profile),backend.owner_marker)
