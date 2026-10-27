"""Local indexed catalog and bounded EPG snapshots for TV callbacks.

Only the worker reads disk/cache or queues service requests. GUI callbacks read
immutable prepared values and update the wanted viewport. No HTTP here.
"""
from collections import OrderedDict
import threading
import sqlite3
import time

from epg_views import guide_for_channel


class CatalogIndex:
    def __init__(self, channels):
        self.channels = tuple(channels)
        self.by_sid, self.groups = {}, {}
        self.positions, self.group_positions = {}, {}
        for i,channel in enumerate(self.channels):
            sid,cid = str(channel.extra.get('stream_id','')),str(channel.extra.get('category_id',''))
            self.by_sid[sid] = channel
            self.positions[sid] = i
            group=self.groups.setdefault(cid,[])
            self.group_positions.setdefault(cid,{})[sid]=len(group)
            group.append(channel)
        self.groups = {k:tuple(v) for k,v in self.groups.items()}
        self._selections = OrderedDict()

    def selection(self, category, enabled):
        key = (str(category), None if enabled is None else frozenset(enabled))
        if key not in self._selections:
            if category != '*':
                rows = self.groups.get(str(category), ()) if enabled is None or str(category) in enabled else ()
                positions=self.group_positions.get(str(category),{}) if rows else {}
            elif enabled is None: rows,positions = self.channels,self.positions
            else:
                rows = tuple(c for c in self.channels if str(c.extra.get('category_id','')) in enabled)
                positions={str(c.extra.get('stream_id','')):i for i,c in enumerate(rows)}
            self._selections[key] = (rows, positions)
            if len(self._selections) > 4: self._selections.popitem(last=False)
        return self._selections[key]


class GuideSnapshot:
    def __init__(self, portal, client):
        self.portal, self.client = portal, client
        self._lock = threading.Lock()
        self._wake, self._stop = threading.Event(), threading.Event()
        self._wanted, self._values = (), OrderedDict()
        self.generation = 0
        self._revision, self._cache, self._mappings = None, {}, {}
        self._thread = None
        self._request_generation=0;self._refresh_serial=0

    def start(self):
        if self._thread is None:
            self._thread = threading.Thread(target=self._run, daemon=True, name='XCMateLocalGuide')
            self._thread.start()

    def close(self):
        self._stop.set()
        self._wake.set()

    def request(self, channels):
        unique = {str(c.extra.get('stream_id','')):c for c in channels}
        wanted = tuple(unique.values())[:16]
        with self._lock:
            if wanted != self._wanted:
                self._request_generation+=1
                self._wanted = wanted
                self._wake.set()

    def get(self, sid, now=None):
        ts = time.time() if now is None else now
        with self._lock: base = self._values.get(str(sid))
        if base is None: return guide_for_channel({}, now=ts)
        if base.get('start',0) <= ts < base.get('stop',0):
            info = dict(base)
            info.update(elapsed=ts-info['start'], remaining=info['stop']-ts,
                        progress=max(0.,min(1.,(ts-info['start'])/(info['stop']-info['start']))))
            return info
        if not base.get('now') and base.get('next_start',0)>ts:
            return dict(base)
        # Re-evaluate only a bounded, already normalized programme list in RAM.
        info = guide_for_channel({'v':[dict(name=e['title'], start_timestamp=e['start'],
            stop_timestamp=e['stop'], descr=e.get('description','')) for e in base.get('programme_events',base['events'])]}, 'v', now=ts)
        info.update(epg_id=base.get('epg_id',''), mapping=base.get('mapping',''),
                    source_index=base.get('source_index'),snapshot_revision=base.get('snapshot_revision'))
        if base.get('programme_events'):info['programme_events']=base['programme_events']
        if not info['events']: info['reason'] = base.get('reason','NO_DATA')
        return info

    def request_programme(self,sid):
        with self._lock:
            if str(sid)!=getattr(self,'_programme_sid',''):
                self._request_generation+=1
                self._programme_sid=str(sid);self._wake.set()

    def refresh(self):
        """One worker iteration, also usable deterministically in integration tests."""
        from epg import load_cache, _mem_clear
        from epg_sources import configuration
        from epg_status import revision
        from epg_views import resolve_guide
        now = time.time()
        started=time.perf_counter()
        rev = revision(self.portal['id'])
        reloaded=rev != self._revision
        with self._lock:
            wanted=self._wanted;generation=self._request_generation
            self._refresh_serial+=1;serial=self._refresh_serial
        if reloaded:self._mappings = configuration(self.portal['id'])['mappings']
        from guide_viewport import cache as viewport_cache
        selected=getattr(self,'_programme_sid','')
        local=viewport_cache(self.portal['id'],wanted,self._mappings,now,focus_sid=selected) if selected else viewport_cache(self.portal['id'],wanted,self._mappings,now)
        if local is None:
            if reloaded or getattr(self,'_indexed',False):
                _mem_clear(self.portal['id'])
                self._cache = load_cache(self.portal['id'])
            self._indexed=False
        else:
            self._cache=local;self._indexed=True
        self._revision = rev
        cache_ms=(time.perf_counter()-started)*1000
        from logo_cache import request as request_logos
        request_logos(wanted)
        values, missing = {}, []
        for c in wanted:
            sid = str(c.extra.get('stream_id',''))
            info = resolve_guide(self._cache, c.tvg_id, sid, now, None if self._indexed else self.client, self._mappings)
            info['snapshot_revision']=getattr(local,'revision',None)
            if not info['now'] and not self._indexed:
                # A saved ten-day guide outlives its small compatibility
                # snapshot. Read only this worker's bounded visible viewport.
                try:
                    from guide_store import events
                    ident=self._mappings.get(sid) or sid
                    rows,_=events(self.portal['id'],ident,int(now),int(now)+2*86400,limit=4)
                    if not rows and sid not in self._mappings and c.tvg_id:
                        rows,_=events(self.portal['id'],c.tvg_id,int(now),int(now)+2*86400,limit=4)
                    if rows:
                        stored=guide_for_channel({'v':[dict(name=r['title'],descr=r['description'],start_timestamp=r['start'],stop_timestamp=r['stop'],_source_index=r['source']) for r in rows]},'v',now=now)
                        if stored['now'] or not info['next']: info=stored
                except (OSError,RuntimeError,sqlite3.Error): pass
            if sid==selected:
                from epg_events import deduplicate
                raw=self._cache.get(info.get('epg_id',''),[])
                info['programme_events']=[e for e in deduplicate(raw,channel=info.get('epg_id','')) if e['stop']>now][:256] if raw else info.get('events',[])
            values[sid] = info
            if not info['now'] and sid not in self._mappings: missing.append(c)
        with self._lock:
            if generation!=self._request_generation or serial!=self._refresh_serial:return  # Late old viewport cannot publish.
            from render_diff44 import signature
            changed=signature(values)!=signature({sid:self._values[sid] for sid in values if sid in self._values})
            self._values.update(values)
            for sid in values: self._values.move_to_end(sid)
            while len(self._values) > 128: self._values.popitem(last=False)
            if changed:self.generation += 1
        # Visible selection is a read request, never a per-channel network job.
        # Configured imports run independently on the background service timer.
        from live_diagnostics import record
        record('epg_performance','GUIDE_WORKER',cache_ms=cache_ms,cache_hit=not reloaded,
               snapshot_ms=(time.perf_counter()-started)*1000-cache_ms,items=len(values))

    def _run(self):
        while not self._stop.is_set():
            self._wake.wait(5)
            self._wake.clear()
            if self._stop.is_set(): break
            try: self.refresh()
            except Exception as exc:
                from live_diagnostics import record
                record('epg', 'LOCAL_SNAPSHOT_FAILED', exception_class=type(exc).__name__)
