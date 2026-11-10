"""Migration adapter for exact owned programme image names, never databases."""
import os,re
from artwork_backend import LocalArtworkStorage
from artwork_vfs import StorageFailure
PATTERN=re.compile(r'(?:blob46-|user86-)[a-f0-9]{64}\.(?:jpg|png)')
class ProgrammeStorage(LocalArtworkStorage):
 def _safe(self):
  current=self.root
  while current and current!='/':
   if os.path.islink(current):raise StorageFailure('TARGET_SYMLINK')
   current=os.path.dirname(current)
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
 return ProgrammeStorage(programme_root(config))
def target(path,profile):
 from artwork_vfs import backend_for
 if '://' in path:raise StorageFailure('UNSUPPORTED_TARGET')
 return ProgrammeStorage(os.path.join(os.path.dirname(os.path.dirname(backend_for(path,profile,'logos').root)),'programme_images87',profile))
