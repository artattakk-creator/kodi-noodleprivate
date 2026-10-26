"""Optional read-only Box-A preflight. Never installs, copies, repairs or deletes.

Host: --profile PATH [--verify-backup PATH --quiescent-confirmed].
Kodi RunScript from an external medium: no arguments; resolve installed profile
and show only a private summary. A live Kodi process cannot claim a verified,
quiescent multi-database backup. No raw settings/URLs/credentials are printed.
"""
import argparse,hashlib,json,os,stat
from pathlib import Path
import xml.etree.ElementTree as ET
ROOTS=('media_art_v1','tv_logos')


def digest(path):
    before=path.stat(follow_symlinks=False)
    if not stat.S_ISREG(before.st_mode) or before.st_nlink!=1:raise ValueError('UNSAFE_FILE')
    value=hashlib.sha256()
    with path.open('rb') as stream:
        while True:
            block=stream.read(65536)
            if not block:break
            value.update(block)
    after=path.stat(follow_symlinks=False)
    if (before.st_ino,before.st_size,before.st_mtime_ns)!=(after.st_ino,after.st_size,after.st_mtime_ns):raise ValueError('SOURCE_CHANGED')
    return before.st_size,value.hexdigest()


def scan(folder):
    root=Path(folder)
    if root.is_symlink() or not root.is_dir():raise ValueError('PROFILE_UNAVAILABLE')
    files={};unsafe=0;images={name:dict(files=0,bytes=0) for name in ROOTS}
    for entry in root.iterdir():
        if entry.is_symlink():unsafe+=1;continue
        if entry.is_file() and entry.name.endswith(('.json','.xml','.sqlite','.sqlite-wal','.sqlite-shm','.db','.db-wal')):
            files[entry.name]=digest(entry)
    for name in ROOTS:
        directory=root/name
        if directory.is_symlink():unsafe+=1;continue
        if not directory.is_dir():continue
        for entry in directory.iterdir():
            if entry.is_symlink():unsafe+=1;continue
            leaf=entry.name
            if len(leaf)!=68 or not leaf.endswith('.img') or any(c not in '0123456789abcdef' for c in leaf[:64]):continue
            if not entry.is_file():continue
            value=digest(entry);files[name+'/'+leaf]=value;images[name]['files']+=1;images[name]['bytes']+=value[0]
    aggregate=hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest()
    return dict(files=files,images=images,scoped_files=len(files),scoped_bytes=sum(v[0] for v in files.values()),aggregate_sha256=aggregate,unsafe=unsafe)


def audit(profile,backup=None,quiescent=False):
    source=scan(profile);result={k:v for k,v in source.items() if k!='files'}
    result.update(code='OK',readonly=True,scope='Internal URL-hashed image roots and root JSON/XML/SQLite(+WAL/SHM); image headers are not decoded by this audit',backup_verified=False,backup_reason='NO_BACKUP_COMPARED')
    if backup:
        target=scan(backup);match=source['files']==target['files']
        result['backup_files_match']=match
        result['backup_verified']=bool(match and quiescent and not source['unsafe'] and not target['unsafe'])
        result['backup_reason']='VERIFIED_SCOPED_BYTES' if result['backup_verified'] else 'SOURCE_NOT_QUIESCENT' if not quiescent else 'UNSAFE_LINKS_PRESENT' if source['unsafe'] or target['unsafe'] else 'BACKUP_MISMATCH'
    return result


def main():
    p=argparse.ArgumentParser();p.add_argument('--profile');p.add_argument('--verify-backup');p.add_argument('--quiescent-confirmed',action='store_true');p.add_argument('--addon');args=p.parse_args()
    kodi=False;version='UNKNOWN';build='UNKNOWN'
    try:
        if not args.profile:
            import xbmcvfs,xbmcaddon,xbmc
            args.profile=xbmcvfs.translatePath('special://profile/addon_data/plugin.video.xtreammate/')
            version=xbmcaddon.Addon('plugin.video.xtreammate').getAddonInfo('version');build=xbmc.getInfoLabel('System.BuildVersion');kodi=True
        if not args.profile:raise ValueError('PROFILE_REQUIRED')
        result=audit(args.profile,args.verify_backup,args.quiescent_confirmed and not kodi)
        if args.addon:version=ET.parse(Path(args.addon)/'addon.xml').getroot().get('version','UNKNOWN')
        result.update(installed_addon_version=version,kodi_version=build)
    except Exception as error:result=dict(code='AUDIT_UNAVAILABLE',error=type(error).__name__,readonly=True,backup_verified=False)
    text=json.dumps(result,indent=2,ensure_ascii=False)
    if kodi:
        import xbmcgui
        xbmcgui.Dialog().textviewer('XCMate – private read-only inventory',text)
    else:print(text)
if __name__=='__main__':main()
