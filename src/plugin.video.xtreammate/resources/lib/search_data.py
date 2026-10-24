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


class LiveSearch:
    """Worker-owned bounded slices; incomplete caches never become final zeroes."""
    def __init__(self,portal,query,reader,now,correlation=''):
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
        self.portal=portal;self.query=query;self.now=now;self.channels=channels
        self.mappings=mappings;self.events=events;self.aliases=aliases;self.code=code
        self.tokens=tokens;self.result=result;self.counts=counts;self.position=0
        self.client=None;self.client_checked=False
        self.correlation=correlation if len(correlation)==32 and all(c in '0123456789abcdef' for c in correlation) else ''

    @property
    def done(self):return self.position>=len(self.channels)

    def step(self,budget=.2):
        from library_index import normalized
        deadline=time.monotonic()+budget;processed=0
        while not self.done:
            row=self.channels[self.position];self.position+=1;processed+=1
            manual=self.mappings.get(row['sid']);self.counts['manual_count']+=int(bool(manual))
            keys=[str(manual)] if manual else [row['sid'],str(row.get('epg_channel_id') or '')]
            self.counts['alias_count']+=int(any(self.aliases.get(k,k)!=k for k in keys))
            event=next((self.events[self.aliases.get(k,k)] for k in keys if k and self.aliases.get(k,k) in self.events),None)
            title=event['title'] if event else ''
            if title:self.counts['xml_now']+=1
            elif manual:self.counts['manual_missing']+=1
            else:
                if not self.client_checked:self.client=_short_client(self.portal);self.client_checked=True
                if self.client is not None:
                    from epg_views import cached_short_guide
                    title=cached_short_guide(self.client,row['sid'],now=self.now).get('now','')
                    if title:self.counts['short_now']+=1
            if title:self.counts['now_count']+=1
            name=all(t in normalized(row.get('name','')) for t in self.tokens)
            programme=bool(title and all(t in normalized(title) for t in self.tokens))
            self.counts['name_hits']+=int(name);self.counts['programme_hits']+=int(programme)
            if name or programme:self.result.append(dict(row,_now_title=title if programme else '',_now_match=programme))
            if processed>=64 or time.monotonic()>=deadline:break
        code='EPG_PARTIAL' if not self.done else 'READY' if self.counts['now_count'] and self.code!='EPG_UNAVAILABLE' else self.code
        from live_diagnostics import record
        record('epg_search',code,matched=len(self.result),scanned=self.position,**self.counts)
        try:
            import xbmc
            xbmc.log('[XCMate][SEARCH_EPG] '+json.dumps(dict(code=code,dispatch=self.correlation,scanned=self.position,matched=len(self.result),**self.counts),sort_keys=True),xbmc.LOGINFO)
        except (ImportError,AttributeError,RuntimeError):pass
        return self.result,code


def live_matches(portal,query,reader,now):
    cursor=LiveSearch(portal,query,reader,now)
    while True:
        result,code=cursor.step()
        if cursor.done:return result,code



def search(portal,query,kind='vod',offset=0,now=None,incremental=False,continuation=None,correlation=''):
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
                if incremental:
                    cursor=continuation or LiveSearch(portal,query,reader,int(time.time() if now is None else now),correlation)
                    if cursor.portal['id']!=portal['id'] or cursor.query!=query:raise ValueError('SEARCH_SESSION_CHANGED')
                    rows,code=cursor.step()
                    if not cursor.done:result['_continuation']=cursor
                else:rows,code=live_matches(portal,query,reader,int(time.time() if now is None else now))
                total=len(rows);rows=rows[start:start+PAGE]
            else:rows,total=reader.page(section,query,offset=start,limit=PAGE);code='READY'
            result[section]=dict(rows=rows,total=total,code=code,partial=section=='live' and '_continuation' in result)
        except (IndexReadError,sqlite3.Error,OSError,ValueError):
            result[section]=dict(rows=[],total=None,code='INDEX_ERROR')
    return result
