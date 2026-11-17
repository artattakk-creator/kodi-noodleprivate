"""Bounded local source catalogue and suggestions; never fetches a feed."""
import re
import sqlite3
import time
import unicodedata


class MappingReadError(OSError):
    def __init__(self,code):self.code=code;super().__init__(code)


def failure(error):
    code=getattr(error,'code','')
    allowed={'DB_BUSY','SOURCE_TIMEOUT','SOURCE_UNAVAILABLE','NO_LOCAL_INDEX','NO_PROGRAMMES',
             'SOURCE_INVALID','SOURCE_LIMIT','MAPPING_CANCELLED','MAPPING_BUSY'}
    if code in allowed:return code
    name=getattr(error,'sqlite_errorname','')
    if name in ('SQLITE_BUSY','SQLITE_LOCKED') or isinstance(error,sqlite3.Error) and str(error) in ('database is locked','database table is locked'):return 'DB_BUSY'
    if name=='SQLITE_INTERRUPT' or isinstance(error,TimeoutError):return 'SOURCE_TIMEOUT'
    if isinstance(error,InterruptedError):return 'MAPPING_CANCELLED'
    hint=str(error) if isinstance(error,ValueError) else ''
    if hint in ('PREVIEW_BYTE_BUDGET','PREVIEW_CHANNEL_BUDGET','PREVIEW_EVENT_BUDGET'):return 'SOURCE_LIMIT'
    if isinstance(error,ValueError):return 'SOURCE_INVALID' if hint not in ('SOURCE_MISSING','SOURCE_DISABLED') else 'SOURCE_UNAVAILABLE'
    return 'SOURCE_UNAVAILABLE'


_PREFIX=re.compile(r'^\s*[A-Za-z]{2}\s*[|:]\s*')
_QUALITY=re.compile(r'(?:uhd|hevc|fhd|hd|sd|4k|8k)\s*$')
_EINS=re.compile(r'\beins\b')
_ASCII_OTHER=re.compile(r'[^a-z0-9+]')


def normal(value):
    text=str(value)
    if '|' in text or ':' in text:text=_PREFIX.sub('',text)
    text=text.casefold()
    if not text.isascii():text=unicodedata.normalize('NFKD',text)
    text=_QUALITY.sub('',text)
    if 'eins' in text:text=_EINS.sub('1',text)
    # C regex handles the common ASCII catalogue path; international letters
    # retain the previous Unicode alphanumeric semantics.
    return _ASCII_OTHER.sub('',text) if text.isascii() else ''.join(c for c in text if c.isalnum() or c=='+')


def _matches(cid,name,query,wanted):
    if not query:return True
    if str(cid).casefold()==query:return True
    name=normal(name)
    if '+' in name and '+' not in wanted and name.split('+',1)[0]==wanted:return False
    return bool(wanted and (wanted in name or wanted in normal(cid)))


def matches(row,query):
    return _matches(row['id'],row.get('name',''),query.casefold(),normal(query))


def terms(query):
    clean=normal(query)
    spaced=re.sub(r'(?<=[a-z])(?=\d)',' ',clean)
    return list(dict.fromkeys((query.casefold(),clean,spaced,re.sub(r'\b1\b','eins',spaced))))[:4]


def _deadline(db):
    deadline=time.monotonic()+.15
    db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)


def search(pid,source,query='',offset=0):
    from programme_index46 import connect
    from epg_binding48 import connection
    db=None
    try:
        db=connect(False)
        if db is not None:
            _deadline(db)
            if db.execute("SELECT 1 FROM sqlite_master WHERE name='source_channels48'").fetchone():
                count=db.execute('SELECT count(*) FROM source_channels48 WHERE pid=? AND source_id=?',(str(pid),source)).fetchone()[0]
                if count:
                    # Apply the same normalizer before pagination. Raw-text SQL
                    # filtering loses accents/punctuation and can spend its cap
                    # on excluded +1 channels before the first valid result.
                    query=str(query)[:160];folded=query.casefold();wanted=normal(query)
                    db.create_function('mapping_match482',2,
                        lambda cid,name:int(_matches(cid,name,folded,wanted)),deterministic=True)
                    rows=db.execute('SELECT cid,name FROM source_channels48 WHERE pid=? AND source_id=? AND mapping_match482(cid,name) ORDER BY cid LIMIT 100 OFFSET ?',
                        (str(pid),source,max(0,int(offset))))
                    return [dict(id=r[0],name=r[1],first=None,last=None) for r in rows]
            db.close();db=None
        db=connection()
        if db is None:raise MappingReadError('NO_LOCAL_INDEX')
        _deadline(db)
        count=db.execute('SELECT 1 FROM guide44_inputs WHERE pid=? AND source_id=? LIMIT 1',(str(pid),source)).fetchone()
        if not count:raise MappingReadError('NO_LOCAL_INDEX')
        rows=db.execute('SELECT DISTINCT cid FROM guide44_inputs WHERE pid=? AND source_id=? AND instr(lower(cid),lower(?))>0 ORDER BY cid LIMIT 100 OFFSET ?',
                        (str(pid),source,str(query)[:160],max(0,int(offset)))).fetchall()
        if not rows and query:raise MappingReadError('NO_LOCAL_INDEX')
        return [dict(id=r[0],name=r[0],first=None,last=None) for r in rows]
    except MappingReadError:raise
    except (sqlite3.Error,OSError,ValueError) as error:raise MappingReadError(failure(error)) from None
    finally:
        if db is not None:db.close()


def source_rows(portal):
    from epg_binding48 import sources,connection
    from programme_index46 import connect
    rows=sources(portal);counts={};code='NO_LOCAL_INDEX';db=None
    try:
        db=connect(False)
        if db is not None:
            _deadline(db)
            if db.execute("SELECT 1 FROM sqlite_master WHERE name='source_channels48'").fetchone():
                counts=dict(db.execute('SELECT source_id,count(*) FROM source_channels48 WHERE pid=? GROUP BY source_id LIMIT 129',(str(portal['id']),)))
                code='READY'
        if any(row['id'] not in counts for row in rows):
            if db is not None:db.close();db=None
            db=connection()
            if db is not None:
                _deadline(db)
                for identity,count in db.execute('SELECT source_id,count(DISTINCT cid) FROM guide44_inputs WHERE pid=? GROUP BY source_id LIMIT 129',(str(portal['id']),)):
                    counts.setdefault(identity,count)
                code='READY'
    except (sqlite3.Error,OSError,ValueError) as error:code=failure(error)
    finally:
        if db is not None:db.close()
    return [dict(row,local_count=counts.get(row['id']),local_code=code if row['id'] in counts else code if code!='READY' else 'NO_LOCAL_INDEX') for row in rows]
