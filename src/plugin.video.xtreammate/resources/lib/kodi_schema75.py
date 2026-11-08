"""Explicit worker-only, bounded read-only Kodi video-library diagnosis."""
import os,re,sqlite3,time
from urllib.parse import quote

def inspect():
    import xbmcvfs
    directory=xbmcvfs.translatePath('special://database/')
    try:
        names=[n for n in os.listdir(directory) if re.fullmatch(r'MyVideos\d+\.db',n)]
        if not names:return dict(code='KODI_LIBRARY_NOT_FOUND',missing=[])
        # Kodi 21 uses schema 131. Never inspect an unrelated newer database
        # left by another Kodi version and call it this installation's library.
        if 'MyVideos131.db' not in names:return dict(code='KODI_LIBRARY_VERSION_UNVERIFIED',missing=[],read_only=True)
        name='MyVideos131.db';path=os.path.join(directory,name)
        if os.path.islink(path):return dict(code='UNSAFE_DATABASE_PATH',missing=[])
        db=sqlite3.connect('file:'+quote(path,safe='/')+'?mode=ro',uri=True,timeout=.05)
        try:
            db.execute('PRAGMA query_only=ON');end=time.monotonic()+.5
            db.set_progress_handler(lambda:int(time.monotonic()>end),1000)
            views={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='view'")}
            missing=sorted({'movie_view','tvshow_view','musicvideo_view'}-views)
            integrity=db.execute('PRAGMA integrity_check(1)').fetchone()
            known={'movie','tvshow','musicvideo','episode','files','path','version'}
            tables=sorted(r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'") if r[0] in known)
            queries={}
            for view in ('movie_view','tvshow_view','musicvideo_view'):
                if view not in views:queries[view]='MISSING_VIEW';continue
                try:db.execute('SELECT * FROM '+view+' LIMIT 0');queries[view]='QUERY_VALID'
                except sqlite3.Error:queries[view]='QUERY_FAILED'
            actual_version=None
            if 'version' in tables:
                try:
                    row=db.execute('SELECT idVersion FROM version LIMIT 1').fetchone()
                    if row and type(row[0]) is int:actual_version=row[0]
                except sqlite3.Error:pass
            code=('KODI_LIBRARY_MISSING_VIEWS' if missing else 'KODI_LIBRARY_QUERY_ERROR' if 'QUERY_FAILED' in queries.values() else 'KODI_LIBRARY_VERSION_MISMATCH' if actual_version not in (None,131) else 'READY' if integrity and integrity[0]=='ok' else 'KODI_LIBRARY_INTEGRITY_ERROR')
            return dict(code=code,missing=missing,version=int(name[8:-3]),read_only=True,tables=tables,queries=queries,stored_schema_version=actual_version,integrity='OK' if integrity and integrity[0]=='ok' else 'FAILED')
        finally:db.close()
    except (OSError,sqlite3.Error,ValueError):return dict(code='KODI_LIBRARY_READ_UNAVAILABLE',missing=[],read_only=True)
