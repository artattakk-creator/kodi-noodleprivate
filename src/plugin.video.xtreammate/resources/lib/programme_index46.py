"""Shared additive programme/artwork SQLite snapshot; never writes guide_v1.

Writers run in source/data/art workers. Readers open mode=ro, never create a
database or fetch HTTP. Missing feeds are not deletion instructions. No image
or published guide retention/deletion is performed by this cache.
"""
import hashlib,json,os,sqlite3,time,tempfile
from urllib.parse import quote
from programme_read47 import scoped
MAX_BYTES=128*1024*1024
APPLICATION_ID=0x58434D46
_scans={};_reports={};_pauses={}
FIELDS=('pid','sid','canonical','key','start','stop','title','description','source','revision','code','subtitle','genre','episode_label','year','season','episode','cast','director','xmltv_image','provider_image','epg_source46','epg_text46','placeholder','source_key46','fact_revision46','field_sources52','updated52')


def path(guide=None):
    if guide:return str(guide)+'.programme_artwork.sqlite'
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'programme_artwork.sqlite')


def report(category,error=None,guide=None):
    """Fixed write status only; never exception text, source IDs or URLs."""
    code='READY' if error is None else 'PROGRAMME_DATA_BUDGET' if getattr(error,'sqlite_errorname','')=='SQLITE_FULL' else 'DISK_FULL' if getattr(error,'errno',None)==28 else 'PROGRAMME_DB_BUSY' if getattr(error,'sqlite_errorname','') in ('SQLITE_BUSY','SQLITE_LOCKED') else 'PROGRAMME_DB_IO'
    filename=path(guide)+'.status.json';key=(filename,category);old=_reports.get(key);now=time.time()
    if old and old[0]==code and now-old[1]<60:return
    _reports[key]=(code,now);temp=None
    try:
        states={}
        try:
            with open(filename,encoding='utf-8') as f:states=json.loads(f.read(2049))
        except (OSError,ValueError):pass
        if not isinstance(states,dict):states={}
        states={k:v for k,v in states.items() if k in ('facts','events','art') and isinstance(v,dict)}
        states[category]=dict(code=code,at=now)
        fd,temp=tempfile.mkstemp(prefix='.programme-db-status46-',dir=os.path.dirname(filename))
        with os.fdopen(fd,'w',encoding='utf-8') as f:json.dump(states,f)
        os.replace(temp,filename);temp=None
    except OSError:pass
    finally:
        if temp:
            try:os.unlink(temp)
            except OSError:pass
    if error is not None:
        try:
            import xbmc
            xbmc.log('[XCMate][PROGRAMME_DB46] stage='+category+' code='+code,xbmc.LOGINFO)
        except (ImportError,AttributeError,RuntimeError):pass


def bounds(now=None):
    from guide_store import day_window
    return day_window(-7,now)[0],day_window(21,now)[0]


def connect(write=False,guide=None):
    filename=path(guide)
    if os.path.islink(filename):raise OSError('PROGRAMME_DB_UNSAFE')
    if not write:
        from programme_read47 import borrowed,retain
        old=borrowed(filename)
        if old is not None:return old
        if not os.path.isfile(filename):return None
        db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.02)
        db.execute('PRAGMA query_only=ON')
        if db.execute('PRAGMA application_id').fetchone()[0]!=APPLICATION_ID or db.execute('PRAGMA user_version').fetchone()[0]!=1:
            db.close();raise ValueError('UNSUPPORTED_PROGRAMME_SCHEMA')
        return retain(filename,db)
    from import_budget import check_space
    check_space(filename,65536)
    db=sqlite3.connect(filename,timeout=.05)
    try:
        application=db.execute('PRAGMA application_id').fetchone()[0];version=db.execute('PRAGMA user_version').fetchone()[0]
        empty=db.execute("SELECT 1 FROM sqlite_master WHERE type='table' LIMIT 1").fetchone() is None
        if not (application==APPLICATION_ID and version==1 or application==0 and version==0 and empty):raise ValueError('UNSUPPORTED_PROGRAMME_SCHEMA')
        db.execute('PRAGMA journal_mode=WAL');db.execute('PRAGMA synchronous=FULL');db.execute('PRAGMA cache_size=-1024')
        db.execute('PRAGMA max_page_count=32768')
        if application==APPLICATION_ID and version==1:return db
        db.executescript('''BEGIN IMMEDIATE;
          CREATE TABLE IF NOT EXISTS facts(pid TEXT,cid TEXT,start INTEGER,stop INTEGER,source_id TEXT,titlehash TEXT,fingerprint TEXT,data TEXT,updated REAL,PRIMARY KEY(pid,cid,start,stop,source_id));
          CREATE INDEX IF NOT EXISTS programme_canonical_time46 ON facts(pid,cid,start,stop);
          CREATE INDEX IF NOT EXISTS programme_stop46 ON facts(pid,stop);
          CREATE TABLE IF NOT EXISTS fact_versions(pid TEXT,cid TEXT,version INTEGER,PRIMARY KEY(pid,cid));
          CREATE TABLE IF NOT EXISTS pending46(generation TEXT,pid TEXT,cid TEXT,start INTEGER,stop INTEGER,source_id TEXT,titlehash TEXT,fingerprint TEXT,data TEXT,PRIMARY KEY(generation,pid,cid,start,stop,source_id));
          CREATE TABLE IF NOT EXISTS events(event_key TEXT PRIMARY KEY,pid TEXT,sid TEXT,canonical_sid TEXT,start INTEGER,stop INTEGER,base_hash TEXT,data TEXT,version INTEGER,updated REAL);
          CREATE INDEX IF NOT EXISTS event_canonical_time46 ON events(pid,canonical_sid,start,stop);
          CREATE TABLE IF NOT EXISTS artwork(event_key TEXT PRIMARY KEY,fingerprint TEXT,data TEXT,version INTEGER,checked REAL,expires REAL);
          CREATE TABLE IF NOT EXISTS image_sources(source_hash TEXT PRIMARY KEY,data TEXT,expires REAL);
          PRAGMA application_id=1480805702;
          PRAGMA user_version=1;COMMIT;''')
        return db
    except Exception:db.close();raise


def encoded(value):return json.dumps(value,ensure_ascii=False,sort_keys=True,separators=(',',':'))
def digest(value):return hashlib.sha256(encoded(value).encode()).hexdigest()
def base_hash(event,facts_version=0):
    from programme_store46 import path as metadata_path
    signature=[]
    for filename in (metadata_path(),metadata_path()+'-wal'):
        try:s=os.stat(filename);signature.append((s.st_mtime_ns,s.st_size))
        except OSError:signature.append(None)
    return digest([[event.get(k) for k in ('pid','sid','canonical','start','stop','title','description','source','revision','source_key46','fact_revision46')],signature,facts_version])


def fact_version(db,event):
    row=db.execute('SELECT version FROM fact_versions WHERE pid=? AND cid=?',(str(event['pid']),str(event.get('canonical','')))).fetchone()
    return row[0] if row else 0


class Stage:
    def __init__(self,pid,generation,guide=None):self.pid=str(pid);self.generation=generation;self.guide=guide;self.rows=[];self.failed=False;self.left,self.right=bounds()
    def add(self,event,extra,source_id):
        if self.failed:return
        try:
            from programme_store46 import title_hash
            start=int(event.get('start_timestamp',event.get('start',0)));stop=int(event.get('stop_timestamp',event.get('stop',0)))
            title=str(event.get('name') or event.get('title') or '')[:512]
            if start<=0 or stop<=start or stop<=self.left or start>=self.right or not title:return
            value=dict(extra,name=title,title=title,descr=str(event.get('descr') or event.get('description') or '')[:8192],start_timestamp=start,stop_timestamp=stop,channel=str(event.get('channel') or event.get('cid') or ''),source_key46=source_id)
            value.setdefault('epg_source46',source_id);value.setdefault('epg_text46',hashlib.sha256(value['descr'][:4096].encode()).hexdigest())
            value.pop('metadata_code46',None)
            data=encoded(value)
            self.rows.append((self.generation,self.pid,value['channel'],start,stop,source_id,title_hash(title),hashlib.sha256(data.encode()).hexdigest(),data))
            if len(self.rows)>=128:self.flush()
        except (ValueError,TypeError,MemoryError):self.failed=True;self.rows.clear()
    def flush(self):
        if not self.rows:return
        db=None
        try:
            db=connect(True,self.guide)
            with db:db.executemany('INSERT OR REPLACE INTO pending46 VALUES(?,?,?,?,?,?,?,?,?)',self.rows)
        except (OSError,sqlite3.Error,ValueError,MemoryError) as exc:self.failed=True;report('facts',exc,self.guide)
        finally:
            if db is not None:db.close()
            self.rows.clear()


def finish(pid,generation,publish,guide=None):
    if not os.path.isfile(path(guide)):return
    db=None
    try:
        db=connect(True,guide)
        with db:
            while True:
                rows=db.execute('SELECT pid,cid,start,stop,source_id,titlehash,fingerprint,data FROM pending46 WHERE generation=? AND pid=? LIMIT 128',(generation,str(pid))).fetchall()
                if not rows:break
                db.executemany('DELETE FROM pending46 WHERE generation=? AND pid=? AND cid=? AND start=? AND stop=? AND source_id=?',[(generation,*r[:5]) for r in rows])
                if publish:
                    # A partial observation of the same event cannot erase
                    # already verified description/image/episode facts.
                    marks=','.join('(?,?,?,?)' for _ in rows)
                    old={tuple(r[:4]):json.loads(r[4]) for r in db.execute('SELECT cid,start,stop,source_id,data FROM facts WHERE pid=? AND (cid,start,stop,source_id) IN ('+marks+')',[str(pid)]+[v for row in rows for v in row[1:5]])}
                    from epg_merge52 import retained
                    merged=[]
                    for row in rows:
                        prior=old.get(tuple(row[1:5]))
                        if prior:
                            value=retained(prior,json.loads(row[7]));data=encoded(value)
                            row=(*row[:6],hashlib.sha256(data.encode()).hexdigest(),data)
                        merged.append(row)
                    rows=merged
                    for cid in {r[1] for r in rows}:
                        count=db.executemany('''INSERT INTO facts VALUES(?,?,?,?,?,?,?,?,?) ON CONFLICT(pid,cid,start,stop,source_id) DO UPDATE SET titlehash=excluded.titlehash,fingerprint=excluded.fingerprint,data=excluded.data,updated=excluded.updated WHERE facts.fingerprint!=excluded.fingerprint''',[(*r,time.time()) for r in rows if r[1]==cid]).rowcount
                        if count:db.execute('INSERT INTO fact_versions VALUES(?,?,1) ON CONFLICT(pid,cid) DO UPDATE SET version=version+1',(str(pid),cid))
        if publish:report('facts',guide=guide)
        return True
    except (OSError,sqlite3.Error,ValueError,MemoryError) as exc:
        report('facts',exc,guide)
        if db is not None:db.rollback()
        return False
    finally:
        if db is not None:db.close()


def ranks(pid):
    from programme_read47 import memo
    return memo(('ranks47',str(pid)),lambda:_ranks47(pid))


def _ranks47(pid):
    from epg_sources import configuration
    from guide_publish44 import source_id
    result={'provider':0,'compatibility':0}
    for index,source in enumerate(configuration(pid).get('sources',[]),1):
        if source.get('enabled',True):result[source_id(source,index)]=index
    return result


def window(pid,cid,start,stop,primary=(),limit=256,guide=None,source48=None):
    db=None
    try:
        db=connect(False,guide)
        if db is None:return []
        left,right=bounds();start=max(left,start);stop=min(right,stop)
        end=time.monotonic()+.03;db.set_progress_handler(lambda:int(time.monotonic()>end),1000)
        allowed=ranks(pid);values=[]
        for source,fingerprint,data,updated in db.execute('SELECT source_id,fingerprint,data,updated FROM facts WHERE pid=? AND cid=? AND start<? AND stop>?'+(' AND source_id=?' if source48 else '')+' ORDER BY start,stop LIMIT ?',tuple([str(pid),str(cid),stop,start]+([source48] if source48 else [])+[min(512,limit*4)])):
            if source not in allowed or len(data)>24576:continue
            value=json.loads(data);value['_source_index']=value['source']=allowed[source];value['fact_revision46']=fingerprint;value['_updated46']=updated
            values.append(value)
        accepted=[];intervals=[(e.get('start_timestamp',e.get('start')),e.get('stop_timestamp',e.get('stop'))) for e in primary]
        for value in sorted(values,key=lambda v:(v['source'],-v['_updated46'],v['start_timestamp'],v['stop_timestamp'])):
            a,b=value['start_timestamp'],value['stop_timestamp']
            if any(a<y and b>x for x,y in intervals):continue
            accepted.append(value);intervals.append((a,b))
            if len(accepted)>=limit:break
        return sorted(accepted,key=lambda v:v['start_timestamp'])
    except (OSError,sqlite3.Error,ValueError,TypeError,KeyError):return []
    finally:
        if db is not None:db.close()


def metadata(pid,cid,event,guide=None):
    rows=window(pid,cid,event['start'],event['stop'],guide=guide)
    for row in rows:
        if (row['start_timestamp']==event['start'] and row['stop_timestamp']==event['stop']
                and row['name']==event['title'] and row.get('descr')==event.get('description')):
            if event.get('source_key46'):
                if row.get('source_key46')!=event['source_key46'] or row.get('fact_revision46')!=event.get('fact_revision46'):continue
            else:
                from programme_store46 import origin_matches
                if not origin_matches(pid,cid,event,row.get('source_key46'),guide):continue
            value={k:row[k] for k in FIELDS if k in row and k not in ('title','start','stop','source','revision','code','key','pid','sid','canonical','description')}
            if not event.get('source_key46'):
                value.pop('source_key46',None);value.pop('fact_revision46',None)
            return value
    return {}


def event(event,write=False):
    db=None
    try:
        db=connect(write)
        if db is None:return
        code=base_hash(event,fact_version(db,event))
        if write:
            value={k:event[k] for k in FIELDS if k in event};data=encoded(value)
            with db:db.execute('''INSERT INTO events VALUES(?,?,?,?,?,?,?,?,1,?) ON CONFLICT(event_key) DO UPDATE SET base_hash=excluded.base_hash,data=excluded.data,updated=excluded.updated WHERE events.base_hash!=excluded.base_hash OR events.data!=excluded.data''',(event['key'],event['pid'],event['sid'],event.get('canonical',''),event['start'],event['stop'],code,data,time.time()))
            report('events')
            return value
        row=db.execute('SELECT base_hash,data FROM events WHERE event_key=?',(event['key'],)).fetchone()
        if row and row[0]==code and len(row[1])<=24576:return json.loads(row[1])
    except (OSError,sqlite3.Error,ValueError,TypeError,KeyError) as exc:
        if write:report('events',exc)
        return
    finally:
        if db is not None:db.close()


def art(event,value=None):
    db=None
    try:
        from programme_art46 import fingerprint
        db=connect(value is not None)
        if db is None:return
        if value is not None:
            data=encoded(value)
            with db:
                db.execute('''INSERT INTO artwork VALUES(?,?,?,1,?,?) ON CONFLICT(event_key) DO UPDATE SET fingerprint=excluded.fingerprint,data=excluded.data,checked=excluded.checked,expires=excluded.expires''',(event['key'],fingerprint(event),data,time.time(),value.get('until',0)))
                if value.get('source_url') and value.get('code')=='READY':db.execute('INSERT OR REPLACE INTO image_sources VALUES(?,?,?)',(digest([value['source'],value['source_url']]),data,value.get('until',0)))
            report('art')
            return dict(value)
        row=db.execute('SELECT fingerprint,data FROM artwork WHERE event_key=?',(event['key'],)).fetchone()
        if row and row[0]==fingerprint(event) and len(row[1])<=16384:return json.loads(row[1])
    except (OSError,sqlite3.Error,ValueError,TypeError,KeyError) as exc:
        if value is not None:report('art',exc)
        return
    finally:
        if db is not None:db.close()


def reused(candidate):
    db=None
    try:
        db=connect(False)
        if db is None:return
        row=db.execute('SELECT data,expires FROM image_sources WHERE source_hash=?',(digest([candidate['source'],candidate['url']]),)).fetchone()
        if row and row[1]>time.time() and len(row[0])<=16384:return json.loads(row[0])
    except (OSError,sqlite3.Error,ValueError,TypeError,KeyError):return
    finally:
        if db is not None:db.close()


def publish(records,include_art=True):
    """One transaction for a bounded worker page, including negative art TTL."""
    db=None
    try:
        from programme_art46 import peek,fingerprint
        db=connect(True)
        with db:
            for record in records[:64]:
                data=encoded({k:record[k] for k in FIELDS if k in record})
                db.execute('''INSERT INTO events VALUES(?,?,?,?,?,?,?,?,1,?) ON CONFLICT(event_key) DO UPDATE SET base_hash=excluded.base_hash,data=excluded.data,updated=excluded.updated WHERE events.base_hash!=excluded.base_hash OR events.data!=excluded.data''',(record['key'],record['pid'],record['sid'],record.get('canonical',''),record['start'],record['stop'],base_hash(record,fact_version(db,record)),data,time.time()))
                # URL55 has its own committed writer. A producer may have read
                # an older RAM manifest before that commit; it must not replace
                # the newer durable reference with that stale observation.
                value=peek(record) if include_art else {}
                if value.get('until'):
                    db.execute('''INSERT INTO artwork VALUES(?,?,?,1,?,?) ON CONFLICT(event_key) DO UPDATE SET fingerprint=excluded.fingerprint,data=excluded.data,checked=excluded.checked,expires=excluded.expires WHERE artwork.fingerprint!=excluded.fingerprint OR artwork.data!=excluded.data''',(record['key'],fingerprint(record),encoded(value),time.time(),value['until']))
        report('events');return True
    except (OSError,sqlite3.Error,ValueError,TypeError,KeyError) as exc:report('events',exc);return False
    finally:
        if db is not None:db.close()


@scoped
def prepare_local(portal,cancel=lambda:False):
    """Incremental 32-record copy from a read-only stable guide transaction."""
    import uuid
    from guide_store import path as guide_path
    from programme_store46 import read as rich
    filename=guide_path();key=(filename,str(portal['id']));db=None
    if not os.path.isfile(filename) or cancel() or time.monotonic()<_pauses.get(key,0):return False
    try:
        db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.03)
        db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        meta=db.execute('SELECT revision,updated FROM guide_meta WHERE pid=?',(str(portal['id']),)).fetchone()
        if not meta:return False
        old=_scans.get(key);cursor=old[1] if old and old[0]==meta else None
        if old and old[0]==meta and old[2]:return False
        end=time.monotonic()+.15;db.set_progress_handler(lambda:int(time.monotonic()>end),1000)
        suffix=' AND (cid,start,stop)>(?,?,?)' if cursor else ''
        left,right=bounds()
        rows=db.execute('SELECT cid,start,stop,title,description,source FROM programmes WHERE pid=?'+suffix+' AND stop>? AND start<? ORDER BY cid,start,stop LIMIT 32',[str(portal['id'])]+(list(cursor) if cursor else [])+[left,right]).fetchall()
        stage=Stage(portal['id'],uuid.uuid4().hex);last=cursor;processed=0
        for cid,start,stop,title,description,source in rows:
            if cancel():return False
            value=dict(start=start,stop=stop,title=title,description=description,source=source)
            extra=rich(portal['id'],cid,value,verify_source=True)
            stage.add(dict(channel=cid,start=start,stop=stop,title=title,description=description),extra,extra.get('epg_source46','compatibility'))
            last=(cid,start,stop);processed+=1
            if time.monotonic()>end:break
        stage.flush()
        if stage.failed or not finish(portal['id'],stage.generation,True):
            finish(portal['id'],stage.generation,False);_pauses[key]=time.monotonic()+300
            return False
        _pauses.pop(key,None)
        _scans[key]=(meta,last,len(rows)<32 and processed==len(rows))
        if len(_scans)>8:_scans.pop(next(iter(_scans)))
        return bool(processed)
    except (OSError,sqlite3.Error,ValueError,TypeError,MemoryError):return False
    finally:
        if db is not None:db.close()


def available_days(pid,guide=None):
    db=None
    try:
        db=connect(False,guide)
        if db is None:return 0
        row=db.execute('SELECT max(stop) FROM facts WHERE pid=?',(str(pid),)).fetchone()
        if not row or not row[0]:return 0
        import datetime
        return min(21,max(0,(datetime.date.fromtimestamp(row[0]-1)-datetime.date.today()).days+1))
    except (OSError,sqlite3.Error,ValueError):return 0
    finally:
        if db is not None:db.close()


def last_event(pid,cid,guide=None):
    db=None
    try:
        db=connect(False,guide)
        if db is None:return None
        left,right=bounds();end=time.monotonic()+.03;db.set_progress_handler(lambda:int(time.monotonic()>end),1000)
        row=db.execute('SELECT max(stop) FROM facts WHERE pid=? AND cid=? AND stop>? AND start<?',(str(pid),str(cid),left,right)).fetchone()
        return row[0] if row else None
    except (OSError,sqlite3.Error,ValueError):return None
    finally:
        if db is not None:db.close()


def status():
    db=None
    try:
        db=connect(False)
        if db is None:return dict(code='NOT_CREATED',bytes=0)
        page=db.execute('PRAGMA page_count').fetchone()[0]*db.execute('PRAGMA page_size').fetchone()[0]
        version=db.execute('PRAGMA user_version').fetchone()[0]
        free=db.execute('PRAGMA freelist_count').fetchone()[0]*db.execute('PRAGMA page_size').fetchone()[0]
        states={}
        try:
            with open(path()+'.status.json',encoding='utf-8') as f:states=json.loads(f.read(2049))
        except (OSError,ValueError):pass
        codes={'READY','PROGRAMME_DATA_BUDGET','DISK_FULL','PROGRAMME_DB_BUSY','PROGRAMME_DB_IO'}
        failures={k:v['code'] for k,v in states.items() if isinstance(v,dict) and v.get('code') in codes-{'READY'}} if isinstance(states,dict) else {}
        return dict(code=next(iter(failures.values())) if failures else 'PROGRAMME_DATA_BUDGET' if page-free>=MAX_BYTES else 'READY' if version==1 else 'UNSUPPORTED_SCHEMA',bytes=page,used=page-free,version=version,last_write_failures=failures)
    except ValueError:return dict(code='BLOCKED_SCHEMA')
    except (OSError,sqlite3.Error):return dict(code='PROGRAMME_DB_UNAVAILABLE')
    finally:
        if db is not None:db.close()
