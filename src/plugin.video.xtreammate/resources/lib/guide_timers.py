"""ID-based notification timers; no automatic tune, recording or wake promise."""
import hashlib
import json
import os
import sqlite3
import time


def db():
    from utils import addon_data_dir
    conn=sqlite3.connect(os.path.join(addon_data_dir(),'guide_timers_v1.sqlite'),timeout=2)
    conn.row_factory=sqlite3.Row
    conn.execute('''CREATE TABLE IF NOT EXISTS timers(id TEXT PRIMARY KEY,pid TEXT,sid TEXT,
      channel TEXT,title TEXT,start INTEGER,stop INTEGER,notify_at INTEGER,state TEXT)''')
    return conn


def add(pid,sid,channel,event,minutes=5):
    start,stop=int(event['start']),int(event['stop'])
    if stop<=start or start<=time.time(): return False
    ident=hashlib.sha256(json.dumps([str(pid),str(sid),start,stop]).encode()).hexdigest()
    conn=db()
    try:
        with conn:
            conn.execute('INSERT OR IGNORE INTO timers VALUES(?,?,?,?,?,?,?,?,?)',
              (ident,str(pid),str(sid),str(channel)[:160],str(event['title'])[:512],start,stop,
               start-max(0,min(int(minutes),60))*60,'pending'))
    finally: conn.close()
    return True


def list_timers(pid):
    conn=db()
    try: return [dict(r) for r in conn.execute('SELECT * FROM timers WHERE pid=? ORDER BY start',(str(pid),))]
    finally: conn.close()


def cancel(ident):
    conn=db()
    try:
        with conn: conn.execute("UPDATE timers SET state='cancelled' WHERE id=? AND state='pending'",(ident,))
    finally: conn.close()


def poll(now=None,notify=None):
    import xbmcgui
    now=int(time.time() if now is None else now)
    conn=db()
    try:
        conn.execute('BEGIN IMMEDIATE')
        conn.execute("UPDATE timers SET state='missed' WHERE state='pending' AND stop<=?",(now,))
        due=[dict(r) for r in conn.execute("SELECT * FROM timers WHERE state='pending' AND notify_at<=? AND stop>? LIMIT 20",(now,now))]
        conn.executemany("UPDATE timers SET state='notified' WHERE id=?",[(r['id'],) for r in due])
        conn.execute('DELETE FROM timers WHERE stop<?',(now-30*86400,))
        conn.commit()
    finally: conn.close()
    # Persist the claim BEFORE notifying: at most once across service restarts.
    for row in due:
        message=row['channel']+' · '+row['title']+' · '+time.strftime('%H:%M',time.localtime(row['start']))
        if notify: notify(message)
        else: xbmcgui.Dialog().notification('XCMate · Erinnerung',message,time=8000)


def manage(pid):
    import xbmcgui
    rows=list_timers(pid)
    selected=xbmcgui.Dialog().select('XCMate · Erinnerungen',[
        '{} · {} · {}'.format(r['state'],time.strftime('%d.%m. %H:%M',time.localtime(r['start'])),r['title']) for r in rows])
    if 0<=selected<len(rows) and rows[selected]['state']=='pending' and xbmcgui.Dialog().yesno('XCMate','Erinnerung stornieren?'):
        cancel(rows[selected]['id'])
