"""Own tagged player, asynchronous Stop, persistent intent and native callback wiring."""
import ast,importlib,json,sys,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture,LIB,ADDON

class StopTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for n in ('live_exit','playback_exit','live_overlay'):sys.modules.pop(n,None)
        sys.modules['xbmcgui'].WindowDialog=object
        self.live=importlib.import_module('live_overlay');self.exit=importlib.import_module('live_exit')
        self.session=dict(pid='p',sid='1',nonce='own',at=time.time())
        self.properties[self.exit.SESSION]=json.dumps(self.session)
        self.playing=True;self.tag=json.dumps(self.session);self.stops=0;self.sync=True;self.callbacks=[]
        def stop():
            self.stops+=1;self.assertFalse(self.callbacks)
            if self.sync:self.playing=False
        self.player=types.SimpleNamespace(isPlayingVideo=lambda:self.playing,isPlaying=lambda:self.playing,stop=stop,
            getVideoInfoTag=lambda:types.SimpleNamespace(getUniqueID=lambda key:self.tag if key=='xcmate_live' else ''))
        sys.modules['xbmc'].Player=lambda:self.player
        self.nav=types.SimpleNamespace(portal=self.portal,sid='1',_closed=False,_owned_token=('live',self.session))
        def close():self.assertFalse(self.callbacks);self.nav._closed=True
        self.nav.close=mock.Mock(side_effect=close)
    def ready(self):
        value=self.exit.state();value['not_before']=0;self.exit._save(value)
    def finish(self):
        self.ready()
        for _ in range(4):self.exit.poll(self.nav)
    def test_request_is_callback_only_and_many_ticks_stop_and_return_exactly_once(self):
        self.callbacks.append('native')
        self.assertTrue(self.exit.request(self.nav));self.assertTrue(self.exit.request(self.nav))
        self.assertEqual(self.stops,0);self.nav.close.assert_not_called();self.assertFalse(self.builtins)
        self.callbacks.clear();self.finish()
        for _ in range(20):self.exit.poll(self.nav)
        self.assertEqual(self.stops,1);self.nav.close.assert_called_once()
        self.assertEqual(len(self.builtins),1);self.assertIn('action=xcmate_home',self.builtins[0]);self.assertNotIn('home_start',self.builtins[0])
        self.assertEqual(self.exit.state()['phase'],'complete')
    def test_async_stop_holds_input_and_recovery_until_video_really_ends(self):
        self.sync=False;self.exit.request(self.nav);self.ready()
        for _ in range(10):self.assertTrue(self.exit.poll(self.nav))
        self.assertEqual(self.stops,1);self.nav.close.assert_not_called();self.assertFalse(self.builtins)
        self.playing=False;self.finish();self.assertEqual(len(self.builtins),1)
    def test_changed_foreign_item_between_request_and_tick_is_never_stopped_or_navigated(self):
        self.exit.request(self.nav);self.ready();self.tag='foreign'
        self.exit.poll(self.nav);self.assertEqual(self.stops,0);self.assertFalse(self.builtins)
        self.assertEqual(self.exit.state()['phase'],'failed')
    def test_wrong_portal_or_forged_announcement_never_creates_intent(self):
        self.nav.portal=dict(self.portal,id='other');self.assertFalse(self.exit.request(self.nav))
        self.nav.portal=self.portal;self.properties[self.exit.SESSION]=json.dumps(dict(self.session,nonce='new'))
        self.assertFalse(self.exit.request(self.nav));self.assertIsNone(self.exit.state());self.assertEqual(self.stops,0)
    def test_new_explicit_session_cancels_old_exit_without_clearing_new_marker(self):
        self.exit.request(self.nav);new=self.live.announce('p','2')
        self.assertIsNone(self.exit.state());self.exit.poll(self.nav)
        self.assertEqual(json.loads(self.properties[self.exit.SESSION])['nonce'],new['nonce']);self.assertEqual(self.stops,0);self.assertFalse(self.builtins)
    def test_stopped_native_player_uses_last_verified_item_and_returns_home(self):
        self.playing=False;self.assertTrue(self.exit.request(self.nav));self.finish()
        self.assertEqual(self.stops,0);self.assertEqual(len(self.builtins),1)
    def test_stop_timeout_is_bounded_no_retry_loop_no_false_home(self):
        self.sync=False;self.exit.request(self.nav);value=self.exit.state();value.update(not_before=0,deadline=0);self.exit._save(value)
        for _ in range(8):self.exit.poll(self.nav)
        self.assertEqual(self.stops,1);self.assertEqual(self.exit.state()['phase'],'failed');self.assertFalse(self.builtins)
    def test_preplay_properties_are_nonce_scoped_and_cancel_is_retained(self):
        for key in ('XCMate.PrePlay.Request','XCMate.PrePlay.Ready','XCMate.PrePlay.Ack'):
            self.properties[key]=json.dumps(self.session) if key.endswith('Request') else 'own'
        self.exit.request(self.nav);self.finish()
        self.assertEqual(self.properties.get('XCMate.PrePlay.Cancel'),'own')
        self.assertFalse(self.properties.get('XCMate.PrePlay.Request'));self.assertFalse(self.properties.get('XCMate.PrePlay.Ready'))
    def test_future_new_session_properties_are_not_erased(self):
        self.exit.request(self.nav);self.properties['XCMate.PrePlay.Request']=json.dumps(dict(self.session,nonce='other'))
        self.finish();self.assertIn('other',self.properties['XCMate.PrePlay.Request'])
    def test_home_start_is_action_not_reloadable_directory(self):
        home=importlib.import_module('home_menu');home.show(self.router,self.portal)
        rows=[row for row in self.added if 'action=home_start' in row[0]]
        self.assertEqual(len(rows),1);self.assertFalse(rows[0][2]);self.assertEqual(rows[0][1].props['IsPlayable'],'false')
    def test_legacy_start_folder_anchors_home_before_play_and_new_action_keeps_home(self):
        self.router._params['action']='home_start';self.router._play_start_direct=mock.Mock()
        self.routes.dispatch(self.router);self.assertIn('action=xcmate_home',self.current_folder)
        self.assertEqual(len(self.added),6);self.assertEqual(sum('action=home_start' in x[0] for x in self.added),1)
        self.assertEqual(self.router._play_start_direct.call_count,1)
        self.router._handle=-1;self.builtins.clear();self.routes.dispatch(self.router)
        self.assertFalse(self.builtins);self.assertEqual(self.router._play_start_direct.call_count,2)
    def test_controls_stop_long_back_hidden_back_and_native_stop_only_request(self):
        nav=self.live.LiveNavigator.__new__(self.live.LiveNavigator)
        nav.mode='hidden';nav._closed=False;nav._request_exit=mock.Mock(return_value=True)
        nav._execute('controls',3);nav._handle_command('long_back');nav._handle_command('back')
        nav.onAction(types.SimpleNamespace(getId=lambda:13,getButtonCode=lambda:0))
        self.assertEqual(nav._request_exit.call_count,4);self.assertEqual(self.stops,0);self.assertFalse(self.builtins)
    def test_exit_latch_blocks_late_ok_back_and_zap(self):
        nav=self.live.LiveNavigator.__new__(self.live.LiveNavigator)
        nav._closed=False;nav._exiting=True
        self.assertFalse(nav._accept_input());self.assertEqual(self.stops,0)
    def test_service_gate_is_before_playback_exit_preplay_and_recovery_but_after_background_jobs(self):
        source=(ADDON/'service.py').read_text();self.assertLess(source.index('exiting=poll_live_exit'),source.index('if not exiting:poll_playback_exit'))
        self.assertLess(source.index('if exiting:'),source.index('poll_preplay(self._overlay)'))
        self.assertLess(source.index('poll_app_features()'),source.index('if exiting:'))
    def test_exit_blocks_root_autoplay_until_explicit_selection(self):
        spec=importlib.util.spec_from_file_location('main_stop17',LIB/'main.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        router=module.Router(['plugin://plugin.video.xtreammate','7','?action=root'])
        self.exit.request(self.nav);self.playing=False;self.options['autoplay_diagnostics_safe']=False
        self.portal['autoplay_start']=True;router._maybe_autoplay_start(self.portal)
        self.assertFalse(self.builtins)
        self.exit.new_selection();self.assertIsNone(self.exit.state())
    def test_double_stop_ten_sessions_do_not_block_new_conscious_selection(self):
        for i in range(10):
            self.session=dict(self.session,nonce='session'+str(i));self.tag=json.dumps(self.session);self.properties[self.exit.SESSION]=self.tag
            self.exit.new_selection();self.playing=True;self.nav._exiting=False;self.nav._closed=False;self.nav.close.reset_mock()
            self.assertTrue(self.exit.request(self.nav));self.assertTrue(self.exit.request(self.nav));self.finish()
        self.assertEqual(self.stops,10);self.assertEqual(len(self.builtins),10)
    def test_disappearing_infotag_cannot_terminate_service_or_stop_foreign(self):
        self.exit.request(self.nav)
        self.player.getVideoInfoTag=mock.Mock(side_effect=RuntimeError('unavailable'))
        self.assertTrue(self.exit.poll(self.nav));self.assertEqual(self.stops,0);self.assertFalse(self.builtins)
    def test_modal_is_not_forcibly_closed_or_navigated_away(self):
        self.exit.request(self.nav);self.ready();self.exit.poll(self.nav)
        with mock.patch.object(sys.modules['xbmc'],'getCondVisibility',return_value=True):
            for _ in range(3):self.exit.poll(self.nav)
        self.assertFalse(self.builtins)
        self.exit.poll(self.nav);self.assertEqual(len(self.builtins),1)
    def test_completed_live_exit_does_not_disable_later_media_or_foreign_player_service(self):
        self.exit.request(self.nav);self.finish();self.playing=True;self.tag='foreign-video'
        self.assertFalse(self.exit.poll(self.nav));self.assertEqual(self.exit.state()['phase'],'complete')
        self.assertEqual(self.stops,1);self.assertEqual(len(self.builtins),1)
    def test_stop_during_warm_tune_cancels_pending_nonce_and_either_verified_item(self):
        for completes in (False,True):
            self.exit.new_selection();self.nav._exiting=False;self.nav._closed=False;self.playing=True
            self.properties[self.exit.SESSION]=json.dumps(dict(self.session,sid='2',nonce='pending'))
            self.nav.sid='2';self.nav._previous_session=self.session
            self.tag=json.dumps(self.session)
            self.assertTrue(self.exit.request(self.nav));self.assertEqual(self.properties['XCMate.PrePlay.Cancel'],'pending')
            if completes:self.tag=self.properties[self.exit.SESSION]
            self.finish();self.assertEqual(self.exit.state()['phase'],'complete')
        self.assertEqual(self.stops,2)
