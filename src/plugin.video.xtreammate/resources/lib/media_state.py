"""Separate ID-only favourites/progress. Never rewrites legacy live favourites."""
import json
import math
import os
import time


def key(pid,kind,sid):
    return json.dumps([str(pid),str(kind),str(sid)],separators=(',',':'))


def path():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'media_state_v1.sqlite')


def _db(timeout=2):
    import sqlite3
    db=sqlite3.connect(path(),timeout=timeout)
    db.executescript('CREATE TABLE IF NOT EXISTS favourites(ident TEXT PRIMARY KEY);'
                     'CREATE TABLE IF NOT EXISTS progress(ident TEXT PRIMARY KEY,payload TEXT);')
    return db


def read():
    db=_db()
    try:
        return {'version':1,'favourites':[r[0] for r in db.execute('SELECT ident FROM favourites')],
                'progress':{r[0]:json.loads(r[1]) for r in db.execute('SELECT ident,payload FROM progress')}}
    finally: db.close()


def favourite(pid,kind,sid):
    db=_db()
    try: return db.execute('SELECT 1 FROM favourites WHERE ident=?',(key(pid,kind,sid),)).fetchone() is not None
    finally: db.close()


def toggle(pid,kind,sid,item=None):
    ident=key(pid,kind,sid);db=_db()
    try:
        db.execute('BEGIN IMMEDIATE')
        exists=db.execute('SELECT 1 FROM favourites WHERE ident=?',(ident,)).fetchone()
        db.execute('DELETE FROM favourites WHERE ident=?' if exists else 'INSERT INTO favourites VALUES(?)',(ident,))
        if not exists and item:
            db.execute('CREATE TABLE IF NOT EXISTS favourite_items(ident TEXT PRIMARY KEY,payload TEXT)')
            db.execute('INSERT OR REPLACE INTO favourite_items VALUES(?,?)',(ident,json.dumps(item)))
        db.commit()
        return not bool(exists)
    finally: db.close()


def progress_key(pid,kind,sid,series_id='',season=''):
    return key(pid,kind,sid) if kind!='episode' else json.dumps(
        [str(pid),kind,str(series_id),str(season),str(sid)],separators=(',',':'))


def progress(pid,kind,sid,series_id='',season=''):
    db=_db()
    try:
        row=db.execute('SELECT payload FROM progress WHERE ident=?',
                       (progress_key(pid,kind,sid,series_id,season),)).fetchone()
        return json.loads(row[0]) if row else {}
    finally: db.close()


def save_progress(session,position,duration,timeout=2):
    if session.get('kind') not in ('vod','episode','series_item'): return False
    if session['kind']=='episode' and not all(k in session for k in ('series_id','season')): return False
    if not all(isinstance(v,(float,int)) and math.isfinite(v) for v in (position,duration)): return False
    if position<60 or duration<60 or position>duration+2: return False
    watched=position/duration>=.9 or (duration-position<=120 and position/duration>=.5)
    fields={k:str(session[k]) for k in ('pid','kind','sid','series_id','season','episode') if k in session}
    fields.update(position=min(position,duration),duration=duration,watched=watched,updated=time.time())
    ident=progress_key(session['pid'],session['kind'],session['sid'],session.get('series_id',''),session.get('season',''))
    db=_db(timeout=timeout)
    try:
        with db: db.execute('INSERT OR REPLACE INTO progress VALUES(?,?)',(ident,json.dumps(fields)))
    finally: db.close()
    return True


def resume_position(value):
    p=value.get('position',0);d=value.get('duration',0)
    if value.get('watched') or not all(isinstance(v,(int,float)) and math.isfinite(v) for v in (p,d)):
        return 0
    return p if 60<=p<d-30 else 0


def mark_episode(pid,episode,watched=None):
    ident=progress_key(pid,'episode',episode['sid'],episode['series_id'],episode['season'])
    db=_db()
    try:
        with db:
            if watched is None:
                db.execute('DELETE FROM progress WHERE ident=?',(ident,))
            else:
                row=db.execute('SELECT payload FROM progress WHERE ident=?',(ident,)).fetchone()
                value=json.loads(row[0]) if row else {}
                value.update(watched=bool(watched),updated=time.time())
                db.execute('INSERT OR REPLACE INTO progress VALUES(?,?)',(ident,json.dumps(value)))
    finally: db.close()


def rail_items(pid,kind,reader,rail='favourites'):
    """Local ID-based rails; ended playback never changes favourites."""
    state=read();ids=[]
    if rail=='favourites':
        ids=[json.loads(k)[2] for k in state['favourites'] if json.loads(k)[:2]==[str(pid),kind]]
    else:
        pairs=sorted(state['progress'].items(),key=lambda pair:pair[1].get('updated',0),reverse=True)
        for ident,value in pairs:
            fields=json.loads(ident)
            if fields[0]!=str(pid) or not resume_position(value): continue
            if kind=='vod' and fields[1]=='vod': ids.append(fields[2])
            elif kind=='series' and fields[1]=='series_item': ids.append(fields[2])
            elif kind=='series' and fields[1]=='episode' and len(fields)==5: ids.append(fields[2])
    suppressed=set()
    if rail=='continue' and kind=='vod':
        from media_continue import hidden
        suppressed=hidden(pid)
    rows=[];db=_db()
    try:
        db.execute('CREATE TABLE IF NOT EXISTS favourite_items(ident TEXT PRIMARY KEY,payload TEXT)')
        for sid in dict.fromkeys(ids):
            if sid in suppressed:continue
            item=reader.get(kind,sid)
            if item:
                if rail=='favourites':
                    with db: db.execute('INSERT OR REPLACE INTO favourite_items VALUES(?,?)',(key(pid,kind,sid),json.dumps(item)))
            elif rail=='favourites':
                saved=db.execute('SELECT payload FROM favourite_items WHERE ident=?',(key(pid,kind,sid),)).fetchone()
                from localization import tr
                item=json.loads(saved[0]) if saved else dict(sid=sid,kind=kind,name=tr(32666))
                item=dict(item,_unavailable=True)
            if item: rows.append(item)
    finally: db.close()
    return rows
