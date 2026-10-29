"""Shared, additive asset/channel references in programme_artwork.sqlite.

The existing guide and manual-choice manifests remain authoritative. Dynamic
movie covers stay dynamic: only their short-lived approved references are
stored. No global artwork job reset, profile switch, skin write or image removal.
UI consumers read exact keys; DNS, image verification and all writes are workers.
"""
import hashlib
import json
import os
import sqlite3
import time
from urllib.parse import unquote, urlsplit

_cursor = {}
_visual_revision47=0
TABLES = {
    'asset_refs47': '''CREATE TABLE IF NOT EXISTS asset_refs47(
        pid TEXT,kind TEXT,sid TEXT,role TEXT,fingerprint TEXT,data TEXT,expires REAL,
        PRIMARY KEY(pid,kind,sid,role))''',
    'channels47': '''CREATE TABLE IF NOT EXISTS channels47(
        pid TEXT,sid TEXT,canonical TEXT,data TEXT,updated REAL,PRIMARY KEY(pid,sid))''',
    'widget_diagnostics47': '''CREATE TABLE IF NOT EXISTS widget_diagnostics47(
        pid TEXT,kind TEXT,stage TEXT,data TEXT,updated REAL,PRIMARY KEY(pid,kind,stage))''',
}
COLUMNS = {
    'asset_refs47': ('pid','kind','sid','role','fingerprint','data','expires'),
    'channels47': ('pid','sid','canonical','data','updated'),
    'widget_diagnostics47': ('pid','kind','stage','data','updated'),
}


def station_image(uri):
    """Only our actual bundled placeholders are non-logos, not any tv.png."""
    if not isinstance(uri,str) or not uri:return False
    root=os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    if uri.startswith('special://home/addons/plugin.video.xtreammate/'):
        uri=os.path.join(root,uri[len('special://home/addons/plugin.video.xtreammate/'):])
    placeholders={os.path.join(root,'resources','media',name) for name in ('tv.png','vod.png','series.png')}
    placeholders.update(os.path.join(root,name) for name in ('icon.png','icon-81da1003a2753ec6.png'))
    return uri not in placeholders


def writer():
    from programme_index46 import connect
    db = connect(True)
    try:
        db.execute('SAVEPOINT assets47')
        for name, sql in TABLES.items():
            db.execute(sql)
            if tuple(r[1] for r in db.execute('PRAGMA table_info('+name+')')) != COLUMNS[name]:
                raise ValueError('UNSUPPORTED_ASSET_SCHEMA')
        db.execute('RELEASE assets47')
        return db
    except Exception:
        db.rollback()
        db.close()
        raise


def local_uri(uri):
    """Normalize Kodi/Android file paths; no network, decode or file creation."""
    if not isinstance(uri, str) or not uri or len(uri)>8192 or any(ord(c)<32 for c in uri):
        return ''
    if uri.startswith('special://'):
        try:
            import xbmcvfs
            uri = xbmcvfs.translatePath(uri)
        except (ImportError, AttributeError, RuntimeError):
            return ''
    elif uri.startswith('file:'):
        parts = urlsplit(uri)
        if parts.netloc or parts.query or parts.fragment:
            return ''
        uri = unquote(parts.path)
    if not os.path.isabs(uri) or os.path.islink(uri):
        return ''
    try:
        if os.path.isfile(uri) and 0<os.path.getsize(uri)<=3*1024*1024:
            return uri
    except OSError:
        pass
    return ''


def sources(row):
    from media_art import sources as provider
    from media_overrides43 import cached_art
    poster, fanart = provider(row)
    manual = cached_art(row)
    return {'poster': manual.get('poster') or poster, 'fanart': manual.get('fanart') or fanart}


def fingerprint(source):
    return hashlib.sha256(str(source or '').encode()).hexdigest()


def _store(pid, kind, records):
    global _visual_revision47
    from programme_index46 import encoded, report
    db = None
    try:
        db = writer()
        with db:
            changed=False
            for sid,role,fp,data in records[:128]:
                old=db.execute('SELECT fingerprint,data FROM asset_refs47 WHERE pid=? AND kind=? AND sid=? AND role=?',
                               (str(pid),kind,str(sid),role)).fetchone()
                prior=json.loads(old[1]) if old and len(old[1])<=16384 else {}
                if not old or old[0]!=fp or prior.get('uri')!=data.get('uri') or prior.get('code')!=data.get('code'):changed=True
            db.executemany('INSERT OR REPLACE INTO asset_refs47 VALUES(?,?,?,?,?,?,?)',
                [(str(pid),kind,str(sid),role,fp,encoded(data),data['until'])
                 for sid,role,fp,data in records[:128]])
        if changed:_visual_revision47+=1
        return True
    except (OSError, sqlite3.Error, ValueError) as error:
        report('art',error)
        return False
    finally:
        if db is not None:
            db.close()


def read_many(pid, kind, rows):
    """Bounded RO batches. Missing old schema means no optional references."""
    from programme_index46 import connect
    db = None
    result = {}
    try:
        db = connect(False)
        if db is None:
            return result
        deadline = time.monotonic()+.1
        db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
        by_sid = {str(r['sid']):r for r in rows}
        keys = list(by_sid)
        for offset in range(0,len(keys),64):
            chunk = keys[offset:offset+64]
            for sid,role,fp,raw,expires in db.execute(
                    'SELECT sid,role,fingerprint,data,expires FROM asset_refs47 '
                    'WHERE pid=? AND kind=? AND sid IN ('+','.join('?' for _ in chunk)+')',
                    [str(pid),kind]+chunk):
                if role not in ('poster','fanart') or expires<=time.time() or len(raw)>16384:
                    continue
                source = sources(by_sid[sid]).get(role,'')
                if not source or fingerprint(source)!=fp:
                    continue
                value = json.loads(raw)
                if not isinstance(value,dict):
                    continue
                uri = value.get('uri','')
                if value.get('mode')=='dynamic':
                    from artwork_visible import syntactic, KODI_OPTIONS
                    if not syntactic(source) or uri!=source+KODI_OPTIONS or expires-time.time()>30:
                        continue
                elif not local_uri(uri):
                    continue
                result.setdefault(sid,{})[role]=uri
        return result
    except (OSError, sqlite3.Error, ValueError, TypeError, KeyError):
        return result
    finally:
        if db is not None:
            db.close()


def prepare(portal, kind, rows, cancel=lambda:False):
    """Finite background approval, including logos beyond the old first 24.

    Existing dynamic DNS expiry and redirect policy are kept. No expired remote
    URI is admitted to a new item; Kodi remains the dynamic texture consumer.
    """
    if not rows or kind not in ('live','vod','series'):
        return
    from artwork_config import persistent
    from media_art import cached, dimensions
    from artwork_visible import public_dns, syntactic, KODI_OPTIONS, _dns_cache, _lock
    key = (str(portal['id']),kind)
    cursor = _cursor.get(key,0)%len(rows)
    cap = min(256 if kind=='live' else 24,len(rows))
    selected = [rows[(cursor+i)%len(rows)] for i in range(cap)]
    existing = read_many(portal['id'],kind,selected)
    records = []
    deadline = time.monotonic()+1
    processed = 0
    for row in selected:
        if cancel() or time.monotonic()>deadline:
            break
        processed += 1
        for role,source in sources(row).items():
            prior=existing.get(str(row['sid']),{}).get(role,'')
            if not source or prior and not prior.startswith(('http://','https://')):
                continue
            uri = local_uri(source) or local_uri(cached(source))
            value = dict(uri='',mode='local',code='NO_SOURCE',until=time.time()+30)
            if uri:
                try:
                    with open(uri,'rb') as stream:
                        width,height=dimensions(stream.read(65536))
                    if 0<width<=4096 and 0<height<=4096 and width*height<=8*1024*1024:
                        value.update(uri=uri,code='LOCAL_HEADER_VALID',until=time.time()+86400)
                except (OSError, ValueError):
                    value['code']='INVALID_LOCAL_IMAGE'
            elif not persistent() and syntactic(source):
                approved = public_dns(source)
                parts = urlsplit(source)
                with _lock:
                    dns = _dns_cache.get((parts.hostname,parts.port or (443 if parts.scheme=='https' else 80)))
                remaining = max(0,min(30,dns[0]-time.monotonic())) if dns and approved and dns[1] else 0
                value.update(uri=source+KODI_OPTIONS if remaining else '',mode='dynamic',
                    code='DYNAMIC_APPROVED' if remaining else 'DNS_UNAVAILABLE',until=time.time()+(remaining or 5))
            else:
                value['code']='PENDING_LOCAL_DOWNLOAD' if syntactic(source) else 'INVALID_SOURCE'
            records.append((row['sid'],role,fingerprint(source),value))
            if len(records)>=64:
                _store(portal['id'],kind,records)
                records=[]
    if records:
        _store(portal['id'],kind,records)
    _cursor[key]=(cursor+processed)%len(rows)
    if len(_cursor)>16:
        _cursor.pop(next(iter(_cursor)))
    from widget_diagnostics47 import note,save
    refs=read_many(portal['id'],kind,selected[:processed])
    available=[uri for values in refs.values() for uri in values.values() if uri]
    value=note(portal['id'],kind,'ASSETS','REFERENCES_READY' if available else 'NO_RENDERABLE_REFERENCE',
        selected=processed,poster_sources=sum(bool(sources(r)['poster']) for r in selected[:processed]),
        logo_sources=sum(bool(sources(r)['poster']) for r in selected[:processed]) if kind=='live' else 0,
        dynamic_images=sum(uri.startswith(('http://','https://')) for uri in available),
        local_images=sum(not uri.startswith(('http://','https://')) for uri in available))
    save(portal['id'],kind,'ASSETS',value)


def channels(portal, records):
    """Store actual canonical IDs/labels, never a new parallel guide truth."""
    from programme_index46 import encoded, report
    db = None
    try:
        db = writer()
        with db:
            db.executemany('INSERT OR REPLACE INTO channels47 VALUES(?,?,?,?,?)',
                [(str(portal['id']),str(e['sid']),str(e.get('canonical','')),
                  encoded({k:e[k] for k in ('channel','key','start','stop','source','revision') if k in e}),time.time())
                 for e in records[:64]])
    except (OSError, sqlite3.Error, ValueError, KeyError) as error:
        report('events',error)
    finally:
        if db is not None:
            db.close()


def remember_choice(pid, kind, sid, role, image):
    """Mirror an explicit Save, preserving the original SHA-named manual file.

    The common layer references an extension-correct verified display copy.
    Failure does not roll back the user's already valid legacy choice.
    """
    from media_sources43 import validate_image
    from programme_art46 import root, space, atomic
    from programme_index46 import encoded
    validate_image(image)
    digest = hashlib.sha256(image).hexdigest()
    name = 'choice47-'+digest+('.png' if image.startswith(b'\x89PNG') else '.jpg')
    filename = os.path.join(root(),name)
    if os.path.islink(filename):
        raise OSError('UNSAFE_CHOICE_REFERENCE')
    if not os.path.isfile(filename):
        space(len(image))
        atomic(filename,image)
    with open(filename,'rb') as stream:
        if hashlib.sha256(stream.read(3*1024*1024+1)).hexdigest()!=digest:
            raise ValueError('CHOICE_REFERENCE_HASH')
    db = writer()
    try:
        with db:
            db.execute('INSERT OR REPLACE INTO asset_refs47 VALUES(?,?,?,?,?,?,?)',
                (str(pid),kind,str(sid),'choice_'+('poster' if role=='replacement' else role),digest,
                 encoded(dict(uri=filename,sha256=digest,mode='manual',code='READY')),time.time()+365*86400))
    finally:
        db.close()
    return filename


def choice(pid, kind, sid, role, digest):
    from programme_index46 import connect
    db = None
    try:
        db = connect(False)
        if db is None:
            return ''
        row = db.execute('SELECT fingerprint,data FROM asset_refs47 '
                         'WHERE pid=? AND kind=? AND sid=? AND role=?',
                         (str(pid),kind,str(sid),'choice_'+role)).fetchone()
        if row and row[0]==digest and len(row[1])<16384:
            value=json.loads(row[1])
            if value.get('sha256')==digest:
                filename=local_uri(value.get('uri',''))
                if filename:
                    with open(filename,'rb') as stream:
                        if hashlib.sha256(stream.read(3*1024*1024+1)).hexdigest()==digest:return filename
    except (OSError, sqlite3.Error, ValueError, TypeError):
        pass
    finally:
        if db is not None:
            db.close()
    return ''
