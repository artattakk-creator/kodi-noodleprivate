"""Local indexed catalog and bounded EPG snapshots for TV callbacks.

Only the worker reads disk/cache or queues service requests. GUI callbacks read
immutable prepared values and update the wanted viewport. No HTTP here.
"""
from collections import OrderedDict
import threading
import sqlite3
import time

from epg_views import guide_for_channel
from programme_read47 import scoped


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
    def __init__(self, portal, client, initial_sid=''):
        self.portal, self.client = portal, client
        self._lock = threading.Lock()
        self._wake, self._stop = threading.Event(), threading.Event()
        self._wanted, self._values = (), OrderedDict()
        self.generation = 0
        self._revision, self._cache, self._mappings = None, {}, {}
        self._thread = None
        self._request_generation=0;self._refresh_serial=0
        self._seeded63={}
        self._preview96={};self._preview_epoch96=0
        if initial_sid:self.seed63(initial_sid)

    def seed63(self,sid):
        from epg_handoff63 import get,note
        from epg_status import revision
        value=get(self.portal['id'],str(sid))
        if value is None:return
        with self._lock:
            self._values[str(sid)]=value;self._seeded63[str(sid)]=revision(self.portal['id'])
            self.generation+=1
        note('SNAPSHOT_SEEDED',self.portal['id'],sid)


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
        for sid in tuple(unique)[:16]:
            if sid not in self._values:self.seed63(sid)
        with self._lock:
            if wanted != self._wanted:
                self._request_generation+=1
                self._wanted = wanted
                self._wake.set()

    def request_infobar45(self,sid):
        with self._lock:
            if getattr(self,'_infobar_sid45','')!=str(sid):
                self._infobar_sid45=str(sid);self._wake.set()

    def begin_preview96(self,sid):
        """Reserve a dialog epoch; background snapshots remain separate."""
        with self._lock:
            self._preview_epoch96+=1
            epoch=self._preview_epoch96
            self._preview96[str(sid)]=(epoch,None)
            return epoch

    def set_preview96(self,sid,epoch,info):
        with self._lock:
            current=self._preview96.get(str(sid))
            if current is None or current[0]!=epoch:return False
            self._preview96[str(sid)]=(epoch,dict(info));self.generation+=1
            return True

    def clear_preview96(self,sid,epoch,refresh=False):
        with self._lock:
            current=self._preview96.get(str(sid))
            if current is None or current[0]!=epoch:return False
            self._preview96.pop(str(sid));self.generation+=1
            if refresh:
                self._values.pop(str(sid),None);self._seeded63.pop(str(sid),None)
                self._revision=None;self._request_generation+=1;self._wake.set()
            return True

    def get(self, sid, now=None):
        ts = time.time() if now is None else now
        with self._lock:
            preview96=self._preview96.get(str(sid))
            base=preview96[1] if preview96 and preview96[1] is not None else self._values.get(str(sid))
        is_preview96=bool(preview96 and preview96[1] is not None)
        guide_revision = self._seeded63.get(str(sid)) if base is None else base.get('_guide_revision104',self._seeded63.get(str(sid)))
        if not is_preview96 and guide_revision is not None:
            from epg_status import revision
            if guide_revision!=revision(self.portal['id']):
                base=None;self._wake.set()
        if base is None:
            from epg_handoff63 import get
            base=get(self.portal['id'],str(sid),now=ts)
        if base is None:
            value=guide_for_channel({},now=ts);value['loading68']=True;return value
        if base.get('start',0) <= ts < base.get('stop',0):
            info = dict(base)
            info.update(elapsed=ts-info['start'], remaining=info['stop']-ts,
                        progress=max(0.,min(1.,(ts-info['start'])/(info['stop']-info['start']))))
            return info
        if not base.get('now') and base.get('next_start',0)>ts:
            return dict(base)
        # Re-evaluate only a bounded, already normalized programme list in RAM.
        canonical=base.get('canonical46') or base.get('epg_id') or 'v'
        info = guide_for_channel({canonical:base.get('programme_events',base['events'])},canonical,now=ts)
        info['previous']=base.get('now') if base.get('now') and base.get('stop',0)<=ts else base.get('previous','')
        info.update(epg_id=base.get('epg_id',''), mapping=base.get('mapping',''),
                    snapshot_revision=base.get('snapshot_revision'),canonical46=base.get('canonical46',''),
                    _guide_revision104=base.get('_guide_revision104'))
        if is_preview96:info['preview_epoch96']=preview96[0]
        if base.get('programme_events'):info['programme_events']=base['programme_events']
        if not info['events']: info['reason'] = base.get('reason','NO_DATA')
        from programme_snapshot47 import bind
        return bind(self.portal['id'],dict(sid=str(sid)),info)

    def request_programme(self,sid):
        with self._lock:
            if str(sid)!=getattr(self,'_programme_sid',''):
                self._request_generation+=1
                self._programme_sid=str(sid);self._wake.set()

    @scoped
    def refresh(self):
        """One worker iteration, also usable deterministically in integration tests."""
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
        import guide_store,os
        guide_path65=getattr(guide_store,'path',lambda:'')()
        contended65=local is None and bool(guide_path65) and os.path.isfile(guide_path65)
        if contended65:self._cache={};self._indexed=False
        elif local is None:
            from epg import load_cache, _mem_clear
            if reloaded or getattr(self,'_indexed',False):
                _mem_clear(self.portal['id'])
                self._cache = load_cache(self.portal['id'])
            self._indexed=False
        else:
            self._cache=local;self._indexed=True
        from epg_handoff63 import register as register63
        if local is not None:register63(self.portal['id'],getattr(local,'revision',None),expected_revision=rev)
        self._revision = rev
        cache_ms=(time.perf_counter()-started)*1000
        values, missing = {}, []
        for c in wanted:
            sid = str(c.extra.get('stream_id',''))
            compatibility47=not contended65 and (not self._indexed or getattr(local,'code','')=='SHARED_LASTGOOD47')
            from epg_binding48 import binding as source_binding48
            qualified48=source_binding48(self._mappings,sid)
            # A legacy flattened cache cannot prove source identity. Never
            # silently replace a qualified manual source with another feed.
            selected_cache48={} if qualified48 and not self._indexed else self._cache
            info = resolve_guide(selected_cache48, c.tvg_id, sid, now, self.client if compatibility47 else None, self._mappings)
            info['snapshot_revision']=getattr(local,'revision',None)
            if not info['now'] and not self._indexed and not qualified48 and not contended65:
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
                from epg_binding48 import qualified_cache
                from infobar_epg45 import history
                from local_epg import for_channel
                raw=qualified_cache(for_channel(self._cache,sid),self._mappings,sid).get(info.get('epg_id',''),[])
                earlier=history(self.portal['id'],c,self._mappings,info.get('start') or now,
                                info.get('snapshot_revision'),guide_id=info.get('epg_id') or None)
                upcoming=[e for e in deduplicate(raw,channel=info.get('epg_id','')) if e['stop']>now][:256]
                info['programme_events']=earlier+(upcoming or info.get('events',[]))
            if sid==getattr(self,'_infobar_sid45',''):
                from infobar_epg45 import previous
                info['previous']=previous(self.portal['id'],c,self._mappings,info.get('start') or now,info.get('snapshot_revision'))
            info['canonical46']=getattr(local,'canonical',{}).get(info.get('epg_id',''),info.get('epg_id',''))
            info['_guide_revision104']=rev
            from programme_snapshot47 import bind
            values[sid] = bind(self.portal['id'],c,info)
            from epg_handoff63 import remember,get as warm63
            if local is None and not values[sid].get('now'):
                prior63=warm63(self.portal['id'],sid,now=now,mappings=self._mappings,_previous_guide67=True)
                if prior63 and prior63.get('now'):values[sid]=prior63
            if local is not None and getattr(local,'code','')!='RAM_LASTGOOD67':remember(self.portal['id'],c,values[sid],self._mappings,expected_revision=rev)
            values[sid]['loading68']=local is None and not values[sid].get('now') and not values[sid].get('next')
            if not values[sid].get('_published_at63'):values[sid]['_published_at63']=time.time()
            if not info['now'] and sid not in self._mappings: missing.append(c)
        with self._lock:
            if generation!=self._request_generation or serial!=self._refresh_serial or revision(self.portal['id'])!=rev:return
            from render_diff44 import signature
            changed=signature(values)!=signature({sid:self._values[sid] for sid in values if sid in self._values})
            self._values.update(values)
            for sid in values:self._seeded63.pop(sid,None)
            for sid in values: self._values.move_to_end(sid)
            while len(self._values) > 128: self._values.popitem(last=False)
            if changed:self.generation += 1
        from logo_cache import request as request_logos
        request_logos(wanted)
        from programme_flow48 import trace
        for info48 in values.values():
            trace('MINI',dict(key=info48.get('programme_key47','')),'READY' if info48.get('now') else 'NO_EPG',duration_ms=(time.perf_counter()-started)*1000)
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
