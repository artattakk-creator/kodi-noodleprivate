"""Source checks complement the Omega lifecycle integration tests."""
import unittest
from pathlib import Path
LIB = Path(__file__).resolve().parents[1] / 'src/plugin.video.xtreammate/resources/lib'

class KodiOverlayTests(unittest.TestCase):
    def test_channel_list_no_sync_epg_download(self):
        source=(LIB/'main.py').read_text(encoding='utf-8')
        section=source[source.index('    def _epg_cache(self, p: dict):'):source.index('    def _epg_mgr(self, p: dict):')]
        self.assertNotIn('_refresh_portal_epg',section)
        self.assertIn('warmup_async',section)
        self.assertIn("xc.get_cached_catalog('get_live_streams')",source)

    def test_remote_epg_is_cache_only_on_gui_thread(self):
        source=(LIB/'live_overlay.py').read_text(encoding='utf-8')
        section=source[source.index('    def _epg(self):'):source.index('    def _execute(',source.index('    def _epg(self):'))]
        self.assertIn('cached_only=True',section)
        self.assertIn('threading.Thread(',section)
        self.assertNotIn('self.xc.get_short_epg(self.sid',section)

if __name__=='__main__':unittest.main()
