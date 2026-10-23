"""Search-only direct transfer: no nested Kodi plugin busy resolver."""
import importlib,json,sys,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture


class SearchLiveTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();sys.modules.pop('search_live',None)
        self.live=importlib.import_module('search_live')
        patch=mock.patch.object(sys.modules['xbmcgui'],'WindowDialog',object,create=True)
        patch.start();self.addCleanup(patch.stop)
        for name in ('live_overlay','live_exit'):sys.modules.pop(name,None)
        self.play=mock.Mock();self.play.isPlayingVideo.return_value=False
        self.item=types.SimpleNamespace(getPath=lambda:'https://private.invalid/SECRET')
        for patch in (
            mock.patch.object(sys.modules['xbmc'],'Player',return_value=self.play),
            mock.patch.object(sys.modules['xbmcgui'],'getCurrentWindowId',return_value=10025,create=True),
            mock.patch.dict(sys.modules,player=types.SimpleNamespace(build_playable_item=mock.Mock(return_value=self.item))),
            mock.patch('live_recovery.tag_live_item',return_value=True)):
            patch.start();self.addCleanup(patch.stop)
        self.play.isPlaying.return_value=False

    def intent(self):return dict(pid='p',sid='1',player=(False,''),session='',window=13001)
    def prepare(self):return self.portal,dict(sid='1',name='Test'),'https://private.invalid/SECRET',{}

    def test_direct_play_occurs_once_without_directory_resolver_or_container_transition(self):
        intent=self.intent()
        with mock.patch.object(self.live,'_prepare',return_value=self.prepare()) as prepare:
            self.assertTrue(self.live.handoff(self.router,self.portal,intent))
            self.assertFalse(self.live.handoff(self.router,self.portal,intent))
        prepare.assert_called_once();self.play.play.assert_called_once_with(self.item.getPath(),self.item)
        self.assertFalse(self.builtins);sys.modules['xbmcplugin'].setResolvedUrl.assert_not_called()

    def test_busy_gate_waits_for_actual_clear_without_closing_foreign_dialog(self):
        waits=[];busy=[True]
        def wait(n):waits.append(n);busy[0]=False;return False
        with mock.patch.object(self.live,'_prepare',return_value=self.prepare()),\
             mock.patch.object(sys.modules['xbmc'],'getCondVisibility',side_effect=lambda c:busy[0] and c=='Window.IsActive(busydialognocancel)'),\
             mock.patch.object(sys.modules['xbmc'],'Monitor',return_value=types.SimpleNamespace(waitForAbort=wait)):
            self.assertTrue(self.live.handoff(self.router,self.portal,self.intent()))
        self.assertEqual(waits,[.05]);self.assertFalse(self.builtins)

    def test_stuck_busy_fails_before_source_resolution_or_player(self):
        with mock.patch.object(self.live,'_prepare') as prepare,\
             mock.patch.object(sys.modules['xbmc'],'getCondVisibility',return_value=True),\
             mock.patch.object(self.live.time,'monotonic',side_effect=[0,6]):
            self.assertFalse(self.live.handoff(self.router,self.portal,self.intent()))
        prepare.assert_not_called();self.play.play.assert_not_called()

    def test_player_change_during_resolution_does_not_override_new_playback(self):
        def prepare(*args):self.play.isPlaying.return_value=True;self.play.getPlayingFile.return_value='foreign';return self.prepare()
        with mock.patch.object(self.live,'_prepare',side_effect=prepare):
            self.assertFalse(self.live.handoff(self.router,self.portal,self.intent()))
        self.play.play.assert_not_called()

    def test_unchanged_foreign_player_is_also_rejected(self):
        intent=self.intent();intent['player']=(True,'foreign');self.play.isPlaying.return_value=True;self.play.getPlayingFile.return_value='foreign'
        with mock.patch('playback_exit.identity',return_value=None),mock.patch.object(self.live,'_prepare') as prepare:
            self.assertFalse(self.live.handoff(self.router,self.portal,intent))
        prepare.assert_not_called();self.play.play.assert_not_called()

    def test_session_change_and_shutdown_reject_before_source(self):
        for shutdown in (False,True):
            self.properties['XtreamMate.LiveSession']='' if shutdown else 'new'
            monitor=types.SimpleNamespace(abortRequested=lambda:shutdown,waitForAbort=lambda n:False)
            with mock.patch.object(self.live,'_prepare') as prepare,mock.patch.object(sys.modules['xbmc'],'Monitor',return_value=monitor):
                self.assertFalse(self.live.handoff(self.router,self.portal,self.intent()))
            prepare.assert_not_called()
        self.play.play.assert_not_called()

    def test_tag_failure_rolls_back_own_marker_without_play(self):
        with mock.patch.object(self.live,'_prepare',return_value=self.prepare()),mock.patch('live_recovery.tag_live_item',return_value=False):
            self.assertFalse(self.live.handoff(self.router,self.portal,self.intent()))
        self.assertEqual(self.properties['XtreamMate.LiveSession'],'');self.play.play.assert_not_called()

    def test_source_failure_is_sanitized_and_never_starts_second_attempt(self):
        with mock.patch.object(self.live,'_prepare',side_effect=RuntimeError('https://private.invalid/SECRET')),\
             mock.patch.object(self.live,'mark') as mark:
            self.assertFalse(self.live.handoff(self.router,self.portal,self.intent()))
        self.assertNotIn('SECRET',str(mark.call_args_list));self.play.play.assert_not_called()

    def test_preparation_uses_enabled_reader_channel_and_existing_source_contract(self):
        factory=mock.Mock(return_value=types.SimpleNamespace(live_stream_url=lambda sid:'private-in-memory'))
        with mock.patch.dict(sys.modules,xtream=types.SimpleNamespace(XtreamClient=factory)):
            current,channel,url,headers=self.live._prepare(self.portal,self.intent())
        self.assertEqual((channel['sid'],url,headers),('1','private-in-memory',{}))
        self.portal['enabled']=False
        with self.assertRaises(self.live.Rejected):self.live._prepare(self.portal,self.intent())

    def test_window_must_finish_owner_before_search_handoff(self):
        import media_search
        window=types.SimpleNamespace(_search_live=self.intent(),_closed=False,_running=False)
        with mock.patch.object(self.live,'handoff') as handoff:
            media_search.handoff(self.router,self.portal,window);handoff.assert_not_called()
            window._closed=True;window._running=True
            media_search.handoff(self.router,self.portal,window);handoff.assert_not_called()
            window._running=False;media_search.handoff(self.router,self.portal,window);handoff.assert_called_once()

    def test_guide_handoff_remains_existing_plugin_resolver(self):
        import guide_playback
        self.assertTrue(guide_playback.handoff(self.router,self.portal,self.intent()))
        self.assertEqual(len(self.builtins),1);self.assertTrue(self.builtins[0].startswith('PlayMedia('))


if __name__=='__main__':unittest.main()
