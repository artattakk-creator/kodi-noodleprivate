"""P0 Android race replays: explicit intent, native release and stop quarantine."""
import importlib,json,sys,threading,time,types,unittest
from unittest import mock
import test_xcmate_exit_040 as base
import test_xcmate_live_stop_02917 as live
import test_xcmate_return_02939 as origin

class PlayerStability40(unittest.TestCase):
    def setUp(self):
        self.m=base.ExitTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.jobs=importlib.import_module('exit_jobs')

    def test_twenty_decoder_start_fullscreen_flaps_never_authorize_a_stop(self):
        for kind in ('vod','episode'):
            self.m.session['kind']=kind;self.m.properties[self.m.progress.PROPERTY]=json.dumps(self.m.session)
            for _ in range(20):
                for full in (False,True,False,True,False):self.assertFalse(self.m.exit.poll(self.m.player,full))
        self.assertIsNone(self.jobs.state());self.assertFalse(self.m.stops)

    def test_owner_view_poll_during_decoder_start_does_not_stop_or_request_return(self):
        w=self.m.media_window();w._play(w.rows[0],'vod');self.m.media_id=w._play_intent
        self.m.session['nonce']=w._play_intent;self.m.properties[self.m.progress.PROPERTY]=json.dumps(self.m.session)
        with mock.patch.object(sys.modules['xbmc'],'getCondVisibility',return_value=False):
            for _ in range(20):w._poll_playback_return();w.onInit()
        self.assertIsNone(self.jobs.state());self.assertFalse(self.m.stops)
        self.assertFalse(importlib.import_module('media_return').read()['requested'])

    def test_explicit_user_stop_is_single_flight_and_logs_whitelisted_cause(self):
        token=self.m.exit.identity(self.m.player)
        for _ in range(20):self.assertTrue(self.jobs.request(self.m.player,expected=token,reason='USER_STOP'))
        self.assertEqual(self.jobs.state()['reason'],'USER_STOP')
        from exit37_fixture import drain_stop
        drain_stop();self.assertEqual(len(self.m.stops),1)
        self.assertFalse(self.jobs.request(self.m.player,reason='provider.invalid/private'))

    def test_explicit_startup_cancel_still_stops_only_owned_item(self):
        import media_intent
        self.m.properties[media_intent.REQUEST]=json.dumps(self.m.session)
        self.assertTrue(media_intent.cancel('p','own'))
        self.assertTrue(self.m.exit.poll(self.m.player,False))
        self.assertEqual(self.jobs.state()['reason'],'STARTUP_ABORT')
        from exit37_fixture import drain_stop
        drain_stop();self.assertEqual(len(self.m.stops),1)

    def test_native_dialog_must_really_release_before_stop_worker_starts(self):
        self.jobs.request(self.m.player,reason='USER_BACK')
        v=self.jobs.state();v['not_before']=0;self.jobs.save(v)
        gui=sys.modules['xbmcgui']
        with mock.patch.object(gui,'getCurrentWindowDialogId',return_value=13003,create=True):
            for _ in range(20):self.assertTrue(self.jobs.poll())
        self.assertIsNone(self.jobs._thread);self.assertFalse(self.m.stops)
        with mock.patch.object(gui,'getCurrentWindowDialogId',return_value=9999,create=True):
            self.jobs.poll();self.jobs._thread.join(2)
        self.assertEqual(len(self.m.stops),1)

    def test_foreign_modal_release_timeout_never_stops_or_closes_dialog(self):
        self.jobs.request(self.m.player);v=self.jobs.state();v.update(not_before=0,deadline=0);self.jobs.save(v)
        with mock.patch.object(sys.modules['xbmcgui'],'getCurrentWindowDialogId',return_value=10124,create=True):self.jobs.poll()
        self.assertEqual(self.jobs.state()['phase'],'timeout');self.assertFalse(self.jobs.blocked())
        self.assertFalse(self.m.stops);self.assertFalse(self.m.builtins)

    def test_blocked_native_stop_quarantines_queries_and_retries_even_after_timeout(self):
        entered=threading.Event();release=threading.Event();calls=[]
        def stop():calls.append(1);entered.set();release.wait(4)
        self.m.player.stop=stop
        self.jobs.request(self.m.player);v=self.jobs.state();v['not_before']=0;self.jobs.save(v);self.jobs.poll()
        try:
            self.assertTrue(entered.wait(1));v=self.jobs.state();v['deadline']=0;self.jobs.save(v);self.jobs.poll()
            self.assertTrue(self.jobs.blocked());self.assertEqual(self.jobs.state()['phase'],'timeout')
            self.m.player.isPlayingVideo=mock.Mock(side_effect=AssertionError('native player mutex'))
            for _ in range(20):
                self.assertFalse(self.jobs.request(self.m.player,manual=True));self.assertFalse(self.m.exit.poll(self.m.player))
                self.assertTrue(self.jobs.blocked());self.jobs.poll()
            # Simulate another Python interpreter with no local thread handle.
            worker=self.jobs._thread;self.jobs._thread=None
            self.assertFalse(self.jobs.request(self.m.player,manual=True));self.jobs._thread=worker
            self.assertEqual(calls,[1])
        finally:release.set();self.jobs._thread.join(2)
        self.assertTrue(self.jobs.state()['worker_done']);self.assertFalse(self.jobs.blocked())

    def test_foreign_replacement_before_stop_worker_never_receives_stop(self):
        self.jobs.request(self.m.player);self.m.media_id='foreign'
        from exit37_fixture import drain_stop
        drain_stop();self.assertFalse(self.m.stops);self.assertEqual(self.jobs.state()['phase'],'failed')

class LiveQuarantine40(unittest.TestCase):
    def test_live_exit_poll_during_blocked_stop_does_not_query_player(self):
        m=live.StopTests(methodName='runTest');m.setUp();self.addCleanup(m.doCleanups)
        m.exit.request(m.nav)
        jobs=importlib.import_module('exit_jobs')
        with mock.patch.object(jobs,'blocked',return_value=True),mock.patch.object(m.player,'isPlayingVideo',side_effect=AssertionError('native lock')):
            for _ in range(20):self.assertTrue(m.exit._poll(m.nav))
        self.assertFalse(m.stops);self.assertFalse(m.builtins)

class SearchNative40(unittest.TestCase):
    def test_search_native_modal_released_without_discarding_origin_or_owner(self):
        m=origin.Return39(methodName='runTest');m.setUp();self.addCleanup(m.doCleanups)
        def run(w):w.show();w._owner_tick();m.settle(w)
        with mock.patch.object(m.media.MediaView,'run',run):w=m.media.open_search(m.router,m.portal,'House')
        self.addCleanup(w.close);w._search_click(701);m.settle(w);w._play(w._search_rows[0],'vod')
        self.assertFalse(w._closed);self.assertIsNotNone(w._playback_origin39)
        self.assertEqual(m.returning.read()['owner'],w._native_owner)

class FailedStartup40(base.Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.player=mock.Mock();self.player.isPlayingVideo.return_value=False;self.player.isPlaying.return_value=False
        sys.modules['xbmc'].Player=lambda:self.player

    def test_failed_resolver_restores_origin_without_stop_and_releases_pending_guard(self):
        w=self.media_window();w._play(w.rows[0],'vod')
        intent=importlib.import_module('media_intent');self.assertTrue(intent.failed(w._play_intent,'p'))
        w._poll_playback_return();self.assertFalse(w._playback_waiting);self.player.stop.assert_not_called()
        self.assertTrue(intent.cancelled(dict(pid='p',sid=w.rows[0]['sid'],nonce=w._play_intent)))

    def test_decoder_failure_before_first_video_has_bounded_return_without_stop(self):
        w=self.media_window();w._play(w.rows[0],'vod');w._playback_started40=time.monotonic()-21
        w._poll_playback_return();self.assertFalse(w._playback_waiting);self.player.stop.assert_not_called()

    def test_startup_deadline_never_stops_or_returns_over_active_foreign_player(self):
        w=self.media_window();w._play(w.rows[0],'vod');w._playback_started40=time.monotonic()-21
        self.player.isPlaying.return_value=True;w._poll_playback_return()
        self.assertTrue(w._playback_waiting);self.player.stop.assert_not_called()

    def test_suspended_search_dialog_with_unknown_native_id_is_shown_on_failed_start_return(self):
        def run(w):w.show();w._owner_tick();self.settle(w)
        with mock.patch.object(self.media.MediaView,'run',run):w=self.media.open_search(self.router,self.portal,'House')
        self.addCleanup(w.close);w._search_click(701);self.settle(w);w._play(w._search_rows[0],'vod')
        self.assertFalse(w.shown);self.assertTrue(w._origin_suspended40)
        importlib.import_module('media_intent').failed(w._play_intent,'p');w._poll_playback_return()
        self.assertTrue(w.shown);self.assertFalse(w._playback_waiting);self.assertEqual(w._search_query,'House')
        self.player.stop.assert_not_called()

    def test_pending_native_stop_blocks_new_vod_and_live_handshake(self):
        w=self.media_window();jobs=importlib.import_module('exit_jobs')
        with mock.patch.object(jobs,'blocked',return_value=True):
            w._play(w.rows[0],'vod')
            self.assertFalse(importlib.import_module('play_intent').before_play(dict(nonce='new')))
        self.assertFalse(self.builtins);self.assertFalse(w._playback_waiting);self.player.stop.assert_not_called()

    def test_old_service_running_stop_without_completion_fields_stays_quarantined(self):
        jobs=importlib.import_module('exit_jobs')
        token=('media',dict(pid='p',sid='1',nonce='old-job',at=time.time(),kind='vod'))
        jobs.save(dict(token=token,phase='running',at=time.time(),deadline=0,not_before=0))
        jobs.poll();self.assertEqual(jobs.state()['phase'],'timeout');self.assertTrue(jobs.blocked())
        self.player.stop.assert_not_called()
