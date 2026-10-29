"""Read-only catalogue and optional enrichment must not hide bound widgets."""
import builtins,errno,importlib,sqlite3,sys,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ListItem


class WidgetData56(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.data=importlib.import_module('widget_data41')

    def readonly_cache(self):
        original=builtins.open
        def open_file(file,*args,**kwargs):
            if str(file).endswith('.lock'):raise OSError(errno.EROFS,'synthetic read-only cache')
            return original(file,*args,**kwargs)
        return mock.patch('builtins.open',side_effect=open_file)

    def test_readable_movies_and_series_survive_unwritable_snapshot_lock_without_writes(self):
        before={str(p):p.read_bytes() for p in self.folder.rglob('*') if p.is_file()}
        with self.readonly_cache():
            for kind in ('vod','series'):
                rows,code=self.data.snapshot(self.portal,kind)
                self.assertTrue(rows,kind);self.assertEqual(code,'READ_ONLY')
        # SQLite may create its own WAL read-mark files even for mode=ro.
        # No main database, profile, snapshot or lock file may be changed.
        after={str(p):p.read_bytes() for p in self.folder.rglob('*') if p.is_file() and not p.name.endswith(('-wal','-shm'))}
        self.assertEqual({k:v for k,v in before.items() if not k.endswith(('-wal','-shm'))},after)

    def test_existing_unchanged_routes_emit_real_items_under_readonly_cache(self):
        with self.readonly_cache():
            for action,kind in [('widget_recent_vod','vod'),('widget_recent_series','series')]:
                self.added.clear();self.ends.clear();self.router._directory_done=False;self.router._params.update(action=action)
                self.routes.dispatch(self.router)
                self.assertTrue(self.added);self.assertEqual(len(self.ends),1)
                self.assertTrue(all(li.props.get('XCMate.WidgetKind41')==kind for _,li,_ in self.added))
                self.assertTrue(all('action=media_detail' in url for url,_,_ in self.added))
        self.assertFalse(self.builtins)

    def test_series_metadata_is_kodi_typed_like_the_working_native_media_view(self):
        widgets=importlib.import_module('widget_items45')
        value=widgets.describe(self.portal,'series',dict(sid='s',kind='series',name='Series',year='2024-01-01',rating='8.2',duration='01:30:00'),{})
        self.assertEqual(value['info'].get('year'),2024);self.assertEqual(value['info'].get('rating'),8.2)
        self.assertEqual(value['info'].get('duration'),5400)

    def test_optional_epg_failure_does_not_remove_the_150_station_base_row(self):
        self.index.import_group('p','live','a',[dict(stream_id=str(i),category_id='a',name='Station '+str(i),epg_channel_id='xml'+str(i)) for i in range(150)])
        home=importlib.import_module('widget_home50')
        with mock.patch('widget_group46.infos',side_effect=sqlite3.OperationalError('synthetic busy')):
            values,code=home.values(self.portal)
        self.assertEqual(code,'READY');self.assertEqual(len(values),150)
        self.assertTrue(all('action=play_live' in v['url'] for v in values));self.assertFalse(self.builtins)

    def test_disabled_and_true_empty_series_are_not_fake_settings_tiles(self):
        self.portal['include_series']=False;self.router._params.update(action='widget_recent_series')
        self.routes.dispatch(self.router);self.assertEqual(self.added,[])
        self.portal['include_series']=True;self.added.clear();self.ends.clear();self.router._directory_done=False
        self.index.replace_catalog('p','series',[],self.catalogs['get_series_categories'])
        self.routes.dispatch(self.router);self.assertEqual(self.added,[]);self.assertEqual(len(self.ends),1)

    def test_all_kinds_have_readonly_access_during_snapshot_lock_contention(self):
        import fcntl
        for kind in ('vod','series','live'):
            filename,lock=self.data.files('p',kind)
            with open(lock,'a') as stream:
                fcntl.flock(stream,fcntl.LOCK_EX|fcntl.LOCK_NB)
                with mock.patch.object(self.data,'store',side_effect=AssertionError('no lock-free writes')):
                    rows,code=self.data.snapshot(self.portal,kind)
            self.assertTrue(rows,kind);self.assertEqual(code,'READ_ONLY');self.assertFalse(Path(filename).exists())

    def test_readonly_reader_observes_committed_rows_during_an_uncommitted_wal_writer(self):
        db=sqlite3.connect(self.index.path());db.execute('BEGIN IMMEDIATE')
        try:
            db.execute("UPDATE titles SET payload='uncommitted invalid payload' WHERE pid='p' AND kind='series'")
            with self.readonly_cache():rows,code=self.data.snapshot(self.portal,'series')
            self.assertTrue(rows);self.assertTrue(all(r['name'] for r in rows));self.assertEqual(code,'READ_ONLY')
        finally:db.rollback();db.close()

    def test_movie_and_series_native_items_have_ten_distinct_covers_and_unchanged_targets(self):
        from urllib.parse import urlsplit,parse_qs
        from artwork_visible import KODI_OPTIONS
        import hashlib,time
        art=importlib.import_module('widget_art44')
        for kind,action in [('vod','widget_recent_vod'),('series','widget_recent_series')]:
            records=[dict(stream_id=str(i),series_id=str(i),category_id='a',name=kind+str(i),stream_icon='https://images.example.test/'+kind+str(i)+'.jpg',cover='https://images.example.test/'+kind+str(i)+'.jpg',added=self.now+i) for i in range(12)]
            self.index.import_group('p',kind,'a',records)
            approved={hashlib.sha256(r['cover'].encode()).hexdigest():dict(uri=r['cover']+KODI_OPTIONS,until=time.time()+29) for r in records}
            self.added.clear();self.ends.clear();self.router._directory_done=False;self.router._params.update(action=action)
            with mock.patch('artwork_config.persistent',return_value=False),mock.patch.object(art,'read',return_value=approved):self.routes.dispatch(self.router)
            self.assertGreaterEqual(len(self.added),10);self.assertGreaterEqual(len({li.art['poster'] for _,li,_ in self.added}),10)
            for url,li,folder in self.added:
                query=parse_qs(urlsplit(url).query)
                self.assertEqual(query['action'],['media_detail']);self.assertEqual(query['kind'],[kind]);self.assertEqual(query['pid'],['p'])
                self.assertFalse(folder);self.assertNotIn('SECRET',url)

    def test_readonly_reload_uses_existing_hook_without_disk_or_skin_writes(self):
        hooks=importlib.import_module('widget_hooks45');hooks._next=0;hooks._memory56.clear()
        binding=dict(code='READY',bindings=[dict(pid='p',kind='series',hooks=['XCMate.Widget45.Reload.series'])])
        with mock.patch.object(hooks,'probe',return_value=binding),mock.patch('tempfile.mkstemp',side_effect=OSError(errno.EROFS,'synthetic')):
            hooks.prepare()
        self.assertEqual(hooks.read()['bindings'],binding['bindings'])
        rows,code=self.data.snapshot(self.portal,'series');bridge=importlib.import_module('widget_readonly56')
        with mock.patch('tempfile.mkstemp',side_effect=AssertionError('readonly publication write')):
            self.assertTrue(bridge.publish(self.portal,'series',rows))
        notice=importlib.import_module('widget_notice46')
        self.assertIn(('p','series'),notice._pending);self.assertEqual(notice._hooks[('p','series')],['XCMate.Widget45.Reload.series'])

    def test_missing_explicit_portal_never_silently_uses_another_account(self):
        self.router._params.update(action='widget_recent_series',pid='missing')
        from widget_entry46 import dispatch
        self.assertTrue(dispatch(self.router));self.assertEqual(self.added,[])
        self.assertFalse(self.builtins)

    def test_readonly_queries_respect_disabled_media_groups(self):
        import group_selection
        group_selection.save('p',[],kind='series',known=['a','b'])
        with self.readonly_cache():rows,code=self.data.snapshot(self.portal,'series')
        self.assertEqual(rows,[]);self.assertEqual(code,'READ_ONLY')

    def test_series_point_reads_are_bounded_primary_key_seeks(self):
        from widget_movie47 import MovieReader
        self.index.import_group('p','series','a',[dict(series_id=str(i),category_id='a',name='Series '+str(i),added=self.now+i) for i in range(12000)])
        reader=MovieReader('p',kind='series');original=reader._query;plans=[]
        def query(sql,args=(),kind=None):
            if 'UNION ALL' in sql and 'payload' in sql:
                db=sqlite3.connect(self.index.path())
                try:plans.extend(row[3] for row in db.execute('EXPLAIN QUERY PLAN '+sql,args))
                finally:db.close()
            return original(sql,args,kind)
        try:
            with mock.patch.object(reader,'_query',side_effect=query):rows=reader.small('series')
        finally:reader.close()
        self.assertEqual(len(rows),24);self.assertEqual(rows[0]['sid'],'11999')
        self.assertEqual(sum('sqlite_autoindex_items_v2_1' in p for p in plans),24)
        self.assertFalse(any('SCAN' in p for p in plans))

    def test_missing_event_images_leave_station_names_and_icons_in_native_basic_feed(self):
        home=importlib.import_module('widget_home50');values,code=home.values(self.portal)
        self.assertTrue(values);self.assertTrue(all(v['label'] for v in values))
        self.assertTrue(all(v['art']['thumb'].endswith('tv.png') or v['props']['XCMate.ProgrammeLogo46'] for v in values))
        self.assertTrue(all(v['props']['XCMate.ProgrammeImage46'] for v in values))
