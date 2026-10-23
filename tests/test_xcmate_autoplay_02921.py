"""Real coordinator/resolver/SQLite, with Kodi callback and IR API simulation.

These host tests do not represent physical Android playback acceptance.
"""
import importlib
import json
import sys
import time
import types
import unittest
from unittest import mock
from urllib.parse import parse_qs,urlsplit
from xcmate027_fixture import Fixture,QueuedPool,ADDON


class AutoplayTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('media_autoplay','media_intent','playback_exit','media_osd','media_actions'):
            sys.modules.pop(name,None)
        self.auto=importlib.import_module('media_autoplay');self.intent=importlib.import_module('media_intent')
        self.progress=importlib.import_module('media_progress');self.exit=importlib.import_module('playback_exit')
        self.events=self.auto.Events();self.pool=QueuedPool();self.clock=100.;self.playing=False;self.unique='';self.pos=300.;self.dur=600.
        self.player=mock.Mock();self.player.isPlayingVideo.side_effect=lambda:self.playing
        self.player.isPlaying.side_effect=lambda:self.playing
        self.player.getVideoInfoTag.return_value.getUniqueID.side_effect=lambda k:self.unique if k=='xcmate_media' else ''
        self.player.getTime.side_effect=lambda:self.pos;self.player.getTotalTime.side_effect=lambda:self.dur
        sys.modules['xbmc'].Player=lambda:self.player
        self.rows=[dict(pid='p',kind='episode',series_id='1',sid=sid,season=season,episode=episode,name='Episode '+sid)
                   for sid,season,episode in [('11',1,1),('12',1,2),('14',1,4),('23',2,3)]]
        self.loader=mock.Mock(return_value=self.rows)
        self.c=self.auto.Coordinator(self.player,self.events,self.pool,self.loader,self.builtins.append,clock=lambda:self.clock)
        self.addCleanup(self.c.shutdown)

    def start(self,row=None,root='root',nonce='one',autoplay=True):
        row=row or self.rows[0]
        self.s=dict(row,pid='p',kind='episode',nonce=nonce,at=time.time(),resume=False,autoplay=autoplay,autoplay_chain=root)
        self.playing=True;self.unique=nonce
        self.properties[self.progress.PROPERTY]=json.dumps(self.s)
        self.events.av_started(self.player);self.c.tick();self.pool.drain();self.c.tick()
        return self.s

    def ended(self):
        self.playing=False;self.events.terminal('ended',self.player);self.c.tick()

    def next_start(self):
        self.c.tick()
        command=self.builtins[-1];params={k:v[0] for k,v in parse_qs(urlsplit(command[len('PlayMedia('):-1]).query).items()}
        row=next(e for e in self.rows if e['sid']==params['sid'])
        self.intent.complete(params['intent']);self.start(row,params['autoplay_chain'],params['intent'])
        return params

    def test_three_natural_ends_then_number_gap_and_next_season_without_confirmation(self):
        self.start()
        for sid in ('12','14','23'):
            self.ended();self.assertEqual(self.c.phase,'ENDED_PENDING')
            self.assertEqual(self.next_start()['sid'],sid);self.assertEqual(self.c.phase,'PLAYING')
        self.assertEqual(len(self.builtins),3);self.assertEqual(self.loader.call_count,1)
        self.assertEqual(len({parse_qs(urlsplit(c[len('PlayMedia('):-1]).query)['intent'][0] for c in self.builtins}),3)
        self.ended();self.c.tick();self.assertEqual(self.c.phase,'FINISHED');self.assertEqual(len(self.builtins),3)
        self.assertEqual(self.c.message,'SERIES_FINISHED')

    def test_explicit_later_start_uses_that_episode_and_does_not_replay_first(self):
        self.start(self.rows[2]);self.ended();self.c.tick()
        self.assertIn('sid=23',self.builtins[-1]);self.assertNotIn('sid=11',self.builtins[-1])

    def test_duplicate_end_callbacks_and_repeated_ticks_start_exactly_once(self):
        self.start();self.playing=False
        for _ in range(10):self.events.terminal('ended',self.player)
        self.c.tick()
        for _ in range(15):self.c.tick()
        self.assertEqual(len(self.builtins),1)
        # Even a late duplicate callback with the old snapshot cannot advance pending next.
        self.events.terminal('ended',self.player);self.c.tick();self.assertEqual(len(self.builtins),1)

    def test_late_duplicate_end_after_successor_av_start_cannot_end_playing_successor(self):
        self.start();self.ended();self.next_start();self.events.terminal('ended',self.player);self.c.tick()
        self.assertEqual(self.c.phase,'PLAYING');self.assertEqual(len(self.builtins),1)

    def test_stopped_mid_episode_never_starts_successor_or_marks_episode_finished(self):
        self.start();self.progress.poll(self.player,now=100)
        self.playing=False;self.events.terminal('stopped',self.player);self.c.tick();self.progress.poll(self.player,now=101)
        self.assertEqual(self.c.phase,'CANCELLED');self.assertFalse(self.builtins)
        progress=self.state.progress('p','episode','11','1','1');self.assertEqual(progress['position'],300);self.assertFalse(progress['watched'])

    def test_stop_wins_both_orders_of_terminal_callback_batch(self):
        for kinds in [('ended','stopped'),('stopped','ended'),('ended','error')]:
            self.start(nonce=str(kinds));self.playing=False
            for kind in kinds:self.events.terminal(kind,self.player)
            self.c.tick();self.c.tick();self.assertFalse(self.builtins);self.assertEqual(self.c.phase,'CANCELLED')

    def test_stop_after_end_before_launch_cancels_chain(self):
        self.start();self.ended();self.auto.request_cancel('root','p');self.c.tick()
        self.assertFalse(self.builtins);self.assertEqual(self.c.phase,'CANCELLED')

    def test_hardware_stopped_callback_during_pending_resolver_cancels_new_intent(self):
        self.start();self.ended();self.c.tick();self.assertEqual(len(self.builtins),1)
        nonce=self.c.session['nonce'];self.events.terminal('stopped',self.player);self.c.tick()
        self.assertEqual(self.c.phase,'CANCELLED')
        # Coordinator cancellation must also invalidate an already issued resolver.
        self.assertFalse(self.intent.allowed(nonce,'p','episode','12'))

    def test_stop_during_launch_race_rejects_resolver_before_resolution(self):
        self.start();self.ended()
        def launch(cmd):self.builtins.append(cmd);self.auto.request_cancel('root','p')
        self.c.launch=launch;self.c.tick()
        params={k:v[0] for k,v in parse_qs(urlsplit(self.builtins[-1][len('PlayMedia('):-1]).query).items()}
        self.router._params=params
        builder=mock.Mock()
        with mock.patch.dict(sys.modules,player=types.SimpleNamespace(build_playable_item=builder)):
            self.progress.play(self.router,self.portal)
        self.assertFalse(sys.modules['xbmcplugin'].setResolvedUrl.call_args.args[1]);builder.assert_not_called()

    def test_error_mid_episode_and_missing_end_event_do_not_infer_natural_end(self):
        self.start();self.playing=False;self.events.terminal('error',self.player);self.c.tick();self.c.tick()
        self.assertEqual(self.c.phase,'CANCELLED');self.assertFalse(self.builtins)
        self.start(nonce='two');self.playing=False;self.c.tick();self.clock+=4;self.c.tick()
        self.assertEqual(self.c.phase,'CANCELLED');self.assertFalse(self.builtins)

    def test_shutdown_during_transition_cancels_without_following_start(self):
        self.start();self.ended();self.c.abort=lambda:True;self.c.tick()
        self.assertTrue(self.events.closed);self.assertTrue(self.auto.cancelled('root','p'));self.assertFalse(self.builtins)

    def test_missing_episode_source_fails_once_without_retry_or_replay(self):
        self.loader.side_effect=OSError('PRIVATE provider TOKEN')
        self.start();self.assertEqual(self.c.phase,'CANCELLED');self.assertEqual(self.loader.call_count,1)
        for _ in range(20):self.c.tick()
        self.assertFalse(self.builtins);self.assertNotIn('PRIVATE',str(self.dialog.notification.call_args))

    def test_invalid_special_foreign_ambiguous_targets_are_not_started(self):
        self.rows[:]=[self.rows[0],dict(self.rows[1],pid='other'),dict(self.rows[2],series_id='other'),
                      dict(self.rows[3],season=0),dict(self.rows[1],sid='duplicate'),dict(self.rows[1],sid='duplicate')]
        self.start();self.ended();self.c.tick();self.assertEqual(self.c.phase,'FINISHED');self.assertFalse(self.builtins)

    def test_movie_live_foreign_or_untagged_session_has_no_autoplay(self):
        for kind in ('vod','series_item','live'):
            self.start(dict(self.rows[0],kind=kind),autoplay=False)
            self.ended();self.c.tick();self.assertFalse(self.builtins)
        self.start();self.unique='foreign';self.events.av_started(self.player);self.c.tick()
        self.playing=False;self.events.terminal('ended',self.player);self.c.tick();self.assertFalse(self.builtins)

    def test_foreign_video_during_gap_and_manual_request_override_pending_chain(self):
        self.start();self.ended();self.unique='foreign';self.playing=True;self.c.tick();self.assertFalse(self.builtins)
        self.start(nonce='two');self.ended();self.intent.begin('p','vod','88');self.c.tick();self.assertFalse(self.builtins)

    def test_toggle_off_cancels_queued_transition_and_does_not_write_settings(self):
        original=dict(self.options);self.start();self.ended();self.assertFalse(self.auto.toggle('root','p'));self.c.tick()
        self.assertFalse(self.builtins);self.assertEqual(self.options,original);self.assertEqual(self.c.phase,'CANCELLED')

    def test_toggle_off_and_on_during_playback_is_session_local(self):
        self.start();self.assertFalse(self.auto.toggle('root','p'));self.c.tick();self.assertFalse(self.c.enabled)
        self.assertTrue(self.auto.toggle('root','p'));self.c.tick();self.assertTrue(self.c.enabled)
        self.ended();self.c.tick();self.assertEqual(len(self.builtins),1);self.assertFalse(self.options)

    def test_end_checkpoint_survives_reload_without_older_poll_overwriting(self):
        self.start();self.progress.poll(self.player,now=100);self.ended();self.progress.poll(self.player,now=101)
        state=importlib.reload(self.state);value=state.progress('p','episode','11','1','1')
        self.assertTrue(value['watched']);self.assertEqual(value['position'],600);self.assertEqual(state.resume_position(value),0)

    def test_checkpoint_failure_cancels_chain_and_does_not_start(self):
        self.start()
        with mock.patch.object(self.state,'save_progress',side_effect=OSError('PRIVATE')):self.ended()
        self.c.tick();self.assertEqual(self.c.phase,'CANCELLED');self.assertFalse(self.builtins)

    def test_pending_start_timeout_invalidates_intent_and_never_retries(self):
        self.start();self.ended();self.c.tick();nonce=self.c.session['nonce'];self.clock+=21;self.c.tick()
        self.assertEqual(self.c.phase,'CANCELLED');self.assertEqual(len(self.builtins),1)
        self.assertFalse(self.intent.allowed(nonce,'p','episode','12'))

    def test_callback_queue_overflow_fails_closed(self):
        self.start();self.playing=False
        for _ in range(40):self.events.terminal('ended',self.player)
        self.c.tick();self.c.tick();self.assertEqual(len(self.events.items),0);self.assertFalse(self.builtins)

    def test_callbacks_never_write_db_or_start_player(self):
        self.start();self.playing=False
        with mock.patch.object(self.state,'save_progress',side_effect=AssertionError('callback SQLite')):
            self.events.terminal('ended',self.player);self.events.terminal('stopped',self.player)
        self.assertEqual(len(self.events.items),2);self.assertFalse(self.builtins)

    def test_resolver_uses_verified_series_cache_and_actual_episode_metadata(self):
        nonce=self.intent.begin('p','episode','12');self.router._params.update(kind='episode',sid='12',series_id='1',intent=nonce,autoplay='1',season='999')
        builder=mock.Mock(return_value=types.SimpleNamespace(getVideoInfoTag=lambda:types.SimpleNamespace(setUniqueIDs=mock.Mock())))
        with mock.patch.dict(sys.modules,player=types.SimpleNamespace(build_playable_item=builder)):
            self.progress.play(self.router,self.portal)
        session=json.loads(self.properties[self.progress.PROPERTY]);self.assertTrue(session['autoplay']);self.assertEqual(session['autoplay_chain'],nonce)
        self.assertEqual((session['season'],session['episode']),('1','2'));self.client._get_json.assert_called_with('get_series_info',extra={'series_id':'1'},cached_only=True)

    def test_successor_av_start_adopts_nonce_and_does_not_reload_series(self):
        self.start();self.ended();params=self.next_start()
        self.assertEqual(self.c.session['nonce'],params['intent']);self.assertEqual(self.c.phase,'PLAYING');self.assertEqual(self.loader.call_count,1)

    def test_player_observer_is_single_callback_class_and_only_queues(self):
        class Player:
            isPlayingVideo=lambda p:self.playing
            getVideoInfoTag=lambda p:self.player.getVideoInfoTag()
        sys.modules['xbmc'].Player=Player
        observer=self.auto.observe(self.events)
        self.start();observer.onAVStarted();self.playing=False;observer.onPlayBackEnded();observer.onPlayBackStopped();observer.onPlayBackError()
        self.assertEqual([k for k,s in self.events.items],['start','ended','stopped','error'])

    def test_explicit_stop_owned_cancels_chain_before_player_stop(self):
        self.start()
        self.player.stop.side_effect=lambda:self.assertTrue(self.auto.cancelled('root','p'))
        self.assertTrue(self.exit.stop_owned(self.player,pid='p'));self.player.stop.assert_called_once()

    def test_media_window_autoplay_handoff_adopts_target_and_restores_correct_season(self):
        window=self.media_window('series');window._details(window.rows[0]);self.settle(window)
        window._play(window.episodes[0],'episode');root=window._autoplay_root
        self.properties[self.auto.STATE]=json.dumps(dict(root=root,pid='p',series_id='1',sid='21',season='2',episode='1',nonce='next',phase='PLAYING',at=time.time()))
        self.assertTrue(window._chain_active());self.assertEqual(window._play_intent,'next');self.assertEqual(window.season,2)
        window.onInit();self.assertTrue(window._playback_waiting);self.assertFalse(self.auto.cancelled(root,'p'))
        window._cancel_chain();self.assertTrue(self.auto.cancelled(root,'p'))
