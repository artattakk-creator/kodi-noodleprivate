"""Synthetic latency and cursor lifetime; no Android performance claims."""
import importlib,sys,unittest
from unittest import mock
from xcmate027_fixture import Fixture


class SearchPerformance35(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();sys.modules.pop('search_data',None)
        self.search=importlib.import_module('search_data')
        entries=[dict(stream_id=str(i),category_id='a',name='Needle station' if i==2763 else 'Station '+str(i),epg_channel_id='xml'+str(i)) for i in range(2764)]
        self.index.replace_catalog('p','live',entries,self.catalogs['get_live_categories'])

    def settle(self,window):
        for _ in range(2048):
            window._pool.drain();window.pump()
            if not window._pool.jobs:return
        self.fail('bounded 50k scan did not finish')

    def test_first_name_result_does_not_wait_for_94_second_epg_init_or_short_scan(self):
        clock=[0.0]
        def epg(*a,**kw):clock[0]+=94;return {},{},'NO_EPG',0
        def short(*a,**kw):clock[0]+=.3;return {'now':''}
        with mock.patch.object(self.search,'_now_events',side_effect=epg),mock.patch('epg_views.cached_short_guide',side_effect=short):
            result=self.search.search(self.portal,'Needle',kind='live',now=self.now,incremental=True)
        self.assertEqual([r['sid'] for r in result['live']['rows']],['2763'])
        self.assertLess(clock[0],5,'local names must precede the injected expensive EPG stage')
        self.assertTrue(result['live']['partial'])

    def test_tab_click_during_worker_keeps_the_same_pending_job(self):
        w=self.media_window();self.dialog.input.return_value='Needle';w._search()
        future=w._pending_future;generation=w._generation
        w.onClick(700)
        self.assertIs(w._pending_future,future);self.assertEqual(w._generation,generation)
        self.assertFalse(future.cancelled())

    def test_same_query_tab_cycle_reuses_one_live_cursor(self):
        with mock.patch.object(self.search,'LiveSearch',wraps=self.search.LiveSearch) as cursor:
            w=self.media_window();self.dialog.input.return_value='Needle';w._search();self.settle(w)
            for cid in (700,700,701,702,700):w.onClick(cid);self.settle(w)
        self.assertEqual(cursor.call_count,1)
        self.assertEqual(w._search_data['live']['total'],1)

    def finish(self,query,**kwargs):
        cursor=None;result=None
        for _ in range(4000):
            result=self.search.search(self.portal,query,kind='live',now=self.now,incremental=True,continuation=cursor,**kwargs)
            cursor=result.get('_continuation')
            if cursor is None:return result
        self.fail('scan did not finish')

    def test_xml_programme_late_in_catalogue_precedes_all_missing_short_lookups(self):
        guide=importlib.import_module('guide_store')
        guide.import_cache('p',{'xml2763':[dict(channel='xml2763',name='Genuine programme',start_timestamp=self.now-60,stop_timestamp=self.now+60)]})
        cursor=None;seen=[]
        def short(client,sid,now=None):seen.append(sid);return {'now':''}
        with mock.patch('epg_views.cached_short_guide',side_effect=short):
            for _ in range(100):
                result=self.search.search(self.portal,'Genuine programme',kind='live',now=self.now,incremental=True,continuation=cursor)
                cursor=result.get('_continuation')
                if result['live']['rows']:break
            else:self.fail('local XML programme never published')
        self.assertEqual([r['sid'] for r in result['live']['rows']],['2763'])
        self.assertLessEqual(len(seen),16,'missing caches cannot precede the local programme pass')

    def test_media_queries_are_not_repeated_for_each_live_slice_or_tab(self):
        original=self.index.Reader.page;queries=[]
        def page(reader,kind,*args,**kwargs):queries.append(kind);return original(reader,kind,*args,**kwargs)
        with mock.patch.object(self.index.Reader,'page',page):
            result=self.finish('Needle');cursor=result['_cursor']
            self.search.search(self.portal,'Needle',kind='series',incremental=True,continuation=cursor)
        self.assertEqual(queries.count('vod'),1);self.assertEqual(queries.count('series'),1)

    def test_cancelled_query_does_not_continue_reading_short_caches(self):
        from threading import Event
        cancel=Event();first=self.search.search(self.portal,'Needle',kind='live',incremental=True,cancel=cancel.is_set)
        cancel.set()
        with mock.patch('epg_views.cached_short_guide') as short:
            first['_cursor'].step()
        short.assert_not_called()

    def test_names_remain_usable_when_the_epg_database_is_locked_or_corrupt(self):
        (self.folder/'guide_v1.sqlite').write_bytes(b'broken database')
        result=self.finish('Needle')
        self.assertEqual(result['live']['rows'][0]['sid'],'2763')
        self.assertEqual(result['live']['code'],'EPG_UNAVAILABLE')

    def test_completed_query_is_reused_until_catalogue_or_mapping_revision_changes(self):
        result=self.finish('Needle');cursor=result['_cursor']
        with mock.patch.object(self.search,'LiveSearch',wraps=self.search.LiveSearch) as created:
            fresh=self.search.search(self.portal,'Needle',kind='live',incremental=True,continuation=cursor)
            created.assert_not_called();self.assertIs(fresh['_cursor'],cursor)
            (self.folder/'xtreammate_epg_sources.json').write_text('{}')
            fresh=self.search.search(self.portal,'Needle',kind='live',incremental=True,continuation=cursor)
            created.assert_called_once();self.assertIsNot(fresh['_cursor'],cursor)

    def test_now_programme_expiry_invalidates_a_completed_snapshot(self):
        result=self.finish('Needle');cursor=result['_cursor'];cursor.expires=self.now-1
        with mock.patch.object(self.search,'LiveSearch',wraps=self.search.LiveSearch) as created:
            fresh=self.search.search(self.portal,'Needle',kind='live',incremental=True,continuation=cursor)
        created.assert_called_once();self.assertIsNot(fresh['_cursor'],cursor)

    def test_profile_contains_only_random_correlations_and_numeric_measurements(self):
        from search_profile import SearchProfile
        xbmc=sys.modules['xbmc'];messages=[];xbmc.LOGINFO=1
        with mock.patch.object(xbmc,'log',side_effect=lambda text,*a:messages.append(text),create=True):
            p=SearchProfile('SECRET QUERY','https://SECRET@provider.invalid')
            p.emit('QUERY_ACCEPTED',duration_ms=3,title='SECRET',pid='PRIVATE',rows=1)
            self.finish('SECRET QUERY',profile=p)
        text=' '.join(messages)
        for private in ('SECRET','PRIVATE','provider.invalid','https://'):self.assertNotIn(private,text)
        self.assertIn('generation=',text);self.assertIn('SCAN_FINAL',text)

    def test_fifty_thousand_bound_is_preserved_and_warm_first_page_needs_no_epg(self):
        import time
        entries=[dict(stream_id=str(i),category_id='a',name='Target '+str(i)) for i in range(50000)]
        self.index.replace_catalog('p','live',entries,self.catalogs['get_live_categories'])
        started=time.perf_counter()
        with mock.patch.object(self.search,'_now_events',side_effect=AssertionError('EPG before names')):
            result=self.search.search(self.portal,'Target 49999',kind='live',incremental=True)
        self.assertEqual(result['live']['total'],1);self.assertEqual(result['live']['rows'][0]['sid'],'49999')
        self.assertLess(time.perf_counter()-started,10,'host bound, not Android PASS')
        self.index.replace_catalog('p','live',entries+[dict(stream_id='50000',category_id='a',name='Target')],self.catalogs['get_live_categories'])
        self.assertEqual(self.search.search(self.portal,'Target',kind='live',incremental=True)['live']['code'],'INDEX_ERROR')

    def test_first_live_row_is_clickable_before_background_epg_scan_finishes(self):
        w=self.media_window();w._search_kind='live';self.dialog.input.return_value='Needle';w._search()
        w._pool.drain();w.pump()  # Commit names; next EPG job remains queued.
        self.assertEqual(w._search_rows[0]['sid'],'2763');self.assertFalse(w._search_loading)
        self.assertIsNotNone(w._pending_future);self.assertTrue(w._search_data['live']['partial'])
        w.native(4);w.native(7)
        self.assertEqual(w._search_live['sid'],'2763');self.assertTrue(w._leaving)
        self.assertFalse(self.builtins)

    def test_real_sqlite_lock_cannot_withhold_indexed_names_or_write_guide(self):
        import sqlite3
        guide=importlib.import_module('guide_store');db=guide.connect();db.close()
        lock=sqlite3.connect(guide.path());lock.execute('PRAGMA locking_mode=EXCLUSIVE');lock.execute('BEGIN EXCLUSIVE')
        try:
            first=self.search.search(self.portal,'Needle',kind='live',incremental=True)
            self.assertEqual(first['live']['rows'][0]['sid'],'2763')
            result=self.finish('Needle');self.assertEqual(result['live']['total'],1)
        finally:lock.rollback();lock.close()

    def test_now_sql_plan_uses_channel_time_index_and_other_portal_cannot_match(self):
        guide=importlib.import_module('guide_store');db=guide.connect()
        with db:db.execute('INSERT INTO programmes VALUES(?,?,?,?,?,?,?)',('other','xml2763',self.now-60,self.now+60,'Foreign programme','',0))
        plan=' '.join(str(tuple(row)) for row in db.execute('EXPLAIN QUERY PLAN SELECT cid,title,source,start,stop FROM programmes WHERE pid=? AND cid IN (?) AND start<=? AND stop>? ORDER BY source,start DESC',('p','xml2763',self.now,self.now)))
        db.close();self.assertIn('SEARCH programmes USING INDEX',plan)
        result=self.finish('Foreign programme');self.assertEqual(result['live']['total'],0)

    def test_unrelated_wal_writes_do_not_restart_the_live_generation(self):
        result=self.finish('Needle');cursor=result['_cursor']
        db=self.index.connect(write=True)
        with db:db.execute('INSERT OR REPLACE INTO sync_requests VALUES(?,?,?,?,?,?)',('p','vod',10,'',0,self.now))
        db.close()
        with mock.patch.object(self.search,'LiveSearch',wraps=self.search.LiveSearch) as created:
            fresh=self.search.search(self.portal,'Needle',kind='live',incremental=True,continuation=cursor)
        created.assert_not_called();self.assertIs(fresh['_cursor'],cursor)

    def test_other_portal_epg_publication_does_not_restart_this_portals_cursor(self):
        guide=importlib.import_module('guide_store')
        guide.import_cache('p',{'xml1':[dict(channel='xml1',name='Current',start_timestamp=self.now-60,stop_timestamp=self.now+60)]})
        result=self.finish('Needle');cursor=result['_cursor']
        guide.import_cache('other',{'xml1':[dict(channel='xml1',name='Unrelated',start_timestamp=self.now-60,stop_timestamp=self.now+60)]})
        with mock.patch.object(self.search,'LiveSearch',wraps=self.search.LiveSearch) as created:
            fresh=self.search.search(self.portal,'Needle',kind='live',incremental=True,continuation=cursor)
        created.assert_not_called();self.assertIs(fresh['_cursor'],cursor)
