"""Provider-backed genre terms; additive, bounded worker materialization only.

Existing catalogue rows/views/configuration are never rewritten. Readers accept
old databases and use terms only when their completed catalogue revision agrees.
"""
import json
import re
import sqlite3
import time
import unicodedata

ALIASES={
    'sci fi':'scifi','science fiction':'scifi','scifi':'scifi','sciencefiction':'scifi',
    'western':'western','thriller':'thriller','krimi':'crime','crime':'crime',
    'komodie':'comedy','komoedie':'comedy','comedy':'comedy','action':'action',
    'horror':'horror','fantasy':'fantasy','drama':'drama','animation':'animation',
    'abenteuer':'adventure','adventure':'adventure','romantik':'romance','romance':'romance',
    'dokumentation':'documentary','dokumentarfilm':'documentary','documentary':'documentary',
    'familie':'family','family':'family','kinder':'children','children':'children',
    'mystery':'mystery','geschichte':'history','history':'history','musik':'music','music':'music'}
BATCH=128
_offset=0
_retry={}


def parse(value):
    value=unicodedata.normalize('NFKD',str(value or '').casefold())
    tokens=re.findall('[a-z0-9]+',''.join(c for c in value if not unicodedata.combining(c)))
    genres=[];rest=[];pos=0
    while pos<len(tokens):
        size=2 if ' '.join(tokens[pos:pos+2]) in ALIASES else 1
        alias=ALIASES.get(' '.join(tokens[pos:pos+size]))
        if alias:genres.append(alias)
        else:rest.append(tokens[pos])
        pos+=size
    return list(dict.fromkeys(genres)),rest


def terms(value):
    values=value[:8] if isinstance(value,list) else [value]
    return sorted({term for item in values if isinstance(item,str) for term in parse(item[:4096])[0]})


def status(reader,kind,query):
    if kind not in ('vod','series') or not parse(query)[0]:return 'UNUSED'
    if not reader._query("SELECT 1 FROM sqlite_master WHERE type='table' AND name='xcmate_genre_state'"):return 'PENDING'
    rows=reader._query('''SELECT s.ready FROM xcmate_genre_state s JOIN catalog c USING(pid,kind)
        WHERE s.pid=? AND s.kind=? AND s.revision IS c.revision AND s.updated=c.updated''',(reader.pid,kind))
    return 'READY' if rows and rows[0]['ready'] else 'PENDING'


def clause(reader,kind,query):
    genres,rest=parse(query)
    if not genres or status(reader,kind,query)!='READY':return None
    parts=[];args=[]
    for genre in genres:
        parts.append('''(results.sid,results.cid) IN (SELECT gt.sid,gt.cid FROM xcmate_genre_terms gt
          JOIN xcmate_genre_state gs USING(pid,kind) JOIN catalog gc USING(pid,kind)
          WHERE gt.pid=? AND gt.kind=? AND gt.term=? AND gs.ready=1
          AND gs.revision IS gc.revision AND gs.updated=gc.updated)''')
        args.extend((reader.pid,kind,genre))
    # Extra words remain title constraints. A provider year/category ID is
    # never silently promoted to a matching title or an invented genre.
    for token in rest:
        parts.append("search LIKE ? ESCAPE '\\'")
        args.append('%'+token.replace('\\','\\\\').replace('%','\\%').replace('_','\\_')+'%')
    return ' AND '.join(parts),args


def advance(pid,kind,filename=None,cancel=lambda:False):
    """At most 128 existing payloads per transaction; no HTTP, no shared DB handle."""
    from library_index import connect
    if kind not in ('vod','series') or cancel():return False
    db=connect(filename,timeout=.05)
    if db is None:return False
    try:
        deadline=time.monotonic()+.5
        db.set_progress_handler(lambda:int(cancel() or time.monotonic()>deadline),1000)
        if db.execute("SELECT 1 FROM sqlite_master WHERE name='xcmate_genre_state'").fetchone():
            if db.execute('''SELECT 1 FROM xcmate_genre_state s JOIN catalog c USING(pid,kind)
                WHERE s.pid=? AND s.kind=? AND s.ready=1 AND s.revision IS c.revision AND s.updated=c.updated''',(pid,kind)).fetchone():return False
        db.execute('BEGIN IMMEDIATE')
        source=db.execute('SELECT revision,updated FROM catalog WHERE pid=? AND kind=?',(pid,kind)).fetchone()
        if source is None:return False
        db.execute('''CREATE TABLE IF NOT EXISTS xcmate_genre_state(pid TEXT,kind TEXT,revision TEXT,
            updated REAL,offset INTEGER,ready INTEGER,last_sid TEXT,last_cid TEXT,PRIMARY KEY(pid,kind))''')
        db.execute('''CREATE TABLE IF NOT EXISTS xcmate_genre_terms(pid TEXT,kind TEXT,term TEXT,sid TEXT,cid TEXT,
            PRIMARY KEY(pid,kind,term,sid,cid))''')
        prior=db.execute('SELECT revision,updated,offset,ready,last_sid,last_cid FROM xcmate_genre_state WHERE pid=? AND kind=?',(pid,kind)).fetchone()
        offset=0;last_sid=last_cid=''
        if prior and tuple(prior[:2])==tuple(source):
            if prior['ready']:return False
            offset=prior['offset'];last_sid=prior['last_sid'];last_cid=prior['last_cid']
        else:
            # Only this derived genre index is replaced, never source titles,
            # heads, portals, watched/resume or any other persistent user rows.
            db.execute('DELETE FROM xcmate_genre_terms WHERE pid=? AND kind=?',(pid,kind))
        view='readable_titles' if db.execute("SELECT 1 FROM sqlite_master WHERE name='readable_titles'").fetchone() else 'titles'
        rows=db.execute('SELECT sid,cid,payload FROM '+view+' WHERE pid=? AND kind=? AND (sid,cid)>(?,?) ORDER BY sid,cid LIMIT ?',
                        (pid,kind,last_sid,last_cid,BATCH)).fetchall()
        for row in rows:
            if cancel():return False
            try:values=terms(json.loads(row['payload']).get('genre'))
            except (ValueError,TypeError,AttributeError):values=[]
            db.executemany('INSERT OR IGNORE INTO xcmate_genre_terms VALUES(?,?,?,?,?)',
                           [(pid,kind,term,row['sid'],row['cid']) for term in values])
        ready=len(rows)<BATCH
        db.execute('INSERT OR REPLACE INTO xcmate_genre_state VALUES(?,?,?,?,?,?,?,?)',
                   (pid,kind,source[0],source[1],offset+len(rows),int(ready),rows[-1]['sid'] if rows else last_sid,rows[-1]['cid'] if rows else last_cid))
        if cancel():return False
        db.commit()
        from live_diagnostics import record
        if ready:record('genre_search','READY',items=offset+len(rows))
        return True
    finally:
        db.close()  # An early return/error rolls back the unfinished transaction.


def run_next(cancel=lambda:False):
    global _offset
    if cancel():return False
    from portals import get_active
    choices=[(p['id'],kind) for p in get_active() for kind in ('vod','series') if p.get('include_'+kind,True)]
    if not choices or cancel():return False
    pid,kind=choices[_offset%len(choices)];_offset+=1
    if time.monotonic()<_retry.get((pid,kind),0):return False
    try:return advance(pid,kind,cancel=cancel)
    except (sqlite3.Error,OSError,ValueError):
        _retry[pid,kind]=time.monotonic()+30
        from live_diagnostics import record
        record('genre_search','RETRY_DEFERRED')
        return False
