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
             'SOURCE_INVALID','SOURCE_LIMIT','MAPPING_CANCELLED','MAPPING_BUSY','SQLITE_INTERRUPT'}
    if code in allowed:return code
    name=getattr(error,'sqlite_errorname','')
    if name.startswith(('SQLITE_BUSY','SQLITE_LOCKED')) or isinstance(error,sqlite3.Error) and str(error) in ('database is locked','database table is locked'):return 'DB_BUSY'
    if name=='SQLITE_INTERRUPT':return 'SQLITE_INTERRUPT'
    if isinstance(error,TimeoutError):return 'SOURCE_TIMEOUT'
    if isinstance(error,InterruptedError):return 'MAPPING_CANCELLED'
    hint=str(error) if isinstance(error,ValueError) else ''
    if hint in ('PREVIEW_BYTE_BUDGET','PREVIEW_CHANNEL_BUDGET','PREVIEW_EVENT_BUDGET'):return 'SOURCE_LIMIT'
    if isinstance(error,ValueError):return 'SOURCE_INVALID' if hint not in ('SOURCE_MISSING','SOURCE_DISABLED') else 'SOURCE_UNAVAILABLE'
    return 'SOURCE_UNAVAILABLE'


_PREFIX=re.compile(r'^\s*(?:[A-Za-z]{2}|AUS)\s*[|:]\s*',re.IGNORECASE)
_QUALITY=re.compile(r'(?:uhd|hevc|fhd|hd|sd|4k|8k)[\s)\]]*$')
_DISTRIBUTION=re.compile(r'^joyn\s+|\s*\(joyn\)\s*$')
_EINS=re.compile(r'\beins\b')
_ASCII_OTHER=re.compile(r'[^a-z0-9+]')
_RESOLUTION=re.compile(r'(?<![A-Z])(UHD|FHD|HD|SD|4K|8K)\b',re.IGNORECASE)
_COUNTRY_PREFIX=re.compile(r'^\s*(DE|AT|CH)\s*[|:]\s*',re.IGNORECASE)
_COUNTRY_ID=re.compile(r'\.(DE|AT|CH)(?:@|$)',re.IGNORECASE)


def normal(value):
    text=str(value)
    if '|' in text or ':' in text:text=_PREFIX.sub('',text)
    text=text.casefold()
    if not text.isascii():text=unicodedata.normalize('NFKD',text)
    if 'joyn' in text:text=_DISTRIBUTION.sub('',text)
    text=text.rstrip()
    while text.endswith(('d','c','k',')',']')):
        shorter=_QUALITY.sub('',text)
        if shorter==text:
            break
        text=shorter.rstrip()
    if 'eins' in text:text=_EINS.sub('1',text)
    # C regex handles the common ASCII catalogue path; international letters
    # retain the previous Unicode alphanumeric semantics.
    return _ASCII_OTHER.sub('',text) if text.isascii() else ''.join(c for c in text if c.isalnum() or c=='+')


def _matches(cid,name,query,wanted):
    if not query:return True
    folded_id=str(cid).casefold()
    if folded_id==query:return True
    if not wanted:return False
    first=wanted[0]
    # Most catalogue names are ASCII. Skip normalization only when it
    # cannot produce the first required character (except eins → 1).
    name=str(name)
    if first=='1' or not name.isascii() or first in name.casefold():
        name=normal(name)
        if '+' in name and '+' not in wanted and name.split('+',1)[0]==wanted:return False
        if wanted in name:return True
    return (first=='1' or not folded_id.isascii() or first in folded_id) and wanted in normal(cid)


def matches(row,query):
    return _matches(row['id'],row.get('name',''),query.casefold(),normal(query))

def variant(name,cid=''):
    quality=_RESOLUTION.search(str(name)) or _RESOLUTION.search(str(cid))
    region=_COUNTRY_PREFIX.search(str(name)) or _COUNTRY_ID.search(str(cid))
    return quality[1].upper() if quality else '',region[1].upper() if region else ''


def rank(query):
    folded=query.casefold()
    wanted=normal(query)
    expected_quality,expected_region=variant(query,query)

    def station(cid,name):
        if not query or cid.casefold()==folded or name.casefold()==folded:return 0
        if normal(name)!=wanted:return 10
        quality,region=variant(name,cid)
        region_penalty=(0 if region==expected_region or not expected_region else 2 if not region else 4)
        quality_penalty=(0 if quality==expected_quality or not expected_quality else 1 if not quality else 2)
        return 1+region_penalty+quality_penalty

    return station


def terms(query):
    clean=normal(query)
    spaced=re.sub(r'(?<=[a-z])(?=\d)',' ',clean)
    return list(dict.fromkeys((query.casefold(),clean,spaced,re.sub(r'\b1\b','eins',spaced))))[:4]


def _deadline(db, cancel=lambda: False):
    deadline=time.monotonic()+.15
    db.set_progress_handler(lambda:int(cancel() or time.monotonic()>deadline),1000)

def _search_order(db,query):
    folded=query.casefold()
    wanted=normal(query)
    db.create_function('mapping_match482',2,lambda cid,name:int(_matches(cid,name,folded,wanted)),deterministic=True)
    if not query:return 'cid'
    db.create_function('mapping_rank',2,rank(query),deterministic=True)
    return 'mapping_rank(cid,name),cid'


def agent_search(pid, query, offset, cancel):
    from contextlib import closing
    from epg_agent100 import local_candidate
    from epg_agent_catalog103 import connect

    db = connect(local_candidate(pid))
    if db is None:
        return None  # A pre-upgrade installation can still read retained rows.
    with closing(db):
        _deadline(db, cancel)
        if cancel():
            raise MappingReadError('MAPPING_CANCELLED')
        if not query:
            rows = db.execute('SELECT cid,name,first,last FROM channels ORDER BY cid LIMIT 100 OFFSET ?', (offset,))
        else:
            # Normalized search keys are prepared once for the generation.
            # Exact CID, then exact normalized station name, then fragments.
            wanted = normal(query)
            db.create_collation('mapping_fold', lambda a, b: (a.casefold() > b.casefold()) - (a.casefold() < b.casefold()))
            rows = db.execute('''SELECT cid,name,first,last FROM channels
              WHERE cid=? COLLATE mapping_fold OR
                    (?!='' AND (instr(name_key,?) OR instr(id_key,?))
                      AND (instr(?, '+') OR instr(name_key,'+')=0
                           OR substr(name_key,1,instr(name_key,'+')-1)!=?))
              ORDER BY CASE WHEN cid=? COLLATE mapping_fold THEN 0
                            WHEN name_key=? THEN 1 ELSE 2 END,cid
              LIMIT 100 OFFSET ?''', (query,wanted,wanted,wanted,wanted,wanted,query,wanted,offset))
        result = [dict(id=cid, name=name, first=first, last=last) for cid,name,first,last in rows]
        if cancel():
            raise MappingReadError('MAPPING_CANCELLED')
        return result


def search(pid,source,query='',offset=0,cancel=lambda:False):
    from programme_index46 import connect
    from epg_binding48 import connection
    db=None
    query=str(query)[:160]
    try:
        args=(str(pid),source,max(0,int(offset)))
        if source=='agent':
            rows = agent_search(pid, query, args[2], cancel)
            if rows is not None:
                return rows
        db=connect(False)
        if db is not None:
            _deadline(db, cancel)
            if db.execute("SELECT 1 FROM sqlite_master WHERE name='source_channels48'").fetchone():
                found=db.execute('SELECT 1 FROM source_channels48 WHERE pid=? AND source_id=? LIMIT 1',(str(pid),source)).fetchone()
                if found:
                    clause = 'pid=? AND source_id=?'
                    scan_args = args[:2]
                    if query:
                        # SQLite can discard ASCII strings without the query's
                        # literal characters in order. Unicode names and exact
                        # IDs still use the full normalizer before pagination.
                        letters = ''.join(c for c in normal(query) if c != '1')[:12]
                        if len(letters) > 1 and letters.isascii():
                            pattern = '*' + '*'.join(letters) + '*'
                            clause += (" AND (cid=? COLLATE NOCASE OR length(name)!=length(CAST(name AS BLOB))"
                                       " OR length(cid)!=length(CAST(cid AS BLOB))"
                                       " OR lower(name) GLOB ? OR lower(cid) GLOB ?)")
                            scan_args += (query, pattern, pattern)
                        clause += ' AND mapping_match482(cid,name)'
                    order = _search_order(db, query)
                    rows = db.execute('SELECT cid,name FROM source_channels48 WHERE ' + clause +
                                      ' ORDER BY ' + order + ' LIMIT 100 OFFSET ?', scan_args + args[2:])
                    return [dict(id=r[0],name=r[1],first=None,last=None) for r in rows]
            db.close();db=None
        db=connection()
        if db is None:raise MappingReadError('NO_LOCAL_INDEX')
        _deadline(db, cancel)
        count=db.execute('SELECT 1 FROM guide44_inputs WHERE pid=? AND source_id=? LIMIT 1',(str(pid),source)).fetchone()
        if not count:raise MappingReadError('NO_LOCAL_INDEX')
        order=_search_order(db,query)
        rows=db.execute('SELECT cid,name FROM (SELECT DISTINCT cid,cid AS name FROM guide44_inputs WHERE pid=? AND source_id=?) '
                        'WHERE mapping_match482(cid,name) ORDER BY '+order+' LIMIT 100 OFFSET ?',args).fetchall()
        if not rows and query:raise MappingReadError('NO_LOCAL_INDEX')
        return [dict(id=r[0],name=r[0],first=None,last=None) for r in rows]
    except MappingReadError:raise
    except (sqlite3.Error,OSError,ValueError) as error:
        raise MappingReadError('MAPPING_CANCELLED' if cancel() else failure(error)) from None
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
    from epg_agent100 import SOURCE_ID, local_candidate, profile, state
    from epg_agent_catalog103 import connect as catalogue
    result = [dict(row, local_count=counts.get(row['id']),
                   local_code=code if row['id'] in counts or code!='READY' else 'NO_LOCAL_INDEX')
              for row in rows]
    for row in result:
        if row['id'] != SOURCE_ID:
            continue
        directory = profile()
        record = state(directory)
        pid = portal['id']
        receipt = record.get('portals', {}).get(str(pid), {})
        phase = record.get('code', '')
        row['local_code'] = 'READY' if row['local_count'] else 'NO_LOCAL_INDEX'
        if phase in ('IMPORTING', 'CHECKING'):
            row['local_code'] = 'IMPORTING'
        elif record.get('remote') == 'ERROR' or receipt.get('code') not in (None, 'READY', 'PARTIAL_PRESERVED'):
            row['local_code'] = 'LAST_GOOD' if receipt.get('generation') else 'SOURCE_UNAVAILABLE'
            row['source_error'] = record.get('code') if record.get('remote') == 'ERROR' else receipt['code']
        try:
            db = catalogue(local_candidate(pid, directory, record))
            if db is not None:
                try:
                    _deadline(db)
                    row['local_count'] = db.execute('SELECT channels FROM totals').fetchone()[0]
                finally:
                    db.close()
                if row['local_code'] == 'NO_LOCAL_INDEX':
                    row['local_code'] = 'READY'
        except (sqlite3.Error, OSError, ValueError) as error:
            row['local_code'] = failure(error)
    return result
