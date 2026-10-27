"""Explicit local consistent SQLite/WAL backup; never refresh EPG automatically."""
import hashlib,json,os,sqlite3,tempfile,time
from pathlib import Path
from urllib.parse import quote


def authorize(filename,cancel=lambda:False):
    """User-requested worker action only. Source stays intact on every failure."""
    from import_budget import check_space
    from guide_publish44 import initialize,ready,diagnose
    source=Path(filename)
    if not source.is_file() or source.is_symlink():raise ValueError('GUIDE_FILE_REQUIRED')
    folder=source.parent/'guide_backups44';folder.mkdir(mode=0o700,exist_ok=True)
    if folder.is_symlink():raise ValueError('UNSAFE_BACKUP_PATH')
    check_space(str(source),source.stat().st_size*2+32*1048576)
    destination=folder/('guide-'+str(time.time_ns())+'.sqlite')
    fd=os.open(destination,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    os.close(fd)
    config=source.parent/'xtreammate_epg_sources.json'
    config_bytes=None;config_stamp=None
    if config.exists():
        if config.is_symlink() or config.stat().st_size>4*1048576:raise ValueError('CONFIG_BACKUP_UNSAFE')
        config_stamp=(config.stat().st_mtime_ns,config.stat().st_size)
        config_bytes=config.read_bytes()
        json.loads(config_bytes)  # A corrupt config is not silently backed up as valid.
        if (config.stat().st_mtime_ns,config.stat().st_size)!=config_stamp:raise ValueError('CONFIG_CHANGED_RETRY_BACKUP')
    incoming=sqlite3.connect('file:'+quote(str(source),safe='/')+'?mode=ro',uri=True,timeout=.2)
    output=sqlite3.connect(str(destination),timeout=.2)
    try:
        def progress(status,remaining,total):
            if cancel():raise InterruptedError('CANCELLED')
        incoming.backup(output,pages=256,progress=progress,sleep=.01)
        if output.execute('PRAGMA quick_check').fetchone()[0]!='ok':raise ValueError('BACKUP_INVALID')
        before=output.execute('SELECT pid,revision,updated FROM guide_meta ORDER BY pid').fetchall()
        coverage=output.execute('SELECT pid,count(*),min(start),max(stop) FROM programmes GROUP BY pid ORDER BY pid').fetchall()
        output.close();output=None
        hash_=hashlib.sha256()
        with open(destination,'rb') as f:
            for chunk in iter(lambda:f.read(1048576),b''):
                if cancel():raise InterruptedError('CANCELLED')
                hash_.update(chunk)
        digest=hash_.hexdigest()
        if cancel():raise InterruptedError('CANCELLED')
        db=sqlite3.connect(str(source),timeout=.2)
        try:
            # Do not authorize from a backup made before a concurrent writer.
            db.execute('BEGIN IMMEDIATE')
            after=db.execute('SELECT pid,revision,updated FROM guide_meta ORDER BY pid').fetchall()
            actual=db.execute('SELECT pid,count(*),min(start),max(stop) FROM programmes GROUP BY pid ORDER BY pid').fetchall()
            if before!=after or coverage!=actual:raise ValueError('GUIDE_CHANGED_RETRY_BACKUP')
            if config_stamp and (config.stat().st_mtime_ns,config.stat().st_size)!=config_stamp:raise ValueError('CONFIG_CHANGED_RETRY_BACKUP')
            if config_bytes is not None:
                fd=os.open(str(destination)+'.sources.json',os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
                with os.fdopen(fd,'wb') as f:f.write(config_bytes);f.flush();os.fsync(f.fileno())
            # DDL only follows explicit backup and validated unchanged snapshot.
            initialize(db)
            with db:
                db.execute('INSERT INTO guide44_authorization VALUES(?,?,?)',('VERIFIED_BACKUP',digest,time.time()))
                db.execute("INSERT OR IGNORE INTO guide44_inputs SELECT pid,'legacy:'||source,cid,start,stop,title,description,source FROM programmes")
        finally:db.close()
        manifest=dict(code='BACKUP_VERIFIED',sha256=digest,bytes=destination.stat().st_size,events=sum(r[1] for r in coverage),backup=destination.name,source_config_sha256=hashlib.sha256(config_bytes).hexdigest() if config_bytes is not None else None)
        with open(str(destination)+'.json','x',encoding='utf-8') as f:json.dump(manifest,f);f.flush();os.fsync(f.fileno())
        return manifest
    finally:
        if output is not None:output.close()
        incoming.close()

_worker=None
_last=''


def request():
    """Called only after native owner confirmation; no filesystem work here."""
    import uuid,xbmcgui
    xbmcgui.Window(10000).setProperty('XCMate.GuideBackup44Request',json.dumps(dict(nonce=uuid.uuid4().hex,at=time.time())))


def poll():
    import threading,xbmcgui
    global _worker,_last
    home=xbmcgui.Window(10000);raw=home.getProperty('XCMate.GuideBackup44Request')
    if not raw or len(raw)>512 or _worker is not None and _worker.is_alive():return
    try:value=json.loads(raw)
    except (TypeError,ValueError):return
    if not isinstance(value,dict) or value.get('nonce')==_last:return
    try:
        if not 0<=time.time()-float(value.get('at',0))<120:return
    except (TypeError,ValueError):return
    _last=value.get('nonce');home.clearProperty('XCMate.GuideBackup44Request')
    def work():
        from guide_store import path
        try:
            import xbmc
            monitor=xbmc.Monitor()
            result=authorize(path(),monitor.abortRequested)
            fields={k:result[k] for k in ('code','bytes','events')}
        except Exception as exc:
            fields=dict(code='BACKUP_FAILED',error=type(exc).__name__)
        home.setProperty('XCMate.GuideBackup44Status',json.dumps(fields))
    _worker=threading.Thread(target=work,name='XCMate-guide-backup44',daemon=True);_worker.start()


def show():
    import xbmcgui
    from localization import tr
    d=xbmcgui.Dialog();status=xbmcgui.Window(10000).getProperty('XCMate.GuideBackup44Status')
    if status:
        try:status=json.loads(status)
        except ValueError:status={}
        d.ok('XCMate EPG',tr(35963)+'\n'+str(status.get('code','UNKNOWN')))
    if d.yesno('XCMate EPG',tr(35961),yeslabel=tr(35962)):
        request();d.notification('XCMate EPG',tr(35964))
