"""Strict native-focus and action/legacy-container models; no Android PASS."""
import importlib
import importlib.util
import types
import unittest
from unittest import mock
from xcmate027_fixture import Fixture,WindowXML,ADDON,LIB


class Navigation298(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.nav=importlib.import_module('window_navigation')

    def test_home_and_settings_use_nonfolder_nonplayable_plugin_actions(self):
        home=importlib.import_module('home_menu');home.show(self.router,self.portal)
        for url,item,folder in self.added:
            if any('action='+a in url for a in self.nav.WINDOW_ACTIONS):
                self.assertFalse(folder);self.assertEqual(item.getProperty('IsPlayable'),'false')
        self.added.clear();home.settings(self.router,self.portal,'storage')
        for url,item,folder in self.added:
            if any('action='+a+'&' in url or url.endswith('action='+a) for a in self.nav.DIALOG_ACTIONS):
                self.assertFalse(folder);self.assertEqual(item.getProperty('IsPlayable'),'false')

    def test_action_window_returns_to_same_home_without_container_update(self):
        for kind in ('vod','series'):
            w=self.media_window(kind);w.native(92)
            self.assertTrue(w._closed)
            self.router._handle=-1
            self.router._params['action']='movies_home' if kind=='vod' else 'series_home'
            with mock.patch.object(self.media,'open_owned_window',return_value=w):
                self.routes.dispatch(self.router)
            self.assertFalse(self.builtins);self.assertEqual(len(self.ends),0)

    def test_two_intentional_backs_close_once_and_never_reopen_or_exit_container(self):
        w=self.media_window();count=[]
        original=WindowXML.close
        with mock.patch.object(WindowXML,'close',lambda x:(count.append(x),original(x))):
            w.native(92);w.native(92)
        self.assertEqual(count,[w]);self.assertTrue(w._return_home)
        self.assertFalse(w._pool.jobs);self.assertFalse(self.builtins)

    def test_running_window_owns_both_back_events_until_transition_is_drained(self):
        w=self.media_window();w._running=True
        w.native(92);w.native(92)
        self.assertTrue(w._leaving);self.assertFalse(w._closed);self.assertTrue(w.shown)
        w._leave_after=0;w.pump()
        self.assertTrue(w._closed);self.assertFalse(self.builtins)

    def test_repeated_ten_movie_and_series_cycles_keep_parent_and_valid_focus(self):
        for kind in ('vod','series'):
            for _ in range(10):
                w=self.media_window(kind);w.setFocusId(120);w.native(7);self.settle(w)
                w.native(92);self.settle(w)
                self.assertEqual(w.mode,'landing');self.assertEqual(w.getFocusId(),120)
                w.native(92);w.native(92);self.assertTrue(w._closed)
        self.assertFalse(self.builtins)

    def test_episode_back_restores_selected_season(self):
        w=self.media_window('series');w.native(7);self.settle(w)
        w.getControl(300).selectItem(0);w.native(7)
        w.getControl(330).selectItem(1);w.native(7)
        w.native(92);self.assertEqual(w.mode,'seasons')
        self.assertEqual(w.getControl(330).getSelectedPosition(),1)

    def test_hidden_120_and_empty_lists_fall_back_to_visible_header(self):
        w=self.media_window()
        for mode in ('groups','grid','detail','seasons','episodes'):
            w.mode=mode;w.rows=[];w.groups=[];w.actions=[]
            w._show(mode);w.setFocusId(120);w.setFocusId(110)
            self.assertEqual(w.getFocusId(),400)
            self.assertTrue(w.getControl(w.getFocusId()).isVisible())
        w.mode='landing';w._show('landing');w.setFocusId(120)
        self.assertEqual(w.getFocusId(),120)
        default=w.tree.find('defaultcontrol')
        self.assertEqual(default.text,'400');self.assertEqual(default.get('always'),'true')

    def test_focus_navigation_never_targets_hidden_or_empty_control(self):
        w=self.media_window();w.native(7);self.settle(w)
        self.assertEqual(w.mode,'detail')
        w.setFocusId(400);w.native(1)
        self.assertNotEqual(w.getFocusId(),120)
        for _ in range(8):
            w.native(3);w.native(4)
            self.assertIn(w.getFocusId(),w._valid_focus())

    def test_empty_favourite_removal_keeps_focus_valid(self):
        self.state.toggle('p','vod','1')
        w=self.media_window();w.setFocusId(111);w.native(117)
        self.assertEqual(w.rails[111],[]);self.assertIn(w.getFocusId(),w._valid_focus())

    def test_disabled_control_is_checked_via_real_kodi_info_condition(self):
        w=self.media_window();w.getControl(120).setEnabled(False);w.setFocusId(120)
        self.assertNotEqual(w.getFocusId(),120)
        self.assertNotIn(501,w._valid_focus())
        self.assertTrue(all(w.getControl(cid).kind in ('button','list','panel') for cid in w._valid_focus()))
        self.assertNotIn('.isEnabled(', (LIB/'media_window.py').read_text())
        self.assertIn('Control.IsEnabled(', (LIB/'media_window.py').read_text())

    def test_full_posterwall_back_restores_groups_then_landing_then_home(self):
        w=self.media_window();w.setFocusId(120);w.native(7);self.settle(w)
        w.setFocusId(200);w.native(2)
        self.assertEqual(w._cols,6)
        w.native(92);self.assertEqual(w.mode,'groups');self.assertEqual(w.getFocusId(),200)
        w.native(92);self.settle(w);self.assertEqual(w.mode,'landing')
        w.native(92);self.assertTrue(w._closed);self.assertFalse(self.builtins)

    def test_cross_interpreter_lease_rejects_second_window_before_constructor(self):
        spec=importlib.util.spec_from_file_location('separate_navigation',LIB/'window_navigation.py')
        other=importlib.util.module_from_spec(spec);spec.loader.exec_module(other)
        self.router._handle=-1;opener=mock.Mock()
        with self.nav.ownership() as owned:
            self.assertTrue(owned)
            other.open_route(self.router,self.portal,opener)
        opener.assert_not_called()
        other.open_route(self.router,self.portal,opener);opener.assert_called_once()

    def test_legacy_directory_anchor_happens_before_open_only_once(self):
        self.router._params['action']='movies_home';events=[]
        original=self.nav.xbmc.executebuiltin
        def builtin(cmd):events.append('anchor');original(cmd)
        with mock.patch.object(self.nav.xbmc,'executebuiltin',side_effect=builtin),\
             mock.patch.object(self.media,'open_media',side_effect=lambda *a,**kw:events.append('window')):
            self.routes.dispatch(self.router)
        self.assertEqual(events,['anchor','window']);self.assertEqual(len(self.ends),1)
        self.assertIn('action=xcmate_home',self.current_folder)

    def test_failed_anchor_does_not_show_window_or_create_recursive_updates(self):
        self.router._params['action']='series_home';open_=mock.Mock()
        xbmc=self.nav.xbmc
        with mock.patch.object(xbmc,'getInfoLabel',return_value=''),\
             mock.patch.object(xbmc,'Monitor',return_value=types.SimpleNamespace(waitForAbort=lambda n:True)):
            self.nav.open_route(self.router,self.portal,open_)
        open_.assert_not_called();self.assertEqual(len(self.builtins),1)

    def test_modal_start_failure_keeps_home_and_notifies_without_dialog_close(self):
        from owner_dispatch import WindowStartError
        self.router._handle=-1;self.router._params['action']='series_home'
        with mock.patch.object(self.media,'open_media',side_effect=WindowStartError('internal')):
            self.routes.dispatch(self.router)
        self.dialog.notification.assert_called_once();self.assertFalse(self.builtins)

    def test_popup_routes_complete_success_once_or_no_directory_for_action_handle(self):
        home=importlib.import_module('home_menu')
        for handle in (7,-1):
            for action in ('art_status','art_retry','art_db_health','recording_capabilities',
                           'appearance_settings','ui_language','account_select','guide_status',
                           'guide_timers','about_xcmate','widget_setup','recording_folder'):
                with self.subTest(handle=handle,action=action),\
                     mock.patch.object(importlib.import_module('art_store'),'retry'),\
                     mock.patch.object(importlib.import_module('artwork_health_ui'),'manage'),\
                     mock.patch.object(home,'recording_folder'),\
                     mock.patch.object(importlib.import_module('guide_store'),'status_lines',return_value=['local status']):
                    self.ends.clear();self.router._directory_done=False
                    self.router._handle=handle;self.router._params['action']=action
                    self.routes.dispatch(self.router)
                    self.assertEqual(len(self.ends),int(handle>=0))
                    if self.ends:self.assertTrue(self.ends[0][0][1])

    def test_invalid_media_route_still_reports_real_failure(self):
        self.router._params.update(action='media_detail',kind='bogus')
        self.routes.dispatch(self.router);self.assertEqual(self.ends[-1][0],(7,False))

    def test_search_transition_runs_after_native_close(self):
        w=self.media_window();self.dialog.input.return_value='Local title'
        w._search();self.assertTrue(w._closed);self.assertFalse(self.builtins)
        with mock.patch.object(self.media,'open_owned_window',return_value=w):
            self.media.open_media(self.router,self.portal,'vod')
        self.assertEqual(len(self.builtins),1);self.assertIn('action=global_search',self.builtins[0])


if __name__=='__main__':unittest.main()
