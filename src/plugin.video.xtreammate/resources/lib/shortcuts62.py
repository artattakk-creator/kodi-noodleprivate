"""Opt-in exact Skinshortcuts 2.1.0 Python fix; never runs at install/startup."""
import ast,difflib,hashlib,json,os,stat,time,uuid
from pathlib import Path
BEFORE='43d51ee82cac216e62ed4fe6defa1c08eadf20f8b18264ab1e4a6e345680a128'
AFTER='10e513d7eb8f61156c71f08078cca6c5b43cca7d2b471ce3488b3fc3cbc0eed5'

def candidate(raw):
    if hashlib.sha256(raw).hexdigest()!=BEFORE:raise ValueError('SHORTCUTS_SOURCE_UNVERIFIED')
    if raw.count(b'.getiterator()')!=2:raise ValueError('SHORTCUTS_SOURCE_UNVERIFIED')
    new=raw.replace(b'.getiterator()',b'.iter()');ast.parse(new);return new

def target(root,version):
    if version!='2.1.0':raise ValueError('SHORTCUTS_VERSION_UNVERIFIED')
    root=Path(root);p=root/'resources/lib/library.py'
    if any(v.is_symlink() for v in (root,p.parent,p.parent.parent,p)):raise ValueError('UNSAFE_TARGET')
    return p

def folder():
    from utils import addon_data_dir
    p=Path(addon_data_dir())/'shortcuts62_plans'
    if p.is_symlink():raise ValueError('UNSAFE_BACKUP_FOLDER')
    p.mkdir(mode=0o700,exist_ok=True);return p

def prepare(root,version):
    from widget_transaction50 import read,private
    p=target(root,version);old=read(p);new=candidate(old);token=uuid.uuid4().hex;backup=folder()/token;backup.mkdir(mode=0o700)
    private(backup/'original',old);private(backup/'candidate',new)
    plan=dict(id=token,target=str(p.resolve()),before=BEFORE,after=hashlib.sha256(new).hexdigest(),mode=stat.S_IMODE(p.stat().st_mode),at=time.time())
    private(backup/'plan.json',json.dumps(plan).encode())
    if read(backup/'original')!=old or read(backup/'candidate')!=new:raise ValueError('BACKUP_VERIFY_FAILED')
    return plan,'\n'.join(difflib.unified_diff(old.decode().splitlines(),new.decode().splitlines(),fromfile='Skinshortcuts 2.1.0 library.py',tofile='library.py – Python 3.11',lineterm=''))

def apply(token,root,version,*,confirmed=False,restore=False):
    if confirmed is not True:raise PermissionError('EXPLICIT_APPROVAL_REQUIRED')
    if len(token)!=32 or any(c not in '0123456789abcdef' for c in token):raise ValueError('UNSAFE_PLAN')
    from widget_transaction50 import read,replace
    import fcntl
    base=folder()
    if (base/token).is_symlink():raise ValueError('UNSAFE_PLAN')
    lock=open(base/'.lock','a')
    try:
        fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        p=target(root,version);plan=json.loads(read(base/token/'plan.json'));old=read(base/token/'original');new=read(base/token/'candidate')
        if str(p.resolve())!=plan['target'] or hashlib.sha256(old).hexdigest()!=BEFORE or candidate(old)!=new or hashlib.sha256(new).hexdigest()!=plan['after']:raise ValueError('BACKUP_VERIFY_FAILED')
        replace(p,old if restore else new,plan['after'] if restore else BEFORE,plan['mode'])
        return 'RESTORED' if restore else 'SHORTCUTS_PATCH_VERIFIED'
    finally:lock.close()

def context():
    import xbmcaddon
    from widget_manager50 import runtime
    runtime()  # Active verified BINGIE, compatible builder, no playing/editor.
    addon=xbmcaddon.Addon('script.skinshortcuts')
    return Path(addon.getAddonInfo('path')),addon.getAddonInfo('version')

def show(restore=False):
    import xbmcgui
    from localization import tr
    from widget_transaction50 import read
    dialog=xbmcgui.Dialog()
    try:
        root,version=context()
        if not restore and hashlib.sha256(read(target(root,version))).hexdigest()==AFTER:
            dialog.ok('XCMate',tr(36649));return
        if restore:
            plans=[]
            for p in folder().iterdir():
                if p.is_dir() and not p.is_symlink() and len(p.name)==32:
                    try:
                        plan=json.loads(read(p/'plan.json'))
                        if plan['target']==str(target(root,version).resolve()) and hashlib.sha256(read(target(root,version))).hexdigest()==plan['after']:plans.append(plan)
                    except (OSError,ValueError,KeyError):pass
            plans.sort(key=lambda p:p['at'],reverse=True)
            if not plans:dialog.ok('XCMate',tr(36647));return
            plan=plans[0];preview=tr(36648)
        else:plan,preview=prepare(root,version)
        dialog.textviewer(tr(36641),plan['before']+' → '+plan['after']+'\n\n'+preview)
        if not dialog.yesno(tr(36641),tr(36644 if restore else 36643),defaultbutton=getattr(xbmcgui,'DLG_YESNO_NO_BTN',10)):return
        now_root,now_version=context()
        if now_root!=root or now_version!=version:raise ValueError('PROFILE_CHANGED')
        apply(plan['id'],root,version,confirmed=True,restore=restore)
        dialog.ok('XCMate',tr(36646))
    except (OSError,ValueError,KeyError,RuntimeError) as exc:
        # No local paths, arbitrary exception text, profile IDs or credentials.
        safe={'SHORTCUTS_SOURCE_UNVERIFIED','SHORTCUTS_VERSION_UNVERIFIED','TARGET_CHANGED_NO_OVERWRITE','BACKUP_VERIFY_FAILED','PROFILE_CHANGED','PLAYER_ACTIVE','NATIVE_EDITOR_BUSY','UNSAFE_PLAN','UNSAFE_TARGET','UNSUPPORTED_SKIN','UNVERIFIED_SHORTCUTS_VERSION'}
        code=str(exc) if str(exc) in safe else 'LOCAL_UNAVAILABLE'
        dialog.ok('XCMate',tr(36645)+'\n'+code)
