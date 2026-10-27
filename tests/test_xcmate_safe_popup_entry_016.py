"""P0 regression: XCMate 0.1.15 popup was preempted by configured autostart.

Kodi mock contracts, not proof of hardware Android remote support.
"""
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parents[1]
LIB = BASE / 'src/plugin.video.xtreammate/resources/lib'
SETTINGS = BASE / 'src/plugin.video.xtreammate/resources/settings.xml'


class SafeModeRegression(unittest.TestCase):
    def setUp(self):
        paths=mock.patch.object(sys,'path',[str(LIB)]+sys.path)
        paths.start();self.addCleanup(paths.stop)
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup)
        self.opts = {}
        self.play_calls = []
        self.properties = {}
        self.saved_settings = []
        self.added = []
        self.portal = {
            'type': 'xtream', 'id': 'provider42', 'name': 'TV',
            'autoplay_start': True, 'start_stream_id': '65',
            'include_live': True,
        }
        utils = types.ModuleType('utils')
        for k in ('setting', 'setting_int', 'load_favourites', 'toggle_favourite',
                  'is_favourite', 'cache_clear', 'notify', 'debug', 'info',
                  'warn', 'error', 'apply_lang_sort', '_L'):
            setattr(utils, k, lambda *a, **kw: '')
        utils.addon_data_dir=lambda:temp.name
        utils.setting_bool = lambda key, default=False: self.opts.get(key, default)
        xbmc = types.ModuleType('xbmc')
        xbmc.getCondVisibility=lambda c:c=='Window.IsActive(videos)'
        xbmc.Player = lambda: types.SimpleNamespace(isPlayingVideo=lambda: False)
        xbmc.executebuiltin = lambda cmd: self.play_calls.append(cmd)
        gui = types.ModuleType('xbmcgui')
        win = types.SimpleNamespace(
            getProperty=lambda k: self.properties.get(k, ''),
            setProperty=lambda k, v: self.properties.__setitem__(k, v),clearProperty=lambda k:self.properties.pop(k,None))
        gui.Window = lambda wid: win
        gui.ListItem = lambda label: types.SimpleNamespace(
            setArt=lambda a: None, setInfo=lambda *a, **kw: None,
            setProperty=lambda *a, **kw: None)
        gui.Dialog = lambda: types.SimpleNamespace(
            yesno=lambda *a: True, ok=lambda *a: None,notification=lambda *a:None)
        plugin = types.ModuleType('xbmcplugin')
        plugin.addDirectoryItem = lambda *a, **kw: self.added.append((a, kw))
        plugin.setPluginCategory = lambda *a: None
        plugin.setContent = lambda *a: None
        plugin.endOfDirectory = lambda *a, **kw: None
        addon = types.ModuleType('xbmcaddon')
        addon.Addon = lambda: types.SimpleNamespace(
            getAddonInfo=lambda key: ('plugin.video.xtreammate' if key == 'id'
                                      else '/tmp/plugin.video.xtreammate'),
            setSetting=lambda key, value: self.saved_settings.append((key, value)))
        portals = types.ModuleType('portals')
        portals.import_from_settings = lambda: None
        portals.get_active = lambda: [self.portal]
        portals.load_all = lambda: [self.portal]
        fake_modules = {
            'xbmc': xbmc, 'xbmcgui': gui, 'xbmcplugin': plugin,
            'xbmcaddon': addon, 'xbmcvfs': types.ModuleType('xbmcvfs'),
            'utils': utils, 'portals': portals,
        }
        p = mock.patch.dict(sys.modules, fake_modules)
        p.start()
        self.addCleanup(p.stop)
        spec = importlib.util.spec_from_file_location(
            'xcmate_safe_016_main', LIB / 'main.py')
        m = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(m)
        self.router = m.Router(['plugin://plugin.video.xtreammate', '7', '?action=root'])

    def test_single_portal_root_does_not_start_television(self):
        # Mirrors the user's real broken flow: entering the only portal
        # used to queue RunPlugin and launch live TV before choosing popup.
        self.portal['autoplay_start']=False  # .38 honors an explicit disabled preference.
        self.router._show_portal_home = lambda p: self.added.append('portal-home')
        self.router._root()
        self.assertEqual(self.added, ['portal-home'])
        self.assertFalse(self.play_calls, 'root must stay navigable')

    def test_user_can_opt_back_in_to_autoplay(self):
        self.opts['autoplay_diagnostics_safe'] = False
        self.router._show_portal_home = lambda p: None
        self.router._root()
        self.assertEqual(len(self.play_calls), 1)
        self.assertIn('play_start_direct', self.play_calls[0])

    def test_toggle_changes_only_addon_setting_not_portal(self):
        before = dict(self.portal)
        self.router._autoplay_diagnostic_mode()
        self.assertEqual(self.saved_settings, [])
        from app_entry import paused
        self.assertTrue(paused())
        self.assertEqual(self.portal, before)

    def test_popup_invocation_does_not_start_tv(self):
        test = types.ModuleType('popup_probe')
        calls = []
        test.run_popup_test = lambda: calls.append('popup')
        with mock.patch.dict(sys.modules, {'popup_probe': test}):
            self.router._popup_probe()
        self.assertEqual(calls, ['popup'])
        self.assertEqual(self.play_calls, [])
        self.assertIn('Popup-Test', self.properties['XtreamMate.AutoplayDiagnosticState'])

    def test_popup_test_moves_to_maintenance_while_normal_home_has_six_items(self):
        rows=[]
        self.router._add_dir=lambda label,url,**kw:rows.append((label,url))
        self.router._show_portal_home(self.portal)
        # Window actions now use native non-folder/non-playable plugin items.
        self.assertEqual(len(rows)+len(self.added),6)
        self.assertFalse(any('popup_probe' in url for _,url in rows))
        rows.clear()
        from home_menu import settings
        settings(self.router,self.portal,'maintenance')
        self.assertFalse(any('popup_probe' in url for _,url in rows))
        from settings_sections45 import EXPERIMENTAL
        self.assertIn('popup_probe',[a for _,a,_ in EXPERIMENTAL['diagnostics']])

    def test_kodi_settings_have_two_recovery_entrances(self):
        root = ET.parse(SETTINGS).getroot()
        controls = {el.get('id'): el for el in root.iter('setting')}
        pause = controls['autoplay_diagnostics_safe']
        popup = controls['popup_xtream_diagnostic']
        self.assertEqual(pause.get('default'), 'false')
        self.assertEqual(pause.get('visible'),'false')
        self.assertIn('action=autoplay_diagnostic_mode',controls['autoplay_pause_action'].get('action'))
        self.assertEqual(pause.get('type'), 'bool')
        self.assertIn('action=popup_probe', popup.get('action'))
        self.assertIn("from app_entry import toggle_pause",
                      (LIB / 'main.py').read_text(encoding='utf-8'))


if __name__ == '__main__':
    unittest.main()
