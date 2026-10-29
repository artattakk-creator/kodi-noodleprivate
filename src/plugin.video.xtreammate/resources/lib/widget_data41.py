"""Bounded read-only widget snapshots, no global COUNT or catalogue rebuild.

A profile-local last-good metadata page is shared between plugin interpreters.
Policy changes invalidate it. Lock contention/SQL failure never means zero
matches and never triggers an import/reset. No raw SQLite text is logged.
"""
import contextlib,hashlib,json,os,sqlite3,tempfile,time
from urllib.parse import quote
from library_index import Reader,IndexReadError,initial_group,path
MAX_BYTES=8*1024*1024
_last_trace46={}

class WidgetReader(Reader):
    def __init__(self,pid,seconds=.75):
        super().__init__(pid,timeout=.05,query_seconds=.25);self.until=time.monotonic()+seconds
    def _query(self,sql,args=(),kind=None):
        db=None
        self.stage46=('STATE' if 'FROM catalog' in sql else 'GROUPS' if 'FROM groups' in sql and 'EXISTS' not in sql else
                      'HEADS' if 'SELECT cid FROM heads' in sql else 'LEGACY_PRESENCE' if 'EXISTS(SELECT 1 FROM titles' in sql else
                      'V2_KEYS' if 'SELECT i.sid,i.cid' in sql else 'LEGACY_KEYS' if 'SELECT t.sid,t.cid' in sql else 'PAYLOAD')
        try:
            if time.monotonic()>=self.until:raise sqlite3.OperationalError('interrupted')
            filename=self.filename or path()
            if not os.path.isfile(filename):return []
            db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=min(.05,max(.001,self.until-time.monotonic())))
            db.row_factory=sqlite3.Row;db.execute('PRAGMA temp_store=MEMORY')
            deadline=min(self.until,time.monotonic()+.25)
            db.set_progress_handler(lambda:int(time.monotonic()>=deadline),1000)
            if '/* direct44 */' not in sql and 'titles' in sql and db.execute("SELECT 1 FROM sqlite_master WHERE name='readable_titles'").fetchone():sql=sql.replace('FROM titles','FROM readable_titles')
            if kind is not None:
                # TEMP only; the library itself is opened mode=ro.
                db.execute('CREATE TEMP TABLE selected_categories(cid TEXT PRIMARY KEY)')
                db.executemany('INSERT INTO selected_categories VALUES(?)',[(cid,) for cid in self._selections[kind]])
            return [dict(r) for r in db.execute(sql,args)]
        except sqlite3.Error as exc:
            name=getattr(exc,'sqlite_errorname','SQLITE_UNKNOWN')
            if not isinstance(name,str) or not name.startswith('SQLITE_') or not name.replace('_','').isalnum():name='SQLITE_UNKNOWN'
            code='BUDGET' if time.monotonic()>=self.until or name=='SQLITE_INTERRUPT' else name
            error=IndexReadError(code);error.code=code;error.sqlite_type=type(exc).__name__;error.stage46=self.stage46;raise error from None
        finally:
            if db is not None:db.close()
    def groups(self,kind):
        from widget_query44 import groups
        return groups(self,kind)
    def get(self,kind,sid):
        from widget_query44 import get
        return get(self,kind,sid)
    def small(self,kind,category=None,limit=24,pin=None):
        from widget_query44 import small
        return small(self,kind,category,limit,pin)

def files(pid,kind):
    from utils import addon_data_dir
    name='xcmate_widget41_'+hashlib.sha256((str(pid)+'|'+kind).encode()).hexdigest()[:24]
    return os.path.join(addon_data_dir(),name+'.json'),os.path.join(addon_data_dir(),name+'.lock')

def policy(portal,kind,offset=0):
    from utils import addon_data_dir,setting_int
    try:s=os.stat(os.path.join(addon_data_dir(),'xtreammate_groups.json'));stamp=[s.st_mtime_ns,s.st_size]
    except OSError:stamp=None
    values=[str(portal['id']),kind,portal.get('start_stream_id'),portal.get('start_group_id'),portal.get('include_'+kind,True),stamp,offset,setting_int('recent_keep',100)]
    if kind=='live':values.append('FULL_GROUP46')
    if kind=='vod':values.append('POINT_PAYLOAD47')  # Reject old empty/error-derived movie snapshots only.
    return hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()

def read(filename,key):
    try:
        with open(filename,encoding='utf-8') as f:raw=f.read(MAX_BYTES+1)
        value=json.loads(raw) if len(raw)<=MAX_BYTES else None
        if isinstance(value,dict) and value.get('policy')==key and isinstance(value.get('rows'),list) and all(isinstance(r,dict) and isinstance(r.get('sid'),str) and isinstance(r.get('name'),str) for r in value['rows']) and 0<=time.time()-value.get('at',0)<7*86400:return value
    except (OSError,ValueError,TypeError):pass
    return None

def store(filename,key,rows,revision=None):
    temp=None
    try:
        data=json.dumps(dict(policy=key,at=time.time(),rows=rows,revision44=revision))
        if len(data.encode())>MAX_BYTES:return
        fd,temp=tempfile.mkstemp(prefix='.widget41-',dir=os.path.dirname(filename))
        with os.fdopen(fd,'w',encoding='utf-8') as f:f.write(data)
        os.replace(temp,filename)
    except OSError:pass
    finally:
        if temp and os.path.exists(temp):os.unlink(temp)

def trace(kind,code,rows,started,stale=False,stage=''):
    import xbmc
    allowed=('READY','CACHE','READ_ONLY','CACHE_UNWRITABLE','CACHE_STORAGE_FULL','LOCKED','BUDGET','SQLITE_BUSY','SQLITE_LOCKED','SQLITE_INTERRUPT','SQLITE_CORRUPT','SQLITE_NOTADB','SQLITE_CANTOPEN','SQLITE_IOERR','INDEX_MISSING','UNAVAILABLE','DISABLED')
    code=code if code in allowed else 'UNAVAILABLE'
    key=(code,rows,bool(stale),stage);now=time.monotonic();prior=_last_trace46.get(kind)
    if prior and prior[0]==key and now-prior[1]<60:return
    _last_trace46[kind]=(key,now)
    if stage not in ('STATE','GROUPS','HEADS','LEGACY_PRESENCE','V2_KEYS','LEGACY_KEYS','PAYLOAD'):stage=''
    try:xbmc.log('[XCMate][WIDGET41] kind='+kind+' code='+code+' rows='+str(rows)+' stale='+str(int(stale))+' ms='+str(int((time.monotonic()-started)*1000))+(' stage='+stage if stage else ''),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass

def snapshot(portal,kind,background=False):
    started=time.monotonic();filename,lock=files(portal['id'],kind);key=policy(portal,kind)
    if not portal.get('include_'+kind,True):trace(kind,'DISABLED',0,started);return [],'DISABLED'
    old=read(filename,key)
    if old and time.time()-old['at']<15 and not background:trace(kind,'CACHE',len(old['rows']),started);return old['rows'],'CACHE'
    stream=None;reader=None;code='UNAVAILABLE';stage46=''
    try:
        import fcntl
        stream=open(lock,'a');fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        # Another interpreter may have published while this one waited to run.
        fresh=read(filename,key)
        if fresh and time.time()-fresh['at']<15 and not background:return fresh['rows'],'CACHE'
        if kind in ('vod','series'):
            from widget_movie47 import MovieReader
            reader=MovieReader(portal['id'],kind=kind)
        else:reader=WidgetReader(portal['id'])
        state=reader.state(kind)
        if not state:return (old['rows'],'INDEX_MISSING') if old else ([], 'INDEX_MISSING')
        revision=[state.get('revision'),state.get('updated')]
        if background and old and old.get('revision44')==revision:
            if time.time()-old['at']>=15:store(filename,key,old['rows'],revision)
            return old['rows'],'CACHE'
        if kind=='live':
            start=reader.get('live',str(portal.get('start_stream_id') or ''))
            cid=initial_group(portal,reader.groups('live'),start)
            from widget_group46 import snapshot as complete_group
            rows=complete_group(portal) if cid else []
        else:rows=reader.small(kind,limit=24)
        store(filename,key,rows,revision);trace(kind,'READY',len(rows),started);return rows,'READY'
    except BlockingIOError:code='LOCKED'
    except OSError as exc:
        import errno
        code='CACHE_STORAGE_FULL' if exc.errno==errno.ENOSPC else 'CACHE_UNWRITABLE'
    except (IndexReadError,sqlite3.Error,ValueError,TypeError,ImportError) as exc:code=getattr(exc,'code','UNAVAILABLE');stage46=getattr(exc,'stage46','')
    finally:
        if reader is not None and hasattr(reader,'close'):reader.close()
        if stream:stream.close()
    if code in ('LOCKED','CACHE_UNWRITABLE','CACHE_STORAGE_FULL') and (not old or not old['rows']):
        trace(kind,code,0,started)
        from widget_read56 import read as read_catalogue
        rows,code=read_catalogue(portal,kind)
        trace(kind,code,len(rows),started);return rows,code
    rows=old['rows'] if old else [];trace(kind,code,len(rows),started,bool(old),stage46);return rows,code
