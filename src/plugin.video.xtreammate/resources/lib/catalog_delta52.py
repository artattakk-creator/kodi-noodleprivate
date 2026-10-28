"""Existing worklist recovery, visible control and whole-worker ownership."""
import functools,json,os,sqlite3,time
from urllib.parse import quote


def serial_worker(call):
    @functools.wraps(call)
    def run(*args,**kwargs):
        from utils import addon_data_dir
        import fcntl
        fd=None
        try:
            fd=os.open(os.path.join(addon_data_dir(),'.catalog-delta52.lock'),os.O_CREAT|os.O_RDWR|getattr(os,'O_NOFOLLOW',0),0o600)
            try:fcntl.flock(fd,fcntl.LOCK_EX|fcntl.LOCK_NB)
            except BlockingIOError:return False
            return call(*args,**kwargs)
        finally:
            if fd is not None:os.close(fd)
    return run


def cancellation(key,owner,upstream):
    next_check=0;stopped=False
    def check():
        nonlocal next_check,stopped
        if upstream():return True
        if time.monotonic()<next_check:return stopped
        next_check=time.monotonic()+.5
        from catalog_delta import _read
        try:
            row=_read()['jobs'].get(key,{})
            stopped=row.get('owner')!=owner or bool(row.get('cancel_requested'))
        except (OSError,ValueError):stopped=True
        return stopped
    return check


def reconcile_series(portal):
    if portal.get('type')!='xtream' or not portal.get('include_series',True):return
    from group_selection import load
    selected=load(portal['id'],'series')
    if not selected:return
    from library_index import Reader
    rows=Reader(portal['id'],timeout=.05,query_seconds=.1)._query('SELECT cid FROM heads WHERE pid=? AND kind=?',(str(portal['id']),'series'))
    missing=sorted(selected-{r['cid'] for r in rows})[:64]
    from catalog_delta import request_many
    if missing:request_many(portal,'series',missing,missing=True)


def progress(pid,kind,rows):
    from library_index import path
    filename=path();db=None
    if not os.path.isfile(filename):return rows
    try:
        db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.03)
        db.execute('PRAGMA query_only=ON');end=time.monotonic()+.05;db.set_progress_handler(lambda:int(time.monotonic()>end),1000)
        for row in rows:
            if row['code']!='RUNNING':continue
            state=db.execute('SELECT stored,received FROM sync_status WHERE pid=? AND kind=? AND cid=?',(str(pid),kind,row['cid'])).fetchone()
            if state:row.update(stored=state[0],received=state[1])
    except (OSError,sqlite3.Error):pass
    finally:
        if db is not None:db.close()
    return rows


def cancel_jobs(pid,kind,keep=None):
    from catalog_delta import _read,_save
    from profile_transaction import writing
    with writing(timeout=.1):
        value=_read()
        for row in value['jobs'].values():
            if row['pid']!=str(pid) or row['kind']!=kind:continue
            if keep is not None and row['cid'] in keep:continue
            if row['code']=='RUNNING':row['cancel_requested']=True
            elif row['code'] in ('PENDING','FAILED'):row.update(code='CANCELLED',attempts=3,updated=time.time())
        _save(value)


def manage(portal,kind):
    import xbmcgui
    from catalog_delta import states,request_many
    from group_selection import load
    from menu_icons45 import select
    rows=states(portal['id'],kind);counts={}
    for row in rows:counts[row['code']]=counts.get(row['code'],0)+1
    text=' · '.join(code+': '+str(n) for code,n in sorted(counts.items())) or 'Keine Importaufträge'
    stored=sum(r.get('stored',0) for r in rows);received=sum(r.get('received',0) for r in rows)
    choice=select(xbmcgui.Dialog(),'Serien-Nachimport · '+text,
        ['Status: '+str(stored)+' gespeichert / '+str(received)+' empfangen','Fehlgeschlagene/abgebrochene Gruppen erneut versuchen','Nachimport abbrechen','Zurück'],default='list')
    if choice==1:
        allowed=load(portal['id'],kind)
        retry=[r['cid'] for r in rows if r['code'] in ('FAILED','CANCELLED','EMPTY_SOURCE') and (allowed is None or r['cid'] in allowed)]
        request_many(portal,kind,retry,retry=True)
    elif choice==2:cancel_jobs(portal['id'],kind)
