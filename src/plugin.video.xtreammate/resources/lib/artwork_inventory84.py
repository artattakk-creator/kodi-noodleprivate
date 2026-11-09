"""Read-only bounded counts; never walks links or changes Kodi texture files."""
import os,time
from pathlib import Path

def measure():
 import xbmcvfs
 from utils import addon_data_dir
 root=Path(addon_data_dir());deadline=time.monotonic()+3;result={}
 targets={'xcmate_media':root/'media_art_v1','xcmate_logos':root/'tv_logos','xcmate_programme':root/'programme_images46',
          'kodi_textures':Path(xbmcvfs.translatePath('special://thumbnails/'))}
 for name,start in targets.items():
  total=count=0;pending=[start];code='COMPLETE'
  while pending:
   if time.monotonic()>deadline or count>=20000:code='PARTIAL_BUDGET';break
   folder=pending.pop()
   try:
    with os.scandir(folder) as entries:
     for entry in entries:
      if entry.is_symlink():continue
      if entry.is_dir(follow_symlinks=False):pending.append(Path(entry.path))
      elif entry.is_file(follow_symlinks=False):total+=entry.stat(follow_symlinks=False).st_size;count+=1
      if count>=20000 or time.monotonic()>deadline:code='PARTIAL_BUDGET';break
   except FileNotFoundError:pass
   except OSError:code='READ_UNAVAILABLE'
   if code!='COMPLETE':break
  result[name]=dict(bytes=total,files=count,code=code)
 return result
