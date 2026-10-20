"""New-account staging; the portal list is the final publication gate.

A cancelled scan never writes a production portal/selection. Preparing new-ID
index batches before publication keeps old accounts readable and transactions
short. Rollback affects only this newly allocated ID, never an existing account.
"""
import json
from localization import tr
import os
import shutil
import sqlite3
import tempfile
import time
import uuid
from pathlib import Path

KINDS=('live','vod','series')


class Draft:
    def __init__(self,data):
        from utils import addon_data_dir
        self.pid=str(uuid.uuid4());self.data=dict(data,id=self.pid,source_schema=1)
        self.folder=tempfile.mkdtemp(prefix='xcmate-setup-',dir=addon_data_dir())
        self.index=os.path.join(self.folder,'library.sqlite');self.guide=os.path.join(self.folder,'guide.sqlite')
        self.playlist=os.path.join(self.folder,'playlist.sqlite')
        self.categories={k:[] for k in KINDS};self.selected={k:set() for k in KINDS}
        self.epg_sources=[];self.provider_epg=False;self.saved=False;self.scanned=False;self._files=set()
        self.report=dict(groups=0,live=0,vod=0,series=0,epg=0,sources=[],warnings=[])
        from source_adapters import for_portal
        self.adapter=for_portal(self.data,filename=self.index,playlist=self.playlist)

    def discover(self,cancel=lambda:False,status=lambda *a:None):
        status(0,tr(32711))
        self.adapter.authenticate(cancel,lambda count:status(0,tr(32773,count)))
        for i,kind in enumerate(KINDS):
            if cancel(): raise InterruptedError('setup cancelled')
            self.categories[kind]=self.adapter.categories(kind,remote=True)
            status((i+1)*100//3,str(len(self.categories[kind]))+' Kategorien · '+kind)
        if not any(self.categories.values()): raise ValueError('no usable categories')
        return self.categories

    def scan(self,cancel=lambda:False,status=lambda *a:None):
        from library_index import connect,import_group
        groups=[(kind,g) for kind in KINDS for g in self.categories[kind] if str(g['category_id']) in self.selected[kind]]
        if not groups: raise ValueError('select at least one category')
        self.scanned=False
        self.report=dict(groups=len(groups),live=0,vod=0,series=0,epg=0,sources=[],warnings=[])
        db=connect(self.index,write=True)
        try:
            with db:
                for kind in KINDS:
                    db.executemany('INSERT OR REPLACE INTO groups VALUES(?,?,?,?,?)',[(self.pid,kind,str(g['category_id']),str(g['category_name']),i) for i,g in enumerate(self.categories[kind])])
        finally: db.close()
        completed={k:set() for k in KINDS}
        for number,(kind,group) in enumerate(groups):
            cid=str(group['category_id'])
            if cid in completed[kind]: continue
            if cancel(): raise InterruptedError('setup cancelled')
            state={'done':False,'received':0}
            def rows():
                for row in self.adapter.entries(kind,cid,cancel,allowed=self.selected[kind]):
                    state['received']+=1;yield row
                state['done']=True
            def progress(received,stored,discarded):
                status(number*85//len(groups),kind+' · '+tr(32774,number+1,len(groups),received,stored))
            try:
                counts=import_group(self.pid,kind,cid,rows(),filename=self.index,cancel=cancel,
                    progress=progress,allowed=self.selected[kind])
                completed[kind].update(counts['categories'])
            except ValueError:
                if not state['done']: raise
                self.report['warnings'].append(kind+': leere ausgewählte Kategorie')
        from library_index import Reader
        reader=Reader(self.pid,self.index)
        for kind in KINDS:
            # Staging contains no entries from disabled categories. No global
            # profile selection is written before the explicit save operation.
            self.report[kind]=reader.page(kind,limit=1)[1]
        if not sum(self.report[k] for k in KINDS): raise ValueError('no selected content imported')
        self._scan_epg(cancel,status)
        self.scanned=True;status(100,tr(32742))
        return self.report

    def _scan_epg(self,cancel,status):
        from library_index import Reader
        from stream_epg import import_source
        reader=Reader(self.pid,self.index);streams=[];offset=0
        while True:
            rows,total=reader.page('live',offset=offset,limit=100);streams.extend(rows);offset+=len(rows)
            if not rows or offset>=total: break
        if not streams: return
        sources=list(self.epg_sources)
        uri=self.adapter.get_xmltv_epg_url()
        if self.provider_epg and uri: sources.insert(0,dict(uri=uri,local=not uri.startswith(('http://','https://'))))
        for index,source in enumerate(sources):
            if cancel(): raise InterruptedError('setup cancelled')
            status(85+index*14//max(1,len(sources)),tr(32706)+' '+str(index+1)+'/'+str(len(sources)))
            try:
                counts=import_source(self.pid,source,index,streams,{},filename=self.guide,cancel=cancel)
                self.report['epg']+=counts['stored'];self.report['sources'].append(dict(code='READY',bytes=counts['bytes'],stored=counts['stored']))
            except InterruptedError: raise
            except Exception as exc:
                self.report['sources'].append(dict(code='FAILED',error=type(exc).__name__))
                self.report['warnings'].append('EPG: '+type(exc).__name__)

    def _copy(self,source,destination,tables,cancel):
        db=sqlite3.connect(source);db.row_factory=sqlite3.Row
        try:
            available={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
            for table in tables:
                if table not in available: continue
                columns=[r[1] for r in db.execute('PRAGMA table_info('+table+')')]
                query='INSERT OR REPLACE INTO '+table+'('+','.join(columns)+') VALUES('+','.join('?' for _ in columns)+')'
                cursor=db.execute('SELECT * FROM '+table+' WHERE pid=?',(self.pid,))
                while True:
                    if cancel(): raise InterruptedError('setup save cancelled')
                    batch=cursor.fetchmany(256)
                    if not batch: break
                    from import_budget import check_space
                    check_space(destination.execute('PRAGMA database_list').fetchone()[2],sum(sum(len(str(v)) for v in row) for row in batch)*4)
                    with destination: destination.executemany(query,[tuple(row) for row in batch])
        finally: db.close()

    def save(self,cancel=lambda:False):
        if self.saved: raise ValueError('setup already saved')
        if not self.scanned: raise ValueError('scan not complete')
        from profile_transaction import writing
        import portals
        from library_index import connect
        from group_selection import save as save_groups
        from epg_sources import _save as save_sources
        with writing():
            if portals.get_by_id(self.pid): raise ValueError('portal ID already exists')
            try:
                db=connect(write=True)
                try:
                    db.execute('CREATE TABLE IF NOT EXISTS source_payloads(pid TEXT,ident TEXT,payload TEXT,PRIMARY KEY(pid,ident))')
                    self._copy(self.index,db,('groups','items_v2','heads','catalog','source_payloads'),cancel)
                finally: db.close()
                if os.path.isfile(self.guide):
                    from guide_store import connect as guide_connect
                    db=guide_connect(write=True)
                    try: self._copy(self.guide,db,('guide_meta','guide_alias','programmes'),cancel)
                    finally: db.close()
                if self.data['type']=='m3u':
                    from m3u_store import path,export_lines
                    target=path(self.pid)
                    descriptor=os.open(target,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600);os.close(descriptor)
                    self._files.add(target)
                    source=sqlite3.connect(self.playlist);destination=sqlite3.connect(target)
                    try: source.backup(destination)
                    finally: source.close();destination.close()
                    # Compatibility snapshot is a private copy, never original.
                    snapshot=target+'.m3u';temporary=snapshot+'.tmp'
                    if os.path.exists(snapshot): raise FileExistsError('private snapshot already exists')
                    descriptor=os.open(temporary,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
                    self._files.add(temporary)
                    with os.fdopen(descriptor,'w',encoding='utf-8') as stream:
                        for text in export_lines(self.playlist,include_disabled=True): stream.write(text)
                        stream.flush();os.fsync(stream.fileno())
                    os.replace(temporary,snapshot);self._files.add(snapshot)
                    self.data['m3u_original']=self.data.get('m3u_url','')
                    if self.data.get('m3u_url','').startswith(('http://','https://')):
                        self.data['m3u_origin']=self.data['m3u_url']
                    self.data['m3u_url']=snapshot
                for kind in KINDS:
                    save_groups(self.pid,self.selected[kind],kind,known=[str(g['category_id']) for g in self.categories[kind]],auto_new=False)
                    self.data['include_'+kind]=bool(self.selected[kind])
                self.data['provider_epg_enabled']=self.provider_epg
                self.data['epg_show']=bool(self.provider_epg or self.epg_sources)
                save_sources(self.pid,dict(sources=self.epg_sources,mappings={}))
                if os.path.isfile(self.guide):
                    from stream_epg import fast_snapshot,active_streams
                    from epg import _save_disk,_mem_set
                    snapshot=fast_snapshot(self.pid,active_streams(self.data),{})
                    if snapshot: _save_disk(self.pid,snapshot);_mem_set(self.pid,snapshot)
                if cancel(): raise InterruptedError('setup save cancelled')
                portal=portals.add(self.data,portal_id=self.pid)
                self.saved=True
                return portal
            except BaseException:
                # Check the publication gate before rollback. If an atomic
                # write succeeded but readback failed, never blindly erase an
                # unreadable list; leave all prepared data coherent for review.
                try: published=portals.get_by_id(self.pid)
                except Exception: published=True
                if not published:
                    try: self._rollback_new_id()
                    except Exception:
                        from utils import warn
                        warn('XCMate setup: ROLLBACK_INCOMPLETE; unpublished new ID only')
                raise

    def _rollback_new_id(self):
        from library_index import connect
        db=connect(write=True)
        try:
            for table in ('groups','items_v2','heads','catalog','source_payloads'):
                while True:
                    with db: count=db.execute('DELETE FROM '+table+' WHERE rowid IN (SELECT rowid FROM '+table+' WHERE pid=? LIMIT 256)',(self.pid,)).rowcount
                    if count<256: break
        finally: db.close()
        from group_selection import _read,_write
        groups=_read();groups.get('_v2',{}).pop(self.pid,None);groups.pop(self.pid,None);_write(groups)
        from epg_sources import _load_all,_write_all
        sources=_load_all();sources.pop(self.pid,None);_write_all(sources)
        for candidate in self._files:
            if os.path.isfile(candidate): os.unlink(candidate)
        if os.path.isfile(self.guide):
            from guide_store import connect as guide_connect
            db=guide_connect(write=True)
            try:
                for table in ('guide_meta','guide_alias','programmes'):
                    with db: db.execute('DELETE FROM '+table+' WHERE pid=?',(self.pid,))
            finally: db.close()

    def dispose(self): shutil.rmtree(self.folder,ignore_errors=True)
