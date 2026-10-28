"""Selected-channel long DB evidence. Worker-only, bounded, strictly read-only."""
import os,sqlite3,time
from urllib.parse import quote
from localization import tr


def _stamp(value):
    return time.strftime('%d.%m.%Y %H:%M',time.localtime(value)) if value is not None else '—'


def inspect(portal,row,origin,cursor,focus,client=None,snapshot=None):
    from guide_store import path
    from epg_sources import configuration
    from epg_preview import safe_name
    from epg_status import read,source_key
    config=configuration(portal['id']);state=read(portal['id']);channel=row['channel']
    manual=config.get('mappings',{}).get(channel['sid'])
    ids=[str(manual)] if manual else list(dict.fromkeys([str(channel['sid']),str(channel.get('epg_channel_id') or '')]))
    lines=[tr(33121),safe_name(channel['name'])+' | SID: '+safe_name(channel['sid']),
           'Viewport: '+str(row['mapping'])+' | CID: '+safe_name(row.get('epg_id'),'—'),
           'Cursor: '+_stamp(cursor)+' | origin: '+_stamp(origin)+' | focus: '+str(int(focus)),
           'guide_v1.sqlite (read-only) | '+('MANUAL' if manual else 'AUTO'),
           'Provider EPG-ID: '+safe_name(channel.get('epg_channel_id'),'—')]
    if snapshot:lines.append('loading='+str(bool(snapshot['loading']))+' | cells='+str(int(snapshot['cells'])))
    filename=path();db=None
    try:
        if not os.path.exists(filename):lines.append('NOT_CREATED')
        else:
            db=sqlite3.connect('file:'+quote(filename,safe='/')+'?mode=ro',uri=True,timeout=.05)
            db.row_factory=sqlite3.Row
            deadline=time.monotonic()+.4;db.set_progress_handler(lambda:int(time.monotonic()>deadline),1000)
            # Same alias candidates/order as the viewport. Unlike the viewport,
            # coverage is queried across the full stored horizon, including gaps.
            for ident in ids:
                if not ident:continue
                alias=db.execute('SELECT cid FROM guide_alias WHERE pid=? AND alias=?',(portal['id'],ident)).fetchone()
                cid=alias[0] if alias else ident;args=(portal['id'],cid)
                lines+=['','Alias: '+safe_name(ident)+' → CID: '+safe_name(cid)]
                first=db.execute('SELECT start,stop,title FROM programmes WHERE pid=? AND cid=? ORDER BY start,stop LIMIT 1',args).fetchone()
                last=db.execute('SELECT start,stop,title FROM programmes WHERE pid=? AND cid=? ORDER BY start DESC,stop DESC LIMIT 1',args).fetchone()
                sources=db.execute('SELECT source,min(start),max(stop),count(*) FROM programmes WHERE pid=? AND cid=? GROUP BY source',args).fetchall()
                lines.append('Erster / First: '+(_stamp(first['start'])+' – '+_stamp(first['stop'])+' | '+first['title'] if first else '—'))
                lines.append('Letzter / Last: '+(_stamp(last['start'])+' – '+_stamp(last['stop'])+' | '+last['title'] if last else '—'))
                # Full coverage equivalent to horizon(pid,cid), without its
                # schema-writing connect(). Last stop may differ from last start.
                lines.append('Programme: '+str(sum(s['count(*)'] for s in sources)))
                for source in sources:
                    index=source['source'];records=config.get('sources',[])
                    record=records[index-1] if 0<index<=len(records) else None
                    entry=state.get(source_key(record) if record else 'provider',{})
                    name=safe_name(record.get('name')) if record else ('Provider' if index==0 else 'Source '+str(index))
                    lines.append('Quelle / Source: '+name+' | '+str(entry.get('code','UNKNOWN'))+' | '+str(source['count(*)'])+' | '+_stamp(source['min(start)'])+' → '+_stamp(source['max(stop)'])+' | Erfolg / Success: '+_stamp(entry.get('last_success')))
                days=db.execute("SELECT date(start,'unixepoch','localtime'),count(*) FROM programmes WHERE pid=? AND cid=? GROUP BY 1 ORDER BY 1 LIMIT 12",args).fetchall()
                lines.append('Tage / Days: '+', '.join(str(d[0])+': '+str(d[1]) for d in days))
                local=time.localtime(cursor);after=int(time.mktime((local.tm_year,local.tm_mon,local.tm_mday,14,0,0,0,0,-1)))
                future=db.execute('SELECT start,stop,title FROM programmes WHERE pid=? AND cid=? AND stop>? ORDER BY start,stop LIMIT 3',args+(after,)).fetchall()
                lines.append('Nach / After '+_stamp(after)+':')
                lines.extend(_stamp(e['start'])+' – '+_stamp(e['stop'])+' | '+e['title'] for e in future)
                if not future:lines.append('—')
    except sqlite3.Error as exc:
        code=getattr(exc,'sqlite_errorcode',0)
        lines.append('DB: '+('BUSY' if code in (5,6) else 'QUERY_FAILED')+' (keine Aussage über fehlende Daten / coverage unknown)')
    finally:
        if db is not None:db.close()
    # Only the existing local short cache; never start a fetch or compare its
    # coverage percentage with the independent long-term database.
    lines+=['','SHORT_EPG (separater Cache / separate cache):']
    if client is not None:
        from epg_views import cached_short_guide
        try:short=cached_short_guide(client,channel['sid'])
        except (OSError,ValueError,RuntimeError):short={}
        events=short.get('events',[])
        lines.append(str(len(events))+' | '+_stamp(min((e['start'] for e in events),default=None))+' → '+_stamp(max((e['stop'] for e in events),default=None)))
    else:lines.append('NOT_AVAILABLE')
    from guide_coverage52 import inspect as coverage52
    import json
    lines+=['','Quellen-/Tagesabdeckung (lokal, read-only):',json.dumps(coverage52(portal['id'],channel['sid'],row.get('epg_id') or channel.get('epg_channel_id') or channel['sid']),ensure_ascii=False)]
    return '\n'.join(lines)
