"""Real original ZIP + strict Omega callbacks, no manual WindowDialog.onInit."""
import importlib
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock

import test_xcmate_kodi21_overlay as omega

ROOT=Path(__file__).resolve().parents[1]
THEME=ROOT/'themes/xcmate/space-premium'


class LiveTextureTests(unittest.TestCase):
    def setUp(self):
        omega.OverlayLifecycleTests.setUp(self)
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        sys.modules['utils'].addon_data_dir=lambda:self.temp.name
        addon=ROOT/'src/plugin.video.xtreammate'
        sys.modules['xbmcaddon'].Addon=lambda:types.SimpleNamespace(getAddonInfo=lambda k:{'path':str(addon),'version':'0.1.29.24','id':'plugin.video.xtreammate'}.get(k,''))
        for name in ('theme_store','theme_package'):sys.modules.pop(name,None)
        self.store=importlib.import_module('theme_store')
        revision=self.store.install(THEME/'XCMate-Space-Premium-1.0.0.zip')
        with mock.patch.object(self.store,'playing',return_value=False):self.store.select(revision)

    def test_approved_textures_are_used_by_real_controls_and_native_events_stay_identical(self):
        themed=self.module.LiveNavigator(self.portal,'1');themed.show();self.addCleanup(themed.close)
        self.assertTrue(themed.info_bg.options['filename'].endswith('infobar45/glass.png'))
        self.assertTrue(themed.bg.options['filename'].endswith('assets/shared/sidebar-bg.png'))
        self.assertTrue(themed.info_track.options['filename'].endswith('assets/player/panel-progress-track.png'))
        # Fresh core navigator with no theme; same inputs and same Kodi-native
        # callbacks/focus movement, no reimplementation of the state machine.
        with mock.patch.object(importlib.import_module('theme_render'),'snapshot',return_value=None):
            core=self.module.LiveNavigator(self.portal,'1');core.show();self.addCleanup(core.close)
        def state(nav):
            controls=[nav.capture,nav.control,*nav.main_buttons,*nav.extra_buttons]
            return nav.mode,nav.control.getSelectedPosition(),controls.index(nav.focus)
        for key in (42,42,2,1,92,1,1,2,92,42,42,117,92,92):
            with self.subTest(key=key):
                core.native(key);themed.native(key)
                self.assertEqual(state(core),state(themed))
        themed.handle_command('more')
        self.assertTrue(themed.osd_bg.image.endswith('assets/player/panel-options.png'))
        self.client._get_json.assert_not_called();self.client.get_short_epg.assert_not_called()

    def test_missing_theme_texture_falls_back_without_new_focus_targets(self):
        nav=self.module.LiveNavigator(self.portal,'1');nav.show();self.addCleanup(nav.close)
        count=len(nav.controls);nav._theme['spec']['assets'].pop('icon.player.play',None)
        self.paused=True;nav._render_transport()
        self.assertTrue(nav._button_icons[0][1].image.endswith('resources/media/navigation/player-play-normal.png'))
        self.assertEqual(len(nav.controls),count)


from xcmate027_fixture import Fixture


class WindowAndDiagnosticTests(Fixture,unittest.TestCase):
    def test_media_favourite_action_art_and_widget_fallback_use_real_originals(self):
        store=importlib.import_module('theme_store')
        with mock.patch.object(store,'core_version',return_value='0.1.29.24'):
            revision=store.install(THEME/'XCMate-Space-Premium-1.0.0.zip')
            with mock.patch.object(store,'playing',return_value=False):store.select(revision)
            window=self.media_window();window._details(window.rows[0]);window._pool.drain()
            actions=window.getControl(300).items
            self.assertTrue(any(item.art.get('icon','').endswith('assets/media/icon-play.png') for item in actions))
            favourite=next(i for i,pair in enumerate(window.actions) if pair[1]=='favourite')
            self.assertTrue(actions[favourite].art['icon'].endswith('assets/media/icon-favorite-add.png'))
            window.getControl(300).selectItem(favourite);window.native(7);window._pool.drain()
            self.assertTrue(window.getControl(300).items[favourite].art['icon'].endswith('assets/media/icon-favorite-remove.png'))
            self.routes.add_index_item(self.router,self.portal,'vod',window.selected,widget=True)
            self.assertTrue(self.added[-1][1].art['landscape'].endswith('assets/widgets/widget-movie-fallback.png'))
            art=importlib.import_module('media_art')
            with mock.patch.object(art,'cached',side_effect=lambda url:'/cached/provider.jpg' if url else ''):
                row=dict(window.selected,cover='https://image.invalid/provider')
                self.routes.add_index_item(self.router,self.portal,'vod',row,widget=True)
            self.assertEqual(self.added[-1][1].art['landscape'],'/cached/provider.jpg')
        sys.modules['utils'].http_get.assert_not_called()

    def test_real_guide_callbacks_publish_local_theme_status_and_keep_native_focus(self):
        import xbmcaddon
        addon=xbmcaddon.Addon()
        with mock.patch.object(addon,'getAddonInfo',side_effect=lambda k:{'path':str(ROOT/'src/plugin.video.xtreammate'),'version':'0.1.29.24','id':'plugin.video.xtreammate'}.get(k,'')),mock.patch.object(xbmcaddon,'Addon',return_value=addon):
            store=importlib.import_module('theme_store')
            revision=store.install(THEME/'XCMate-Space-Premium-1.0.0.zip')
            with mock.patch.object(store,'playing',return_value=False):store.select(revision)
            window=self.guide_window()
            self.assertIn('assets/',window.getProperty('XCMate.ThemeEpgStatus'))
            importlib.import_module('theme_render').guide_status(window,'error')
            window.native(2)
            self.assertTrue(window.getProperty('XCMate.ThemeEpgStatus').endswith('assets/epg/source-error.png'))
            window.native(92);self.assertTrue(window.shown);self.assertEqual(window.getFocusId(),210)
            window.native(92);self.assertFalse(window.shown)
        sys.modules['utils'].http_get.assert_not_called()

