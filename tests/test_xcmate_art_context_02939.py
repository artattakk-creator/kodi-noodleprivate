"""Already displayed row art survives rebuilds, not new URL admission."""
import importlib,sys,threading,unittest
from unittest import mock
import test_xcmate_flicker_02938 as model


class ArtContext39(unittest.TestCase):
    def setUp(self):
        self.m=model.Flicker38(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.fixture=self.m.fixture;self.v=self.m.v;self.w=self.fixture.m.media_window()
        self.row=dict(self.m.row,sid='same',name='Visible cover',kind='vod')

    def test_twenty_rebuilds_at_30_60_120_seconds_keep_seen_cover_across_rows_and_tabs(self):
        self.w._fill(210,[self.row]);original=self.w.getControl(210).getListItem(0).art['poster']
        self.m.block=True
        for stamp in (31,61,121):
            self.m.now[0]=stamp
            for _ in range(20):
                self.w._fill(210,[]);self.w._fill(710,[self.row]);self.w._fill(210,[self.row])
                self.assertEqual(self.w.getControl(710).getListItem(0).art['poster'],original)
                self.assertEqual(self.w.getControl(210).getListItem(0).art['poster'],original)
        self.m.release.set();self.fixture.drain()

    def test_definitive_dns_rejection_clears_rebuilt_art_without_weakening_admission(self):
        self.w._fill(710,[self.row]);original=self.w.getControl(710).getListItem(0).art['poster']
        self.m.now[0]=31;self.m.fail=True;self.m.refresh()
        self.w._fill(710,[self.row]);self.assertNotEqual(self.w.getControl(710).getListItem(0).art['poster'],original)

    def test_changed_provider_url_and_new_view_cannot_inherit_expired_seen_art(self):
        self.w._fill(710,[self.row]);original=self.w.getControl(710).getListItem(0).art['poster']
        self.m.now[0]=31;self.m.block=True
        self.w._fill(710,[dict(self.row,cover=self.row['cover']+'-new')])
        self.assertNotEqual(self.w.getControl(710).getListItem(0).art['poster'],original)
        other=self.fixture.m.media_window();other._fill(710,[self.row])
        self.assertNotEqual(other.getControl(710).getListItem(0).art['poster'],original)
        self.m.release.set();self.fixture.drain()

    def test_art_reference_history_is_bounded_without_deleting_any_images(self):
        for n in range(300):self.w._display_art39(dict(sid=str(n),kind='vod',name='No provider image'))
        self.assertLessEqual(len(self.w._art_history39),256)
