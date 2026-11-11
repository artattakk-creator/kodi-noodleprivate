"""Separate bounded JSON receipts; never licenses an image/SQLite archive write."""
from pathlib import Path
MAX_FILE=512*1024
QUOTA=4*1024*1024
PREFIXES=('widget-refs74-','widget-textures79-','xcmate_widget41_')

def check(filename,size):
 from import_budget import check_space
 from art_storage82 import capacity
 from utils import addon_data_dir
 target=Path(filename);root=Path(addon_data_dir())
 if target.parent.resolve()!=root.resolve() or target.is_symlink() or not (target.name.startswith(PREFIXES) and target.suffix=='.json' or target.name=='programme_references84.json'):raise OSError('METADATA_SCOPE_BLOCKED')
 if not 0<size<=MAX_FILE+65536:raise OSError('METADATA_FILE_QUOTA')
 measured=capacity(str(root))
 if measured.get('capacity82')!='SAME_VOLUME_VERIFIED' or type(measured.get('free')) is not int or type(measured.get('total')) is not int:raise OSError('METADATA_CAPACITY_UNKNOWN')
 floor=max(32*1024*1024,min(64*1024*1024,int(measured['total']*.01)))
 if measured['free']<floor+size+65536:raise OSError('METADATA_SAFETY_FLOOR')
 used=0;count=0
 for entry in root.iterdir():
  if entry.name.startswith(PREFIXES) and entry.suffix=='.json' or entry.name=='programme_references84.json':
   if entry.is_symlink():raise OSError('METADATA_UNSAFE_FILE')
   used+=entry.stat().st_size;count+=1
   if used+size>QUOTA or count>128:raise OSError('METADATA_TOTAL_QUOTA')
 check_space(filename,size)
