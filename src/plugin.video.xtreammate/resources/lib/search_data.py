"""Worker-only local search; same group filters and guide aliases as the grid."""
import json
import os
import sqlite3
import time
from urllib.parse import quote

KINDS=('live','vod','series')
PAGE=48


def _short_client(portal):
    # Constructing an adapter does not authenticate or fetch. Only cache-only
    # short EPG is read below, just as in the current-time guide viewport.
    if portal.get('type')=='xtream':
        from xtream import XtreamClient
        return XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
    return None


def _now_events(pid,identifiers,now):
    from guide_store import path
    events={};aliases={};db=None;code='NO_EPG';sources=set()
    if not os.path.exists(path()):return events,aliases,code,0
    try:
        db=sqlite3.connect('file:'+quote(path(),safe='/')+'?mode=ro',uri=True,timeout=.075)
        db.row_factory=sqlite3.Row;db.execute('PRAGMA query_only=ON')
        deadline=time.monotonic()+1
        db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
        ids=sorted(identifiers)
        for offset in range(0,len(ids),256):
            chunk=ids[offset:offset+256];marks=','.join('?' for _ in chunk)
            aliases.update(db.execute('SELECT alias,cid FROM guide_alias WHERE pid=? AND alias IN ('+marks+')',[pid]+chunk))
        ids=sorted({aliases.get(ident,ident) for ident in identifiers})
        examined=0
        for offset in range(0,len(ids),256):
            chunk=ids[offset:offset+256];marks=','.join('?' for _ in chunk)
            # No descriptions/full guide hydration, and unrelated channels cannot
            # consume a global result limit before a selected channel is seen.
            cursor=db.execute('SELECT cid,title,source,start FROM programmes WHERE pid=? AND cid IN ('+marks+') AND start<=? AND stop>? ORDER BY source,start DESC',[pid]+chunk+[now,now])
            for row in cursor:
                examined+=1
                if examined>100000:raise ValueError('SEARCH_GUIDE_LIMIT')
                events.setdefault(row['cid'],dict(row));sources.add(row['source'])
        code='READY' if events else 'NO_CURRENT_EPG'
    except (sqlite3.Error,OSError,ValueError):events={};aliases={};code='EPG_UNAVAILABLE';sources.clear()
    finally:
        if db is not None:db.close()
    return events,aliases,code,len(sources)


def live_matches(portal,query,reader,now):
    from library_index import normalized
    from epg_sources import configuration
    where='pid=? AND kind=?'+reader._filter('live')
    raw=reader._query('SELECT payload FROM titles WHERE '+where+' GROUP BY sid ORDER BY ordinal LIMIT 50001',
                      (portal['id'],'live'),'live')
    if len(raw)>50000:raise ValueError('SEARCH_CHANNEL_LIMIT')
    channels=[json.loads(r['payload']) for r in raw]
    mappings=configuration(portal['id']).get('mappings',{})
    def ids(row):
        manual=mappings.get(row['sid'])
        return [str(manual)] if manual else [row['sid'],str(row.get('epg_channel_id') or '')]
    identifiers={ident for row in channels for ident in ids(row) if ident}
    events,aliases,code,source_count=_now_events(portal['id'],identifiers,now)
    tokens=list(dict.fromkeys(normalized(query).split()));result=[]
    counts=dict(channels=len(channels),now_count=0,xml_now=0,short_now=0,manual_count=0,
                manual_missing=0,alias_count=0,name_hits=0,programme_hits=0,source_count=source_count)
    client=None;client_checked=False;deadline=time.monotonic()+2;partial=False
    for row in channels:
        manual=bool(mappings.get(row['sid']));counts['manual_count']+=int(manual)
        keys=ids(row);counts['alias_count']+=int(any(aliases.get(k,k)!=k for k in keys))
        event=next((events[aliases.get(ident,ident)] for ident in keys if ident and aliases.get(ident,ident) in events),None)
        title=event['title'] if event else ''
        if title:counts['xml_now']+=1
        elif manual:counts['manual_missing']+=1  # Never override an explicit mapping.
        elif not partial:
            if time.monotonic()>deadline:partial=True
            else:
                if not client_checked:client=_short_client(portal);client_checked=True
                if client is not None:
                    from epg_views import cached_short_guide
                    short=cached_short_guide(client,row['sid'],now=now)
                    title=short.get('now','')
                    if title:counts['short_now']+=1
        if title:counts['now_count']+=1
        channel_name=normalized(row.get('name',''));programme_name=normalized(title)
        name=all(t in channel_name for t in tokens)
        programme=bool(title and all(t in programme_name for t in tokens))
        counts['name_hits']+=int(name);counts['programme_hits']+=int(programme)
        if name or programme:result.append(dict(row,_now_title=title if programme else '',_now_match=programme))
    if partial:code='EPG_PARTIAL'
    elif counts['now_count'] and code!='EPG_UNAVAILABLE':code='READY'
    from live_diagnostics import record
    record('epg_search',code,matched=len(result),**counts)
    # One anonymous line makes a user-provided Kodi log actionable too.
    try:
        import xbmc
        xbmc.log('[XCMate][SEARCH_EPG] '+json.dumps(dict(code=code,matched=len(result),**counts),sort_keys=True),xbmc.LOGINFO)
    except (ImportError,AttributeError,RuntimeError):pass
    return result,code



def search(portal,query,kind='vod',offset=0,now=None):
    from library_index import Reader,IndexReadError
    from catalog_sync import request
    reader=Reader(portal['id'],timeout=.15,query_seconds=1)
    query=str(query).strip()[:200];result={}
    for section in KINDS:
        if not portal.get('include_'+section,True):
            result[section]=dict(rows=[],total=0,code='DISABLED');continue
        start=max(0,offset) if section==kind else 0
        try:
            state=reader.state(section)
            if not state:
                request(portal,section,portal.get('start_group_id','') if section=='live' else '',priority=5)
                result[section]=dict(rows=[],total=None,code='INDEX_PENDING');continue
            if section=='live':
                rows,code=live_matches(portal,query,reader,int(time.time() if now is None else now))
                total=len(rows);rows=rows[start:start+PAGE]
            else:rows,total=reader.page(section,query,offset=start,limit=PAGE);code='READY'
            result[section]=dict(rows=rows,total=total,code=code)
        except (IndexReadError,sqlite3.Error,OSError,ValueError):
            result[section]=dict(rows=[],total=None,code='INDEX_ERROR')
    return result
