"""Read-only refresh authorization. A schema marker is not a verified backup."""
import json,os,sqlite3,time
from urllib.parse import quote


def access(filename):
    from guide_publish44 import access as schema_access
    state=schema_access(filename)
    if state!='READY':return state
    db=None
    try:
        db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.05)
        db.execute('PRAGMA query_only=ON');db.execute('BEGIN')
        end=time.monotonic()+.05;db.set_progress_handler(lambda:int(time.monotonic()>end),1000)
        if not db.execute('SELECT 1 FROM programmes LIMIT 1').fetchone():return 'READY'
        row=db.execute("SELECT backup_sha FROM guide44_authorization WHERE kind='VERIFIED_BACKUP' ORDER BY created DESC LIMIT 1").fetchone()
        if not row or len(row[0])!=64 or any(c not in '0123456789abcdef' for c in row[0]):return 'BACKUP_REQUIRED'
        # Verified authorizations are written only after SQLite backup,
        # quick_check, SHA and unchanged source checks. Revalidate the local
        # receipt and file size without hashing a multi-GB guide on the GUI.
        folder=os.path.join(os.path.dirname(filename),'guide_backups44')
        if os.path.islink(folder):return 'BACKUP_REQUIRED'
        with os.scandir(folder) as entries:
            for number,entry in enumerate(entries):
                if number>=128 or time.monotonic()>end:return 'BACKUP_REQUIRED'
                if not entry.name.endswith('.sqlite.json') or entry.is_symlink():continue
                if entry.stat().st_size>4096:continue
                with open(entry.path,encoding='utf-8') as f:value=json.load(f)
                target=os.path.join(folder,entry.name[:-5])
                if (value.get('code')=='BACKUP_VERIFIED' and value.get('sha256')==row[0]
                        and value.get('backup')==os.path.basename(target) and not os.path.islink(target)
                        and os.path.getsize(target)==value.get('bytes')):return 'READY'
        return 'BACKUP_REQUIRED'
    except (OSError,sqlite3.Error,ValueError,TypeError):return 'BACKUP_REQUIRED'
    finally:
        if db is not None:db.close()
