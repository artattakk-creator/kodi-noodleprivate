"""Persistent 10-day guide, separate from the frozen fast Now/Next resolver.

Only local normalized cache is imported. Failed/shorter imports retain future
programmes outside the new source window. No GUI callback performs an import.
"""
from localization import tr
import datetime
import hashlib
import json
import os
import sqlite3
import time

MAX_EVENTS=200000


def path():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'guide_v1.sqlite')


def connect(filename=None):
    db=sqlite3.connect(filename or path(),timeout=2)
    db.row_factory=sqlite3.Row
    page_size=db.execute('PRAGMA page_size').fetchone()[0]
    db.execute('PRAGMA max_page_count='+str((80*1024*1024)//page_size))
    db.executescript('''CREATE TABLE IF NOT EXISTS guide_meta(pid TEXT PRIMARY KEY,revision TEXT,updated REAL);
      CREATE TABLE IF NOT EXISTS guide_alias(pid TEXT,alias TEXT,cid TEXT,PRIMARY KEY(pid,alias));
      CREATE TABLE IF NOT EXISTS programmes(pid TEXT,cid TEXT,start INTEGER,stop INTEGER,
        title TEXT,description TEXT,source INTEGER,PRIMARY KEY(pid,cid,start,stop));
      CREATE INDEX IF NOT EXISTS guide_window ON programmes(pid,cid,start);''')
    return db


def import_cache(pid,cache,revision='',now=None,filename=None):
    from epg_views import _as_int
    now=int(time.time() if now is None else now)
    if not isinstance(cache,dict) or not cache: return False
    db=connect(filename)
    try:
        with db:
            db.execute('DELETE FROM programmes WHERE stop<?',(now-86400,))
            db.execute('CREATE TEMP TABLE incoming(cid TEXT,start INTEGER,stop INTEGER,title TEXT,description TEXT,source INTEGER,PRIMARY KEY(cid,start,stop))')
            for alias,events in cache.items():
                if not isinstance(events,list): continue
                canonical=None
                for event in events:
                    if not isinstance(event,dict): continue
                    start=_as_int(event.get('start_timestamp'));stop=_as_int(event.get('stop_timestamp'))
                    title=str(event.get('name') or event.get('title') or '')[:512]
                    if start<=0 or stop<=max(start,now) or start>=now+10*86400 or not title: continue
                    cid=str(event.get('channel') or alias)
                    canonical=cid
                    try: source=int(event.get('_source_index',0))
                    except (ValueError,TypeError): source=0
                    # Canonical XMLTV rows win over a stale stream alias with
                    # the same channel/time, independent of dict iteration.
                    db.execute(('INSERT OR REPLACE' if str(alias)==cid else 'INSERT OR IGNORE')+' INTO incoming VALUES(?,?,?,?,?,?)',
                        (cid,start,stop,title,str(event.get('descr') or event.get('description') or '')[:4096],source))
                if canonical: db.execute('INSERT OR REPLACE INTO guide_alias VALUES(?,?,?)',(pid,str(alias),canonical))
            count=db.execute('SELECT count(*) FROM incoming').fetchone()[0]
            if not count: return False
            if count>MAX_EVENTS: raise ValueError('guide index budget')
            # Replace only newly covered channel intervals. Keep a previously
            # downloaded +7/+9 day even when the next import contains only 24h.
            for row in db.execute('SELECT cid,min(start),max(stop) FROM incoming GROUP BY cid').fetchall():
                db.execute('DELETE FROM programmes WHERE pid=? AND cid=? AND start<? AND stop>?',
                           (pid,row[0],row[2],row[1]))
            db.execute('INSERT OR REPLACE INTO programmes SELECT ?,cid,start,stop,title,description,source FROM incoming',(pid,))
            count=db.execute('SELECT count(*) FROM programmes WHERE pid=?',(pid,)).fetchone()[0]
            if count>MAX_EVENTS: raise ValueError('guide index budget')
            db.execute('INSERT OR REPLACE INTO guide_meta VALUES(?,?,?)',(pid,revision,time.time()))
        return True
    finally: db.close()


def refresh(portal,filename=None):
    from epg import load_cache
    from epg_status import revision,read
    rev=revision(portal['id'])+'|'+str(read(portal['id']).get('cache',{}).get('last_success',0))
    # Revision Home properties disappear on restart. A saved populated DB is
    # still useful; a process-local first refresh imports once, never per key.
    db=connect(filename)
    try: prior=db.execute('SELECT revision FROM guide_meta WHERE pid=?',(portal['id'],)).fetchone()
    finally: db.close()
    if prior and prior[0]==rev: return False
    return import_cache(portal['id'],load_cache(portal['id']),rev,filename=filename)


def day_window(day,now=None):
    """Local calendar midnights; DST days are 23/25 hours, not always 86400s."""
    today=datetime.date.fromtimestamp(time.time() if now is None else now)
    date=today+datetime.timedelta(days=int(day))
    def midnight(d): return int(time.mktime((d.year,d.month,d.day,0,0,0,0,0,-1)))
    return midnight(date),midnight(date+datetime.timedelta(days=1))


def events(pid,epg_id,start,stop,offset=0,limit=100,filename=None):
    db=connect(filename)
    try:
        alias=db.execute('SELECT cid FROM guide_alias WHERE pid=? AND alias=?',(pid,str(epg_id))).fetchone()
        cid=alias[0] if alias else str(epg_id)
        where='pid=? AND cid=? AND start<? AND stop>?'
        args=(pid,cid,stop,start)
        total=db.execute('SELECT count(*) FROM programmes WHERE '+where,args).fetchone()[0]
        rows=db.execute('SELECT * FROM programmes WHERE '+where+' ORDER BY start,stop LIMIT ? OFFSET ?',
                        args+(min(100,max(1,int(limit))),max(0,int(offset)))).fetchall()
        return [dict(r) for r in rows],total
    finally: db.close()


def horizon(pid,epg_id=None,filename=None):
    db=connect(filename)
    try:
        where='pid=?';args=[pid]
        if epg_id is not None:
            alias=db.execute('SELECT cid FROM guide_alias WHERE pid=? AND alias=?',(pid,str(epg_id))).fetchone()
            where+=' AND cid=?';args.append(alias[0] if alias else str(epg_id))
        row=db.execute('SELECT min(start),max(stop),count(*) FROM programmes WHERE '+where,args).fetchone()
        return dict(first_event=row[0],last_event=row[1],programmes=row[2])
    finally: db.close()


def status_lines(portal,filename=None):
    from epg_sources import configuration
    from epg_status import read,source_key
    from epg_preview import safe_name
    config=configuration(portal['id']);state=read(portal['id'])
    db=connect(filename)
    try:
        rows=db.execute('SELECT source,min(start),max(stop),count(*) FROM programmes WHERE pid=? GROUP BY source',(portal['id'],)).fetchall()
    finally: db.close()
    lines=[tr(32558),
           tr(32559)]
    for source,first,last,count in rows:
        source_record=None
        if source>0 and source<=len(config['sources']): source_record=config['sources'][source-1]
        name=safe_name(source_record.get('name')) if source_record else tr(32560) if source==0 else tr(32561)
        entry=state.get(source_key(source_record) if source_record else 'provider',{})
        success=entry.get('last_success')
        lines+=['',tr(32562).format(name,count),
                tr(32563).format(time.strftime(tr(32585),time.localtime(first)),time.strftime(tr(32585),time.localtime(last))),
                tr(32564)+(time.strftime(tr(32585),time.localtime(success)) if success else tr(32565)),
                tr(32566)+str(entry.get('code',tr(32567)))]
    if not rows: lines.append(tr(32568))
    return lines
