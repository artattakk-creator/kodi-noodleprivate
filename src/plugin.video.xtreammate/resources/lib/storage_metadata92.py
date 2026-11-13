"""Small bounded control-plane writes; never licenses an artwork/DB bulk write."""
import os
import re
from pathlib import Path
MAX_RECORD = 1024 * 1024
FLOOR = 4 * 1024 * 1024

def check(filename, upcoming=65536, *, kind='mapping'):
    from utils import addon_data_dir
    from artwork_vfs import StorageFailure
    target = Path(filename)
    root = Path(addon_data_dir()).resolve()
    permitted = {'mapping': 'programme_manual85.json', 'migration': 'artwork_transfer_v1.sqlite',
                 'policy': 'storage_policy92.json', 'maintenance': 'storage_maintenance92.json'}
    if kind=='receipt' and re.fullmatch(r'xcmate_external89_[a-f0-9]{24}\.json',target.name):
        permitted['receipt']=target.name
        if upcoming>512*1024+65536:raise StorageFailure('METADATA_SCOPE_BLOCKED')
        used=count=0
        for file in root.glob('xcmate_external89_*.json'):
            if file.is_symlink():raise StorageFailure('METADATA_SCOPE_BLOCKED')
            if file!=target:used+=file.stat().st_size;count+=1
            if used+upcoming>4*1024**2 or count>=128:raise StorageFailure('METADATA_TOTAL_QUOTA')
    if (kind not in permitted or target.name != permitted[kind] or target.parent.resolve() != root
            or target.is_symlink() or any(p.is_symlink() for p in target.parents)
            or not 0 <= upcoming <= MAX_RECORD):
        raise StorageFailure('METADATA_SCOPE_BLOCKED')
    facts = os.statvfs(str(root));unit = facts.f_frsize or facts.f_bsize
    available = facts.f_bavail * unit
    # Separate 4-MiB metadata floor, bounded record + atomic replacement space.
    # The 32-MiB import / 1-GiB image policies are left intact.
    if available < FLOOR + 2 * upcoming:
        raise StorageFailure('RESERVE_BLOCKED')
    return dict(available=available, reserve=FLOOR, requested=upcoming)
