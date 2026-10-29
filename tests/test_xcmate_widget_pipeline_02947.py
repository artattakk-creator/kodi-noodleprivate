"""#244: actual indexed movies -> native items, without changing series SQL."""
import importlib
import json
from pathlib import Path
import sqlite3
import sys
import time
import unittest
from unittest import mock
from xcmate027_fixture import Fixture, ListItem


class WidgetPipeline47(Fixture, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.widgets=importlib.import_module('widget_data41')
        self.items=importlib.import_module('widget_items45')

    def test_real_v2_payload_query_is_primary_key_search_not_whole_movie_scan(self):
        rows=[dict(stream_id=str(i),category_id='a',name='Film '+str(i),added=self.now+i) for i in range(12000)]
        self.index.import_group('p','vod','a',rows)
        reader=self.widgets.WidgetReader('p')
        original=reader._query
        plans=[]
        def query(sql,args=(),kind=None):
            if 'UNION ALL' in sql and 'payload' in sql:
                db=sqlite3.connect(self.index.path())
                try:plans.extend(r[3] for r in db.execute('EXPLAIN QUERY PLAN '+sql,args))
                finally:db.close()
            return original(sql,args,kind)
        with mock.patch.object(reader,'_query',side_effect=query):result=reader.small('vod')
        self.assertEqual(len(result),24)
        self.assertEqual(result[0]['sid'],'11999')
        self.assertTrue(plans)
        self.assertEqual(sum('sqlite_autoindex_items_v2_1' in p for p in plans),24)
        self.assertFalse(any('SCAN' in p or 'identity_v2' in p for p in plans))

    def test_old_or_payload_exceeds_opcode_budget_new_point_reads_do_not(self):
        rows=[dict(stream_id=str(i),category_id='a',name='Movie',added=self.now+i) for i in range(18000)]
        self.index.import_group('p','vod','a',rows)
        db=sqlite3.connect(self.index.path())
        head=db.execute("SELECT generation FROM heads WHERE pid='p' AND kind='vod' AND cid='a'").fetchone()[0]
        count=[0]
        def interrupt():count[0]+=1;return count[0]>10
        db.set_progress_handler(interrupt,1000)
        branches=' OR '.join('(cid=? AND generation=? AND sid=?)' for _ in range(24))
        args=[v for i in range(17976,18000) for v in ('a',head,str(i))]
        with self.assertRaises(sqlite3.OperationalError):
            db.execute("SELECT sid,payload FROM items_v2 WHERE pid='p' AND kind='vod' AND ("+branches+')',args).fetchall()
        db.close()
        original_connect=sqlite3.connect
        class BudgetConnection(sqlite3.Connection):
            def set_progress_handler(self,callback,n):
                count=[0]
                def bounded():count[0]+=1;return callback() or count[0]>10
                return super().set_progress_handler(bounded,n)
        def connect(*args,**kwargs):return original_connect(*args,**dict(kwargs,factory=BudgetConnection))
        with mock.patch.object(sqlite3,'connect',side_effect=connect):
            actual=self.widgets.WidgetReader('p').small('vod')
        self.assertEqual(len(actual),24)

    def test_legacy_movie_point_reads_keep_order_and_exact_ids(self):
        rows=self.widgets.WidgetReader('p').small('vod')
        self.assertEqual([r['sid'] for r in rows],list(map(str,range(1,25))))

    def test_mixed_legacy_and_v2_movies_keep_distinct_click_targets(self):
        self.index.import_group('p','vod','b',[dict(stream_id='new'+str(i),category_id='b',name='New '+str(i),added=self.now+100-i) for i in range(6)])
        self.router._params['action']='widget_recent_vod'
        self.routes.dispatch(self.router)
        self.assertEqual(len(self.added),24)
        self.assertEqual(len({li.props['XCMate.MediaId'] for _,li,_ in self.added}),24)
        for url,li,is_folder in self.added:
            self.assertIn('sid='+li.props['XCMate.MediaId'],url)
            self.assertIn('kind=vod',url)
            self.assertFalse(is_folder)

    def test_real_native_movie_item_receives_typed_numeric_metadata(self):
        row=dict(sid='x',kind='vod',name='Movie',year='2024-01-01',rating='8.3',duration='01:30:00')
        value=self.items.describe(self.portal,'vod',row,{})
        original=ListItem.setInfo
        def strict(li,kind,info):
            for key in ('year','duration'):
                if key in info:self.assertIsInstance(info[key],int)
            if 'rating' in info:self.assertIsInstance(info['rating'],float)
            original(li,kind,info)
        with mock.patch.object(ListItem,'setInfo',strict):li=self.items.item(value)
        self.assertEqual((li.info['year'],li.info['rating'],li.info['duration']),(2024,8.3,5400))

    def test_invalid_movie_numbers_are_omitted_not_native_exceptions(self):
        value=self.items.describe(self.portal,'vod',dict(sid='x',kind='vod',name='Movie',year='NaN',rating='NaN',duration='broken'),{})
        self.assertFalse({'year','rating','duration'} & value['info'].keys())

    def test_true_empty_movie_directory_has_no_fake_icon_movie(self):
        self.index.replace_catalog('p','vod',[],self.catalogs['get_vod_categories'])
        self.router._params['action']='widget_recent_vod';self.routes.dispatch(self.router)
        self.assertEqual(self.added,[])
        self.assertEqual(len(self.ends),1)
        sys.modules['xbmcplugin'].setPluginCategory.assert_called_once()

    def test_failed_movie_directory_has_no_fake_icon_movie(self):
        self.router._params['action']='widget_recent_vod'
        with mock.patch.object(self.widgets,'snapshot',return_value=([],'BUDGET')):
            self.routes.dispatch(self.router)
        self.assertEqual(self.added,[])
        self.assertIn('Filmindex',sys.modules['xbmcplugin'].setPluginCategory.call_args.args[1])

    def test_vod_policy_invalidates_old_empty_cache_without_touching_series_cache(self):
        portal=self.portal
        for kind in ('vod','series'):
            key=self.widgets.policy(portal,kind)
            self.widgets.store(self.widgets.files('p',kind)[0],key,[])
        series_before=Path(self.widgets.files('p','series')[0]).read_bytes()
        # Actual .46 policy/unchanged index revision, not an arbitrary bad key.
        import hashlib
        legacy_policy=hashlib.sha256(json.dumps([str(portal['id']),'vod',portal.get('start_stream_id'),
            portal.get('start_group_id'),portal.get('include_vod',True),None,0,100],sort_keys=True).encode()).hexdigest()
        state=self.index.Reader('p').state('vod')
        self.widgets.store(self.widgets.files('p','vod')[0],legacy_policy,[],[state['revision'],state['updated']])
        rows,code=self.widgets.snapshot(portal,'vod',background=True)
        self.assertEqual(len(rows),24)
        self.assertEqual(Path(self.widgets.files('p','series')[0]).read_bytes(),series_before)

    def test_successful_series_reader_does_not_use_new_movie_payload_code(self):
        with mock.patch('widget_sql47.payloads',side_effect=AssertionError('series rewrite')):
            rows=self.widgets.WidgetReader('p').small('series')
        self.assertEqual([r['sid'] for r in rows],['1','2','3'])
        value=self.items.describe(self.portal,'series',dict(rows[0],year='2024',rating='8.2'),{})
        self.assertEqual(value['info']['year'],2024)
        self.assertEqual(value['info']['rating'],8.2)
        self.assertNotIn('XCMate.ProgrammeKey47',value['props'])

    def test_directory_stage_is_recorded_only_after_real_end_of_directory(self):
        self.router._params['action']='widget_recent_vod'
        events=[]
        def note(pid,kind,stage,*a,**kw):events.append(stage)
        with mock.patch('widget_diagnostics47.note',side_effect=note),mock.patch.object(sys.modules['xbmcplugin'],'endOfDirectory',side_effect=lambda *a,**kw:events.append('END')):
            self.routes.dispatch(self.router)
        self.assertLess(events.index('ITEMS'),events.index('END'))
        self.assertLess(events.index('END'),events.index('DIRECTORY'))

    def test_one_widget_preparation_error_does_not_starve_movie_or_series_publication(self):
        service=importlib.import_module('app_services')
        service._retry_after.clear()
        def prepare(pid,rows):
            if rows and rows[0]['kind']=='live':raise OSError('private source details must not escape')
        with mock.patch('widget_hooks45.prepare'),mock.patch('guide_store.refresh'),mock.patch('programme_index46.prepare_local'),mock.patch('widget_art44.prepare',side_effect=prepare),mock.patch('programme_assets47.prepare'),mock.patch('widget_diagnostics47.inspect_index'),mock.patch('widget_refresh45.publish') as publish:
            service.refresh_local()
        self.assertEqual([c.args[1] for c in publish.call_args_list],['live','vod','series'])

    def test_safe_diagnostics_never_log_titles_provider_urls_or_private_ids(self):
        diag=importlib.import_module('widget_diagnostics47');diag._seen.clear()
        with mock.patch.object(sys.modules['xbmc'],'log',create=True) as log,mock.patch.object(sys.modules['xbmc'],'LOGINFO',1,create=True):
            diag.note('PRIVATE-PORTAL','vod','SELECT','SQLITE_BUSY',selected=24,title='SECRET',url='https://private.invalid/user/pass')
        text=log.call_args.args[0]
        for secret in ('PRIVATE-PORTAL','SECRET','https://','private.invalid'):self.assertNotIn(secret,text)
        self.assertIn('selected=24',text)

    def test_full_live_group_native_navigation_still_has_137_exact_sender_targets(self):
        rows=[dict(stream_id=str(i),category_id='a',name='Station '+str(i)) for i in range(137)]
        self.index.import_group('p','live','a',rows);self.portal['start_stream_id']='136'
        self.router._params['action']='widget_live_start_group';self.routes.dispatch(self.router)
        self.assertEqual(len(self.added),137)
        self.assertEqual(self.added[0][1].props['XCMate.MediaId'],'136')
        self.assertEqual({li.props['XCMate.MediaId'] for _,li,_ in self.added},set(map(str,range(137))))

    def test_movie_snapshot_uses_one_readonly_connection_and_closes_it(self):
        module=importlib.import_module('widget_movie47');original=sqlite3.connect;opened=[]
        def connect(*a,**kw):
            self.assertIn('mode=ro',a[0]);db=original(*a,**kw);opened.append(db);return db
        with mock.patch.object(sqlite3,'connect',side_effect=connect):
            rows,code=self.widgets.snapshot(self.portal,'vod')
        self.assertEqual((len(rows),code),(24,'READY'))
        self.assertEqual(len(opened),1)
        with self.assertRaises(sqlite3.ProgrammingError):opened[0].execute('SELECT 1')

    def test_many_enabled_movie_groups_do_not_force_4096_key_overscan(self):
        db=self.index.connect(write=True)
        with db:db.executemany('INSERT OR IGNORE INTO groups VALUES(?,?,?,?,?)',
            [('p','vod','empty-'+str(i),'Empty '+str(i),i+2) for i in range(200)])
        db.close()
        self.index.import_group('p','vod','a',[dict(stream_id=str(i),category_id='a',name='Film',added=self.now+i) for i in range(500)])
        reader=importlib.import_module('widget_movie47').MovieReader('p')
        try:
            rows=reader.small('vod')
            self.assertEqual(len(rows),24)
            self.assertEqual(reader.stats47['V2_KEYS']['rows'],24)
        finally:reader.close()

    def test_actual_duplicate_movies_across_groups_expand_only_when_needed(self):
        for group in ('a','b','c','d'):
            self.index.import_group('p','vod',group,[dict(stream_id=str(i),category_id=group,name='Film '+str(i),added=self.now+i) for i in range(24)])
        reader=importlib.import_module('widget_movie47').MovieReader('p')
        try:
            rows=reader.small('vod')
            self.assertEqual(len(rows),24)
            self.assertEqual(len({r['sid'] for r in rows}),24)
            self.assertGreater(reader.stats47['V2_KEYS']['queries'],1)
        finally:reader.close()

    def test_movie_query_budget_does_not_expire_during_non_sql_cold_import_gap(self):
        reader=importlib.import_module('widget_movie47').MovieReader('p')
        self.addCleanup(reader.close)
        self.assertIsNotNone(reader.state('vod'))
        time.sleep(.8)  # Real scheduler/import gap; SQL budget stays strict.
        self.assertEqual(len(reader.small('vod')),24)
        self.assertLessEqual(reader._remaining47,.35)

    def test_movie_state_keys_and_payload_share_one_pinned_catalog_generation(self):
        reader=importlib.import_module('widget_movie47').MovieReader('p')
        reader.state('vod')
        self.index.import_group('p','vod','a',[dict(stream_id='new',category_id='a',name='New',added=self.now+100)])
        self.assertEqual(reader.small('vod')[0]['sid'],'1')
        reader.close()
        other=importlib.import_module('widget_movie47').MovieReader('p')
        try:self.assertEqual(other.small('vod')[0]['sid'],'new')
        finally:other.close()

    def test_movie_sql_error_closes_pinned_connection_and_keeps_lastgood(self):
        good,_=self.widgets.snapshot(self.portal,'vod');filename,_=self.widgets.files('p','vod')
        old=json.loads(Path(filename).read_text());old['at']=time.time()-3600;old['revision44']=['prior',0];Path(filename).write_text(json.dumps(old))
        module=importlib.import_module('widget_movie47');closed=[];original=module.MovieReader.close
        def close(reader):closed.append(True);return original(reader)
        error=self.index.IndexReadError('SQLITE_BUSY');error.code='SQLITE_BUSY'
        with mock.patch.object(module.MovieReader,'small',side_effect=error),mock.patch.object(module.MovieReader,'close',close):
            rows,code=self.widgets.snapshot(self.portal,'vod',background=True)
        # Force a different catalog revision to avoid the valid LastGood shortcut.
        self.assertEqual(rows,good);self.assertEqual(code,'SQLITE_BUSY');self.assertTrue(closed)

    def test_live_start_model_uses_local_group_names_without_loading_provider_json(self):
        catalog=importlib.import_module('live_catalog')
        prepared=[];builder=importlib.import_module('live_prepare47');original_model=builder.model;original_cached=self.client.get_cached_catalog
        def model(*a,**kw):value=original_model(*a,**kw);prepared.append(value);return value
        def cached(action):
            self.assertTrue(prepared,'provider JSON before first start-group model')
            return original_cached(action)
        with mock.patch.object(builder,'model',side_effect=model),mock.patch.object(self.client,'get_cached_catalog',side_effect=cached):
            future=catalog.prepare(self.portal,self.client,force=True)
            value=future.result(timeout=5)
        self.assertEqual(len(value[1]),3)
        self.assertEqual(len(future.first_model47['channels']),3)
        self.assertIsNotNone(future.model47['index'])
        self.assertEqual(future.model47['groups'][0]['category_name'],'A')
