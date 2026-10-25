"""XtreamMate Android-native playback and remote regression tests."""
import importlib.util
import json
import os
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

LIB=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/lib'

class NativeRemoteTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.folder=temp.name
        self.utils=types.ModuleType('utils')
        self.utils.addon_data_dir=lambda:self.folder
        self.patch=mock.patch.dict(sys.modules, {'utils':self.utils})
        self.patch.start()
        self.addCleanup(self.patch.stop)
        spec=importlib.util.spec_from_file_location('xtreammate_remote_profile_test',
                                                     LIB/'remote_profiles.py')
        self.profile=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.profile)

    def test_android_default_actions(self):
        profile=self.profile
        self.assertEqual(profile.mapped_action(1),'left')
        self.assertEqual(profile.mapped_action(3),'up')
        self.assertEqual(profile.mapped_action(4),'down')
        self.assertEqual(profile.mapped_action(7),'ok')
        self.assertEqual(profile.mapped_action(92),'back')

    def test_learned_actions_persist_and_take_effect(self):
        profile=self.profile
        new=dict(profile.load())
        new['epg']=501
        profile.save(new)
        self.assertEqual(profile.mapped_action(501),'epg')
        self.assertEqual(profile.mapped_action(117),'menu')
        self.assertEqual(json.loads(Path(profile.path()).read_text(encoding='utf-8'))['epg'],501)

    def test_conflicting_buttons_are_rejected(self):
        values=self.profile.load()
        values['epg']=7
        with self.assertRaises(ValueError):
            self.profile.save(values)
        self.assertFalse(os.path.isfile(self.profile.path()))

    def test_foreign_profile_is_not_misinterpreted(self):
        Path(self.profile.path()).write_text('{"epg": "not a number"}',encoding='utf-8')
        self.assertEqual(self.profile.load()['epg'],117)

    def test_legacy_profile_preserved_native_directions_win_and_extra_left_still_works(self):
        profile=self.profile
        saved=dict(profile.DEFAULT,left=501,more=1)
        Path(profile.path()).write_text(json.dumps(saved),encoding='utf-8')
        before=Path(profile.path()).read_bytes()
        bindings=profile.load()
        self.assertEqual(profile.mapped_action(1,bindings),'left')
        self.assertEqual(profile.mapped_action(501,bindings),'left')
        self.assertEqual(profile.mapped_action(2,bindings),'right')
        self.assertEqual(Path(profile.path()).read_bytes(),before)

    def test_startsender_uses_separate_kodi_playback_modes(self):
        source=(LIB/'main.py').read_text(encoding='utf-8')
        common=source[source.index('    def _startup_playable(self):'):
                      source.index('    def _groups_manager(self):')]
        manual=common[common.index('    def _play_start(self):'):
                      common.index('    def _play_start_direct(self):')]
        direct=common[common.index('    def _play_start_direct(self):'):]
        self.assertIn('xbmcplugin.setResolvedUrl(self._handle, True, item)',manual)
        self.assertNotIn('xbmc.Player().play(',manual)
        self.assertIn('xbmc.Player().play(item.getPath(), item)',direct)
        self.assertNotIn('xbmcplugin.setResolvedUrl(',direct)
        self.assertIn('start_channel(p,xc)',common)
        self.assertNotIn("xc.get_cached_catalog('get_live_streams')",common)
        automatic=source[source.index('    def _maybe_autoplay_start('):
                         source.index('    def _portal_home(',source.index('    def _maybe_autoplay_start('))]
        self.assertIn("self.url(action='play_start_direct'",automatic)
        self.assertNotIn("xbmc.executebuiltin('PlayMedia(",automatic)

    def test_overlay_retains_focus_when_hidden_and_uses_mapped_actions(self):
        source=(LIB/'live_overlay.py').read_text(encoding='utf-8')
        self.assertIn('target = self.capture',source)
        self.assertIn('mapped_action(key, self._bindings)',source)
        self.assertIn("self.handle_command(mapped,source='native'",source)
        self.assertIn("self.capture.getId()",source)
        self.assertIn("def onControl(self, control):",source)

    def test_android_remote_learning_accessible_from_home_settings(self):
        main=(LIB/'main.py').read_text(encoding='utf-8')
        self.assertIn("'remote_learn': self._remote_learn",main)
        self.assertIn('Fernbedienungstasten anlernen (Android)',main)
        settings=(LIB.parent/'settings.xml').read_text(encoding='utf-8')
        self.assertIn('id="remote_learn"',settings)

if __name__=='__main__':
    unittest.main()
