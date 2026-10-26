"""Bounded read-only widget snapshots, no global COUNT or catalogue rebuild.

A profile-local last-good metadata page is shared between plugin interpreters.
Policy changes invalidate it. Lock contention/SQL failure never means zero
matches and never triggers an import/reset. No raw SQLite text is logged.
"""
import contextlib,hashlib,json,os,sqlite3,tempfile,time
from urllib.parse import quote
from library_index import Reader,IndexReadError,initial_group,path
MAX_BYTES=512*1024

class WidgetReader(Reader):
    def __init__(self,pid,seconds=.75):
        super().__init__(pid,timeout=.05,query_seconds=.25);self.until=time.monotonic()+seconds
    def _query(self,sql,args=(),kind=None):
        db=None
        try:
            if time.monotonic()>=self.until:raise sqlite3.OperationalError('interrupted')
            filename=self.filename or path()
            if not os.path.isfile(filename):return []
            db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=min(.05,max(.001,self.until-time.monotonic())))
            db.row_factory=sqlite3.Row
            deadline=min(self.until,time.monotonic()+.25)
            db.set_progress_handler(lambda:int(time.monotonic()>=deadline),1000)
            if 'titles' in sql and db.execute("SELECT 1 FROM sqlite_master WHERE name='readable_titles'").fetchone():sql=sql.replace('FROM titles','FROM readable_titles')
            if kind is not None:
                # TEMP only; the library itself is opened mode=ro.
                db.execute('CREATE TEMP TABLE selected_categories(cid TEXT PRIMARY KEY)')
                db.executemany('INSERT INTO selected_categories VALUES(?)',[(cid,) for cid in self._selections[kind]])
            return [dict(r) for r in db.execute(sql,args)]
        except sqlite3.Error as exc:
            name=getattr(exc,'sqlite_errorname','SQLITE_UNKNOWN')
            if not isinstance(name,str) or not name.startswith('SQLITE_') or not name.replace('_','').isalnum():name='SQLITE_UNKNOWN'
            code='BUDGET' if time.monotonic()>=self.until or name=='SQLITE_INTERRUPT' else name
            error=IndexReadError(code);error.code=code;error.sqlite_type=type(exc).__name__;raise error from None
        finally:
            if db is not None:db.close()
    def small(self,kind,category=None,limit=24,pin=None):
        where='pid=? AND kind=?'+self._filter(kind);args=[self.pid,kind]
        if category is not None:where+=' AND cid=?';args.append(str(category))
        # DESC already puts NULL last. No GROUP BY, COUNT or expression sort
        # over hundreds of thousands of titles for a 12/24-tile Home row.
        order='ordinal' if kind=='live' else 'added DESC'
        raw=self._query('SELECT payload FROM titles WHERE '+where+' ORDER BY '+order+' LIMIT ?',args+[min(96,limit*4)],kind)
        rows=[];seen=set()
        if pin:
            item=self.get(kind,pin)
            if item and (category is None or str(item.get('category_id',''))==str(category)):
                rows.append(item);seen.add(str(item['sid']))
        for value in raw:
            item=json.loads(value['payload']);sid=str(item.get('sid',''))
            if sid and sid not in seen:rows.append(item);seen.add(sid)
            if len(rows)>=limit:break
        return rows

def files(pid,kind):
    from utils import addon_data_dir
    name='xcmate_widget41_'+hashlib.sha256((str(pid)+'|'+kind).encode()).hexdigest()[:24]
    return os.path.join(addon_data_dir(),name+'.json'),os.path.join(addon_data_dir(),name+'.lock')

def policy(portal,kind,offset=0):
    from utils import addon_data_dir,setting_int
    try:s=os.stat(os.path.join(addon_data_dir(),'xtreammate_groups.json'));stamp=[s.st_mtime_ns,s.st_size]
    except OSError:stamp=None
    return hashlib.sha256(json.dumps([str(portal['id']),kind,portal.get('start_stream_id'),portal.get('start_group_id'),portal.get('include_'+kind,True),stamp,offset,setting_int('recent_keep',100)],sort_keys=True).encode()).hexdigest()

def read(filename,key):
    try:
        with open(filename,encoding='utf-8') as f:raw=f.read(MAX_BYTES+1)
        value=json.loads(raw) if len(raw)<=MAX_BYTES else None
        if isinstance(value,dict) and value.get('policy')==key and isinstance(value.get('rows'),list) and len(value['rows'])<=24 and all(isinstance(r,dict) and isinstance(r.get('sid'),str) and isinstance(r.get('name'),str) for r in value['rows']) and 0<=time.time()-value.get('at',0)<600:return value
    except (OSError,ValueError,TypeError):pass
    return None

def store(filename,key,rows):
    temp=None
    try:
        data=json.dumps(dict(policy=key,at=time.time(),rows=rows))
        if len(data.encode())>MAX_BYTES:return
        fd,temp=tempfile.mkstemp(prefix='.widget41-',dir=os.path.dirname(filename))
        with os.fdopen(fd,'w',encoding='utf-8') as f:f.write(data)
        os.replace(temp,filename)
    except OSError:pass
    finally:
        if temp and os.path.exists(temp):os.unlink(temp)

def trace(kind,code,rows,started,stale=False):
    import xbmc
    allowed=('READY','CACHE','LOCKED','BUDGET','SQLITE_BUSY','SQLITE_LOCKED','SQLITE_INTERRUPT','SQLITE_CORRUPT','SQLITE_NOTADB','SQLITE_CANTOPEN','SQLITE_IOERR','INDEX_MISSING','UNAVAILABLE','DISABLED')
    code=code if code in allowed else 'UNAVAILABLE'
    try:xbmc.log('[XCMate][WIDGET41] kind='+kind+' code='+code+' rows='+str(rows)+' stale='+str(int(stale))+' ms='+str(int((time.monotonic()-started)*1000)),xbmc.LOGINFO)
    except (AttributeError,RuntimeError):pass

def snapshot(portal,kind):
    started=time.monotonic();filename,lock=files(portal['id'],kind);key=policy(portal,kind)
    if not portal.get('include_'+kind,True):return [],'DISABLED'
    old=read(filename,key)
    if old and time.time()-old['at']<15:trace(kind,'CACHE',len(old['rows']),started);return old['rows'],'CACHE'
    stream=None;code='UNAVAILABLE'
    try:
        import fcntl
        stream=open(lock,'a');fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
        # Another interpreter may have published while this one waited to run.
        fresh=read(filename,key)
        if fresh and time.time()-fresh['at']<15:return fresh['rows'],'CACHE'
        reader=WidgetReader(portal['id'])
        if not reader.state(kind):return (old['rows'],'INDEX_MISSING') if old else ([], 'INDEX_MISSING')
        if kind=='live':
            start=reader.get('live',str(portal.get('start_stream_id') or ''))
            cid=initial_group(portal,reader.groups('live'),start)
            rows=reader.small(kind,category=cid,limit=12,pin=start['sid'] if start else None) if cid else []
        else:rows=reader.small(kind,limit=24)
        store(filename,key,rows);trace(kind,'READY',len(rows),started);return rows,'READY'
    except BlockingIOError:code='LOCKED'
    except (IndexReadError,sqlite3.Error,OSError,ValueError,TypeError,ImportError) as exc:code=getattr(exc,'code','UNAVAILABLE')
    finally:
        if stream:stream.close()
    rows=old['rows'] if old else [];trace(kind,code,len(rows),started,bool(old));return rows,code
