"""Kodi21 metadata/OSD owner races using the native control API model."""
import importlib,sys,types,unittest
from unittest import mock
import test_xcmate_media_osd_02921 as model


class StreamOSD39(unittest.TestCase):
    def setUp(self):
        self.m=model.MediaOSDTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.player=self.m.player;self.token=('media',self.m.session)
        for name in ('stream_details','osd_ownership'):sys.modules.pop(name,None)
        self.details=importlib.import_module('stream_details');self.reader=self.details.Details()

    def test_actual_pixel_scan_fps_audio_and_hdr_fields_without_title_guessing(self):
        values={'Player.Process(VideoWidth)':'1920','Player.Process(VideoHeight)':'1080','Player.Process(VideoFPS)':'50',
                'Player.Process(VideoScanType)':'interlaced','VideoPlayer.VideoCodec':'h264','VideoPlayer.AudioCodec':'aac',
                'VideoPlayer.AudioChannels':'2.0','VideoPlayer.AudioLanguage':'deu','VideoPlayer.HdrType':'HDR10'}
        with mock.patch.object(sys.modules['xbmc'],'getInfoLabel',side_effect=lambda k:values.get(k,'')):
            result=self.reader.read(self.player,self.token)
        self.assertIn('1920×1080i',self.details.compact(result));self.assertIn('HDR10',self.details.compact(result))
        self.assertEqual(result['channels'],'2.0');self.assertIn('HDMI',self.details.text(result))

    def test_missing_scan_and_hdr_remain_unknown_and_bad_numeric_values_are_omitted(self):
        with mock.patch.object(sys.modules['xbmc'],'getInfoLabel',side_effect=lambda k:{'Player.Process(VideoWidth)':'1920','Player.Process(VideoHeight)':'1080','Player.Process(VideoFPS)':'nan'}.get(k,'')):
            result=self.reader.read(self.player,self.token)
        text=self.details.compact(result);self.assertEqual(text,'1920×1080');self.assertNotIn('SDR',text)
        self.assertNotIn('fps',result);self.assertNotIn('scan',result)

    def test_metadata_is_bounded_to_one_sample_per_two_seconds_and_no_v22_fields(self):
        get=mock.Mock(return_value='')
        with mock.patch.object(sys.modules['xbmc'],'getInfoLabel',get),mock.patch.object(self.details.time,'monotonic',return_value=10):
            for _ in range(20):self.reader.read(self.player,self.token)
        self.assertEqual(get.call_count,len(self.details.LABELS))
        self.assertFalse(any('LiveBitrate' in c.args[0] or 'AudioName' in c.args[0] for c in get.call_args_list))

    def test_foreign_player_never_read_or_keeps_previous_session_details(self):
        with mock.patch.object(sys.modules['xbmc'],'getInfoLabel',return_value='h264') as get:
            self.assertTrue(self.reader.read(self.player,self.token));get.reset_mock()
            self.player.getVideoInfoTag.return_value.getUniqueID.side_effect=lambda k:'foreign'
            self.assertEqual(self.reader.read(self.player,self.token),{});get.assert_not_called()
        self.assertEqual(self.reader.values,{})

    def test_stop_race_in_video_tag_and_during_metadata_sample_is_safe(self):
        self.player.getVideoInfoTag.side_effect=RuntimeError('not playing')
        self.assertIsNone(self.m.exit.identity(self.player));self.assertEqual(self.reader.read(self.player,self.token),{})
        self.player.getVideoInfoTag.side_effect=None
        def stopped(k):self.player.isPlayingVideo.return_value=False;return 'h264'
        with mock.patch.object(sys.modules['xbmc'],'getInfoLabel',side_effect=stopped):self.assertEqual(self.reader.read(self.player,self.token),{})

    def test_twenty_standard_osd_returns_restore_own_controls_once_each(self):
        current=[12901];sys.modules['xbmcgui'].getCurrentWindowDialogId=lambda:current[0]
        for _ in range(20):
            current[0]=12901;self.m.osd.poll(self.player)
            self.assertEqual(self.m.builtins[-1],'Dialog.Close(videoosd)')
            before=len(self.m.builtins);self.m.osd.poll(self.player);self.assertEqual(len(self.m.builtins),before)
            current[0]=9999;self.m.osd.poll(self.player);self.assertTrue(self.m.osd._window.visible)
        self.player.stop.assert_not_called()
        self.m.osd._window.dispose();self.m.osd._window=None

    def test_native_settings_and_foreign_osd_are_never_closed(self):
        guard=importlib.import_module('osd_ownership')
        for dialog in (10124,10123,10153,10138,13007):
            sys.modules['xbmcgui'].getCurrentWindowDialogId=lambda:dialog
            self.assertFalse(guard.recover(self.player,self.token))
        sys.modules['xbmcgui'].getCurrentWindowDialogId=lambda:12901
        self.player.getVideoInfoTag.return_value.getUniqueID.side_effect=lambda k:'foreign'
        self.assertFalse(guard.recover(self.player,self.token));self.assertFalse(self.m.builtins)

    def test_transport_buttons_are_larger_than_settings_and_use_large_local_icons(self):
        w=self.m.window;w.show_bar()
        self.assertGreaterEqual(w.buttons['pause'].options['height'],80)
        self.assertLess(w.buttons['audio'].options['height'],w.buttons['pause'].options['height'])
        self.assertGreaterEqual(w.icons['pause'].options['width'],48)
        self.assertIn('/navigation/',w.icons['pause'].options['filename'])
