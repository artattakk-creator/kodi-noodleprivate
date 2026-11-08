"""Same-volume capacity evidence. No path/host/device identifiers in receipts.

Existing storage selection and reserves remain authoritative. No probing of
unselected volumes, no migration or writes in automatic capacity checks.
"""
import hashlib,json,os,shutil,time
_seen={}
TYPES={'ext4','f2fs','fuse','fuseblk','sdcardfs','esdfs','tmpfs','overlay','cifs','nfs','vfat','exfat'}

def existing(location):
    target=os.path.realpath(location)
    while not os.path.isdir(target):
        parent=os.path.dirname(target)
        if parent==target:break
        target=parent
    return target

def mount_type(target):
    best='UNKNOWN';length=-1
    try:
        with open('/proc/self/mountinfo',encoding='utf-8') as stream:
            for line in stream:
                left,sep,right=line.partition(' - ')
                fields=left.split();parts=right.split()
                if not sep or len(fields)<5 or not parts:continue
                point=fields[4].replace('\\040',' ').replace('\\134','\\')
                if (target==point or target.startswith(point.rstrip('/')+'/')) and len(point)>length:
                    length=len(point);best=parts[0] if parts[0] in TYPES else 'OTHER'
    except OSError:pass
    return best

def capacity(location,usage=None):
    target=existing(location);usage=usage or shutil.disk_usage(target)
    value=dict(free=usage.free,total=usage.total,backend82='LOCAL',location82='SELECTED_LOCAL',mount82=mount_type(target),capacity82='SHUTIL_ONLY')
    try:
        before=os.stat(target);vfs=os.statvfs(target);after=os.stat(target)
        unit=vfs.f_frsize or vfs.f_bsize
        free=vfs.f_bavail*unit;total=vfs.f_blocks*unit
        value['volume82']=hashlib.sha256(str(before.st_dev).encode()).hexdigest()[:12]
        value.update(statvfs_free82=free,statvfs_total82=total)
        if before.st_dev!=after.st_dev:value.update(free=None,total=None,capacity82='VOLUME_CHANGED')
        elif free<0 or total<=0 or free>total:value.update(free=None,total=None,capacity82='CAPACITY_INVALID')
        elif usage.total==total and abs(usage.free-free)<=max(unit,256*1024):
            # f_bavail is capacity available to this application, not root's f_bfree.
            value.update(free=min(usage.free,free),total=total,capacity82='SAME_VOLUME_VERIFIED')
        else:
            # Never borrow a larger unrelated Android emulated volume to pass a check.
            value.update(free=min(usage.free,free),total=min(usage.total,total),capacity82='CAPACITY_DISAGREEMENT')
    except OSError as error:
        value.update(free=None,total=None,capacity82='STORAGE_OFFLINE' if getattr(error,'errno',None) in (2,5,19,107) else 'CAPACITY_UNKNOWN')
    return value

def receipt(location,role='IMAGE',upcoming=0,probe=False):
    """Read-only by default. Explicit 4KiB probe only inside our cache and reserve."""
    from art_storage import capacity as selected,check
    value=selected(location=location)
    value.update(role82=role if role in ('LOGO','POSTER','FANART','IMAGE','METADATA') else 'IMAGE',requested82=max(0,int(upcoming)),write_probe82='NOT_REQUESTED')
    if probe:
        from utils import addon_data_dir
        root=os.path.realpath(addon_data_dir());target=os.path.realpath(location)
        if target not in (os.path.join(root,'programme_images46'),os.path.join(root,'media_art_v1'),os.path.join(root,'tv_logos')):
            value['write_probe82']='OUTSIDE_OWN_CACHE';return value
        try:
            from import_budget import check_space,RESERVE
            check_space(os.path.join(location,'probe82'),4096)
            value['probe_reserve82']=RESERVE
            if not os.path.isdir(location):value['write_probe82']='TARGET_NOT_CREATED';return value
            import tempfile
            fd,name=tempfile.mkstemp(prefix='.probe82-',dir=location)
            try:
                before=os.fstat(fd)
                with os.fdopen(fd,'wb') as stream:stream.write(bytes(4096));stream.flush();os.fsync(stream.fileno())
                after=os.stat(name)
                with open(name,'rb') as stream:valid=stream.read(4097)==bytes(4096)
                value['write_probe82']='VERIFIED_SAME_VOLUME' if valid and before.st_dev==after.st_dev==os.stat(location).st_dev else 'PROBE_MISMATCH'
            finally:
                # Only the newly created named probe; never an existing user file.
                if os.path.exists(name):os.unlink(name)
        except OSError as error:value['write_probe82']=getattr(error,'reason','') or getattr(error,'code','PROBE_BLOCKED')
    return value

def note(value,code):
    """Diagnostic status is explicitly not proof of Android mount/texture success."""
    safe={k:v for k,v in value.items() if k in ('free','total','reserve','budget','backend82','location82','mount82','capacity82','volume82','statvfs_free82','statvfs_total82','role82','requested82','write_probe82','reserve_policy82','probe_reserve82') and type(v) in (str,int,float,bool,type(None))}
    safe['code82']=code if code in ('OK','RESERVE_BLOCKED','BLOCKED_REAL_DISK','BUDGET_FULL','STORAGE_OFFLINE','CAPACITY_UNKNOWN','CAPACITY_DISAGREEMENT') else 'UNAVAILABLE'
    tag=(safe.get('volume82'),safe['code82'],safe.get('role82'));now=time.monotonic()
    if now-_seen.get(tag,-1e9)<60:return
    _seen[tag]=now
    while len(_seen)>64:_seen.pop(next(iter(_seen)))
    import xbmc
    try:xbmc.log('[XCMate][ART_STORAGE82] '+json.dumps(safe,separators=(',',':')),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass


def overview():
    from utils import addon_data_dir
    from artwork_backend import active_backend
    import xbmcvfs
    rows=[]
    locations=[('PROFILE_PROGRAMME',os.path.join(addon_data_dir(),'programme_images46')),('PROFILE_METADATA',addon_data_dir()),('KODI_TEXTURES',xbmcvfs.translatePath('special://thumbnails/'))]
    backend=active_backend()
    if backend.kind=='LOCAL':locations.append(('SELECTED_ARCHIVE',backend.resolve_target()))
    for label,location in locations:
        if not isinstance(location,str) or not os.path.isabs(location):continue
        try:value=receipt(location)
        except OSError:value=dict(capacity82='STORAGE_OFFLINE',free=None,total=None)
        value['location82']=label;rows.append(value)
    return rows
