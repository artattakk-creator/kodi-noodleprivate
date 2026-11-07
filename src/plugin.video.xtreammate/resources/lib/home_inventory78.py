"""Private, read-only inventory before changing own Home hooks.

Never inventories portals/tokens or writes SkinShortcuts/user settings. Copies
are local recovery evidence, not uploadable diagnostics.
"""
import hashlib,json,os,time,uuid
from pathlib import Path

def snapshot(profile,skin):
    from utils import addon_data_dir
    from widget_transaction50 import private,read
    profile=Path(profile).resolve();skin=Path(skin).resolve()
    paths=[profile/'addon_data/skin.titan.bingie.mod/settings.xml',skin/'xml/script-skinshortcuts-includes.xml']
    shortcuts=profile/'addon_data/script.skinshortcuts'
    if shortcuts.is_symlink():raise ValueError('UNSAFE_TARGET')
    if shortcuts.exists():
        paths+=sorted(p for p in shortcuts.iterdir() if p.is_file() and p.suffix.lower() in ('.xml','.properties','.hash'))
    if len(paths)>96:raise ValueError('PROFILE_BUDGET')
    values=[];total=0
    for path in paths:
        if not path.exists():continue
        if path.is_symlink() or (profile not in path.resolve().parents and skin not in path.resolve().parents):raise ValueError('UNSAFE_TARGET')
        data=read(path);total+=len(data)
        if total>32*1024*1024:raise ValueError('PROFILE_BUDGET')
        values.append((path,data))
    root=Path(addon_data_dir())/'home78_inventory'
    if root.is_symlink():raise ValueError('UNSAFE_BACKUP_FOLDER')
    root.mkdir(mode=0o700,exist_ok=True);folder=root/uuid.uuid4().hex;folder.mkdir(mode=0o700)
    records=[]
    for i,(path,data) in enumerate(values):
        name=str(i)+'.original';private(folder/name,data)
        if read(folder/name)!=data:raise ValueError('BACKUP_VERIFY_FAILED')
        records.append(dict(target=str(path),file=name,sha256=hashlib.sha256(data).hexdigest(),bytes=len(data)))
    private(folder/'inventory.json',json.dumps(dict(version=1,at=time.time(),files=records)).encode())
    return folder.name
