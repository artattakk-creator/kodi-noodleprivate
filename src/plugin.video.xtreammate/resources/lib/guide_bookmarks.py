"""Explicit event bookmarks only; no mutation of guide/account databases."""
import hashlib,json,os,tempfile

def remember(pid,sid,event):
    return __import__('reminder_bridge89').toggle(dict(pid=str(pid),sid=str(sid),start=event['start'],stop=event['stop'],title=event['title']),wanted=True)


def entries(pid):
    from utils import addon_data_dir
    try:
        with open(os.path.join(addon_data_dir(),'guide_bookmarks_v1.json'),encoding='utf-8') as stream:values=json.load(stream)
        rows=sorted((v for v in values.values() if v.get('pid')==str(pid)),key=lambda v:v['start'])
        return annotate89(pid,rows)
    except FileNotFoundError:return []


def annotate89(pid,rows):
    import sqlite3,time
    from pathlib import Path
    from utils import addon_data_dir
    from urllib.parse import quote
    filename=Path(addon_data_dir())/'guide_timers_v1.sqlite';states={}
    if filename.is_file() and not filename.is_symlink():
        conn=None
        try:
            conn=sqlite3.connect('file:'+quote(str(filename),safe='/')+'?mode=ro',uri=True,timeout=.1)
            states=dict(conn.execute('SELECT id,state FROM timers WHERE pid=?',(str(pid),)))
        except sqlite3.Error:pass
        finally:
            if conn is not None:conn.close()
    from programme_actions88 import bookmark_id
    return [dict(row,timer_state89=states.get(bookmark_id(row),'watchlist'),aired89=row['stop']<=time.time()) for row in rows]

def status89(row):
    from localization import tr
    if row.get('aired89'):return tr(37161)
    return tr({'pending':32600,'notified':32601,'cancelled':32602,'missed':32603,'dismissed':37158,'selected':37159}.get(row.get('timer_state89'),37162))
