"""24-hour default, preserved explicit settings, bounded per-source retries."""
import time


def interval():
    from utils import setting_int
    return max(1,min(48,setting_int('epg_refresh_hours',24)))*3600


def plan(portal,now=None):
    from epg_report53 import configured,history,SUCCESS,BLOCKED
    from epg_status import read
    if not portal.get('epg_show',True):return []
    now=time.time() if now is None else now;period=interval();runs=history(portal['id']);state=read(portal['id']);wanted=[]
    fallback=max([row.get('last_success',0) for key,row in state.items() if key not in ('cache','refresh')]+[0])
    if not runs and not fallback:
        try:
            from epg import _is_fresh
            if _is_fresh(portal['id']):return []
        except (ImportError,AttributeError,OSError,ValueError):pass
        # Existing populated LastGood is a valid restart anchor, without
        # treating mere future coverage as permission to skip forever.
        try:
            from guide_store import path
            import sqlite3,os
            from urllib.parse import quote
            if os.path.isfile(path()):
                db=sqlite3.connect('file:'+quote(path(),safe='/')+'?mode=ro',uri=True,timeout=.03)
                try:
                    db.execute('PRAGMA query_only=ON');row=db.execute('SELECT updated FROM guide_meta WHERE pid=?',(str(portal['id']),)).fetchone()
                    if row:fallback=row[0]
                finally:db.close()
        except (OSError,sqlite3.Error):pass
    if runs and runs[-1].get('code') in BLOCKED and now-runs[-1]['started']<period:return []
    for source in configured(portal):
        if not source['enabled']:continue
        events=[s for r in runs for s in r.get('sources',[]) if s.get('id')==source['id']]
        success=max([s.get('finished',0) for s in events if s.get('code') in SUCCESS]+[state.get(source['key'],{}).get('last_success',0),fallback if not events else 0])
        if success and now-success<period:continue
        failures=[s for s in events if s.get('finished',0)>success and s.get('code') not in SUCCESS]
        if failures:
            first=failures[0]['started'];last=failures[-1]['finished'];attempts=len(failures)
            if now-first<period:
                if attempts>=3 or now-last<(900 if attempts==1 else 3600):continue
        wanted.append(source['id'])
    return wanted
