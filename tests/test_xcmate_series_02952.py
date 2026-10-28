"""Post-wizard selection to durable jobs, real catalogue heads and widget data."""
import importlib,json,os,sqlite3,sys,threading,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture


class Series52(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.groups=importlib.import_module('group_selection');self.delta=importlib.import_module('catalog_delta');self.control=importlib.import_module('catalog_delta52')
        self.portal['include_series']=True
        self.cats=[dict(category_id='a',category_name='Series A'),dict(category_id='b',category_name='Series B')]
        self.calls=[];self.count=7;self.fail=False;self.empty=False
        def entries(action,cid,**kw):
            self.calls.append((action,cid))
            if self.fail:raise OSError('synthetic network failure')
            for n in range(0 if self.empty else self.count):
                if kw['cancel']():raise InterruptedError()
                yield dict(series_id=cid+str(n),category_id=cid,name='Series '+str(n),cover='https://images.invalid/'+str(n)+'.png')
        self.client52=types.SimpleNamespace(get_cached_catalog=lambda action:[],_get_json=mock.Mock(return_value=self.cats),iter_catalog=entries)
        patch=mock.patch.object(sys.modules['xtream'],'XtreamClient',return_value=self.client52);patch.start();self.addCleanup(patch.stop)
        db=self.index.connect(write=True)
        with db:
            for table in ('titles','heads','items_v2','catalog','groups','sync_status'):db.execute('DELETE FROM '+table+" WHERE pid='p' AND kind='series'")
        db.close();self.groups.save('p',[],'series',known=['a','b'])
    def select(self,categories):
        self.groups.save('p',categories,'series',known=['a','b'])
        self.delta.request_many(self.portal,'series',categories,retry=True)
    def other_rows(self):
        db=self.index.connect()
        try:return [tuple(r) for r in db.execute("SELECT * FROM readable_titles WHERE kind IN ('live','vod') ORDER BY kind,sid")]
        finally:db.close()

    def test_confirmed_group_selection_queues_and_imports_without_wizard(self):
        self.portal['include_series']=False;self.dialog.select.side_effect=[1,6]
        self.assertTrue(self.groups.choose_groups(self.portal,'series',categories=self.cats,allow_refresh=False))
        self.assertTrue(self.portal['include_series']);self.assertTrue(self.delta.pending('p','series'))
        while self.delta.run_next():pass
        self.assertEqual(self.index.Reader('p').page('series')[1],14)
        self.assertEqual({c for _,c in self.calls},{'a','b'})

    def test_stale_empty_category_cache_is_reloaded_for_requested_group(self):
        self.select(['b']);self.delta.run_next()
        self.client52._get_json.assert_called_once_with('get_series_categories',force_refresh=True)
        self.assertEqual(self.index.Reader('p').page('series',category='b')[1],7)

    def test_restart_reconciles_previously_enabled_but_unindexed_groups(self):
        self.groups.save('p',['a','b'],'series',known=['a','b'])
        self.assertFalse(self.delta.pending('p','series'));self.control.reconcile_series(self.portal)
        self.assertTrue(self.delta.pending('p','series'));importlib.reload(self.delta)
        while self.delta.run_next():pass
        self.assertEqual(self.index.Reader('p').page('series')[1],14)

    def test_incremental_series_import_keeps_every_live_and_movie_row(self):
        before=self.other_rows();self.select(['b']);self.delta.run_next()
        self.assertEqual(self.other_rows(),before)

    def test_large_series_group_is_not_cut_off_at_one_page(self):
        self.count=1201;self.select(['a']);self.delta.run_next()
        self.assertEqual(self.index.Reader('p').page('series',limit=1)[1],1201)
        self.assertEqual(self.delta.states('p','series')[0]['stored'],1201)

    def test_widget_snapshot_and_catalogue_share_new_revision_without_rebinding(self):
        self.select(['a']);self.delta.run_next()
        widget=importlib.import_module('widget_data41')
        rows,code=widget.snapshot(self.portal,'series',background=True)
        self.assertEqual(code,'READY');self.assertEqual(len(rows),7)
        self.assertEqual({r['sid'] for r in rows},{r['sid'] for r in self.index.Reader('p').page('series')[0]})
        self.assertTrue(all(r['cover'].startswith('https://images.invalid/') for r in rows))

    def test_reconcile_and_duplicate_saves_do_not_restart_published_heads(self):
        self.select(['a']);self.delta.run_next();before=len(self.calls)
        for _ in range(5):self.control.reconcile_series(self.portal);self.delta.request_many(self.portal,'series',['a'])
        self.assertFalse(self.delta.run_next());self.assertEqual(len(self.calls),before)

    def test_network_failure_retains_old_data_and_has_bounded_explicit_retry(self):
        before=self.other_rows();self.fail=True;self.select(['b']);self.delta.run_next()
        row=self.delta.states('p','series')[0];self.assertEqual(row['code'],'FAILED');self.assertEqual(row['attempts'],1)
        self.assertFalse(self.delta.run_next());self.assertEqual(self.other_rows(),before)
        self.fail=False;self.delta.request_many(self.portal,'series',['b'],retry=True);self.delta.run_next()
        self.assertEqual(self.delta.states('p','series')[0]['code'],'READY')

    def test_empty_source_never_reports_success_or_erases_working_catalogues(self):
        self.empty=True;before=self.other_rows();self.select(['b']);self.delta.run_next()
        self.assertEqual(self.delta.states('p','series')[0]['code'],'FAILED');self.assertEqual(self.other_rows(),before)

    def test_cancel_pending_jobs_does_not_run_provider_and_allows_explicit_retry(self):
        self.select(['a','b']);self.control.cancel_jobs('p','series')
        self.assertFalse(self.delta.run_next());self.assertEqual(self.calls,[])
        self.delta.request_many(self.portal,'series',['b'],retry=True);self.delta.run_next()
        self.assertEqual(self.index.Reader('p').page('series')[1],7)

    def test_cancellation_during_stream_preserves_previous_heads_and_other_media(self):
        self.select(['a']);before=self.other_rows()
        original=self.client52.iter_catalog
        def cancelled(*args,**kwargs):
            for n,row in enumerate(original(*args,**kwargs)):
                if n==2:self.control.cancel_jobs('p','series')
                yield row
        self.client52.iter_catalog=cancelled
        with mock.patch('catalog_delta52.time.monotonic',side_effect=lambda:time.perf_counter()*10000):self.delta.run_next()
        self.assertEqual(self.delta.states('p','series')[0]['code'],'CANCELLED')
        self.assertIsNone(self.index.Reader('p').state('series'));self.assertEqual(self.other_rows(),before)

    def test_missing_remote_category_is_failure_not_empty_success(self):
        self.client52._get_json.return_value=[];self.select(['b']);self.delta.run_next()
        self.assertEqual(self.delta.states('p','series')[0]['code'],'FAILED');self.assertEqual(self.calls,[])

    def test_series_status_control_has_retry_and_cancel_without_changing_selection(self):
        self.select(['a']);self.dialog.select.return_value=2
        before=self.groups.load('p','series');self.control.manage(self.portal,'series')
        self.assertEqual(self.groups.load('p','series'),before)
        self.assertEqual(self.delta.states('p','series')[0]['code'],'CANCELLED')
        self.assertIn('Nachimport',self.groups._menu_items('series',set(),[],set(),False)[8])

    def test_whole_worker_os_lease_rejects_overlap_even_after_job_deadline(self):
        self.select(['a']);entered=threading.Event();release=threading.Event();outcome=[]
        @self.control.serial_worker
        def held():
            entered.set();release.wait(5);return True
        thread=threading.Thread(target=lambda:outcome.append(held()))
        thread.start()
        try:
            self.assertTrue(entered.wait(2))
            with mock.patch.object(self.delta.time,'time',return_value=time.time()+1000):
                self.assertFalse(self.delta.run_next())
            self.assertEqual(self.calls,[])
        finally:release.set();thread.join(5)
        self.assertEqual(outcome,[True]);self.assertTrue(self.delta.run_next())

    def test_disabled_pending_group_is_cancelled_without_touching_other_catalogues(self):
        self.select(['a']);before=self.other_rows();self.groups.save('p',[],'series',known=['a','b'])
        self.assertTrue(self.delta.run_next());self.assertEqual(self.calls,[])
        self.assertEqual(self.delta.states('p','series')[0]['code'],'CANCELLED');self.assertEqual(self.other_rows(),before)

    def test_existing_bingie_binding_receives_imported_series_without_reassignment(self):
        from test_xcmate_widget_refresh_02945 import WidgetRefresh45
        self.select(['b']);self.delta.run_next()
        w=importlib.import_module('widget_refresh45');items=importlib.import_module('widget_items45')
        rows,code=importlib.import_module('widget_data41').snapshot(self.portal,'series',background=True)
        self.w=w;self.h=importlib.import_module('widget_hooks45')
        control=WidgetRefresh45.control(self,[],kind='series')
        WidgetRefresh45.home(self,control,kind='series')
        w._next=0;w._seen={}
        self.assertTrue(w.publish(self.portal,'series',rows,code));w.poll()
        self.assertEqual({li.props['XCMate.MediaId'] for li in control.items},{'b'+str(i) for i in range(7)})
        self.assertEqual(control.refreshes,1);self.assertEqual(control.resets,0)
        self.assertFalse(self.builtins)
