"""INFOMICRO-01..08 are host geometry/owner contracts, not Android VISUAL_PASS."""
import importlib,io,sys,types,unittest
from pathlib import Path
from unittest import mock
import test_xcmate_kodi21_overlay as gui

class InfoMicro44(unittest.TestCase):
    def setUp(self):
        self.m=gui.OverlayLifecycleTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.o=self.m.overlay;self.micro=importlib.import_module('stream_micro44')
    def test_infomicro01_bottom_right_inside_panel_at_720_and_1080(self):
        for width,height in ((1280,720),(1920,1080)):
            specs=self.micro.geometry(width,height,'1920×1080','AAC · 2.0');prior_right=0
            for spec in specs.values():
                x,y,w,h=spec['icon'];lx,ly,lw,lh=spec['label']
                self.assertGreater(x,width/2);self.assertGreaterEqual(y,height-248);self.assertLess(y+h,height-32)
                self.assertGreaterEqual(lx,x+w);self.assertLessEqual(lx+lw,width-32)
                self.assertLessEqual(prior_right,x);prior_right=lx+lw
                self.assertLessEqual(abs((y+h/2)-(ly+lh/2)),1)
            self.assertEqual(width-32-prior_right,round(22*height/1080))
            if height==1080:self.assertTrue(all(12<=s['icon'][2]<=14 for s in specs.values()))
    def test_infomicro02_real_resolution_and_aac_layout_without_quality_or_dolby_guesses(self):
        video,audio=self.micro.labels(dict(width='1920',height='1080',audio='aac',channels='2.0',fps='50',video='hevc',hdr='HDR10'))
        self.assertEqual(video,'1920×1080');self.assertEqual(audio,'AAC · 2.0')
        for invented in ('4K','Atmos','Dolby','fps','HDR'):self.assertNotIn(invented,video+audio)
    def test_infomicro03_dd_layout_uses_reported_codec_and_channels_exactly(self):
        self.assertEqual(self.micro.labels(dict(width='1280',height='720',audio='ac3',channels='5.1')),('1280×720','AC3 · 5.1'))
        self.assertEqual(self.micro.labels(dict(audio='dca',channels='6')),('','DCA · 6'))
    def test_infomicro04_unknown_empty_and_late_fields_have_no_stale_icons_or_values(self):
        self.o._micro44.render({});self.assertTrue(all(not c.visible for c in self.o._micro44.controls))
        self.o._micro44.render(dict(width='1920',height='1080'));self.assertTrue(self.o._micro44.icons['video'].visible);self.assertFalse(self.o._micro44.icons['audio'].visible)
        self.o._micro44.render({});self.assertTrue(all(not c.visible for c in self.o._micro44.controls));self.assertTrue(all(not c.label for c in self.o._micro44.text.values()))
    def test_infomicro05_track_change_updates_audio_without_new_acquisition_path(self):
        self.o._stream_details.read=mock.Mock(side_effect=[dict(audio='aac',channels='2.0'),dict(audio='ac3',channels='5.1'),{}])
        for expected in ('AAC 2.0','AC3 5.1',''):
            self.o._render_info();self.assertEqual(self.o._micro44.text['audio'].label,expected)
        self.assertEqual(self.o._stream_details.read.call_count,3);self.assertFalse(self.o.info_hint.visible);self.assertFalse(getattr(self.o.info_hint,'label',''))
    def test_infomicro06_same_snapshot_has_no_extra_native_setters_or_long_duplicate_line(self):
        values=dict(width='1920',height='1080',audio='aac',channels='2.0');self.o._micro44.render(values)
        with mock.patch.object(self.o._micro44.text['video'],'setLabel',side_effect=AssertionError('unchanged repaint')):
            for _ in range(200):self.o._micro44.render(values)
        self.assertEqual(self.o._micro44.text['video'].label,'1920 × 1080');self.assertFalse(getattr(self.o.info_hint,'label',''))
    def test_infomicro07_ok1_ok2_back_and_left_keep_native_levels_and_never_stop(self):
        o=self.o;o._switch('hidden')
        for _ in range(20):
            o.handle_command('ok');self.assertEqual(o.mode,'info')
            o.handle_command('ok');self.assertEqual(o.mode,'controls');self.assertTrue(all(not c.visible for c in o._micro44.controls))
            o.handle_command('back');self.assertEqual(o.mode,'info');o.handle_command('back');self.assertEqual(o.mode,'hidden')
        o.handle_command('left');self.assertEqual(o.mode,'channels');self.m.player.stop.assert_not_called()
    def test_infomicro08_font_is_registered_or_existing_fallback_and_symbols_are_local(self):
        xml=b'<fonts><fontset><font><name>known-small</name><size>13</size></font><font><name>large</name><size>30</size></font></fontset></fonts>'
        vfs=types.SimpleNamespace(exists=lambda p:True,File=lambda p:types.SimpleNamespace(readBytes=lambda n:xml,close=lambda:None))
        with mock.patch.dict(sys.modules,xbmcvfs=vfs):self.assertEqual(self.micro.choose_font(),'known-small')
        with mock.patch.dict(sys.modules,xbmcvfs=types.SimpleNamespace()):self.assertEqual(self.micro.choose_font(),'font12')
        for control in self.o._micro44.icons.values():
            self.assertIn('infobar45',control.options['filename']);self.assertTrue(Path(control.options['filename']).is_file())
