"""Live-only identity reader: one group/RO generation, independent of EPG/art."""
import json
import os
import sqlite3
import time
from urllib.parse import quote

class Failure(RuntimeError):
    def __init__(self,code,stage):self.code,self.stage=code,stage;super().__init__(code)

CODES={'READY','DISABLED','START_GROUP_MISSING','START_GROUP_UNAVAILABLE','GROUP_DISABLED','GROUP_POLICY_INVALID','INDEX_MISSING','GENERATION_MISSING','EMPTY_GROUP','BUDGET','SQLITE_BUSY','SQLITE_LOCKED','SQLITE_CORRUPT','SQLITE_NOTADB','SQLITE_CANTOPEN','SQLITE_IOERR','SQLITE_SCHEMA','SQLITE_ERROR','PAYLOAD_IDENTITY_RECOVERED','PAYLOAD_INVALID','LAST_GOOD','SNAPSHOT_REJECTED','ENRICHMENT_UNAVAILABLE','LOGO_UNAVAILABLE','DIRECTORY_EMPTY','INTERNAL_ERROR'}
STAGES={'PORTAL','GROUP_POLICY','DATABASE','HEAD','PAGE','PAYLOAD','RENDER','DIRECTORY','FALLBACK'}

def trace(stage,code,rows=0,**counts):
    import xbmc
    stage=stage if stage in STAGES else 'DIRECTORY';code=code if code in CODES else 'INTERNAL_ERROR'
    fields=''.join(' '+k+'='+str(max(0,int(v))) for k,v in counts.items() if k in ('pages','recovered','retryable','sql_ms'))
    try:xbmc.log('[XCMate][HOME62] stage='+stage+' code='+code+' rows='+str(max(0,int(rows)))+fields,xbmc.LOGINFO)
    except (AttributeError,RuntimeError,TypeError,ValueError):pass

def selection(portal):
    if not portal or not portal.get('id') or not portal.get('enabled',True):raise Failure('DISABLED','PORTAL')
    if not portal.get('include_live',True):raise Failure('DISABLED','PORTAL')
    cid=str(portal.get('start_group_id') or '')
    if not cid:raise Failure('START_GROUP_MISSING','GROUP_POLICY')
    from group_selection import enabled_ids
    try:allowed=enabled_ids(portal['id'],'live',[{'category_id':cid}])
    except (OSError,ValueError,TypeError,KeyError):raise Failure('GROUP_POLICY_INVALID','GROUP_POLICY') from None
    if cid not in allowed:raise Failure('GROUP_DISABLED','GROUP_POLICY')
    trace('GROUP_POLICY','READY');return cid

def read(portal,filename=None):
    cid=selection(portal)
    from library_index import path
    filename=filename or path()
    if not os.path.isfile(filename):raise Failure('INDEX_MISSING','DATABASE')
    db=None;stage='DATABASE';remaining=1.5;pages=0;recovered=0
    def query(sql,args):
        nonlocal remaining
        if remaining<=0:raise Failure('BUDGET',stage)
        started=time.monotonic();deadline=started+min(.5,remaining)
        db.set_progress_handler(lambda:int(time.monotonic()>=deadline),1000)
        try:return db.execute(sql,args).fetchall()
        finally:remaining-=max(0,time.monotonic()-started)
    try:
        db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.05)
        db.row_factory=sqlite3.Row;db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        stage='GROUP_POLICY'
        if not query('SELECT cid FROM groups WHERE pid=? AND kind=? AND cid=?',(str(portal['id']),'live',cid)):
            raise Failure('START_GROUP_UNAVAILABLE',stage)
        stage='HEAD';head=query('SELECT generation FROM heads WHERE pid=? AND kind=? AND cid=?',(str(portal['id']),'live',cid))
        table,index=('items_v2','group_order_v2') if head else ('titles','category_titles')
        where='pid=? AND kind=? AND cid=?';args=[str(portal['id']),'live',cid]
        if head:where+=' AND generation=?';args.append(head[0]['generation'])
        trace('HEAD','READY');result=[];last=None;seen=set()
        while True:
            stage='PAGE';suffix=' AND (ordinal,sid)>(?,?)' if last else ''
            rows=query('SELECT sid,title,payload,ordinal FROM '+table+' INDEXED BY '+index+' WHERE '+where+suffix+' ORDER BY ordinal,sid LIMIT 128',args+(list(last) if last else []))
            if not rows:break
            pages+=1
            for row in rows:
                stage='PAYLOAD';sid=row['sid'];name=row['title']
                if not isinstance(sid,str) or not sid or not isinstance(name,str) or not name or not isinstance(row['ordinal'],int):raise Failure('PAYLOAD_INVALID',stage)
                if sid in seen:raise Failure('PAYLOAD_INVALID',stage)
                seen.add(sid)
                try:
                    value=json.loads(row['payload'])
                    if not isinstance(value,dict) or str(value.get('sid',''))!=sid or str(value.get('category_id',''))!=cid:raise ValueError()
                except (ValueError,TypeError):value={};recovered+=1
                value.update(sid=sid,name=name[:512],category_id=cid,kind='live');result.append(value)
            last=(rows[-1]['ordinal'],rows[-1]['sid'])
        if not result and not head:raise Failure('GENERATION_MISSING','HEAD')
        trace('PAGE','READY',len(result),pages=pages,sql_ms=int((1.5-remaining)*1000))
        if recovered:trace('PAYLOAD','PAYLOAD_IDENTITY_RECOVERED',len(result),recovered=recovered)
        return result,'READY' if result else 'EMPTY_GROUP'
    except sqlite3.Error as exc:
        name=getattr(exc,'sqlite_errorname','SQLITE_ERROR')
        code='BUDGET' if name=='SQLITE_INTERRUPT' else 'SQLITE_BUSY' if str(name).startswith('SQLITE_BUSY') else 'SQLITE_LOCKED' if str(name).startswith('SQLITE_LOCKED') else name if name in CODES else 'SQLITE_ERROR'
        raise Failure(code,stage) from None
    except OSError:raise Failure('SQLITE_IOERR',stage) from None
    finally:
        if db is not None:db.close()

TRANSIENT={'BUDGET','SQLITE_BUSY','SQLITE_LOCKED','SQLITE_CANTOPEN','SQLITE_IOERR','INDEX_MISSING'}

def snapshot(portal,code):
    """Reuse only a policy-matching existing full-group metadata publication."""
    if code not in TRANSIENT:return None
    cid=selection(portal)
    from widget_data41 import files,policy,read
    key=policy(portal,'live');value=read(files(portal['id'],'live')[0],key)
    if not value or not value['rows']:return None
    rows=value['rows'];seen=set()
    for row in rows:
        if str(row.get('category_id',''))!=cid or row['sid'] in seen:return None
        seen.add(row['sid'])
    if key!=policy(portal,'live'):return None
    trace('FALLBACK','LAST_GOOD',len(rows));return rows


def rows(portal):
    try:return read(portal)
    except Failure as exc:
        trace(exc.stage,exc.code,retryable=int(exc.code in TRANSIENT))
        try:old=snapshot(portal,exc.code)
        except (Failure,OSError,ValueError,TypeError):old=None
        if old:return old,'LAST_GOOD'
        return [],exc.code
