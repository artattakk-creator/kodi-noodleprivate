"""Post-readback same-volume evidence; RAM streaming never invents raw deletion.

Only known database/cache classes are measured. Unknown XML/archive files are
explicitly preserved. Existing bounded, journalled retention remains separate.
"""
import os,time
from pathlib import Path


def volume(root):
    st=os.stat(root);space=os.statvfs(root)
    return dict(device=st.st_dev,filesystem=getattr(space,'f_fsid',0),free=space.f_bavail*space.f_frsize)


def inventory(root):
    result={}
    for name in ('guide_v1.sqlite','programme_meta46.sqlite','programme_artwork.sqlite'):
        values={}
        for suffix in ('','-wal','-shm'):
            file=root/(name+suffix)
            if file.is_file() and not file.is_symlink():values[suffix or 'database']=file.stat().st_size
        result[name]=values
    raw_count=raw_bytes=0
    # Nonrecursive, bounded inventory only; user-selected feeds are protected.
    with os.scandir(root) as entries:
        complete=True
        for n,entry in enumerate(entries):
            if n>=4096:complete=False;break
            if entry.name.endswith(('.xml','.xml.gz','.gz','.zip','.part')) and entry.is_file(follow_symlinks=False):
                raw_count+=1;raw_bytes+=entry.stat(follow_symlinks=False).st_size
    result['raw']=dict(files=raw_count,bytes=raw_bytes,code='SKIPPED_UNPROVEN',complete=complete)
    return result


def confirmed(pid,revision):
    from epg_snapshot92 import committed
    from utils import addon_data_dir
    root=Path(addon_data_dir())
    if root.is_symlink():raise OSError('EPG_ROOT_UNSAFE')
    before=volume(root);classes=inventory(root)
    if not committed(pid,revision):raise OSError('EPG_READBACK_REVISION_CHANGED')
    after=volume(root)
    if (before['device'],before['filesystem'])!=(after['device'],after['filesystem']):raise OSError('EPG_VOLUME_CHANGED')
    result=dict(code='IMPORT_CONFIRMED_RAW_NOT_PERSISTED',at=time.time(),revision=revision,
        volume=before['device'],filesystem=before['filesystem'],free_before=before['free'],free_after=after['free'],
        observed_free_change=after['free']-before['free'],raw_deleted_files=0,raw_deleted_bytes=0,
        classes=classes,backup='PROTECTED_SEPARATE_RETENTION',active_staging='PROTECTED')
    # Private control writer: no raw URLs or programme text in the receipt.
    # Dedicated file, never overwrite the existing resumable setup checkpoint.
    import json,tempfile
    from wizard_storage71 import protect
    filename=root/'epg_cleanup94.json';fd,temp=tempfile.mkstemp(prefix='.epg-cleanup94-',dir=root)
    try:
        protect(temp,fd=fd)
        with os.fdopen(fd,'w') as stream:fd=None;json.dump(result,stream,separators=(',',':'));stream.flush();os.fsync(stream.fileno())
        os.replace(temp,filename);temp=None
    finally:
        if fd is not None:os.close(fd)
        if temp:os.unlink(temp)
    return result
