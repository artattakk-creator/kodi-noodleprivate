"""Regression coverage for the grid callback/owner/route playback boundary."""
import importlib,sys,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture,QueuedPool,ADDON

class HandoffTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for n in ('guide_grid_window','guide_playback'):sys.modules.pop(n,None)
        self.grid=importlib.import_module('guide_grid_window');self.play=importlib.import_module('guide_playback')
        p=mock.patch.object(self.grid,'ThreadPoolExecutor',QueuedPool);p.start();self.addCleanup(p.stop)
    def window(self):
        w=self.grid.GuideGridWindow('XCMateGuideGrid.xml',str(ADDON),'Default','720p')
        w.configure(self.router,self.portal);w.doModal();self.settle(w);self.addCleanup(w.close);return w
    def intent(self):return self.play.request(self.portal,dict(sid='1'),(False,''))
    def test_watch_callback_never_closes_native_window_or_plays_and_ignores_repeated_input(self):
        w=self.window();self.dialog.select.return_value=1
        with mock.patch.object(w,'close',wraps=w.close) as close:
            w.native(7);w.native(7);w.native(92)
            close.assert_not_called();self.assertFalse(self.builtins)
            self.assertEqual(self.dialog.select.call_count,1);self.assertTrue(w._leaving)
            w._leave_after=0;w._owner_tick();close.assert_called_once()
        self.assertIsNone(w._pending_future);self.assertIsNone(w._pending_apply)
        self.assertTrue(self.play.handoff(self.router,self.portal,w._play_request))
        self.assertFalse(self.play.handoff(self.router,self.portal,w._play_request))
        self.assertEqual(len(self.builtins),1)
    def test_handoff_runs_after_navigation_ownership_is_released(self):
        nav=importlib.import_module('window_navigation');seen=[];self.router._handle=-1
        def after(router,portal,intent):
            with nav.ownership() as acquired:seen.append(acquired)
            self.play.handoff(router,portal,intent)
        nav.open_route(self.router,self.portal,self.intent,after_close=after)
        self.assertEqual(seen,[True]);self.assertEqual(len(self.builtins),1)
    def test_window_wrapper_returns_detached_intent_without_native_window(self):
        w=self.window();w._play_request=self.intent();w.close()
        with mock.patch.object(self.grid,'open_owned_window',return_value=w):result=self.grid.open_grid(self.router,self.portal)
        self.assertIs(result,w._play_request);self.assertNotIn(w,result.values())
    def test_cancel_invalid_sender_portal_or_changed_player_without_stop_or_play(self):
        for change in ('sid','pid','player','disabled'):
            intent=self.intent()
            if change=='sid':intent['sid']='missing'
            elif change=='pid':intent['pid']='other'
            elif change=='player':intent['player']=(True,'foreign-session')
            else:self.portal['enabled']=False
            self.assertFalse(self.play.handoff(self.router,self.portal,intent));self.portal['enabled']=True
        self.assertFalse(self.builtins)
    def test_native_window_must_be_inactive_before_playback(self):
        intent=self.intent();intent['window']=13001
        with mock.patch.object(sys.modules['xbmcgui'],'getCurrentWindowId',return_value=13001,create=True),mock.patch.object(self.play.time,'monotonic',side_effect=[0,3]):
            self.assertFalse(self.play.handoff(self.router,self.portal,intent))
        self.assertFalse(self.builtins)
    def test_each_supported_source_uses_only_existing_live_resolver_once(self):
        for kind,action in [('xtream','play_live'),('m3u','source_play'),('stb','source_play')]:
            self.portal['type']=kind;intent=self.intent()
            self.assertTrue(self.play.handoff(self.router,self.portal,intent));self.assertFalse(self.play.handoff(self.router,self.portal,intent))
            self.assertIn('action='+action,self.builtins[-1]);self.assertIn('sid=1',self.builtins[-1])
        self.assertEqual(len(self.builtins),3)
    def test_real_owner_loop_closes_outside_callback_then_dispatches_after_unlock(self):
        nav=importlib.import_module('window_navigation');self.router._handle=-1
        windows=[];phase=[0];in_callback=[False]
        original=self.grid.GuideGridWindow.configure
        def configure(w,*args):original(w,*args);windows.append(w)
        def wait(seconds):
            if not windows:return False
            w=windows[0];phase[0]+=1
            if phase[0]==1:w._pool.drain()
            elif phase[0]==2:
                in_callback[0]=True
                w.native(7);self.assertFalse(w._closed);self.assertFalse(self.builtins)
                in_callback[0]=False;w._leave_after=0
            elif phase[0]>8:self.fail('owner did not finish')
            return False
        monitor=types.SimpleNamespace(waitForAbort=wait)
        self.dialog.select.return_value=1
        def after(router,portal,intent):
            w=windows[0];self.assertTrue(w._closed);self.assertFalse(w._running);self.assertFalse(in_callback[0])
            self.assertIsNone(w._pending_apply)
            with nav.ownership() as acquired:self.assertTrue(acquired)
            self.assertTrue(self.play.handoff(router,portal,intent))
        with mock.patch.object(self.grid.GuideGridWindow,'configure',configure),mock.patch.object(sys.modules['xbmc'],'Monitor',return_value=monitor):
            nav.open_route(self.router,self.portal,lambda:self.grid.open_grid(self.router,self.portal),after_close=after)
        self.assertEqual(sum(s.startswith('PlayMedia(') for s in self.builtins),1)
    def test_foreign_audio_started_during_guide_is_preserved(self):
        intent=self.intent()
        with mock.patch.object(sys.modules['xbmc'],'Player',return_value=types.SimpleNamespace(isPlaying=lambda:True,getPlayingFile=lambda:'foreign-audio')):
            self.assertFalse(self.play.handoff(self.router,self.portal,intent))
        self.assertFalse(self.builtins)
    def test_new_nonce_on_same_playing_path_cancels_stale_handoff(self):
        intent=self.intent();self.properties['XtreamMate.LiveSession']='new-session'
        self.assertFalse(self.play.handoff(self.router,self.portal,intent));self.assertFalse(self.builtins)
