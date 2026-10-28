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
import threading
from pathlib import Path

KINDS=('live','vod','series')


class SaveError(ValueError):
    def __init__(self,code): self.code=code;super().__init__(code)


class Draft:
    def __init__(self,data):
        from utils import addon_data_dir
        self._guide_publish48=False
        self._save_guard=threading.Lock();self._scan_signature=None;self.verification=None
        self.pid=str(uuid.uuid4());self.data=dict(data,id=self.pid,source_schema=1)
        self.folder=tempfile.mkdtemp(prefix='xcmate-setup-',dir=addon_data_dir())
        self.index=os.path.join(self.folder,'library.sqlite');self.guide=os.path.join(self.folder,'guide.sqlite')
        self.playlist=os.path.join(self.folder,'playlist.sqlite')
        self.categories={k:[] for k in KINDS};self.selected={k:set() for k in KINDS}
        self.epg_sources=[];self.provider_epg=False;self.saved=False;self.scanned=False;self._files=set()
        self.report=dict(groups=0,live=0,vod=0,series=0,epg=0,sources=[],warnings=[])
        from source_adapters import for_portal
        self.adapter=for_portal(self.data,filename=self.index,playlist=self.playlist)

    from wizard_deadline48 import discovery
    @discovery
    def discover(self,cancel=lambda:False,status=lambda *a:None):
        status(None,tr(32711))
        self.adapter.authenticate(cancel,lambda count:status(0,tr(32773,count)))
        for i,kind in enumerate(KINDS):
            if cancel(): raise InterruptedError('setup cancelled')
            self.categories[kind]=self.adapter.categories(kind,remote=True)
            status(None,str(len(self.categories[kind]))+' Kategorien · '+kind)
        if not any(self.categories.values()): raise ValueError('no usable categories')
        return self.categories

    def scan(self,cancel=lambda:False,status=lambda *a:None):
        from library_index import connect,import_group
        groups=[(kind,g) for kind in KINDS for g in self.categories[kind] if str(g['category_id']) in self.selected[kind]]
        if not groups: raise ValueError('select at least one category')
        self.scanned=False;self._scan_signature=None
        for filename in (self.index,self.guide):
            for suffix in ('','-wal','-shm'):
                if os.path.isfile(filename+suffix): os.unlink(filename+suffix)
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
                status(None,tr(32784,kind,number+1,len(groups),str(group['category_name']),received,stored))
            status(None,tr(32784,kind,number+1,len(groups),str(group['category_name']),0,0))
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
        self._scan_signature=self._signature();self.scanned=True;status(100,tr(32742))
        return self.report

    def _scan_epg(self,cancel,status):
        from library_index import Reader
        from stream_epg import import_source
        if not self.epg_sources and not self.provider_epg: return
        reader=Reader(self.pid,self.index);streams=[];offset=0
        while True:
            rows,total=reader.page('live',offset=offset,limit=100);streams.extend(rows);offset+=len(rows)
            if not rows or offset>=total: break
        if not streams: return
        sources=list(self.epg_sources)
        uri=self.adapter.get_xmltv_epg_url()
        if self.provider_epg and uri: sources.insert(0,dict(uri=uri,local=not uri.startswith(('http://','https://'))))
        provider_inserted48=bool(self.provider_epg and uri)
        for index,source in enumerate(sources):
            if cancel(): raise InterruptedError('setup cancelled')
            status(None,tr(32706)+' '+str(index+1)+'/'+str(len(sources)))
            try:
                rank48=index if provider_inserted48 else index+1
                counts=import_source(self.pid,source,rank48,streams,{},filename=self.guide,cancel=cancel)
                self.report['epg']+=counts['stored'];self.report['sources'].append(dict(code='READY',bytes=counts['bytes'],stored=counts['stored']))
                status(None,tr(32706)+' '+str(index+1)+'/'+str(len(sources))+' READY · '+str(counts['stored'])+' · '+str(counts['bytes'])+' Bytes')
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
                    self._save_status(None,self._save_copy_text)
        finally: db.close()

    def _signature(self):
        return json.dumps([sorted((kind,sorted(self.selected[kind])) for kind in KINDS),
                           self.provider_epg,self.epg_sources],sort_keys=True)

    def save(self,cancel=lambda:False,status=lambda *a:None):
        if not self._save_guard.acquire(blocking=False): raise SaveError('XM-SETUP-SAVE-BUSY')
        try:
            self._save_status=status;self._save_copy_text=tr(36505);status(0,tr(32716))
            if self.saved: raise SaveError('XM-SETUP-SAVE-BUSY')
            if not self.scanned or self._scan_signature!=self._signature(): raise SaveError('XM-SETUP-RESCAN')
            return self._save(cancel)
        finally: self._save_guard.release()

    def _verify(self,portal=None):
        """Fresh connections and disk reads, never cached staging counters."""
        from library_index import connect,Reader
        from group_selection import _read,_state
        from epg_sources import configuration
        counts={}
        db=connect()
        try:
            if db is None or db.execute('PRAGMA quick_check').fetchone()[0]!='ok': raise SaveError('XM-SETUP-VERIFY')
            for kind in KINDS:
                actual=db.execute('SELECT count(DISTINCT sid) FROM readable_titles WHERE pid=? AND kind=?',(self.pid,kind)).fetchone()[0]
                wrong=db.execute('SELECT DISTINCT cid FROM readable_titles WHERE pid=? AND kind=?',(self.pid,kind))
                if actual!=self.report[kind] or any(row[0] not in self.selected[kind] for row in wrong): raise SaveError('XM-SETUP-VERIFY')
                counts[kind]=actual
        finally:
            if db is not None: db.close()
        groups=_read()
        for kind in KINDS:
            state=_state(groups,self.pid,kind)
            if state is None or state['enabled']!=self.selected[kind] or state['auto_new'] or state['known']!={str(g['category_id']) for g in self.categories[kind]}: raise SaveError('XM-SETUP-VERIFY')
            if Reader(self.pid).page(kind,limit=1)[1]!=counts[kind]: raise SaveError('XM-SETUP-VERIFY')
        if configuration(self.pid)!=dict(sources=self.epg_sources,mappings={}): raise SaveError('XM-SETUP-VERIFY')
        if os.path.isfile(self.guide):
            from guide_store import connect as guide_connect
            source=sqlite3.connect(self.guide);target=guide_connect()
            try:
                if target.execute('PRAGMA quick_check').fetchone()[0]!='ok': raise SaveError('XM-SETUP-VERIFY')
                for table in ('guide_meta','guide_alias','programmes'):
                    expected=source.execute('SELECT count(*) FROM '+table+' WHERE pid=?',(self.pid,)).fetchone()[0]
                    if target.execute('SELECT count(*) FROM '+table+' WHERE pid=?',(self.pid,)).fetchone()[0]!=expected: raise SaveError('XM-SETUP-VERIFY')
            finally: source.close();target.close()
        if self.data['type']=='m3u':
            from m3u_store import path
            db=sqlite3.connect(path(self.pid))
            try:
                if db.execute('PRAGMA quick_check').fetchone()[0]!='ok': raise SaveError('XM-SETUP-VERIFY')
            finally: db.close()
            if not os.path.isfile(self.data['m3u_url']): raise SaveError('XM-SETUP-VERIFY')
        if portal is not None:
            import portals
            fresh=portals.get_by_id(self.pid)
            keys=('id','type','name','xc_host','xc_user','xc_pass','stb_url','stb_mac','m3u_url','m3u_origin','m3u_original','epg_url','epg_show','provider_epg_enabled','source_schema','stb_serial','stb_device_id','start_group_id','start_stream_id','autoplay_start','enabled')
            if fresh!=portal or any(fresh.get(key)!=self.data[key] for key in keys if key in self.data): raise SaveError('XM-SETUP-VERIFY')
            if any(bool(fresh.get('include_'+kind))!=bool(self.selected[kind]) for kind in KINDS): raise SaveError('XM-SETUP-VERIFY')
        return dict(code='XM-SETUP-VERIFIED',counts=counts,groups=True,epg=True,integrity=True,portal=portal is not None)

    def _save(self,cancel):
        from setup_trace import mark
        mark('SAVE_BEGIN',self.pid)
        from profile_transaction import writing
        import portals
        from library_index import connect
        from group_selection import save as save_groups
        from epg_sources import _load_all,_write_all
        original=dict(self.data)
        if portals.get_by_id(self.pid): raise SaveError('XM-SETUP-SAVE-BUSY')
        try:
            # New-ID rows are invisible until portal publication. Batch copies
            # never hold the cross-interpreter configuration lock for minutes.
            db=connect(write=True)
            try:
                db.execute('CREATE TABLE IF NOT EXISTS source_payloads(pid TEXT,ident TEXT,payload TEXT,PRIMARY KEY(pid,ident))')
                mark('COPY_CATALOG',self.pid)
                self._copy(self.index,db,('groups','items_v2','heads','catalog','source_payloads'),cancel)
            finally: db.close()
            if os.path.isfile(self.guide):
                from setup_epg48 import gate as epg_gate48
                epg_gate48()
                from guide_store import connect as guide_connect
                db=guide_connect(write=True)
                try:
                    mark('COPY_GUIDE',self.pid)
                    from setup_epg48 import GUIDE_TABLES
                    self._guide_publish48=True
                    self._copy(self.guide,db,GUIDE_TABLES,cancel)
                finally: db.close()
                from setup_epg48 import promote as promote_epg48
                promote_epg48(self,cancel)
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
            with writing():
                if portals.get_by_id(self.pid): raise SaveError('XM-SETUP-SAVE-BUSY')
                for kind in KINDS:
                    save_groups(self.pid,self.selected[kind],kind,known=[str(g['category_id']) for g in self.categories[kind]],auto_new=False)
                    self.data['include_'+kind]=bool(self.selected[kind])
                self.data['provider_epg_enabled']=self.provider_epg
                self.data['epg_show']=bool(self.provider_epg or self.epg_sources)
                # A new unpublished portal has no GUI cache to invalidate.
                sources=_load_all();sources[self.pid]=dict(sources=self.epg_sources,mappings={});_write_all(sources)
                if os.path.isfile(self.guide):
                    from stream_epg import fast_snapshot,active_streams
                    from epg import _save_disk,_mem_set,_disk_ck
                    from utils import cache_dir,_private_cache_dir
                    from itertools import islice
                    def initial_rows():
                        # Persistent guide contains every imported programme;
                        # only warm a bounded compatibility cache at save time.
                        for row in islice(active_streams(self.data),256):
                            if cancel(): raise InterruptedError('setup save cancelled')
                            yield row
                    snapshot=fast_snapshot(self.pid,initial_rows(),{})
                    if snapshot:
                        for folder in set((cache_dir(),_private_cache_dir())):
                            self._files.add(os.path.join(folder,_disk_ck(self.pid)+'.json'))
                        _save_disk(self.pid,snapshot,notify=False);_mem_set(self.pid,snapshot)
                self._save_status(None,tr(36506))
                self._verify()
                if self._guide_publish48:
                    from setup_epg48 import verify as verify_epg48
                    verify_epg48(self)
                if cancel(): raise InterruptedError('setup save cancelled')
                mark('CONFIG_PUBLISH',self.pid)
                portal=portals.add(self.data,portal_id=self.pid)
                mark('VERIFY',self.pid)
                self.verification=self._verify(portal)
                self.saved=True
                mark('SAVE_DONE',self.pid)
                return portal
        except BaseException as failure:
            mark('SAVE_FAILED',self.pid)
            try:
                with writing():
                    # Never invoke portals.delete(): it clears global caches.
                    # Re-read under lock and remove only this newly allocated ID.
                    current=portals.load_all()
                    if any(p['id']==self.pid for p in current):
                        portals.save_all([p for p in current if p['id']!=self.pid])
                    self._rollback_new_id()
            except Exception:
                raise SaveError('XM-SETUP-ROLLBACK') from None
            finally: self.data=original
            raise failure

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
        groups=_read()
        if self.pid in groups.get('_v2',{}) or self.pid in groups:
            groups.get('_v2',{}).pop(self.pid,None);groups.pop(self.pid,None);_write(groups)
        from epg_sources import _load_all,_write_all
        sources=_load_all()
        if self.pid in sources: sources.pop(self.pid,None);_write_all(sources)
        for candidate in self._files:
            for suffix in ('','-wal','-shm'):
                filename=candidate+suffix
                if '://' in filename:
                    import xbmcvfs
                    if xbmcvfs.exists(filename) and not xbmcvfs.delete(filename): raise OSError('new cache rollback failed')
                elif os.path.isfile(filename): os.unlink(filename)
        self._files.clear()
        if self._guide_publish48:
            from epg import _mem_clear
            _mem_clear(self.pid)
            from guide_store import connect as guide_connect
            db=guide_connect(write=True)
            try:
                from setup_epg48 import GUIDE_TABLES
                for table in GUIDE_TABLES:
                    with db: db.execute('DELETE FROM '+table+' WHERE pid=?',(self.pid,))
            finally: db.close()
            from setup_epg48 import rollback as rollback_epg48
            rollback_epg48(self)

    def dispose(self):
        session=getattr(self,'resume53',None)
        if session:session.detached(self)
        else:shutil.rmtree(self.folder,ignore_errors=True)
