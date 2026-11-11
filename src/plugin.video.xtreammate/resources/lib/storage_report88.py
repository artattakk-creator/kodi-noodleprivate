"""Read-only volume evidence and owned-artwork inventory, no cleanup action."""
import os,re
from pathlib import Path
def collect():
 from android_storage83 import measure,relation,public
 from artwork_backend import active_backend,LocalArtworkStorage
 from art_storage import capacity
 result={};roots=[]
 for role in ('logos','media'):
  backend=active_backend(role)
  if not isinstance(backend,LocalArtworkStorage):result[role]={'code':'VFS_REQUIRES_EXPLICIT_PROBE'};continue
  values=capacity(backend=backend);root=Path(backend.root);roots.append(root)
  # Existing redacted measure includes mount identity / available bytes, not
  # private provider/account information. No writes or mount assumptions.
  current=measure(str(root),role)
  try:
   shared=measure('/storage/emulated/0','ANDROID_SHARED',require=True);comparison=relation(current,shared)
  except (OSError,ValueError,__import__('artwork_vfs').StorageFailure):shared=dict(role='ANDROID_SHARED',error='TARGET_VOLUME_UNVERIFIED');comparison='TARGET_VOLUME_UNVERIFIED'
  result[role]=dict(volumes=public([current,shared]),free=values.get('free'),total=values.get('total'),reserve=values.get('reserve'),budget=values.get('budget'),availability=values.get('storage_availability'),pool_comparison=comparison)
 inventory=[]
 for root in roots:
  if root.is_symlink() or not root.is_dir():continue
  count=size=0
  for p in root.iterdir():
   if count>=512:break
   if p.is_symlink() or not p.is_file() or not re.fullmatch(r'[a-f0-9]{64}(?:\.(?:img|png|jpg))?',p.name):continue
   count+=1;size+=p.stat().st_size
  inventory.append(dict(owned_candidates=count,bytes=size,limit=512,orphan_status='NOT_PROVEN',cleanup='NOT_IMPLEMENTED_NO_DELETION'))
 result['inventory']=inventory
 return result
