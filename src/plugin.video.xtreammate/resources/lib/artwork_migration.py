"""Explicit copy/verify/activate workflow. Journal stays on internal userdata.

No automatic move, no SQLite relocation. Original cleanup is a different UI
operation requiring the active transfer challenge and a fresh full verification.
All filesystem/network work runs on workers under the common writer gate.
"""
import hashlib
import json
import os
import sqlite3
import time
import uuid
from artwork_vfs import backend_for,prepare_target,image_valid,StorageFailure,MAX_BYTES
from artwork_backend import LocalArtworkStorage
from artwork_gate import writer,guarded

KINDS=('media','logos')  # Legacy fanart shares media's URL-hashed directory.


def path():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'artwork_transfer_v1.sqlite')


def _db():
    from import_budget import check_space
    check_space(path(),65536)
    db=sqlite3.connect(path(),timeout=.1);db.row_factory=sqlite3.Row
    db.executescript('CREATE TABLE IF NOT EXISTS transfers(id TEXT PRIMARY KEY,target TEXT,source TEXT,stage TEXT,rendered INTEGER DEFAULT 0);'
                    'CREATE TABLE IF NOT EXISTS files(transfer TEXT,kind TEXT,ident TEXT,bytes INTEGER,sha TEXT,status TEXT,PRIMARY KEY(transfer,kind,ident));'
                    'CREATE TABLE IF NOT EXISTS selected(id TEXT);'
                    'CREATE TABLE IF NOT EXISTS probes(transfer TEXT,ident TEXT,sha TEXT,PRIMARY KEY(transfer,ident));'
                    'CREATE TABLE IF NOT EXISTS cleanup(transfer TEXT,kind TEXT,ident TEXT,PRIMARY KEY(transfer,kind,ident));')
    return db


def _selected(db):
    row=db.execute('SELECT t.* FROM transfers t JOIN selected s ON s.id=t.id LIMIT 1').fetchone()
    return dict(row) if row else None


def status():
    if not os.path.isfile(path()):return dict(stage='IDLE',files=0,bytes=0,done=0,done_bytes=0)
    # Read-only status never adopts or repairs source/job databases.
    db=sqlite3.connect('file:'+__import__('urllib.parse',fromlist=['quote']).quote(path(),safe='/')+'?mode=ro',uri=True,timeout=.05);db.row_factory=sqlite3.Row
    try:
        item=_selected(db)
        if not item:return dict(stage='IDLE',files=0,bytes=0,done=0,done_bytes=0)
        row=db.execute("SELECT count(*),coalesce(sum(bytes),0),coalesce(sum(status='VERIFIED'),0),coalesce(sum(CASE WHEN status='VERIFIED' THEN bytes ELSE 0 END),0) FROM files WHERE transfer=?",(item['id'],)).fetchone()
        return dict(stage=item['stage'],files=row[0],bytes=row[1],done=row[2],done_bytes=row[3],transfer=item['id'],rendered=bool(item['rendered']))
    finally:db.close()


def busy():
    try:return status()['stage'] in ('INVENTORY','COPYING','VERIFYING')
    except (OSError,sqlite3.Error):return True


def _source(config,kind):
    from utils import addon_data_dir
    if config.get('archive_mode',config['mode'])=='external':return backend_for(config['target'],config['profile'],kind)
    return LocalArtworkStorage(os.path.join(addon_data_dir(),'media_art_v1' if kind=='media' else 'tv_logos'))


def _target(item,kind):
    source=json.loads(item['source'])
    if item['target']=='INTERNAL':
        from utils import addon_data_dir
        return LocalArtworkStorage(os.path.join(addon_data_dir(),'media_art_v1' if kind=='media' else 'tv_logos'))
    return backend_for(item['target'],source['profile'],kind)


def _phase(db,item,stage):
    with db:db.execute('UPDATE transfers SET stage=? WHERE id=?',(stage,item['id']))
    item['stage']=stage


def begin(target):
    from artwork_config import initialize,read
    from artwork_vfs import target_root
    initialize()
    with writer():
        config=read();target='INTERNAL' if target=='INTERNAL' else target_root(target)
        if target!='INTERNAL':prepare_target(target,config['profile'])
        source=json.dumps(config,sort_keys=True)
        db=_db()
        try:
            prior=db.execute('SELECT * FROM transfers WHERE target=? AND source=? ORDER BY rowid DESC LIMIT 1',(target,source)).fetchone()
            ident=prior['id'] if prior else uuid.uuid4().hex
            with db:
                if not prior:db.execute('INSERT INTO transfers VALUES(?,?,?,?,0)',(ident,target,source,'PREPARED'))
                db.execute('DELETE FROM selected');db.execute('INSERT INTO selected VALUES(?)',(ident,))
            return status()
        finally:db.close()


def inventory(cancel=lambda:False,progress=lambda **kw:None):
    with writer():
        db=_db();item=_selected(db)
        if not item:db.close();raise StorageFailure('NO_TRANSFER')
        try:
            _phase(db,item,'INVENTORY');config=json.loads(item['source']);count=0;size=0
            for kind in KINDS:
                storage=_source(config,kind)
                for entry in storage.enumerate_for_migration():
                    if cancel():_phase(db,item,'PAUSED');return status()
                    data=storage.read(entry['ident'],MAX_BYTES+1)
                    if len(data)!=entry['bytes'] or not image_valid(data):raise StorageFailure('SOURCE_IMAGE_INVALID')
                    digest=hashlib.sha256(data).hexdigest()
                    # Changed sources invalidate only their transfer record;
                    # no image/job/READY row is rewritten or deleted.
                    db.execute("INSERT INTO files VALUES(?,?,?,?,?,'PENDING') ON CONFLICT(transfer,kind,ident) DO UPDATE SET bytes=excluded.bytes,sha=excluded.sha,status='PENDING' WHERE files.sha!=excluded.sha OR files.bytes!=excluded.bytes",(item['id'],kind,entry['ident'],len(data),digest))
                    count+=1;size+=len(data)
                    if count%64==0:db.commit();progress(stage='INVENTORY',files=count,bytes=size)
            _phase(db,item,'PAUSED');return status()
        except Exception:
            _phase(db,item,'PAUSED');raise
        finally:db.close()


def copy(cancel=lambda:False,progress=lambda **kw:None):
    # Refresh inventory before resume: source files created while paused remain
    # part of the transfer. Already verified records with unchanged SHA survive.
    inventory(cancel,progress)
    if cancel():return status()
    with writer():
        db=_db();item=_selected(db)
        try:
            _phase(db,item,'COPYING');config=json.loads(item['source'])
            while True:
                rows=db.execute("SELECT * FROM files WHERE transfer=? AND status!='VERIFIED' ORDER BY kind,ident LIMIT 16",(item['id'],)).fetchall()
                if not rows:break
                for row in rows:
                    if cancel():_phase(db,item,'PAUSED');return status()
                    data=_source(config,row['kind']).read(row['ident'],MAX_BYTES+1)
                    if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha'] or not image_valid(data):raise StorageFailure('SOURCE_CHANGED')
                    destination=_target(item,row['kind'])
                    from art_storage import check
                    check(len(data),limit=0,backend=destination)
                    if destination.exists(row['ident']) and destination.read(row['ident'],MAX_BYTES+1)!=data:raise StorageFailure('TARGET_COLLISION')
                    destination.write_verified(row['ident'],data,image_valid)
                    readback=destination.read(row['ident'],MAX_BYTES+1)
                    if len(readback)!=row['bytes'] or hashlib.sha256(readback).hexdigest()!=row['sha']:raise StorageFailure('IMAGE_VERIFY_FAILED')
                    db.execute("UPDATE files SET status='VERIFIED' WHERE transfer=? AND kind=? AND ident=?",(item['id'],row['kind'],row['ident']))
                db.commit();progress(**status())
            _phase(db,item,'COPIED');return status()
        except Exception:
            _phase(db,item,'PAUSED');raise
        finally:db.close()


def verify(cancel=lambda:False,progress=lambda **kw:None):
    """Full source+target verification under the writer gate, not just counts."""
    with writer():
        db=_db();item=_selected(db)
        if not item:db.close();raise StorageFailure('NO_TRANSFER')
        try:
            if item['stage'] not in ('COPIED','VERIFIED','ACTIVE','CLEANUP_PAUSED','CLEANED'):raise StorageFailure('COPY_INCOMPLETE')
            previous=item['stage'];_phase(db,item,'VERIFYING');config=json.loads(item['source'])
            expected={(r['kind'],r['ident']) for r in db.execute('SELECT kind,ident FROM files WHERE transfer=?',(item['id'],))}
            actual=set()
            for kind in KINDS:
                for entry in _source(config,kind).enumerate_for_migration():actual.add((kind,entry['ident']))
            cleanup={(r['kind'],r['ident']) for r in db.execute('SELECT kind,ident FROM cleanup WHERE transfer=?',(item['id'],))}
            if actual!=expected-(cleanup-actual):raise StorageFailure('SOURCE_CHANGED')
            done=0
            for row in db.execute('SELECT * FROM files WHERE transfer=?',(item['id'],)):
                if cancel():_phase(db,item,previous);return False
                source=_source(config,row['kind'])
                stores=(_target(item,row['kind']),) if (row['kind'],row['ident']) in cleanup and not source.exists(row['ident']) else (source,_target(item,row['kind']))
                for storage in stores:
                    data=storage.read(row['ident'],MAX_BYTES+1)
                    if len(data)!=row['bytes'] or hashlib.sha256(data).hexdigest()!=row['sha'] or not image_valid(data):raise StorageFailure('IMAGE_VERIFY_FAILED')
                done+=1
                if done%32==0:progress(stage='VERIFYING',done=done,files=len(expected))
            _phase(db,item,previous if previous in ('ACTIVE','CLEANUP_PAUSED','CLEANED') else 'VERIFIED');return True
        except Exception:
            _phase(db,item,'PAUSED');raise
        finally:db.close()


@guarded
def approve_render(approved):
    db=_db()
    try:
        item=_selected(db)
        if not item or item['stage'] not in ('VERIFIED','ACTIVE') or approved is not True:raise StorageFailure('RENDER_NOT_VERIFIED')
        with db:db.execute('UPDATE transfers SET rendered=1 WHERE id=?',(item['id'],))
    finally:db.close()


def activate(cancel=lambda:False,progress=lambda **kw:None):
    from artwork_config import choose
    with writer():
        if not verify(cancel,progress):return False
        db=_db()
        try:
            item=_selected(db)
            if not item['rendered']:raise StorageFailure('RENDER_NOT_VERIFIED')
            if item['target']=='INTERNAL':choose('internal',strategy='demand')
            else:choose('external',target=item['target'],strategy='demand')
            _phase(db,item,'ACTIVE');return True
        finally:db.close()


def display_candidate():
    db=_db()
    try:
        item=_selected(db)
        if not item or item['stage'] not in ('VERIFIED','ACTIVE'):raise StorageFailure('COPY_INCOMPLETE')
        row=db.execute('SELECT kind,ident FROM files WHERE transfer=? LIMIT 1',(item['id'],)).fetchone()
        return _target(item,row['kind']).make_display_uri(row['ident']) if row else ''
    finally:db.close()


def remove_originals(challenge='',cancel=lambda:False,progress=lambda **kw:None):
    """Separate explicit UI consent. Never called by update/start/copy/activate."""
    from artwork_config import read
    with writer():
        db=_db();item=_selected(db)
        try:
            if not item or not challenge or challenge!=item['id'] or item['stage'] not in ('ACTIVE','CLEANUP_PAUSED'):raise StorageFailure('CLEANUP_NOT_AUTHORIZED')
            config=read();source=json.loads(item['source'])
            if source.get('archive_mode',source['mode'])!='internal' or config['mode']!='external' or config['target']!=item['target']:raise StorageFailure('CLEANUP_NOT_AUTHORIZED')
            if not verify(cancel,progress):return 0
            _phase(db,item,'CLEANUP_PAUSED')
            removed=0
            for row in db.execute('SELECT * FROM files WHERE transfer=?',(item['id'],)):
                if cancel():break
                original=_source(source,row['kind']);target=_target(item,row['kind'])
                filename=original.resolve_target(row['ident'])
                # Re-verify immediately before unlink. No path can name a
                # SQLite/texturecache/portal file or leave these exact roots.
                if not os.path.exists(filename):
                    authorized=db.execute('SELECT 1 FROM cleanup WHERE transfer=? AND kind=? AND ident=?',(item['id'],row['kind'],row['ident'])).fetchone()
                    if authorized:continue
                    raise StorageFailure('SOURCE_CHANGED')
                if os.path.islink(filename) or os.path.realpath(filename)!=os.path.join(os.path.realpath(original.root),row['ident']+'.img'):raise StorageFailure('SOURCE_CHANGED')
                data=original.read(row['ident'],MAX_BYTES+1);copy=target.read(row['ident'],MAX_BYTES+1)
                if hashlib.sha256(data).hexdigest()!=row['sha'] or data!=copy:raise StorageFailure('IMAGE_VERIFY_FAILED')
                with db:db.execute('INSERT OR IGNORE INTO cleanup VALUES(?,?,?)',(item['id'],row['kind'],row['ident']))
                os.unlink(filename);removed+=len(data)
                progress(stage='CLEANUP',removed_bytes=removed)
            _phase(db,item,'CLEANED' if not cancel() else 'CLEANUP_PAUSED');return removed
        finally:db.close()


@guarded
def probe_image():
    """New, invocation-owned probe only; no provider or original image touched."""
    import xbmcaddon
    db=_db()
    try:
        item=_selected(db)
        if not item:raise StorageFailure('NO_TRANSFER')
        target=_target(item,'media');ident=hashlib.sha256(uuid.uuid4().bytes).hexdigest()
        with open(os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'icon.png'),'rb') as stream:data=stream.read(MAX_BYTES+1)
        if not image_valid(data):raise StorageFailure('PROBE_IMAGE_INVALID')
        from art_storage import check
        check(len(data),limit=0,backend=target)
        if target.exists(ident):raise StorageFailure('TARGET_COLLISION')
        uri=target.write_verified(ident,data,image_valid)
        if target.read(ident,MAX_BYTES+1)!=data:raise StorageFailure('IMAGE_VERIFY_FAILED')
        digest=hashlib.sha256(data).hexdigest()
        with db:db.execute('INSERT INTO probes VALUES(?,?,?)',(item['id'],ident,digest))
        return dict(uri=uri,ident=ident,sha=digest,transfer=item['id'])
    finally:db.close()


@guarded
def remove_probe(probe):
    db=_db()
    try:
        item=_selected(db)
        if not item or item['id']!=probe.get('transfer'):return
        owned=db.execute('SELECT 1 FROM probes WHERE transfer=? AND ident=? AND sha=?',(item['id'],probe.get('ident'),probe.get('sha'))).fetchone()
        if not owned:return
        storage=_target(item,'media');data=storage.read(probe['ident'],MAX_BYTES+1)
        if hashlib.sha256(data).hexdigest()!=probe.get('sha'):return
        if storage.kind=='KODI_VFS':
            import xbmcvfs
            xbmcvfs.delete(storage.resolve_target(probe['ident'])+'.ok');xbmcvfs.delete(storage.resolve_target(probe['ident']))
        else:os.unlink(storage.resolve_target(probe['ident']))
        with db:db.execute('DELETE FROM probes WHERE transfer=? AND ident=?',(item['id'],probe['ident']))
    finally:db.close()


def cleanup_report(challenge,cancel=lambda:False,progress=lambda **kw:None):
    import shutil
    from utils import addon_data_dir
    before=shutil.disk_usage(addon_data_dir()).free
    image_bytes=remove_originals(challenge,cancel,progress)
    after=shutil.disk_usage(addon_data_dir()).free
    return dict(image_bytes_unlinked=image_bytes,free_before=before,free_after=after,
                observed_free_change=after-before,measurement='Concurrent system activity may affect filesystem delta')
