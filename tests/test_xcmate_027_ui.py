"""Native XML callback and route integration models, no Android/skin claims."""
import ast
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import types
import unittest
from unittest import mock
import urllib.parse

from xcmate027_fixture import Fixture,ADDON,LIB,ROOT,WindowXML


class NavigationTests(Fixture,unittest.TestCase):
    def test_root_six_items_for_one_or_many_accounts_and_setup_without_accounts(self):
        spec=importlib.util.spec_from_file_location('main027_actual',LIB/'main.py')
        module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        router=module.Router(['plugin://plugin.video.xtreammate','7','?action=root'])
        for accounts in ([self.portal],[self.portal,dict(self.portal,id='other',name='Other')]):
            self.portals=accounts;self.added.clear();router._root()
            self.assertEqual([li.label for _,li,_ in self.added],['Startkanal','Live-TV','EPG','Filme','Serien','Einstellungen'])
            self.assertFalse(self.builtins)
        self.portals=[];self.added.clear();router._root()
        self.assertNotEqual(len(self.added),6)
        self.assertTrue(any('setup_wizard' in url for url,_,_ in self.added))

    def test_settings_ten_categories_and_maintenance_only_diagnostics(self):
        home=importlib.import_module('home_menu')
        home.settings(self.router,self.portal)
        self.assertEqual(len(self.added),10)
        self.assertFalse(any('popup_probe' in url for url,_,_ in self.added))
        self.added.clear();home.settings(self.router,self.portal,'maintenance')
        self.assertTrue(any('popup_probe' in url for url,_,_ in self.added))
        self.added.clear();home.settings(self.router,self.portal,'remote')
        self.assertTrue(any('remote_learn' in url for url,_,_ in self.added))

    def test_explicit_disabled_or_unknown_portal_never_falls_into_another_account(self):
        self.router._params['pid']='unknown'
        self.assertIsNone(self.routes.portal_for(self.router))
        self.router._params['pid']='p';self.portal['enabled']=False
        self.assertIsNone(self.routes.portal_for(self.router))

    def test_start_channel_validates_cache_then_uses_frozen_direct_route(self):
        self.router._params['action']='home_start';self.router._play_start_direct=mock.Mock()
        self.routes.dispatch(self.router)
        self.router._play_start_direct.assert_called_once()
        self.router._play_start_direct.reset_mock();self.portal['start_stream_id']='missing'
        self.routes.dispatch(self.router)
        self.router._play_start_direct.assert_not_called();self.dialog.yesno.assert_called_once()

    def test_background_epg_refresh_reuses_coverage_without_running_download_on_service_thread(self):
        tree=ast.parse((ADDON/'service.py').read_text())
        cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='IPTVMasterService')
        method=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='_maybe_refresh_epg')
        targets=[]
        class Worker:
            def __init__(self,target,**kwargs): targets.append(target)
            def start(self): pass
            def is_alive(self): return False
        namespace=dict(setting_bool=lambda *a:True,setting_int=lambda *a:12,time=time,
                       threading=types.SimpleNamespace(Thread=Worker),info=lambda *a:None,error=lambda *a:None)
        exec(compile(ast.Module(body=[method],type_ignores=[]),'service.py','exec'),namespace)
        service=types.SimpleNamespace(_last_epg=0,_epg_worker=None,abortRequested=lambda:False)
        refresh=mock.Mock();sys.modules['epg'].ensure_epg_loaded_for_portal=refresh
        self.cache={'xml':[dict(name='Full guide',start_timestamp=self.now-10,stop_timestamp=self.now+10*86400)]}
        namespace['_maybe_refresh_epg'](service)
        refresh.assert_not_called();self.assertEqual(len(targets),1)
        targets[0]();refresh.assert_not_called()
        self.cache['xml'][0]['stop_timestamp']=self.now+3600
        targets[0]();refresh.assert_called_once_with(self.portal,force=False)

    def test_search_has_three_true_counts_and_paginates_beyond_fifty(self):
        self.router._params.update(action='global_search',q='house of dragon')
        self.routes.dispatch(self.router)
        self.assertEqual([li.label for _,li,_ in self.added],['LIVE-TV · 1 Treffer','FILME · 100 Treffer','SERIEN · 3 Treffer'])
        self.added.clear();self.router._params.update(action='search_section',kind='vod',offset='96')
        self.routes.dispatch(self.router)
        media=[(u,li) for u,li,_ in self.added if 'action=media_detail' in u]
        self.assertEqual(len(media),4)
        self.assertTrue(all('SECRET' not in u and 'provider.invalid' not in u for u,_ in media))

    def test_widgets_start_group_start_first_correct_content_and_no_credential_paths(self):
        self.router._params['action']='widget_live_start_group'
        self.cache={'xml':[dict(name='Actual Now',start_timestamp=self.now-100,stop_timestamp=self.now+100),
                           dict(name='Actual Next',start_timestamp=self.now+100,stop_timestamp=self.now+400)]}
        self.routes.dispatch(self.router)
        self.assertEqual(len(self.added),3)
        self.assertIn('sid=1',self.added[0][0])
        self.assertEqual(self.added[0][1].props['XtreamMate.Now'],'Actual Now')
        self.assertEqual(self.added[0][1].props['XtreamMate.Next'],'Actual Next')
        self.assertFalse(self.added[0][2])
        for action,kind in (('widget_recent_vod','vod'),('widget_recent_series','series')):
            self.added.clear();self.router._params['action']=action;self.routes.dispatch(self.router)
            self.assertIn('action=media_detail',self.added[0][0]);self.assertIn('kind='+kind,self.added[0][0])
            self.assertTrue(self.added[0][2]);self.assertTrue(any('Alle anzeigen' in li.label for _,li,_ in self.added))
        self.assertTrue(all('SECRET' not in url and 'https%3A' not in url for url,_,_ in self.added))
        sys.modules['utils'].http_get.assert_not_called()

    def test_widgets_share_manual_epg_mapping_over_stale_alias(self):
        self.cache={'1':[dict(name='Wrong',start_timestamp=self.now-100,stop_timestamp=self.now+100)],
                    'right':[dict(name='Mapped',start_timestamp=self.now-100,stop_timestamp=self.now+100)]}
        sys.modules['epg_sources'].configuration=lambda pid:{'mappings':{'1':'right'},'sources':[]}
        self.router._params['action']='widget_live_start_group';self.routes.dispatch(self.router)
        self.assertEqual(self.added[0][1].props['XtreamMate.Now'],'Mapped')

    def test_cold_widgets_show_cache_status_without_inventing_titles_or_fetching(self):
        Path(self.index.path()).unlink()
        for action in ('widget_live_start_group','widget_recent_vod','widget_recent_series'):
            self.added.clear();self.router._params['action']=action;self.routes.dispatch(self.router)
            self.assertTrue(self.added)
            self.assertTrue(any('wird geladen' in li.label or 'nicht lokal verfügbar' in li.label for _,li,_ in self.added))
            self.assertFalse(any('media_detail' in url or 'play_live' in url for url,_,_ in self.added))
        sys.modules['utils'].http_get.assert_not_called()

    def test_first_active_movie_group_native_left_edge_expand_and_right_collapse(self):
        w=self.media_window()
        self.assertEqual(w.mode,'landing');self.assertEqual(w.total,100)
        w.native(4);self.assertEqual(w.focus,120);w.native(7);w._pool.drain()
        self.assertEqual((w.mode,w.category),('grid','a'))
        w.native(1);self.assertEqual(w.mode,'groups');self.assertEqual(w.focus,200)
        w.native(2);self.assertEqual(w.mode,'grid');self.assertEqual(w._cols,6)
        self.assertFalse(w.getControl(200).visible)
        w.native(2);self.assertEqual(w._last_position,1)
        w.native(1);self.assertEqual(w._last_position,0);self.assertEqual(w.mode,'grid')
        w.native(1);self.assertEqual(w.mode,'groups')

    def test_left_edge_after_first_grid_row_preserves_identity_despite_native_wrap(self):
        w=self.media_window();w.native(4);w.native(7);w._pool.drain()
        w.native(1);w.native(2)
        w.getControl(210).selectItem(6);w._last_position=6
        w.native(1)  # Native panel can move to 5 before Python handles the edge.
        self.assertEqual(w.mode,'groups');self.assertEqual(w.getControl(210).selected,6)
        w.native(2);self.assertEqual(w.getControl(210).selected,6)

    def test_empty_group_keeps_group_focus_and_recovers_with_another_group(self):
        w=self.media_window();w.native(4);w.native(7);w._pool.drain()
        w.native(1);w.native(4);w.native(7);w._pool.drain()
        self.assertEqual((w.category,w.mode,w.focus),('b','groups',200))
        w.native(2);self.assertEqual(w.focus,200)
        w.native(3);w.native(7);w._pool.drain()
        self.assertEqual((w.category,w.mode),('a','grid'))

    def test_native_cover_click_opens_details_once_and_back_restores_cover_position(self):
        w=self.media_window()
        w.native(2);w.native(2);self.assertEqual(w._last_position,2)
        w.native(7);self.assertEqual(w.mode,'detail')
        self.assertEqual(self.builtins,[])
        # Metadata runs only after the key callback, by the worker queue.
        self.client._get_json.reset_mock()
        self.assertTrue(w._pool.jobs);w._pool.drain()
        self.client._get_json.assert_called_once()
        self.assertIn('Actual plot',w.getControl(320).text)
        w.native(92);w._pool.drain()
        self.assertEqual((w.mode,w._last_position),('landing',2))

    def test_rail_all_hundred_items_reachable_with_bounded_native_controls(self):
        w=self.media_window();ids=[]
        for page in range(5):
            ids.extend(r['sid'] for r in w.rows)
            self.assertLessEqual(len(w.getControl(110).items),24)
            if w.offset+len(w.rows)<w.total:
                w.getControl(110).selectItem(len(w.rows)-1);w._last_position=len(w.rows)-1
                w.native(2);w._pool.drain()
        self.assertEqual(len(ids),100);self.assertEqual(len(set(ids)),100)
        self.assertLess(len(w.controls),20)

    def test_favourites_resume_and_trailer_are_real_conditional_actions(self):
        self.state.save_progress(dict(pid='p',kind='vod',sid='1'),1050,2700)
        w=self.media_window();w.native(7);w._pool.drain()
        actions=dict((key,label) for label,key in w.actions)
        self.assertIn('resume',actions);self.assertIn('00:17:30',actions['resume'])
        self.assertIn('trailer',actions)
        idx=next(i for i,a in enumerate(w.actions) if a[1]=='favourite')
        w.getControl(300).selectItem(idx);w.native(7)
        self.assertTrue(self.state.favourite('p','vod','1'))
        self.assertIn('Aus Favoriten entfernen',[label for label,_ in w.actions])
        idx=next(i for i,a in enumerate(w.actions) if a[1]=='trailer')
        w.getControl(300).selectItem(idx);w.native(7)
        self.router._play_youtube_id.assert_called_once_with('abcdefghijk')

    def test_series_has_numerically_sorted_seasons_and_starts_only_selected_episode(self):
        w=self.media_window('series');w.native(7);w._pool.drain()
        self.assertEqual([(e['season'],e['episode']) for e in w.episodes],[(1,1),(1,2),(2,1)])
        w.getControl(300).selectItem(0);w.native(7)
        self.assertEqual(w.mode,'seasons');w.native(7)
        self.assertEqual(w.mode,'episodes');w.native(4);w.native(7)
        self.assertIn('kind=episode',self.builtins[-1]);self.assertIn('sid=12',self.builtins[-1])
        self.assertNotIn('SECRET',self.builtins[-1])

    def test_back_cancels_late_metadata_without_switching_view_or_focus(self):
        w=self.media_window();w.native(7)
        self.assertEqual(w.mode,'detail')
        w.native(92);w._pool.drain()
        self.assertEqual(w.mode,'landing');self.assertEqual(w.focus,110)

    def test_guide_starts_in_start_channel_group_and_native_group_navigation(self):
        self.cache={'xml':[dict(channel='xml',name='Actual',start_timestamp=self.now-60,stop_timestamp=self.now+3600)]}
        w=self.guide_window()
        self.assertEqual(w.category,'a')  # Start channel beats configured group b.
        self.assertTrue(any(e['title']=='Actual' for e in w.programmes))
        w.native(1);self.assertEqual(w.focus,200)
        w.native(2);self.assertEqual(w.focus,210)
        w.native(2);self.assertEqual(w.focus,220)
        w.native(1);self.assertEqual(w.focus,210)

    def test_guide_ten_days_missing_data_is_honest_no_download_on_navigation(self):
        self.options['epg_days']=10;w=self.guide_window()
        for _ in range(12): w.onClick(311);w._pool.drain()
        self.assertEqual(w.day,9)
        self.assertIn('keine echten Programmdaten',w.getControl(220).items[0].label)
        sys.modules['utils'].http_get.assert_not_called()

    def test_guide_pending_channel_query_cannot_remind_previous_channels_programme(self):
        self.cache={'xml':[dict(channel='xml',name='Actual',start_timestamp=self.now-60,stop_timestamp=self.now+3600)]}
        w=self.guide_window();self.assertTrue(w.programmes)
        w.native(4)  # Channel changed; worker has not run yet.
        self.assertEqual(w.programmes,[]);self.assertEqual(w.getControl(220).items,[])
        w.native(2);w.native(7)
        self.dialog.select.assert_not_called()
        w._pool.drain();self.assertEqual(w.sid,'2');self.assertTrue(w.programmes)

    def test_bad_image_headers_and_giant_images_rejected_before_native_rendering(self):
        import struct
        art=importlib.import_module('media_art')
        self.assertRaises(ValueError,art.dimensions,b'not an image')
        png=b'\x89PNG\r\n\x1a\n'+b'\0'*8+struct.pack('>II',100000,100000)
        sys.modules['utils'].http_get.side_effect=None;sys.modules['utils'].http_get.return_value=(png,{})
        self.assertRaises(ValueError,art.fetch,'https://image.invalid/huge')
        self.assertFalse(any(self.folder.glob('media_art_v1/*.img')))

    def test_xml_window_factory_rejects_non_api_constructor_keywords(self):
        with self.assertRaises(TypeError):
            WindowXML('XCMateMedia.xml',str(ADDON),router=self.router)

    def test_detail_metadata_budget_and_failed_cache_do_not_offer_unplayable_episodes(self):
        data=importlib.import_module('media_data')
        self.client._get_json.side_effect=None;self.client._get_json.return_value=None
        self.client._api_url=lambda:'https://provider.invalid/player_api.php'
        self.client._base_params=lambda:{'username':'user','password':'SECRET'}
        sys.modules['utils'].http_get.side_effect=None
        sys.modules['utils'].http_get.return_value=(json.dumps(self.details['get_series_info']).encode(),{})
        result=data.details(self.client,'series','1')
        self.assertIn('episodes',result)
        kwargs=sys.modules['utils'].http_get.call_args.kwargs
        self.assertEqual((kwargs['max_seconds'],kwargs['max_bytes']),(10,2*1024*1024))
        sys.modules['utils'].cache_set.return_value=False
        with self.assertRaises(OSError): data.details(self.client,'series','1')

    def test_window_reinitialization_after_fullscreen_preserves_grid_and_detail_focus(self):
        w=self.media_window();w.native(2);w.native(2)
        w.native(7);w._pool.drain()
        index=next(i for i,a in enumerate(w.actions) if a[1]=='favourite')
        w.getControl(300).selectItem(index)
        w.onInit()  # Native XML WINDOW_INIT also occurs on reactivation.
        self.assertEqual(w.mode,'detail')
        self.assertEqual(w.actions[w.getControl(300).getSelectedPosition()][1],'favourite')
        w.native(92);w._pool.drain();w.onInit()
        self.assertEqual((w.mode,w._last_position),('landing',2))

    def test_series_continue_next_and_manual_seen_are_independent_of_live_playback(self):
        e=dict(pid='p',kind='episode',sid='11',series_id='1',season='1',episode='1')
        self.state.save_progress(e,1050,2700)
        w=self.media_window('series');w.native(7);w._pool.drain()
        self.assertIn('continue_episode',[action for _,action in w.actions])
        self.state.save_progress(e,2600,2700);w.onInit()
        self.assertIn('next_episode',[action for _,action in w.actions])
        self.assertEqual(w.next_episode['sid'],'12')
        self.assertEqual(self.builtins,[])

    def test_profile_corruption_disables_state_actions_and_preserves_bytes(self):
        statefile=Path(self.state.path());statefile.write_bytes(b'corrupt profile')
        w=self.media_window();w.native(7);w._pool.drain()
        self.assertIn('nicht lesbar',w.getControl(102).label)
        self.assertNotIn('favourite',[action for _,action in w.actions])
        self.assertNotIn('resume',[action for _,action in w.actions])
        self.assertEqual(statefile.read_bytes(),b'corrupt profile')

    def test_changed_group_selection_applies_before_background_reindex(self):
        groups=importlib.import_module('group_selection')
        groups.save('p',['b'],'vod',known=['a','b'])
        reader=self.index.Reader('p')
        self.assertEqual(reader.page('vod')[1],0)
        self.assertIsNone(reader.get('vod','1'))

    def test_no_date_rail_still_fills_with_explicit_available_label(self):
        self.index.replace_catalog('p','vod',[dict(stream_id='1',name='Undated',category_id='a')],
                                   [dict(category_id='a',category_name='A')])
        w=self.media_window()
        # Initial refresh reuses cached provider rows; replace again to exercise
        # the actual persistent rail query, independent of provider dates.
        self.index.replace_catalog('p','vod',[dict(stream_id='1',name='Undated',category_id='a')],
                                   [dict(category_id='a',category_name='A')])
        w._page('landing');w._pool.drain()
        self.assertEqual(len(w.rows),1)
        self.assertIn('Hinzufügedatum unbekannt',w.getControl(102).label)

    def test_empty_followup_catalog_preserves_populated_local_widget_snapshot(self):
        self.catalogs['get_vod_streams']=[]
        with mock.patch.object(self.index,'revision',return_value='next empty result'):
            self.index.refresh(self.portal,self.client)
        self.assertEqual(self.index.Reader('p').page('vod')[1],100)
        self.router._params.update(action='widget_recent_vod')
        self.routes.dispatch(self.router)
        self.assertTrue(any('action=media_detail' in url for url,_,_ in self.added))


class FreezeTests(unittest.TestCase):
    def test_frozen_026_live_modules_and_player_routes_unchanged(self):
        frozen=json.loads((ROOT/'tests/fixtures/xcmate_026_freeze.json').read_text())
        for file,digest in frozen['files'].items():
            self.assertEqual(hashlib.sha256((ROOT/file).read_bytes()).hexdigest(),digest,file)
        tree=ast.parse((LIB/'main.py').read_text())
        methods={n.name:ast.dump(n,include_attributes=False) for n in ast.walk(tree) if isinstance(n,ast.FunctionDef)}
        for name,digest in frozen['methods'].items():
            self.assertEqual(hashlib.sha256(methods[name].encode()).hexdigest(),digest,name)
