"""Android-reported slots, SQLite imports and REAL executor/GUI owner boundaries."""
import base64
import importlib
import io
import json
from pathlib import Path
import sys
import threading
import time
import types
import unittest
from concurrent.futures import ThreadPoolExecutor,wait
from unittest import mock
from xcmate027_fixture import Fixture,WindowXML,Control,ADDON


class EPGHotfixTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.events=importlib.import_module('epg_events');self.views=importlib.import_module('epg_views')
        self.start=self.now-300
        self.raw={'epg_listings':[
            dict(title='Two and a Half Men',start_timestamp=self.start,stop_timestamp=self.start+1800),
            dict(title='Two and a Half Men',start_timestamp=self.start+60,stop_timestamp=self.start+1800),
            dict(title='Two and a Half Men',start_timestamp=self.start+1800,stop_timestamp=self.start+3540),
            dict(title='Two and a Half Men',start_timestamp=self.start+1800,stop_timestamp=self.start+3540)]}
    def test_reported_1506_1507_and_1536_duplicates_have_two_distinct_slots(self):
        # Translate 15:06/15:07/15:36/16:05 into absolute timestamps, no timezone dependency.
        start=21*86400+15*3600+6*60
        raw=json.loads(json.dumps(self.raw))
        for row in raw['epg_listings']:
            row['start_timestamp']+=start-self.start;row['stop_timestamp']+=start-self.start
        guide=self.views._short_guide(raw,start+300)
        self.assertEqual([(r['start'],r['stop']) for r in guide['events']],[(start,start+1800),(start+1800,start+3540)])
        self.assertEqual((guide['raw_count'],guide['unique_count'],guide['duplicates']),(4,2,2))
        self.assertEqual(guide['next_start'],start+1800)
    def test_order_independent_quality_description_source_and_episode_safety(self):
        row=dict(start=self.start,stop=self.start+1800,title='Two AND a half men',cid='pro7',source=2)
        better=dict(row,start=self.start+60,description='Full synopsis',source=0)
        for entries in ([row,better],[better,row]):
            result=self.events.deduplicate(entries)
            self.assertEqual(len(result),1);self.assertEqual(result[0]['description'],'Full synopsis')
            self.assertEqual(result[0]['source'],0)
        for other in (dict(row,cid='pro7maxx'),dict(row,title='Other'),dict(row,episode_id='2'),
                      dict(row,start=self.start+1800,stop=self.start+3600),
                      dict(row,start=self.start+300,stop=self.start+2100)):
            self.assertEqual(len(self.events.deduplicate([dict(row,episode_id='1'),other])),2)
    def test_exact_offset_duplicates_consistent_across_alias_manual_and_short_views(self):
        events=[dict(r,name=r['title']) for r in self.raw['epg_listings']]
        before=json.dumps(events)
        for info in (self.views.guide_for_channel({'xml':events},'xml',now=self.now),
                     self.views.resolve_guide({'xml':events,'1':[]},'missing','1',self.now,self.client,{'1':'xml'}),
                     self.views._short_guide(self.raw,self.now)):
            self.assertEqual(len(info['events']),2);self.assertEqual(info['next_start'],self.start+1800)
        self.assertEqual(json.dumps(events),before)
    def test_import_and_legacy_database_reads_deduplicate_without_migrating_cache(self):
        store=importlib.import_module('guide_store')
        cache={'xml':[dict(e,name=e['title'],channel='xml') for e in self.raw['epg_listings']]}
        self.assertTrue(store.import_cache('p',cache,now=self.now))
        rows,total=store.events('p','xml',self.start,self.start+4000)
        self.assertEqual((len(rows),total),(2,2))
        db=store.connect(write=True)
        with db:db.execute('INSERT INTO programmes VALUES(?,?,?,?,?,?,?)',('p','xml',self.start+60,self.start+1800,'Two and a Half Men','',0))
        db.close()
        rows,total=store.events('p','xml',self.start,self.start+4000,offset=1,limit=1)
        self.assertEqual((len(rows),total,rows[0]['start']),(1,2,self.start+1800))
        db=store.connect();self.assertEqual(db.execute('SELECT count(*) FROM programmes').fetchone()[0],3);db.close()
    def test_streamed_xmltv_stage_deduplicates_before_atomic_publication(self):
        sys.modules['epg_sources']._channel_name_key=lambda value:str(value).lower()
        stream=importlib.import_module('stream_epg');store=importlib.import_module('guide_store')
        from contextlib import contextmanager
        @contextmanager
        def source(*args,**kwargs):yield io.BytesIO(b'not used')
        def parse(file,channel,programme,cancel):
            channel('xml','Channel 1')
            for row in self.raw['epg_listings']:programme(dict(channel='xml',name=row['title'],descr='',**{k:v for k,v in row.items() if k!='title'}))
            return dict(programmes=4,channels=1)
        with mock.patch.object(stream,'source_stream',source),mock.patch('xmltv_stream.parse',parse):
            stream.import_source('p',dict(uri='local',local=True),1,[dict(sid='1',name='Channel 1',epg_channel_id='xml')],{})
        self.assertEqual(store.events('p','1',self.start,self.start+4000)[1],2)
        db=store.connect();self.assertEqual(db.execute('SELECT count(*) FROM programmes').fetchone()[0],2);db.close()
    def test_cached_extended_guide_is_local_and_legacy_fallback_is_preserved(self):
        calls=[]
        def get(action,extra,cached_only):
            self.assertTrue(cached_only);calls.append(extra['limit'])
            return self.raw if extra['limit']==4 else None
        info=self.views.cached_short_guide(types.SimpleNamespace(_get_json=get),'1',self.now)
        self.assertEqual(len(info['events']),2);self.assertEqual(calls,[12,4])
    def test_bounded_background_expansion_once_and_persistent_private_diagnostics(self):
        m=self.views;jobs=[];requests=[];cached={4:self.raw}
        def get(action,extra,**kwargs):return cached.get(extra['limit'])
        def fetch(sid,limit,**kwargs):
            requests.append(limit)
            cached[limit]=dict(epg_listings=self.raw['epg_listings']+[dict(title='Later',start_timestamp=self.start+3540,stop_timestamp=self.start+7200)])
            return cached[limit]
        xc=types.SimpleNamespace(_get_json=get,get_short_epg=fetch)
        m._SHORT_INFLIGHT.clear();m._SHORT_SEEN.clear();m._SHORT_FAILED.clear()
        with mock.patch.dict(sys.modules,xtream=types.SimpleNamespace(XtreamClient=lambda *a:xc)),\
             mock.patch('threading.Thread',side_effect=lambda **kw:types.SimpleNamespace(start=lambda:jobs.append(kw['target']))):
            self.assertTrue(m._start_short_guides(self.portal,['1']))
            jobs.pop()();self.assertEqual(requests,[12])
            self.assertTrue(m._start_short_guides(self.portal,['1']));self.assertFalse(jobs)
        diagnostics=importlib.import_module('epg_dedup_diagnostics');saved=diagnostics.read()
        self.assertEqual(saved[-1]['removed'],2);self.assertTrue(saved[-1]['decisions'])
        self.assertNotIn('SECRET',json.dumps(saved));self.assertNotIn('provider.invalid',json.dumps(saved))
    def test_conservative_codec_matching_keeps_station_variants_and_regions(self):
        # Fixture normally substitutes source settings only; load actual matcher.
        from importlib.util import spec_from_file_location,module_from_spec
        spec=spec_from_file_location('actual_matcher_0295',ADDON/'resources/lib/epg_sources.py')
        module=module_from_spec(spec)
        # Actual source module needs additional utility imports, not HTTP.
        utils=sys.modules['utils']
        for key in ('cache_get','cache_key','http_get','http_get_to_file','read_json','write_json','atomic_write'):
            if not hasattr(utils,key):setattr(utils,key,mock.Mock())
        spec.loader.exec_module(module);key=module._channel_name_key
        for name in ('DE| PROSIEBEN HEVC','Germany: ProSieben FHD H.265','DE| ProSieben HD'):
            self.assertEqual(key(name),key('ProSieben'))
        for a,b in (('ProSieben','ProSieben MAXX'),('SAT.1','SAT.1 GOLD'),('WDR Köln','WDR Bonn'),('ORF 2 Wien','ORF 2 Tirol')):
            self.assertNotEqual(key(a),key(b))


class WindowOwnerTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.owner=threading.get_ident();self.violations=[];self.calls=[]
        def guard(fn):
            def call(*args,**kwargs):
                self.calls.append(threading.get_ident())
                if threading.get_ident()!=self.owner:self.violations.append(fn.__name__);raise AssertionError('worker GUI')
                return fn(*args,**kwargs)
            return call
        for cls,names in ((WindowXML,('getControl','setFocusId','setProperty','close')),
                          (Control,('setLabel','setText','setVisible','reset','addItems','selectItem','setImage','setPosition','setWidth'))):
            for name in names:
                p=mock.patch.object(cls,name,guard(getattr(cls,name)));p.start();self.addCleanup(p.stop)
    def actual(self,guide=False):
        module=self.guide if guide else self.media
        with mock.patch.object(module,'ThreadPoolExecutor',ThreadPoolExecutor):
            w=module.GuideWindow('XCMateGuide.xml',str(ADDON),'Default','720p') if guide else module.MediaWindow('XCMateMedia.xml',str(ADDON),'Default','720p')
            w.configure(self.router,self.portal) if guide else w.configure(self.router,self.portal,'vod')
        self.addCleanup(w._pool.shutdown,wait=True,cancel_futures=True);self.addCleanup(w.close)
        return w
    def finish(self,w):
        for _ in range(15):
            f=w._pending_future
            if f is None:return
            self.assertTrue(wait([f],timeout=3).done);w.pump()
        self.fail('owner completion loop')
    def test_real_workers_complete_guide_and_media_only_when_owner_pumps(self):
        for guide in (True,False):
            w=self.actual(guide);w.show();future=w._pending_future
            self.assertTrue(wait([future],timeout=3).done)
            self.assertEqual(w.channels if guide else w.rows,[])
            self.finish(w);self.assertTrue(w.channels if guide else w.rows)
            w.close()
        self.assertFalse(self.violations);self.assertTrue(all(t==self.owner for t in self.calls))
    def test_owner_run_receives_native_initialization_and_applies_without_keypress(self):
        w=self.actual(True)
        def tick(seconds):
            f=w._pending_future
            if f:wait([f],timeout=3)
            return bool(w.channels)
        with mock.patch.object(importlib.import_module('owner_dispatch').xbmc,'Monitor',return_value=types.SimpleNamespace(waitForAbort=tick),create=True):w.run()
        self.assertTrue(w.channels);self.assertTrue(w._closed);self.assertFalse(self.violations)
    def test_real_catalog_watcher_defers_all_controls_and_refresh_to_owner(self):
        w=self.actual();w.show();self.finish(w)
        self.index.import_group('p','vod','a',[dict(stream_id='new',category_id='a',name='Fresh')])
        before=len(self.calls)
        with ThreadPoolExecutor(max_workers=1) as pool:pool.submit(w._poll_catalog).result(timeout=3)
        self.assertEqual(len(self.calls),before);self.assertNotEqual(w.rows[0]['sid'],'new')
        w.pump();self.finish(w);self.assertEqual(w.rows[0]['sid'],'new');self.assertFalse(self.violations)
    def test_close_during_worker_and_stale_generation_never_apply(self):
        for guide in (True,False):
            w=self.actual(guide);started=threading.Event();release=threading.Event();applied=[]
            def load():started.set();release.wait(3);return 'late'
            w._request(load,applied.append);old=w._pending_future;self.assertTrue(started.wait(2))
            w._request(lambda:'fresh',applied.append);release.set();self.finish(w)
            self.assertEqual(applied,['fresh'])
            w._request(lambda:'after close',applied.append);future=w._pending_future;w.close();before=len(self.calls)
            wait([old,future],timeout=3);w.pump()
            self.assertEqual(applied,['fresh']);self.assertEqual(len(self.calls),before)
        self.assertFalse(self.violations)
    def test_back_epg_programmes_to_channels_then_root_without_new_jobs(self):
        w=self.guide_window();w.setFocusId(220);jobs=len(w._pool.jobs)
        w.native(92);self.assertEqual(w.getFocusId(),210);self.assertFalse(w._closed)
        w.native(92);self.assertTrue(w._closed);self.assertTrue(w._return_home)
        self.assertEqual(len(w._pool.jobs),jobs)
    def test_back_media_intermediate_levels_then_home_exit_intent(self):
        w=self.media_window();w.native(7);self.settle(w);self.assertEqual(w.mode,'detail')
        w.native(92);self.settle(w);self.assertEqual(w.mode,'landing');self.assertFalse(w._closed)
        w.native(92);self.assertTrue(w._closed);self.assertTrue(w._return_home)
    def test_window_routes_succeed_and_back_returns_home_once_with_replace(self):
        for action,module,name in (('guide_browser',self.guide,'open_guide'),('movies_home',self.media,'open_media')):
            self.router._params['action']=action;self.router._directory_done=False
            with mock.patch.object(module,name) as open_:self.routes.dispatch(self.router)
            self.assertEqual(self.ends[-1][0],(7,));self.assertNotEqual(self.ends[-1][1].get('succeeded'),False);open_.assert_called_once()
        w=self.guide_window();w._return_home=True
        with mock.patch.object(self.guide,'GuideWindow',return_value=w),mock.patch.object(w,'run',side_effect=lambda:setattr(w,'_return_home',True)):
            self.guide.open_guide(self.router,self.portal)
        self.assertEqual(len(self.builtins),2);self.assertTrue(all('action=xcmate_home' in b and b.endswith(',replace)') for b in self.builtins))
