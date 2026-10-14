"""Contract tests against photographed TiviMate remote settings, Oct 2026.

Mapping tests are NOT Android input or full EPG interaction tests.
"""
import importlib.util
from pathlib import Path
import unittest

SRC = (Path(__file__).resolve().parents[1] /
       'src/plugin.video.xtreammate/resources/lib/tivimate_keys.py')
spec = importlib.util.spec_from_file_location('xcmate_tivimate_keys_reference', SRC)
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)


class TiviMatePhotoContractTests(unittest.TestCase):
    def test_photo_player_short_press(self):
        expected = {
            'ok': 'show_info_controls', 'back': 'back',
            'left': 'channels_overlay', 'right': 'recent_channel',
            'up': 'channel_next', 'down': 'channel_previous',
            'page_up': 'preview_next_channel',
            'page_down': 'preview_previous_channel',
            'menu': 'show_menu', 'play_pause': 'play_pause',
            'stop': 'stop', 'rewind': 'preview_previous_channel',
            'fast_forward': 'preview_next_channel',
            'record': 'toggle_recording',
            'back_key': 'guide_overlay',
            'info': 'show_info', 'guide': 'guide_overlay',
            'red': 'guide_overlay', 'green': 'guide_overlay',
            'yellow': 'show_info', 'blue': 'settings',
            'volume_up': 'volume_up', 'volume_down': 'volume_down',
            'mute': 'mute',
        }
        for key, command in expected.items():
            with self.subTest(key=key):
                self.assertEqual(reference.resolve('player', key), command)

    def test_photo_player_long_press(self):
        expected = {
            'ok': 'show_menu', 'back': 'stop',
            'left': 'channels_preview', 'right': 'program_description',
            'up': 'history', 'down': 'search',
            'menu': 'guide_overlay', 'play_pause': 'return_live',
        }
        for key, command in expected.items():
            with self.subTest(key=key):
                self.assertEqual(reference.resolve('player', key, True), command)

    def test_photo_epg_context_differs_from_player(self):
        expected = {
            'ok': 'watch_channel', 'back': 'back',
            'left': 'show_groups', 'right': 'scroll_next_program',
            'page_up': 'page_up_channels',
            'page_down': 'page_down_channels',
            'menu': 'show_menu',
            'play_pause': 'program_description',
            'stop': 'toggle_favourite',
            'rewind': 'page_up_channels',
            'fast_forward': 'page_down_channels',
            'record': 'recordings',
            'back_key': 'return_player',
            'info': 'program_description', 'guide': 'show_groups',
            'red': 'toggle_favourite', 'green': 'channel_options',
            'yellow': 'group_options', 'blue': 'settings',
        }
        for key, command in expected.items():
            with self.subTest(key=key):
                self.assertEqual(reference.resolve('epg', key), command)
        self.assertEqual(reference.resolve('epg','ok',True),'show_menu')
        self.assertEqual(reference.resolve('epg','back',True),'return_player')
        self.assertEqual(reference.resolve('epg','menu',True),'search')
        self.assertEqual(reference.resolve('epg','play_pause',True),'open_external')
        self.assertNotEqual(reference.resolve('player','stop'),
                            reference.resolve('epg','stop'))

    def test_unphotographed_bindings_do_not_get_invented(self):
        self.assertIsNone(reference.resolve('epg','up'))
        self.assertIsNone(reference.resolve('epg','long_left'))
        self.assertIsNone(reference.resolve('epg','up',True))
        self.assertIsNone(reference.resolve('recordings','ok'))
        self.assertIsNone(reference.resolve('player','unknown'))
        self.assertIsNone(reference.resolve_kodi('player',991234))
        self.assertIsNone(reference.key_from_kodi_action('invalid'))

    def test_kodi_action_codes_are_not_android_keycodes(self):
        self.assertEqual(reference.resolve_kodi('player',3),'channel_next')
        self.assertEqual(reference.resolve_kodi('player',4),'channel_previous')
        self.assertEqual(reference.resolve_kodi('epg',13),'toggle_favourite')
        self.assertEqual(reference.resolve_kodi('player',13),'stop')
        self.assertEqual(reference.key_from_kodi_action(92),'back')

    def test_photo_seek_switches_preserved(self):
        expected = {
            'rw_ff_pause_to_seek_during_playback': True,
            'rw_to_rewind_live': False,
            'left_right_seek_while_seeking': False,
            'left_to_rewind_live': False,
            'up_down_seek_during_catchup': False,
            'down_to_rewind_live_catchup': False,
        }
        self.assertEqual(reference.seek_settings(), expected)
        altered=reference.seek_settings()
        altered['rw_to_rewind_live']=True
        self.assertFalse(reference.SEEK_OPTIONS['rw_to_rewind_live'])


if __name__=='__main__':
    unittest.main()
