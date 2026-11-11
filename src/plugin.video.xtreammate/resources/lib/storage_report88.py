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
 # Read-only candidate observations: missing Android paths are explicitly
 # unavailable, never measured as a larger parent pool or selected silently.
 import xbmcvfs
 candidates=[('KODI_HOME',xbmcvfs.translatePath('special://home/')),('KODI_PROFILE',xbmcvfs.translatePath('special://profile/')),('ANDROID_KODI_FILES','/storage/emulated/0/Android/data/org.xbmc.kodi/files')]
 observations=[]
 for label,path89 in candidates:
  try:observations.extend(public([measure(path89,label,require=True)]))
  except (OSError,ValueError,__import__('artwork_vfs').StorageFailure):observations.append(dict(role=label,error='TARGET_VOLUME_UNVERIFIED'))
 result['locations89']=observations
 try:
  from logo_store89 import capacity as mini89,QUOTA,MAX_ASSET
  facts=mini89(active_backend('logos'),512*1024)
  result['logo_policy89']=dict(code='MINI_LOGO_ALLOWED',quota=QUOTA,per_asset=MAX_ASSET,**{k:v for k,v in facts.items() if k in ('free','total','reserve','used')})
 except OSError as error:result['logo_policy89']=dict(code=str(error) if str(error).startswith('LOGO_') else 'LOGO_CAPACITY_UNKNOWN')
 result['write_probe89']='NOT_REQUESTED_USE_EXPLICIT_EXISTING_PREFLIGHT'
 result['inventory']=inventory
 return result
