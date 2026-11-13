"""Read-only, bounded per-class and per-volume evidence. No writes or probes."""
import os
import time
from pathlib import Path

def roots():
    from utils import addon_data_dir
    import xbmcvfs
    root = Path(addon_data_dir())
    names = [('COVERS', 'media_art_v1'), ('PROGRAMME_EXTERNAL', 'programme_external89'),
             ('PROGRAMME_IMAGES', 'programme_images46'), ('LOGOS', 'tv_logos'),
             ('TEMP_ARTWORK', 'artwork_temporary85'), ('NORMALIZED_CACHE', 'cache'),
             ('GUIDE_BACKUPS', 'guide_backups44'), ('RESTORE_PLANS', 'widget50_plans')]
    result = [(label, root/name, True) for label, name in names]
    from artwork_backend import active_backend
    from android_artwork87 import programme_root
    for label,location in [('ACTIVE_MEDIA',active_backend('media').root),('ACTIVE_LOGOS',active_backend('logos').root),('ACTIVE_PROGRAMMES',programme_root())]:
        if '://' not in str(location) and str(location) not in {str(row[1]) for row in result}:result.append((label,Path(location),True))
    result += [('EPG_DB', root/'guide_v1.sqlite', True),
               ('EPG_METADATA', root/'programme_meta46.sqlite', True),
               ('PROGRAMME_DB', root/'programme_artwork.sqlite', True),
               ('MIGRATION_JOURNAL', root/'artwork_transfer_v1.sqlite', True)]
    for label, uri in [('KODI_THUMBNAILS', 'special://thumbnails/'),
                       ('KODI_DATABASES', 'special://database/'),
                       ('KODI_PACKAGES', 'special://home/addons/packages/'),
                       ('KODI_TEMP', 'special://temp/')]:
        result.append((label, Path(xbmcvfs.translatePath(uri)), False))
    return result

def size(path, deadline, maximum=100000):
    count = logical = allocated = 0
    todo = [Path(path)]
    complete = True
    while todo:
        if time.monotonic() > deadline or count >= maximum:
            complete = False;break
        current = todo.pop()
        if current.is_symlink():continue
        try:
            if current.is_dir():
                with os.scandir(current) as rows:
                    for row in rows:
                        if len(todo) >= maximum or time.monotonic() > deadline:complete = False;break
                        if not row.is_symlink():todo.append(Path(row.path))
            elif current.is_file():
                stat = current.stat();count += 1;logical += stat.st_size
                allocated += getattr(stat, 'st_blocks', (stat.st_size+511)//512) * 512
        except OSError:complete = False
    return dict(files=count, bytes=logical, allocated_bytes=allocated, complete=complete)

def collect(cancel=lambda: False, progress=lambda **kw: None, budget=4):
    from android_storage83 import measure, public
    deadline = time.monotonic() + max(.1, min(20, budget))
    rows = []
    for label, path, own in roots():
        if cancel():break
        current = dict(category=label, own=own, **size(path, deadline))
        try:current['volume'] = public([measure(str(path), label)])[0]
        except OSError:current['volume'] = dict(role=label, error='VOLUME_UNAVAILABLE')
        if path.suffix == '.sqlite':
            current['wal_bytes'] = Path(str(path)+'-wal').stat().st_size if Path(str(path)+'-wal').is_file() else 0
            current['shm_bytes'] = Path(str(path)+'-shm').stat().st_size if Path(str(path)+'-shm').is_file() else 0
        if path.suffix=='.sqlite' and path.exists() and not path.is_symlink():current['sqlite']=database(path)
        rows.append(current)
    return dict(at=time.time(), categories=sorted(rows, key=lambda r:r['bytes']+r.get('wal_bytes',0), reverse=True),
                measurement='READ_ONLY_NO_ANDROID_QUOTA_ASSUMPTION', android='ANDROID_NOT_TESTED')


def database(path):
    import sqlite3
    from urllib.parse import quote
    db=None;deadline=time.monotonic()+.05
    try:
        db=sqlite3.connect('file:'+quote(str(path),safe='/')+'?mode=ro',uri=True,timeout=.02)
        db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
        value={name:db.execute('PRAGMA '+name).fetchone()[0] for name in ('page_size','page_count','freelist_count','auto_vacuum')}
        try:value['tables']=[dict(name=row[0],allocated_bytes=row[1]) for row in db.execute('SELECT name,sum(pgsize) FROM dbstat GROUP BY name ORDER BY sum(pgsize) DESC LIMIT 32')]
        except sqlite3.Error:value['tables_status']='DBSTAT_UNAVAILABLE_OR_BUDGET'
        value['quota']='ANDROID_QUOTA_UNKNOWN';return value
    except sqlite3.Error:return dict(code='SQLITE_BUSY_OR_BUDGET')
    finally:
        if db is not None:db.close()
