"""XtreamMate 0.1.6 playback and short-guide regression tests."""
import base64
import importlib.util
import time
import unittest
from pathlib import Path

LIB = Path(__file__).resolve().parents[1] / 'src/plugin.video.xtreammate/resources/lib'

class V016Checks(unittest.TestCase):
    def test_short_epg_decodes_now_and_next(self):
        spec=importlib.util.spec_from_file_location('v016_epg',LIB/'epg_views.py')
        mod=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        now=int(time.time())
        raw={'epg_listings':[
            {'title':base64.b64encode('Nachrichten'.encode()).decode(),
             'start_timestamp':now-30,'stop_timestamp':now+200},
            {'title':base64.b64encode('Spielfilm'.encode()).decode(),
             'start_timestamp':now+200,'stop_timestamp':now+2000}]}
        result=mod._short_guide(raw,now)
        self.assertEqual(result['now'],'Nachrichten')
        self.assertEqual(result['next'],'Spielfilm')
    def test_start_channel_is_playable_and_without_server_query(self):
        source=(LIB/'main.py').read_text(encoding='utf-8')
        start=source[source.index('    def _play_start(self):'):source.index('    def _groups_manager(self):')]
        self.assertIn("xc.get_cached_catalog('get_live_streams')",start)
        self.assertNotIn("xc.get_live_streams()",start)
        self.assertIn("is_folder=False)",source)
        self.assertIn("li.setProperty('IsPlayable', 'true')",source)
    def test_home_does_not_wait_for_account_call(self):
        source=(LIB/'main.py').read_text(encoding='utf-8')
        self.assertIn("self._portal_plot(p, cached_only=True)",source)
    def test_remote_diag_records_last_pressed_and_handled_key(self):
        source=(LIB/'main.py').read_text(encoding='utf-8')
        self.assertIn('XtreamMate.LastRemoteKey',source)
        self.assertIn('XtreamMate.LastHandledKey',source)
    def test_live_guide_only_prefetches_off_ui_thread(self):
        source=(LIB/'main.py').read_text(encoding='utf-8')
        part=source[source.index('    def _live_channels(self):'):source.index('    def _add_media_context(',source.index('    def _live_channels(self):'))]
        self.assertIn('prefetch_short_guides(p, chunk)',part)
        self.assertIn('cached_short_guide(',part)
        self.assertNotIn('get_short_epg(',part)

if __name__=='__main__':
    unittest.main()
