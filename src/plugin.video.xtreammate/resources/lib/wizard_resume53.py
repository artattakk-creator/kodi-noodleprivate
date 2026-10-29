"""One private resumable wizard intent, never a production portal or password.

Small state checkpoints retain selections separately from the source catalogue.
No xc_pass, raw provider response, GUI property or exception string is persisted.
The existing worker lease must outlive the last checkpoint and staging cleanup.
"""
import contextlib,hashlib,json,os,shutil,sqlite3,stat,tempfile,threading,time,uuid
from urllib.parse import urlsplit,urlunsplit,parse_qsl,urlencode
_local=threading.local()
KINDS=('live','vod','series');MAX_BYTES=2*1024*1024
NONSECRET=('type','name','xc_host','xc_user','stb_url','stb_mac','stb_serial','stb_device_id','epg_show','enabled')


def current():return getattr(_local,'session',None)


@contextlib.contextmanager
def using(session):
    before=current();_local.session=session
    try:yield session
    finally:_local.session=before


def root():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'wizard_resume53')


def private_folder(path):
    if os.path.islink(path):raise OSError('DRAFT_STORAGE_UNSAFE')
    os.makedirs(path,mode=0o700,exist_ok=True)
    os.chmod(path,0o700)
    if not stat.S_ISDIR(os.stat(path).st_mode) or stat.S_IMODE(os.stat(path).st_mode)&0o077:raise OSError('DRAFT_STORAGE_UNSAFE')


def write_file(path,value):
    private_folder(os.path.dirname(path))
    if os.path.islink(path):raise OSError('DRAFT_STORAGE_UNSAFE')
    raw=json.dumps(value,ensure_ascii=False,separators=(',',':')).encode()
    if len(raw)>MAX_BYTES:raise ValueError('DRAFT_BUDGET')
    fd,temp=tempfile.mkstemp(prefix='.wizard53-',dir=os.path.dirname(path))
    try:
        os.fchmod(fd,0o600)
        if stat.S_IMODE(os.fstat(fd).st_mode)&0o077:raise OSError('DRAFT_STORAGE_UNSAFE')
        with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
        fd=None;os.replace(temp,path);temp=None
    finally:
        if fd is not None:
            try:os.close(fd)
            except OSError:pass
        if temp:
            try:os.unlink(temp)
            except OSError:pass


def read_file(path):
    if os.path.islink(path) or not os.path.isfile(path):return None
    if stat.S_IMODE(os.stat(path).st_mode)&0o077:return None
    with open(path,encoding='utf-8') as f:raw=f.read(MAX_BYTES+1)
    if len(raw)>MAX_BYTES:raise ValueError('DRAFT_BUDGET')
    return json.loads(raw)


def safe_data(data):
    value={key:data[key] for key in NONSECRET if isinstance(data.get(key),(str,bool))}
    # Token-bearing playlist/custom URLs are not password-free restart data.
    # The source is re-entered; an ordinary origin/path without credentials or
    # query can be retained. No secret hash is kept as a substitute password.
    for key in ('m3u_url','epg_url'):
        uri=str(data.get(key) or '')
        parsed=urlsplit(uri)
        sensitive={'password','pass','token','auth','api_key','apikey','access_token'}
        query=parse_qsl(parsed.query,keep_blank_values=True)
        private=bool(parsed.username or parsed.password or any(k.casefold() in sensitive for k,v in query))
        if uri and not private:value[key]=uri
        elif uri:
            host=parsed.hostname or ''
            if parsed.port:host+=':'+str(parsed.port)
            clean=urlunsplit((parsed.scheme,host,parsed.path,urlencode([(k,v) for k,v in query if k.casefold() not in sensitive]),''))
            value[key+'_public53']=clean;value[key+'_needs_input53']=True
    return value


class Session:
    def __init__(self,state=None):
        self.state=state or dict(version=1,token=uuid.uuid4().hex,created=time.time(),status='ACTIVE',stage='input',selected={k:[] for k in KINDS})
        self.data=dict(self.state.get('data',{}));self.live=None;self.error='';self.action='';self._lock=threading.RLock()
    @classmethod
    def load(cls):
        try:
            if os.path.islink(root()) or not os.path.isdir(root()):return None
            if stat.S_IMODE(os.stat(root()).st_mode)&0o077:return None
            value=read_file(os.path.join(root(),'current.json'))
            if not isinstance(value,dict) or value.get('version')!=1 or value.get('status')!='ACTIVE':return None
            if not isinstance(value.get('token'),str) or len(value['token'])!=32:return None
            session=cls(value)
            session.state['revalidate53']=time.time()-float(value.get('updated',0))>86400
            return session
        except (OSError,ValueError,TypeError):return None
    def persist(self):
        try:
            self.state['data']=safe_data(self.data);self.state['updated']=time.time()
            write_file(os.path.join(root(),'current.json'),self.state);self.error='';return True
        except (OSError,ValueError,TypeError):self.error='DRAFT_STORAGE_UNAVAILABLE';return False
    def input(self,data,key=None):
        with self._lock:
            self.data=dict(data);self.state['stage']='input';self.state['input_key']=key or ''
            if key=='name':self.state['name_confirmed']=True
            return self.persist()
    def checkpoint(self,draft,stage=None,categories=False):
        with self._lock:
            # A delayed worker cannot resurrect an explicitly discarded or
            # completed intent after its GUI has closed.
            if self.state.get('status')!='ACTIVE':return False
            self.data={k:v for k,v in draft.data.items() if k!='id'}
            self.state['name_confirmed']=True
            self.state.update(pid=draft.pid,folder=os.path.basename(draft.folder),stage=stage or self.state.get('stage','groups'),
                selected={k:sorted(draft.selected[k]) for k in KINDS},provider_epg=bool(draft.provider_epg),
                epg_sources=[dict(s) for s in draft.epg_sources],scanned=bool(draft.scanned),signature=draft._scan_signature,
                report={k:draft.report.get(k,0) for k in ('groups','live','vod','series','epg')})
            if getattr(draft,'phased54',False):self.state.update(phased54=True,published54=bool(draft.saved))
            try:
                private_folder(draft.folder)
                stages=list(self.state.get('staging53',[]));record=dict(folder=os.path.basename(draft.folder),pid=draft.pid)
                if record not in stages:
                    if len(stages)>=4:raise ValueError('DRAFT_STAGE_BUDGET')
                    stages.append(record)
                write_file(os.path.join(draft.folder,'owner53.json'),dict(token=self.state['token'],pid=draft.pid))
                self.state['staging53']=stages
                # Existing staging can contain private stream/artwork URLs.
                # Enforce real file modes before allowing restart reuse.
                for filename in os.scandir(draft.folder):
                    if filename.is_symlink():raise OSError('DRAFT_STORAGE_UNSAFE')
                    if filename.is_file():
                        os.chmod(filename.path,0o600)
                        if stat.S_IMODE(filename.stat().st_mode)&0o077:raise OSError('DRAFT_STORAGE_UNSAFE')
                if categories:
                    clean={kind:[dict(category_id=str(g['category_id'])[:512],category_name=str(g['category_name'])[:512]) for g in draft.categories[kind]][:20000] for kind in KINDS}
                    if any(len(draft.categories[k])>20000 for k in KINDS):raise ValueError('DRAFT_BUDGET')
                    write_file(os.path.join(draft.folder,'categories53.json'),clean)
                return self.persist()
            except (OSError,ValueError,TypeError):self.error='DRAFT_STORAGE_UNAVAILABLE';return False
    def folder(self):
        from utils import addon_data_dir
        name=self.state.get('folder','')
        if not isinstance(name,str) or not name.startswith('xcmate-setup-') or os.path.basename(name)!=name:return None
        path=os.path.join(addon_data_dir(),name)
        if os.path.islink(path) or not os.path.isdir(path) or stat.S_IMODE(os.stat(path).st_mode)&0o077:return None
        try:owner=read_file(os.path.join(path,'owner53.json'))
        except (OSError,ValueError):return None
        if owner!=dict(token=self.state['token'],pid=self.state.get('pid')):return None
        return path
    def restore(self,data):
        from setup_draft import Draft
        from source_adapters import for_portal
        # Reuse RAM state, but re-authenticate if the user edited credentials.
        prior=self.live
        if prior is not None and not prior.saved:
            changed=any(prior.data.get(k)!=data.get(k) for k in ('type','xc_host','xc_user','m3u_url','stb_url','stb_mac'))
            if not changed:
                if prior.data.get('xc_pass')!=data.get('xc_pass'):self.authenticated53=False
                prior.data.update(data);prior.adapter=for_portal(prior.data,filename=prior.index,playlist=prior.playlist);return prior
        if len(self.state.get('staging53',[]))>=4 and prior is not None:raise ValueError('DRAFT_STAGE_BUDGET')
        draft=Draft(data);draft.phased54=bool(self.state.get('phased54'));folder=self.folder()
        if prior is not None:
            draft.selected={k:set(prior.selected[k]) for k in KINDS}
            draft.epg_sources=list(prior.epg_sources);draft.provider_epg=prior.provider_epg
        if any(self.state.get('data',{}).get(k)!=data.get(k) for k in ('type','xc_host','xc_user','stb_url','stb_mac')):folder=None
        self.live=draft
        if folder is None:return draft
        pid=str(self.state.get('pid',''))
        try:uuid.UUID(pid)
        except (ValueError,AttributeError):return draft
        from portals import get_by_id
        if get_by_id(pid) is not None:return draft
        try:
            categories=read_file(os.path.join(folder,'categories53.json'))
            if not isinstance(categories,dict):return draft
            # Drop only the unused, just-created empty private folder.
            os.rmdir(draft.folder);draft.folder=folder;draft.pid=pid;draft.data['id']=pid
            draft.index=os.path.join(folder,'library.sqlite');draft.guide=os.path.join(folder,'guide.sqlite');draft.playlist=os.path.join(folder,'playlist.sqlite')
            draft.categories={k:list(categories.get(k,[])) for k in KINDS}
            draft.selected={k:set(map(str,self.state.get('selected',{}).get(k,[]))) for k in KINDS}
            draft.provider_epg=bool(self.state.get('provider_epg'));draft.epg_sources=list(self.state.get('epg_sources',[]))
            draft.report.update(self.state.get('report',{}));draft._scan_signature=self.state.get('signature')
            draft.adapter=for_portal(draft.data,filename=draft.index,playlist=draft.playlist)
            # Only a validated owned .53 folder for the same Xtream account
            # may bootstrap old atomic group heads into .54 receipts.
            draft._trusted_legacy54=bool(draft.data.get('type')=='xtream' and not self.state.get('revalidate53'))
            draft._legacy_selected54={k:set(draft.selected[k]) for k in KINDS}
            if self.state.get('scanned') and not self.state.get('revalidate53') and os.path.isfile(draft.index):
                db=sqlite3.connect('file:'+__import__('urllib.parse',fromlist=['quote']).quote(draft.index,safe='/')+'?mode=ro',uri=True,timeout=.05)
                try:draft.scanned=db.execute('PRAGMA quick_check').fetchone()[0]=='ok' and draft._scan_signature==draft._signature()
                finally:db.close()
        except (OSError,sqlite3.Error,ValueError,TypeError):draft.scanned=False
        return draft
    def _cleanup_stages(self):
        from utils import addon_data_dir
        for row in self.state.get('staging53',[])[:4]:
            name=row.get('folder','')
            if not name.startswith('xcmate-setup-') or os.path.basename(name)!=name:continue
            folder=os.path.join(addon_data_dir(),name)
            if os.path.islink(folder) or not os.path.isdir(folder):continue
            try:owner=read_file(os.path.join(folder,'owner53.json'))
            except (OSError,ValueError):continue
            if owner==dict(token=self.state['token'],pid=row.get('pid')):
                # .53 source archives have no .54 source/configuration receipt.
                # Preserve that older unpublished EPG instead of discarding it
                # when the newly separated catalogue setup completes.
                if self.state.get('phased54') and os.path.isfile(os.path.join(folder,'guide.sqlite')):continue
                shutil.rmtree(folder,ignore_errors=True)
    def completed(self):
        with self._lock:
            self.state['status']='COMPLETE';ok=self.persist()
            if self.live is None:self._cleanup_stages()
            return ok
    def discard(self,confirmed=False):
        if not confirmed:return False
        with self._lock:
            self.state['status']='DISCARDED';ok=self.persist()
            if self.live is None:self._cleanup_stages()
            return ok
    def detached(self,draft):
        if draft.saved and getattr(draft,'phased54',False):
            from wizard_epg54 import pending
            if pending(draft.data):
                self.checkpoint(draft,'epg_pending');self.live=None;return
            self.completed();self._cleanup_stages();self.live=None
        elif draft.saved:self.completed();self._cleanup_stages();self.live=None
        elif self.state.get('status')=='DISCARDED':self._cleanup_stages();self.live=None
        else:self.checkpoint(draft)


def unreadable_intent():
    """Do not silently overwrite an existing corrupt/unsafe ACTIVE intent."""
    filename=os.path.join(root(),'current.json')
    if not os.path.lexists(filename):return False
    try:
        if os.path.islink(root()) or stat.S_IMODE(os.stat(root()).st_mode)&0o077:return True
        value=read_file(filename)
        if isinstance(value,dict) and value.get('version')==1 and value.get('status') in ('COMPLETE','DISCARDED'):return False
        return Session.load() is None
    except (OSError,ValueError,TypeError):return True
