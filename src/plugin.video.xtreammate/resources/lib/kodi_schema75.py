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
            return dict(code='KODI_LIBRARY_MISSING_VIEWS' if missing else 'READY' if integrity and integrity[0]=='ok' else 'KODI_LIBRARY_INTEGRITY_ERROR',missing=missing,version=int(name[8:-3]),read_only=True)
        finally:db.close()
    except (OSError,sqlite3.Error,ValueError):return dict(code='KODI_LIBRARY_READ_UNAVAILABLE',missing=[],read_only=True)
