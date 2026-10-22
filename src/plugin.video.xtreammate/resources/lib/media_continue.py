"""Portal-local Continue suppression; independent of progress and favourites."""
import os,sqlite3
from urllib.parse import quote


def path():
    from utils import addon_data_dir
    return os.path.join(addon_data_dir(),'media_continue_hidden_v1.sqlite')


def hidden(pid):
    if not os.path.exists(path()):return set()
    db=sqlite3.connect('file:'+quote(path(),safe='/')+'?mode=ro',uri=True,timeout=.05)
    try:return {row[0] for row in db.execute('SELECT sid FROM hidden WHERE pid=?',(str(pid),))}
    finally:db.close()


def hide(pid,sid):
    db=sqlite3.connect(path(),timeout=.2)
    try:
        with db:
            db.execute('CREATE TABLE IF NOT EXISTS hidden(pid TEXT,sid TEXT,PRIMARY KEY(pid,sid))')
            db.execute('INSERT OR IGNORE INTO hidden VALUES(?,?)',(str(pid),str(sid)))
    finally:db.close()


def reveal(pid,sid):
    if not os.path.exists(path()):return
    db=sqlite3.connect(path(),timeout=.2)
    try:
        with db:db.execute('DELETE FROM hidden WHERE pid=? AND sid=?',(str(pid),str(sid)))
    finally:db.close()
