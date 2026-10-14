"""XCMate fallback session recognition for the real Android symptom:
service is alive, Player.isPlayingVideo yes, XCMate.LiveSession absent.

The algorithm may only recognize exactly authenticated, cached/configured
Xtream live streams and must not take ownership of other Kodi playback.
"""
import importlib.util
import pathlib
import unittest

HERE = pathlib.Path(__file__).resolve().parents[1]
SRC = HERE / 'src/plugin.video.xtreammate/resources/lib/live_recovery.py'
spec = importlib.util.spec_from_file_location('xcmate_recovery_test', SRC)
recovery = importlib.util.module_from_spec(spec)
spec.loader.exec_module(recovery)


class FakeClient:
    factory_calls = 0
    def __init__(self, host, username, password):
        self.host, self.username, self.password = host, username, password
        self.cached = [{'stream_id': 99, 'name': 'Cache'}]
        self.__class__.factory_calls += 1

    def live_stream_url(self, sid, ext='ts'):
        return '{}live/{}/{}/{}.{}'.format(
            self.host, self.username, self.password, sid, ext)

    def get_cached_catalog(self, what):
        assert what == 'get_live_streams'
        return self.cached


PORTALS = [
    {'id': 'portal-A', 'type': 'xtream',
     'xc_host': 'https://provider.invalid/',
     'xc_user': 'userA', 'xc_pass': 'sensitive1',
     'start_stream_id': '123'},
    {'id': 'portal-B', 'type': 'xtream',
     'xc_host': 'https://provider.invalid/',
     'xc_user': 'userB', 'xc_pass': 'sensitive2',
     'start_stream_id': '456'},
]


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        FakeClient.factory_calls = 0

    def test_exact_start_stream_recovers_after_marker_lost(self):
        actual = 'https://provider.invalid/live/userA/sensitive1/123.ts'
        self.assertEqual(recovery.recover_from_player_path(actual, PORTALS, FakeClient),
                         ('portal-A', '123'))

    def test_provider_credentials_must_match_not_just_host(self):
        wrong = 'https://provider.invalid/live/userA/other/123.ts'
        self.assertIsNone(recovery.recover_from_player_path(wrong, PORTALS, FakeClient))
        wrong = 'https://provider.invalid/movie/userA/sensitive1/123.ts'
        self.assertIsNone(recovery.recover_from_player_path(wrong, PORTALS, FakeClient))

    def test_other_kodi_video_or_plugin_never_activates(self):
        for value in ('', 'file:///media/movie.mkv',
                      'plugin://plugin.video.other/?action=play_live&pid=portal-A&sid=123',
                      'https://unrelated.invalid/live/userA/sensitive1/123.ts',
                      'https://provider.invalid/live/userA/sensitive1/123.mp4'):
            with self.subTest(value=value):
                self.assertIsNone(recovery.recover_from_player_path(
                    value, PORTALS, FakeClient))

    def test_kodi_header_suffix_is_ignored_without_logging(self):
        actual = ('https://provider.invalid/live/userB/sensitive2/456.m3u8'
                  '|User-Agent=Kodi&X-Custom=anything')
        self.assertEqual(recovery.recover_from_player_path(actual, PORTALS, FakeClient),
                         ('portal-B', '456'))

    def test_cached_channel_can_be_recovered_without_start_id(self):
        actual = 'https://provider.invalid/live/userB/sensitive2/99.ts'
        self.assertEqual(recovery.recover_from_player_path(actual, PORTALS, FakeClient),
                         ('portal-B', '99'))
        noncached = 'https://provider.invalid/live/userB/sensitive2/100.ts'
        self.assertIsNone(recovery.recover_from_player_path(noncached, PORTALS, FakeClient))

    def test_exact_plugin_uri_and_no_vod_plugin(self):
        valid = ('plugin://plugin.video.xtreammate/'
                 '?action=play_start_direct&pid=portal-A')
        self.assertEqual(recovery.recover_from_player_path(valid, PORTALS, FakeClient),
                         ('portal-A', '123'))
        video = ('plugin://plugin.video.xtreammate/'
                 '?action=play_vod&pid=portal-A&sid=123')
        self.assertIsNone(recovery.recover_from_player_path(video, PORTALS, FakeClient))

    def test_no_network_and_local_nonsecret_diagnostics(self):
        source = SRC.read_text(encoding='utf-8')
        service = (HERE/'src/plugin.video.xtreammate/service.py').read_text(
            encoding='utf-8')
        main = (HERE/'src/plugin.video.xtreammate/resources/lib/main.py').read_text(
            encoding='utf-8')
        self.assertNotIn('requests.', source)
        self.assertNotIn('print(', source)
        self.assertNotIn('get_live_streams(', source)
        self.assertIn('recover_from_player_path(', service)
        self.assertIn('player.getPlayingFile()', service)
        self.assertIn('XtreamMate.SessionRecovery', main)


if __name__ == '__main__':
    unittest.main()
