"""Omega native-control model, verified media ownership; device tests separate."""
import importlib,json,sys,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture
from test_xcmate_kodi21_overlay import OmegaDialog,ControlButton,ControlImage,ControlLabel

class MediaOSDTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();gui=sys.modules['xbmcgui'];gui.WindowDialog=OmegaDialog
        OmegaDialog.removeControl=lambda self,c:self.controls.remove(c)
        gui.ControlButton=ControlButton;gui.ControlImage=ControlImage;gui.ControlLabel=ControlLabel
        gui.getCurrentWindowDialogId=lambda:9999
        self.flags={'Window.IsVisible(fullscreenvideo)':True,'Player.SeekEnabled':True,'Player.PauseEnabled':True}
        sys.modules['xbmc'].getCondVisibility=lambda key:self.flags.get(key,False)
        self.session=dict(pid='p',kind='vod',sid='2',nonce='ours',at=time.time(),title='Local title')
        self.properties['XCMate.MediaSession']=json.dumps(self.session)
        self.player=mock.Mock();self.player.isPlayingVideo.return_value=True
        self.player.getVideoInfoTag.return_value.getUniqueID.side_effect=lambda key:'ours' if key=='xcmate_media' else ''
        self.player.getTime.return_value=600;self.player.getTotalTime.return_value=2700
        self.player.getAvailableAudioStreams.return_value=['German','English'];self.player.getAvailableSubtitleStreams.return_value=['German']
        sys.modules['xbmc'].Player=lambda:self.player
        for name in ('media_osd','media_actions','playback_exit'):sys.modules.pop(name,None)
        self.osd=importlib.import_module('media_osd');self.exit=importlib.import_module('playback_exit')
        self.window=self.osd.MediaOSD(('media',self.session),self.player);self.window.show_capture()
        self.addCleanup(self.window.dispose)

    def key(self,n):self.window.onAction(types.SimpleNamespace(getId=lambda:n))

    def test_ok_click_opens_once_then_native_pause_click_does_not_double_toggle(self):
        self.window.onControl(self.window.capture);self.key(7);self.assertTrue(self.window.visible)
        self.player.pause.assert_not_called()
        self.window.onControl(self.window.buttons['pause']);self.key(7)
        self.player.pause.assert_called_once()
        self.assertTrue(self.window.buttons['pause'].options['focusTexture'].endswith('xcmate_focus_neon.png'))

    def test_back_hides_osd_without_stop_then_hidden_back_exits_owned_media_with_resume(self):
        self.window.show_bar();self.key(92);self.assertFalse(self.window.visible);self.player.stop.assert_not_called()
        self.key(92);self.player.stop.assert_called_once();self.assertTrue(self.window.closed)
        self.assertEqual(self.state.progress('p','vod','2')['position'],600)

    def test_native_left_right_navigation_is_immediate_and_only_one_step(self):
        self.window.show_bar();first=self.window.buttons['pause'];next_control=first.navigation[3]
        self.window.setFocus(next_control);self.key(2)
        self.assertEqual(self.window.getFocusId(),next_control.getId());self.player.seekTime.assert_not_called()

    def test_seek_requires_capability_and_clamps_to_media_bounds(self):
        self.window.invoke('back');self.player.seekTime.assert_called_with(590)
        self.player.getTime.return_value=2699;self.window.invoke('forward');self.player.seekTime.assert_called_with(2699.9)
        self.player.seekTime.reset_mock();self.flags['Player.SeekEnabled']=False
        self.window.show_bar();self.assertNotIn('back',self.window.buttons);self.assertFalse(self.window.invoke('back'));self.player.seekTime.assert_not_called()

    def test_audio_subtitle_selection_and_toggle_are_real_player_calls(self):
        self.dialog.select.return_value=1;self.window.invoke('audio');self.player.setAudioStream.assert_called_once_with(1)
        self.dialog.select.return_value=0;self.window.invoke('subtitles');self.player.setSubtitleStream.assert_called_once_with(0)
        self.player.showSubtitles.assert_called_with(True)
        self.flags['VideoPlayer.SubtitlesEnabled']=True;self.window.invoke('subtitle_toggle');self.player.showSubtitles.assert_called_with(False)

    def test_stream_takeover_during_track_dialog_does_not_touch_foreign_player(self):
        def takeover(*args):self.player.getVideoInfoTag.return_value.getUniqueID.side_effect=lambda key:'foreign';return 0
        self.dialog.select.side_effect=takeover;self.window.invoke('audio');self.player.setAudioStream.assert_not_called()
        self.window.invoke('stop');self.player.stop.assert_not_called()

    def test_unsupported_audio_and_subtitle_actions_are_hidden(self):
        self.player.getAvailableAudioStreams.return_value=[];self.player.getAvailableSubtitleStreams.return_value=[]
        self.window.show_bar();self.assertFalse({'audio','subtitles','subtitle_toggle'}&self.window.buttons.keys())

    def test_picture_dialog_releases_capture_without_stopping_and_suspends_reopen(self):
        self.window.show_bar();self.window.invoke('video');self.assertTrue(self.window.suspended)
        self.assertIn('ActivateWindow(osdvideosettings)',self.builtins);self.player.stop.assert_not_called()

    def test_ten_movie_and_ten_episode_stop_cycles_checkpoint_before_stop(self):
        for kind in ('vod','episode'):
            for _ in range(10):
                session=dict(self.session,kind=kind,series_id='1',season='1');self.properties['XCMate.MediaSession']=json.dumps(session)
                w=self.osd.MediaOSD(('media',session),self.player);w.show_capture();w.show_bar()
                self.assertTrue(w.invoke('stop'));self.assertTrue(w.closed)
        self.assertEqual(self.player.stop.call_count,20)
        self.assertEqual(self.state.progress('p','episode','2','1','1')['position'],600)

    def test_service_poll_ignores_live_foreign_and_modal_playback(self):
        self.properties.clear();self.osd.poll(self.player);self.assertIsNone(self.osd._window)
        self.properties['XCMate.MediaSession']=json.dumps(self.session)
        sys.modules['xbmcgui'].getCurrentWindowDialogId=lambda:12005
        self.osd.poll(self.player);self.assertIsNone(self.osd._window)

    def test_service_poll_disposes_capture_on_foreign_handoff(self):
        self.osd.poll(self.player);self.assertIsNotNone(self.osd._window)
        self.player.getVideoInfoTag.return_value.getUniqueID.side_effect=lambda key:'foreign'
        self.osd.poll(self.player);self.assertIsNone(self.osd._window);self.player.stop.assert_not_called()

    def test_unavailable_pause_and_seek_are_hidden_when_player_rejects_capability(self):
        self.flags['Player.PauseEnabled']=False;self.flags['Player.SeekEnabled']=False
        self.window.show_bar()
        self.assertNotIn('pause',self.window.buttons);self.assertNotIn('back',self.window.buttons)
        self.assertEqual(self.window.focus_action(),'info');self.assertFalse(self.window.invoke('pause'))
        self.player.pause.assert_not_called()


    def test_future_download_registry_is_absent_and_extensions_receive_ids_only(self):
        actions=importlib.import_module('media_actions');self.assertNotIn('download',[a[0] for a in actions.available(self.session,self.window.capabilities())])
        handler=mock.Mock();actions.register('future',33010,handler,lambda ids:ids['kind']=='episode',kinds=('episode',))
        self.assertNotIn('future',[a[0] for a in actions.available(self.session,{})])
        episode=dict(self.session,kind='episode',url='PRIVATE',series_id='1');actions.extension('future',episode)
        self.assertNotIn('url',handler.call_args.args[0]);self.assertEqual(handler.call_args.args[0]['series_id'],'1')
