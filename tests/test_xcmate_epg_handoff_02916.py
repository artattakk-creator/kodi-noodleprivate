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
