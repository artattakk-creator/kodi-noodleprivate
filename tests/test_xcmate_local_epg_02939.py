"""Real published guide transactions; widgets never import or request provider IO."""
import importlib,sqlite3,sys,types,unittest
from unittest import mock
import xcmate027_fixture as model


class LocalEPG39(model.Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.store=importlib.import_module('guide_store');self.local=importlib.import_module('local_epg')
        self.channels=[dict(sid='1',epg_channel_id='xml')];self.install()

    def install(self):
        self.store.import_cache('p',{'xml':[
            dict(name='Provider',start_timestamp=self.now-100,stop_timestamp=self.now+100)],
            'manual':[
            dict(name='Mapped now',start_timestamp=self.now-100,stop_timestamp=self.now+100,_source_index=2),
            dict(name='Mapped next',start_timestamp=self.now+100,stop_timestamp=self.now+300,_source_index=2)]},revision='published-1')

    def test_widget_live_and_grid_resolve_same_manual_source_with_no_http(self):
        mapping={'1':'manual'};sys.modules['epg_sources'].configuration=lambda pid:dict(mappings=mapping)
        info=self.local.now_next('p',self.channels,mapping,self.now,client=self.client)['1']
        grid=importlib.import_module('guide_grid_data').page(self.portal,0,self.now-10,'a',self.client)
        channel=types.SimpleNamespace(tvg_id='xml',extra={'stream_id':'1'})
        live=importlib.import_module('tv_data').GuideSnapshot(self.portal,self.client);live.request([channel]);live.refresh()
        self.assertEqual(info['now'],'Mapped now');self.assertEqual(live.get('1',self.now)['now'],info['now'])
        self.assertEqual(grid['rows'][0]['events'][0]['title'],info['now'])
        self.router._params['action']='widget_live_start_group';self.routes.dispatch(self.router)
        self.assertEqual(self.added[0][1].props['XtreamMate.Now'],info['now'])
        self.assertIn('Mapped now',self.added[0][1].info['plot']);sys.modules['utils'].http_get.assert_not_called()

    def test_rollover_progress_and_gap_are_computed_from_local_event_times(self):
        def read(now):return self.local.now_next('p',self.channels,{'1':'manual'},now)['1']
        self.assertAlmostEqual(read(self.now)['progress'],.5)
        self.assertEqual(read(self.now+100)['now'],'Mapped next')
        self.assertEqual(read(self.now+300)['now'],'');self.assertIsNone(read(self.now+300)['progress'])
        self.assertEqual(read(self.now-101)['reason'],'FUTURE_ONLY')

    def test_missing_manual_mapping_never_uses_stale_provider_or_short_epg(self):
        info=self.local.now_next('p',self.channels,{'1':'missing'},self.now,self.client)['1']
        self.assertEqual(info['now'],'');self.assertEqual(info['reason'],'MANUAL_ID_MISSING')
        self.client._get_json.assert_not_called()

    def test_read_only_snapshot_preserves_payloads_and_only_allows_sqlite_coordination(self):
        before={p.name:p.read_bytes() for p in self.folder.iterdir() if p.is_file()}
        for _ in range(20):self.local.now_next('p',self.channels,{},self.now)
        after={p.name:p.read_bytes() for p in self.folder.iterdir() if p.is_file()}
        self.assertTrue(all(after[k]==v for k,v in before.items()))
        self.assertTrue(set(after)-set(before)<={'guide_v1.sqlite-wal','guide_v1.sqlite-shm'})

    def test_failed_publication_preserves_last_successful_revision(self):
        self.assertFalse(self.store.import_cache('p',{},revision='failed'))
        view=self.local.window('p',self.channels,{},self.now,self.now+300)
        self.assertEqual(view.revision[0],'published-1');self.assertEqual(view['xml'][0]['name'],'Provider')

    def test_sqlite_transaction_cannot_mix_new_metadata_with_old_programmes(self):
        original=sqlite3.connect;fired=[]
        def connect(*args,**kw):
            db=original(*args,**kw)
            if kw.get('uri'):
                def trace(sql):
                    if 'SELECT cid FROM guide_alias' in sql and not fired:
                        fired.append(True)
                        self.store.import_cache('p',{'xml':[dict(name='New',start_timestamp=self.now-100,stop_timestamp=self.now+100)]},revision='published-2',trusted_feed=True)
                db.set_trace_callback(trace)
            return db
        with mock.patch.object(self.local.sqlite3,'connect',side_effect=connect):
            old=self.local.window('p',self.channels,{},self.now,self.now+300)
        self.assertTrue(fired);self.assertEqual((old.revision[0],old['xml'][0]['name']),('published-1','Provider'))
        new=self.local.window('p',self.channels,{},self.now,self.now+300)
        self.assertEqual((new.revision[0],new['xml'][0]['name']),('published-2','New'))

    def test_existing_live_widget_is_bounded_to_twelve_and_start_channel_first(self):
        rows=[dict(stream_id=str(i),name='Channel '+str(i),category_id='a',epg_channel_id='xml') for i in range(1,1002)]
        self.index.replace_catalog('p','live',rows,self.catalogs['get_live_categories'])
        self.portal['start_stream_id']='1000';self.router._params['action']='widget_live_start_group'
        with mock.patch.object(sys.modules['epg'],'load_cache',side_effect=AssertionError('global hydrate')):
            self.routes.dispatch(self.router)
        # #241 expressly replaces the former twelve-sender UI contract.
        self.assertEqual(len(self.added),1001);self.assertIn('sid=1000',self.added[0][0])
        self.assertFalse(self.builtins)

    def test_missing_and_corrupt_guide_are_not_created_or_reset_by_widget_reads(self):
        from pathlib import Path
        p=Path(self.store.path());p.unlink()
        self.assertIsNone(self.local.window('p',self.channels,{},self.now,self.now+300));self.assertFalse(p.exists())
        p.write_bytes(b'broken')
        self.assertIsNone(self.local.window('p',self.channels,{},self.now,self.now+300));self.assertEqual(p.read_bytes(),b'broken')
