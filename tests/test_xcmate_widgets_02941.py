"""Bounded widget SQL, shared last-good pages and correct Kodi directory routes."""
import importlib,json,sqlite3,sys,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture

class Widgets41(Fixture,unittest.TestCase):
    def setUp(self):super().setUp();self.widgets=importlib.import_module('widget_data41')
    def test_all_three_routes_return_bounded_valid_items_without_playback(self):
        for action,kind,maximum in [('widget_live_start_group','live',12),('widget_recent_vod','vod',24),('widget_recent_series','series',24)]:
            self.added.clear();self.router._params['action']=action;self.routes.dispatch(self.router)
            items=[(u,li,f) for u,li,f in self.added if li.props.get('XCMate.WidgetKind41')]
            self.assertLessEqual(len(items),maximum);self.assertTrue(items)
            for url,li,folder in items:
                self.assertIn('action=play_live' if kind=='live' else 'action=media_detail',url)
                self.assertEqual(li.props['IsPlayable'],'true' if kind=='live' else 'false');self.assertFalse(folder)
            self.assertTrue(self.ends);self.assertFalse(self.builtins)
    def test_fresh_snapshot_is_shared_without_sql_and_policy_change_invalidates(self):
        rows,code=self.widgets.snapshot(self.portal,'vod');self.assertTrue(rows);self.assertEqual(code,'READY')
        with mock.patch.object(self.widgets.WidgetReader,'state',side_effect=AssertionError('repeat SQL')):
            again,code=self.widgets.snapshot(self.portal,'vod');self.assertEqual(again,rows);self.assertEqual(code,'CACHE')
        self.portal['include_vod']=False;self.assertEqual(self.widgets.snapshot(self.portal,'vod'),([], 'DISABLED'))
    def stale(self,kind):
        filename,keyfile=self.widgets.files('p',kind);data=json.loads(Path(filename).read_text());data['at']=time.time()-20
        with open(filename,'w') as f:json.dump(data,f)
    def test_index_error_preserves_last_good_and_does_not_reset_or_scan(self):
        rows,_=self.widgets.snapshot(self.portal,'series');self.stale('series')
        error=self.index.IndexReadError('private account / URL text');error.code='SQLITE_BUSY'
        with mock.patch.object(self.widgets.WidgetReader,'state',side_effect=error):again,code=self.widgets.snapshot(self.portal,'series')
        self.assertEqual(again,rows);self.assertEqual(code,'SQLITE_BUSY')
    def test_parallel_widget_refresh_uses_lkg_without_waiting_on_file_lock(self):
        import fcntl
        rows,_=self.widgets.snapshot(self.portal,'vod');self.stale('vod');_,lock=self.widgets.files('p','vod')
        with open(lock,'a') as stream:
            fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
            again,code=self.widgets.snapshot(self.portal,'vod')
        self.assertEqual(again,rows);self.assertEqual(code,'LOCKED')
    def test_sqlite_exclusive_lock_is_bounded_and_reports_safe_error(self):
        reader=self.widgets.WidgetReader('p',seconds=.15)
        db=sqlite3.connect(self.index.path());db.execute('PRAGMA journal_mode=DELETE');db.execute('BEGIN EXCLUSIVE')
        started=time.monotonic()
        try:
            with self.assertRaises(self.index.IndexReadError) as caught:reader.state('vod')
            self.assertIn(caught.exception.code,('SQLITE_BUSY','BUDGET'));self.assertLess(time.monotonic()-started,1)
        finally:db.rollback();db.close()
    def test_small_widget_query_never_counts_entire_catalogue(self):
        reader=self.widgets.WidgetReader('p');original=reader._query;queries=[]
        def query(sql,*a,**kw):queries.append(sql);return original(sql,*a,**kw)
        with mock.patch.object(reader,'_query',side_effect=query):rows=reader.small('vod',limit=24)
        self.assertEqual(len(rows),24);self.assertFalse(any('COUNT(' in q.upper() or 'GROUP BY' in q.upper() for q in queries))
    def test_missing_corrupt_index_completes_directory_without_repair(self):
        self.index.connect().close();p=self.folder/'library_v1.sqlite'
        # Separate corrupt database path for the read-only backend.
        broken=self.folder/'broken.sqlite';broken.write_bytes(b'not a database')
        reader=self.widgets.WidgetReader('p');reader.filename=str(broken)
        with self.assertRaises(self.index.IndexReadError):reader.state('vod')
        self.assertEqual(broken.read_bytes(),b'not a database')
        with mock.patch.object(self.widgets.WidgetReader,'state',side_effect=self.index.IndexReadError('unknown')):
            self.router._params['action']='widget_recent_vod';self.routes.dispatch(self.router)
        self.assertTrue(self.ends);self.assertFalse(self.builtins)
    def test_live_logo_scale_and_epg_progress_are_explicit_adapter_properties(self):
        self.router._params['action']='widget_live_start_group';self.routes.dispatch(self.router)
        li=self.added[0][1];self.assertEqual(li.props['XCMate.LogoScale41'],'0.5')
        self.assertIn('XCMate.EpgPercent41',li.props);self.assertEqual(li.props['XtreamMate.Now'],'')
    def test_large_widget_catalogue_returns_first_page_without_full_sort_or_count(self):
        rows=[dict(stream_id=str(i),category_id='a',name='Film '+str(i),added=str(self.now+i)) for i in range(20005)]
        self.index.replace_catalog('p','vod',rows,self.catalogs['get_vod_categories'])
        started=time.monotonic();data,code=self.widgets.snapshot(self.portal,'vod')
        print('WIDGET41_HOST',dict(rows=20005,returned=len(data),code=code,ms=round((time.monotonic()-started)*1000,3)))
        self.assertEqual(code,'READY');self.assertEqual(len(data),24);self.assertEqual(data[0]['sid'],'20004')
