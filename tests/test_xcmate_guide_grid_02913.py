"""Local grid geometry, real SQLite, paged >2400 channels, strict Kodi controls."""
import importlib,json,os,sqlite3,sys,time,types,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ADDON,QueuedPool,Control

class GridTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for n in ('guide_grid_data','guide_grid_window'):sys.modules.pop(n,None)
        self.data=importlib.import_module('guide_grid_data');self.grid=importlib.import_module('guide_grid_window')
        p=mock.patch.object(self.grid,'ThreadPoolExecutor',QueuedPool);p.start();self.addCleanup(p.stop)
        self.store=importlib.import_module('guide_store');self.origin=int(time.time())//1800*1800
        self.store.import_cache('p',{'xml':[dict(channel='xml',start_timestamp=self.origin-600,stop_timestamp=self.origin+1800,name='Current',descr='Real details'),dict(channel='xml',start_timestamp=self.origin+1800,stop_timestamp=self.origin+3600,name='Next')]},now=self.origin-1000)

    def window(self):
        w=self.grid.GuideGridWindow('XCMateGuideGrid.xml',str(ADDON),'Default','720p');w.configure(self.router,self.portal)
        self.addCleanup(w.close);w.doModal();self.settle(w);return w

    def key(self,w,k):w.onAction(types.SimpleNamespace(getId=lambda:k));self.settle(w)

    def test_shared_axis_clips_and_keeps_duration_proportions(self):
        self.assertEqual(self.data.rectangle(0,3600,0),(0,298))
        self.assertEqual(self.data.rectangle(3600,7200,0),(298,299))
        self.assertEqual(self.data.rectangle(-100,1800,0),(0,149))
        self.assertIsNone(self.data.rectangle(-100,-1,0))
        self.assertEqual(self.data.rectangle(0,10800,0),(0,896))

    def test_manual_mapping_wins_and_missing_does_not_fall_back_silently(self):
        sys.modules['epg_sources'].configuration=lambda pid:dict(mappings={'1':'missing'},sources=[])
        page=self.data.page(self.portal,0,self.origin)
        self.assertEqual(page['rows'][0]['mapping'],'MANUAL');self.assertEqual(page['rows'][0]['events'],[])
        self.assertEqual(page['rows'][1]['events'][0]['title'],'Current')

    def test_native_grid_visible_focus_and_now_marker_do_not_start_playback(self):
        w=self.window();self.assertGreaterEqual(w.getFocusId(),1000)
        self.assertTrue(w.getControl(w.getFocusId()).visible);self.assertTrue(w.getControl(500).visible)
        self.assertEqual(w.getControl(700).kind,'textbox');self.assertEqual(w.rows[0]['channel']['name'],w.getControl(700).text)
        self.assertFalse(self.builtins);sys.modules['utils'].http_get.assert_not_called()

    def test_in_page_directions_do_not_query_database_or_network(self):
        w=self.window()
        with mock.patch.object(self.data,'page',side_effect=AssertionError('key query')):
            self.key(w,4);self.key(w,3);self.key(w,2);self.key(w,1)
        self.assertFalse(self.builtins);sys.modules['utils'].http_get.assert_not_called()

    def test_empty_data_is_named_empty_and_ok_watch_is_explicit(self):
        w=self.window();w.rows[0]['events']=[];w._render();self.assertIsNone(w._selected())
        self.assertIn('Keine',w.getControl(w.getFocusId()).label)
        self.dialog.select.return_value=-1;w.onClick(w.getFocusId());self.assertFalse(self.builtins)
        self.dialog.select.return_value=1;w.onClick(w.getFocusId())
        self.assertTrue(w._leaving);self.assertFalse(w._closed);self.assertFalse(self.builtins)
        w._leave_after=0;w._owner_tick()
        import guide_playback
        self.assertTrue(guide_playback.handoff(self.router,self.portal,w._play_request))
        self.assertIn('action=play_live',self.builtins[-1]);self.assertIn('sid=1',self.builtins[-1])

    def test_selected_event_details_context_back_keeps_grid_and_cursor(self):
        w=self.window();cursor=w.cursor;self.dialog.select.return_value=0
        w.onClick(w.getFocusId());self.assertIsNotNone(w._programme_request46);self.dialog.textviewer.assert_not_called()
        with mock.patch('programme_window46.show') as details:w._owner_tick();details.assert_called_once()
        self.assertFalse(w._closed);self.assertEqual(w.cursor,cursor)
        self.dialog.select.return_value=-1;self.key(w,117);self.assertFalse(w._closed)
        self.key(w,92);self.assertTrue(w._closed)

    def test_over_2400_channels_render_only_eight_and_page_synchronously(self):
        rows=[dict(stream_id=str(i),category_id='a',name='Channel '+str(i),epg_channel_id='xml') for i in range(2501)]
        self.index.import_group('p','live','a',rows)
        self.portal['start_stream_id']='0'
        w=self.window();self.assertEqual(w.total,2501);self.assertEqual(len(w.rows),8)
        for _ in range(8):self.key(w,4)
        self.assertEqual(w.offset,8);self.assertEqual(w.row,0);self.assertEqual(w.rows[0]['channel']['sid'],'8')
        self.assertLessEqual(len(w._cells),8*24);self.assertFalse(self.builtins)

    def test_readonly_guide_does_not_change_existing_database(self):
        before=Path(self.store.path()).read_bytes()
        with mock.patch.object(self.store,'connect',side_effect=AssertionError('write connector')):result=self.data.page(self.portal,0,self.origin)
        self.assertTrue(result['rows'][0]['events']);self.assertEqual(Path(self.store.path()).read_bytes(),before)

    def test_missing_database_is_not_created_and_no_programmes_are_invented(self):
        expected=[[ (e['start'],e['stop'],e['title']) for e in row['events']] for row in self.data.page(self.portal,0,self.origin)['rows']]
        Path(self.store.path()).unlink();result=self.data.page(self.portal,0,self.origin)
        # .47 may show only the exact previously committed shared LastGood.
        self.assertFalse(Path(self.store.path()).exists())
        self.assertEqual([[(e['start'],e['stop'],e['title']) for e in row['events']] for row in result['rows']],expected)
        with mock.patch('programme_snapshot47.fallback_window',return_value=None):
            self.assertTrue(all(not row['events'] for row in self.data.page(self.portal,0,self.origin)['rows']))

    def test_new_home_epg_route_is_action_and_legacy_route_still_exists(self):
        import home_menu
        home_menu.show(self.router,self.portal)
        row=next(row for row in self.added if 'action=guide_grid' in row[0]);self.assertFalse(row[2])
        self.assertIn('guide_browser',self.routes.ACTIONS);self.assertIn('guide_grid',self.routes.ACTIONS)

    def test_day_buttons_use_local_calendar_across_dst(self):
        if not hasattr(time,'tzset'):self.skipTest('POSIX timezone API')
        old=os.environ.get('TZ');os.environ['TZ']='Europe/Berlin';time.tzset()
        try:
            import datetime
            w=self.window();before=datetime.datetime(2026,10,25,0,0)
            w.cursor=int(time.mktime(before.timetuple()));stamp=w.cursor
            class FixedDate(datetime.date):
                @classmethod
                def today(cls):return cls(2026,10,25)
            with mock.patch.object(self.grid.datetime,'date',FixedDate):w._day(1)
            self.assertEqual(w.cursor-stamp,25*3600)
        finally:
            if old is None:os.environ.pop('TZ',None)
            else:os.environ['TZ']=old
            time.tzset()

    def test_fast_double_back_keeps_owner_until_transition_finishes(self):
        w=self.window();w._running=True
        self.key(w,92);self.assertTrue(w._leaving);self.assertFalse(w._closed)
        self.key(w,92);self.assertFalse(w._closed);self.assertFalse(self.builtins)
        w._leave_after=0;w._owner_tick();self.assertTrue(w._closed)

    def test_dense_schedule_pans_exactly_to_selected_event_without_recursive_load(self):
        db=self.store.connect()
        with db:db.execute('DELETE FROM programmes')
        db.close()
        data=[dict(channel='xml',start_timestamp=self.origin+n*60,stop_timestamp=self.origin+(n+1)*60,name='Short '+str(n)) for n in range(60)]
        self.store.import_cache('p',{'xml':data},now=self.origin-1)
        with mock.patch.object(self.grid.time,'time',return_value=self.origin):w=self.window()
        w.cursor=self.origin+29*60;w._render()
        self.assertEqual(w.origin,self.origin+29*60);self.assertTrue(w._loading)
        self.settle(w);self.assertFalse(w._loading);self.assertEqual(w._selected()['title'],'Short 29')


    def test_logos_use_existing_local_artwork_and_refresh_without_remote_textures(self):
        w=self.window();art=importlib.import_module('media_art')
        with mock.patch.object(art,'local_art',return_value=dict(thumb='/local/logo.img')):w._refresh_logos()
        self.assertEqual(w.getControl(720).image,'/local/logo.img')
        self.data.page(self.portal,0,self.origin);art.request.assert_called()
        sys.modules['utils'].http_get.assert_not_called()


    def test_m3u_watch_uses_existing_tagged_source_resolver(self):
        self.portal['type']='m3u';w=self.window();self.dialog.select.return_value=1
        w.onClick(w.getFocusId());self.assertFalse(self.builtins)
        w._leave_after=0;w._owner_tick()
        import guide_playback
        self.assertTrue(guide_playback.handoff(self.router,self.portal,w._play_request))
        self.assertIn('action=source_play',self.builtins[-1]);self.assertIn('sid=1',self.builtins[-1])


    def test_bookmark_contains_ids_facts_and_no_source_urls(self):
        bookmarks=importlib.import_module('guide_bookmarks')
        event=dict(start=self.origin,stop=self.origin+1800,title='A',url='SECRET')
        bookmarks.remember('p','1',event)
        text=(self.folder/'guide_bookmarks_v1.json').read_text();self.assertNotIn('SECRET',text)
        self.assertEqual(len(json.loads(text)),1)
