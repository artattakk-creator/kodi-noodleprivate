"""Real service/action/Guide boundaries in a native-dialog host model."""
import importlib,json,sys,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture,ADDON,QueuedPool
import test_xcmate_kodi21_overlay as _overlay_model


class InfoButton35(unittest.TestCase):
    setUp=_overlay_model.OverlayLifecycleTests.setUp
    def test_only_extra_epg_button_queues_one_request_after_native_double_delivery(self):
        self.overlay._switch('extras');self.overlay._focus_extra=3;self.overlay._render()
        helper=types.SimpleNamespace(request=mock.Mock(side_effect=lambda nav:setattr(nav,'_guide_handoff',True)))
        with mock.patch.dict(sys.modules,live_guide_navigation=helper):
            self.overlay.native(7);self.overlay.native(7)
        helper.request.assert_called_once_with(self.overlay)
        self.player.stop.assert_not_called();self.player.play.assert_not_called()
        sys.modules['xbmc'].executebuiltin.assert_not_called()

    def test_left_keeps_the_mini_list_then_groups_and_configured_epg_key_stays_mini(self):
        self.overlay._switch('hidden');self.overlay.handle_command('left');self.assertEqual(self.overlay.mode,'channels')
        self.overlay.handle_command('left');self.assertEqual(self.overlay.mode,'groups')
        self.overlay.handle_command('epg');self.assertEqual(self.overlay.mode,'guide')
        self.player.stop.assert_not_called()


class LiveGuide35(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('live_overlay','live_guide_navigation','playback_exit','guide_grid_window'):
            sys.modules.pop(name,None)
        self.gui=sys.modules['xbmcgui'];self.xbmc=sys.modules['xbmc'];self.gui.WindowDialog=object
        self.live=importlib.import_module('live_overlay');self.module=importlib.import_module('live_guide_navigation')
        self.session=dict(pid='p',sid='1',nonce='own',at=time.time())
        self.properties[self.live.SESSION_KEY]=json.dumps(self.session)
        self.properties['XtreamMate.NavigatorIdentity']='native-owner'
        self.dialog_id=13007;self.foreign=False;self.tag=json.dumps(self.session)
        self.player=types.SimpleNamespace(isPlayingVideo=lambda:True,isPlaying=lambda:True,
            getPlayingFile=lambda:'private-playing-path',stop=mock.Mock(),play=mock.Mock(),
            getVideoInfoTag=lambda:types.SimpleNamespace(getUniqueID=lambda key:self.tag if key=='xcmate_live' else ''))
        self.xbmc.Player=lambda:self.player
        self.gui.getCurrentWindowId=lambda:12005
        def native_dialog():
            active=getattr(self.xbmc,'_focus_window',None)
            return 13001 if active is not None and active.shown else self.dialog_id
        self.gui.getCurrentWindowDialogId=native_dialog
        original=self.xbmc.getCondVisibility
        self.xbmc.getCondVisibility=lambda c:(self.dialog_id not in (0,9999) if c=='System.HasActiveModalDialog' else True if c=='Window.IsActive(fullscreenvideo)' else original(c))
        self.nav=types.SimpleNamespace(portal=self.portal,sid='1',_closed=False,_window_nonce='native-owner',owns_playback=lambda:True)
        def suspend():self.nav._closed=True;self.dialog_id=9999
        self.nav.suspend_for_guide=mock.Mock(side_effect=suspend)
        self.grid=importlib.import_module('guide_grid_window')
        patch=mock.patch.object(self.grid,'ThreadPoolExecutor',QueuedPool);patch.start();self.addCleanup(patch.stop)

    def dispatch(self):
        self.assertTrue(self.module.request(self.nav));self.assertTrue(self.module.poll(self.nav))
        self.assertTrue(self.module.poll(self.nav));return self.module._state()['token']

    def test_callback_never_closes_or_navigates_and_service_dispatch_is_once(self):
        self.assertTrue(self.module.request(self.nav));self.assertFalse(self.module.request(self.nav))
        self.nav.suspend_for_guide.assert_not_called();self.assertFalse(self.builtins)
        self.module.poll(self.nav);self.module.poll(self.nav)
        for _ in range(10):self.module.poll(self.nav)
        self.nav.suspend_for_guide.assert_called_once();self.assertEqual(len(self.builtins),1)
        self.assertIn('action=live_guide&token=',self.builtins[0]);self.assertNotIn('pid=',self.builtins[0])
        self.player.stop.assert_not_called();self.player.play.assert_not_called()
        self.assertEqual(json.loads(self.properties[self.live.SESSION_KEY]),self.session)

    def test_real_guide_owner_back_returns_without_home_or_restarting_player(self):
        token=self.dispatch();seen=[]
        def run(window):
            window.show();self.settle(window);seen.append(window)
            self.assertTrue(self.module.preserves_player());self.assertEqual(self.module._state()['phase'],'ACTIVE')
            self.assertFalse(self.module.run(token));window.close()
        with mock.patch.object(self.grid.GuideGridWindow,'run',run):self.assertTrue(self.module.run(token))
        self.assertEqual(len(seen),1);self.assertFalse(self.module.poll(self.nav))
        self.assertEqual(self.module.consume_resume(),'own');self.assertEqual(self.module.consume_resume(),'')
        self.assertEqual(len(self.builtins),1);self.player.stop.assert_not_called();self.player.play.assert_not_called()
        self.assertFalse(any('Container.Update' in c or 'ActivateWindow' in c for c in self.builtins))

    def test_selected_channel_reaches_existing_resolver_only_after_unlock(self):
        token=self.dispatch();play=importlib.import_module('guide_playback')
        def run(window):
            window.show();self.settle(window);self.dialog.select.return_value=1;window.native(7)
            window._leave_after=0;window._owner_tick()
        with mock.patch.object(self.grid.GuideGridWindow,'run',run):self.assertTrue(self.module.run(token))
        self.assertEqual(sum(c.startswith('PlayMedia(') for c in self.builtins),1)
        self.assertEqual(self.module._state()['phase'],'SWITCH');self.assertTrue(self.module.poll(self.nav))
        self.assertFalse(self.module.run(token));self.player.stop.assert_not_called()

    def test_foreign_modal_waits_without_close_and_foreign_player_rejects(self):
        self.assertTrue(self.module.request(self.nav));self.dialog_id=10103
        self.assertTrue(self.module.poll(self.nav));self.nav.suspend_for_guide.assert_not_called();self.assertFalse(self.builtins)
        self.tag='foreign';self.assertFalse(self.module.poll(self.nav));self.nav.suspend_for_guide.assert_not_called()
        self.player.stop.assert_not_called();self.assertFalse(self.module.preserves_player())

    def test_dispatch_timeout_and_stale_token_cannot_reopen_guide(self):
        token=self.dispatch();state=self.module._state();state['deadline']=0;self.module._save(state)
        self.assertFalse(self.module.run(token));self.assertFalse(self.module.poll(self.nav))
        self.assertFalse(self.module.run(token));self.assertEqual(len(self.builtins),1)

    def test_missing_lease_after_plugin_failure_releases_intent_without_player_work(self):
        token=self.dispatch();state=self.module._state();state.update(phase='ACTIVE',lease='a'*32);self.module._save(state)
        self.assertFalse(self.module.poll(self.nav));self.assertIsNone(self.module._state())
        self.assertEqual(self.module.consume_resume(),'own');self.player.stop.assert_not_called()

    def test_action_route_does_not_anchor_home_or_enumerate_portals(self):
        self.router._handle=-1;self.router._params={'action':'live_guide','token':'a'*32}
        with mock.patch.object(self.module,'run') as run,mock.patch.object(self.routes,'portal_for',side_effect=AssertionError('unneeded portal enumeration')):
            self.routes.dispatch(self.router)
        run.assert_called_once_with('a'*32);self.assertFalse(self.builtins)

    def test_guide_guard_does_not_claim_new_media_or_other_portals(self):
        self.dispatch();self.tag='foreign';self.assertFalse(self.module.preserves_player())
        self.assertEqual(len(self.builtins),1);self.player.stop.assert_not_called()

    def test_resume_waits_for_foreign_modal_and_never_replaces_new_session(self):
        self.module._finish(dict(token='a'*32,session=self.session),types.SimpleNamespace(_closed=True))
        self.dialog_id=10103;self.assertEqual(self.module.consume_resume(),'')
        self.dialog_id=9999;nonce=self.module.consume_resume();self.assertEqual(nonce,'own')
        candidate=types.SimpleNamespace(mode='hidden',owns_playback=lambda:True,_info_timeout=5)
        self.module.restore_info(candidate,nonce);self.assertEqual(candidate.mode,'info')
        candidate.mode='hidden';self.properties[self.live.SESSION_KEY]=json.dumps(dict(self.session,nonce='new'))
        self.module.restore_info(candidate,nonce);self.assertEqual(candidate.mode,'hidden')

    def test_service_keeps_autoplay_background_and_preplay_before_guide_overlay_guard(self):
        import ast
        source=(ADDON/'service.py').read_text()
        ast.parse(source)
        self.assertLess(source.index('poll_app_features()'),source.index('if guide_active:'))
        self.assertLess(source.index('poll_preplay(self._overlay)'),source.index('if guide_active:'))
        self.assertLess(source.index('if guide_active:'),source.index('recover_from_player_path'))
        self.assertIn('if not exiting and not preserves_player():poll_playback_exit()',source)

    def test_kodi_shutdown_cancels_queued_navigation_without_touching_player(self):
        self.module.request(self.nav)
        with mock.patch.object(self.xbmc,'Monitor',return_value=types.SimpleNamespace(abortRequested=lambda:True)):
            self.assertFalse(self.module.poll(self.nav))
        self.nav.suspend_for_guide.assert_not_called();self.assertFalse(self.builtins);self.player.stop.assert_not_called()
