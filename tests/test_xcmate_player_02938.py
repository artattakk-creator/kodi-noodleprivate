"""New capability controls and async Stop lifetime; no real-device claims."""
import importlib,json,sys,types,unittest
from unittest import mock
import test_xcmate_media_osd_02921 as model

class Player38(unittest.TestCase):
    def setUp(self):
        self.m=model.MediaOSDTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.w=self.m.window;self.w.show_bar()

    def test_forward_back_skips_clamp_and_require_actual_seek_capability(self):
        self.assertTrue(self.w.invoke('back30'));self.m.player.seekTime.assert_called_with(570)
        self.assertTrue(self.w.invoke('forward10'));self.m.player.seekTime.assert_called_with(610)
        self.m.flags['Player.SeekEnabled']=False;self.m.player.seekTime.reset_mock()
        for action in ('back','forward','back30','forward10','rewind','fastforward'):self.assertFalse(self.w.invoke(action))
        self.m.player.seekTime.assert_not_called()

    def test_fast_forward_and_rewind_use_existing_kodi_engine_only(self):
        self.assertTrue(self.w.invoke('rewind'));self.assertIn('PlayerControl(Rewind)',self.m.builtins)
        self.assertTrue(self.w.invoke('fastforward'));self.assertIn('PlayerControl(Forward)',self.m.builtins)
        self.m.player.play.assert_not_called()

    def test_timeline_includes_actual_remaining_duration(self):
        self.w.update();self.assertIn('00:10:00',self.w.position.label);self.assertIn('00:35:00',self.w.position.label)
        self.assertTrue(self.w.progress.visible)

    def test_hidden_back_does_not_stop_or_cancel_autoplay(self):
        self.w.hide_bar();self.m.key(92);self.assertFalse(self.w.closed);self.m.player.stop.assert_not_called()

    def test_pending_stop_cannot_recreate_capture_or_block_gui(self):
        self.m.osd._window=self.w
        self.assertTrue(self.w.invoke('stop'));self.m.player.stop.assert_not_called()
        self.m.osd.poll(self.m.player);self.assertIsNone(self.m.osd._window);self.m.player.stop.assert_not_called()
        from exit37_fixture import drain_stop
        drain_stop();self.m.player.stop.assert_called_once()

    def test_actual_codecs_are_reported_without_guessing_quality_from_title(self):
        helper=importlib.import_module('player_controls')
        with mock.patch.object(sys.modules['xbmc'],'getInfoLabel',side_effect=lambda k:{'VideoPlayer.VideoCodec':'h264','VideoPlayer.AudioCodec':'aac'}.get(k,'')):
            self.assertEqual(helper.status(),'h264 · aac');self.assertNotIn('4K',helper.status())

    def test_stop_request_can_be_retried_by_user_after_failure_not_by_service_loop(self):
        jobs=importlib.import_module('exit_jobs');self.w.invoke('stop');value=jobs.state();value['phase']='failed';jobs.save(value)
        self.assertFalse(jobs.request(self.m.player,expected=self.w.token))
        self.assertTrue(jobs.request(self.m.player,expected=self.w.token,manual=True))
        self.m.player.stop.assert_not_called()
