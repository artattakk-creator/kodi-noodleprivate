"""Read-only exact-local-path capacity evidence. No remote target probes."""
import hashlib,os,re
from pathlib import Path

def local(role,path):
 result=dict(role=role,code='UNKNOWN')
 if not isinstance(path,str) or '://' in path:return dict(result,code='VFS_NOT_PROBED')
 try:
  resolved=os.path.realpath(path);actual=resolved
  while not os.path.exists(actual):
   parent=os.path.dirname(actual)
   if parent==actual:raise OSError('NO_ANCESTOR')
   actual=parent
  stat=os.stat(actual);vfs=os.statvfs(actual);unit=vfs.f_frsize or vfs.f_bsize
  from art_storage import capacity
  policy=capacity(resolved)
  result.update(code='READY',path_hash=hashlib.sha256(resolved.encode()).hexdigest()[:12],device_hash=hashlib.sha256(str(stat.st_dev).encode()).hexdigest()[:12],free_user=vfs.f_bavail*unit,free_root=vfs.f_bfree*unit,total=vfs.f_blocks*unit,reserve=policy['reserve'],write_available=vfs.f_bavail*unit>policy['reserve']+65536)
  longest=-1
  with open('/proc/self/mountinfo') as stream:
   for line in stream:
    left,separator,right=line.partition(' - ')
    if not separator:continue
    fields=left.split();types=right.split()
    if len(fields)<5 or not types:continue
    mount=fields[4].replace('\\040',' ')
    if (resolved==mount or resolved.startswith(mount.rstrip('/')+'/')) and len(mount)>longest:
     longest=len(mount);result['filesystem']=types[0] if re.fullmatch('[a-zA-Z0-9_.-]{1,32}',types[0]) else 'OTHER'
  return result
 except (OSError,AttributeError,TypeError,ValueError):return dict(result,code='READ_UNAVAILABLE')
def report():
 from utils import addon_data_dir
 from programme_art46 import root
 from guide_store import path
 targets=[('PROFILE',addon_data_dir()),('EPG',path()),('PROGRAMME_ARCHIVE',root()),('TEMPORARY85',str(Path(addon_data_dir())/'artwork_temporary85'))]
 return [local(role,str(location)) for role,location in targets]
