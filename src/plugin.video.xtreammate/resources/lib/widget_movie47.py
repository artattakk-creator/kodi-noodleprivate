"""One pinned RO movie transaction; bounded SQL work, no import-time deadline.

.46 starts a .75s clock before optional imports/group-policy reads and reconnects
for every query. Android can exhaust that clock before executing GROUPS. Here
only actual SQL work consumes the .35s total/.15s statement budget. Native
window owners never run this reader; it has no HTTP/import/rebuild path.
"""
import os
import sqlite3
import time
from urllib.parse import quote
from widget_data41 import WidgetReader
from library_index import IndexReadError, path


def cold_read(portal):
    """Concurrent cache publication does not lock the read-only movie catalog.

    Used only when no valid LastGood exists. Never publish without the cache
    lease, and never wait for its owner or start an importer.
    """
    reader=MovieReader(portal['id'])
    try:
        if reader.state('vod') is None:return [],'INDEX_MISSING'
        return reader.small('vod',limit=24),'READY'
    except (IndexReadError,OSError,ValueError,sqlite3.Error) as error:
        return [],getattr(error,'code','UNAVAILABLE')
    finally:reader.close()


class MovieReader(WidgetReader):
    def __init__(self,pid,filename=None,kind='vod'):
        super().__init__(pid)
        self.filename=filename
        self.kind47=kind
        self._connection47=None
        self._selected47=None
        self._remaining47=.35
        self.stats47={}

    def _query(self,sql,args=(),kind=None):
        self.stage46=('STATE' if 'FROM catalog' in sql else 'GROUPS' if 'FROM groups' in sql and 'EXISTS' not in sql else
                      'HEADS' if 'SELECT cid FROM heads' in sql else 'LEGACY_PRESENCE' if 'EXISTS(SELECT 1 FROM titles' in sql else
                      'V2_KEYS' if 'SELECT i.sid,i.cid' in sql else 'LEGACY_KEYS' if 'SELECT t.sid,t.cid' in sql else 'PAYLOAD')
        started=None
        try:
            if self._connection47 is None:
                filename=self.filename or path()
                if not os.path.isfile(filename):return []
                self._connection47=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.02)
                self._connection47.row_factory=sqlite3.Row
                self._connection47.execute('PRAGMA temp_store=MEMORY')
                self._connection47.execute('BEGIN')
            db=self._connection47
            if self._remaining47<=0:raise sqlite3.OperationalError('interrupted')
            started=time.monotonic()
            deadline=started+min(.15,self._remaining47)
            db.set_progress_handler(lambda:int(time.monotonic()>=deadline),1000)
            if kind is not None:
                selection=tuple(sorted(self._selections[kind]))
                if selection!=self._selected47:
                    db.execute('CREATE TEMP TABLE IF NOT EXISTS selected_categories(cid TEXT PRIMARY KEY)')
                    db.execute('DELETE FROM selected_categories')
                    db.executemany('INSERT INTO selected_categories VALUES(?)',[(cid,) for cid in selection])
                    self._selected47=selection
            rows=[dict(r) for r in db.execute(sql,args)]
            prior=self.stats47.setdefault(self.stage46,dict(rows=0,queries=0,query_ms=0))
            prior['rows']+=len(rows);prior['queries']+=1;prior['query_ms']+=int((time.monotonic()-started)*1000)
            return rows
        except sqlite3.Error as exc:
            name=getattr(exc,'sqlite_errorname','SQLITE_UNKNOWN')
            if not isinstance(name,str) or not name.startswith('SQLITE_') or not name.replace('_','').isalnum():name='SQLITE_UNKNOWN'
            code='BUDGET' if self._remaining47<=0 or name=='SQLITE_INTERRUPT' else name
            error=IndexReadError(code);error.code=code;error.stage46=self.stage46
            raise error from None
        finally:
            if started is not None:self._remaining47-=max(0,time.monotonic()-started)

    def close(self):
        from widget_diagnostics47 import note
        for stage,values in self.stats47.items():
            note(self.pid,self.kind47,'SQL_'+stage,selected=values['rows'],queries=values['queries'],query_ms=values['query_ms'])
        if self._connection47 is not None:
            self._connection47.close()
            self._connection47=None
