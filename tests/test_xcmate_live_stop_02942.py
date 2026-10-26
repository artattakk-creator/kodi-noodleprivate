"""Two native lifecycle models. Passing these is NOT a Rockchip decoder PASS."""
import importlib
import json
import sys
import unittest
from unittest import mock
from pathlib import Path
import xml.etree.ElementTree as ET

import test_xcmate_live_stop_02917 as old


class LiveStop42(unittest.TestCase):
    def setUp(self):
        self.m = old.StopTests(methodName='runTest')
        self.m.setUp()
        self.addCleanup(self.m.doCleanups)
        self.jobs = importlib.import_module('exit_jobs')
        self.compat = importlib.import_module('live_stop42')
        self.native = importlib.import_module('native_stop41')
        self.xbmc = sys.modules['xbmc']
        self.gui = sys.modules['xbmcgui']
        self.m.options[self.compat.SETTING] = True
        self.screen, self.dialog, self.visible = 12005, 9999, True
        self.modal, self.android, self.build = False, True, '21.3 (21.3.0)'
        self.queue, self.executed, self.logs = [], [], []
        self.native_hang, self.main_hang, self.stop_entered = False, False, False
        condition = self.xbmc.getCondVisibility
        self.xbmc.getCondVisibility = lambda c: {
            'System.Platform.Android': self.android,
            'System.HasActiveModalDialog': self.modal,
            'Window.IsVisible(fullscreenvideo)': self.visible,
        }.get(c, condition(c))
        label = self.xbmc.getInfoLabel
        self.xbmc.getInfoLabel = lambda k: self.build if k == 'System.BuildVersion' else label(k)
        self.gui.getCurrentWindowId = lambda: self.screen
        self.gui.getCurrentWindowDialogId = lambda: self.dialog
        native = self.xbmc.executebuiltin
        def post(command, wait=False):
            self.assertFalse(wait)
            self.queue.append(command)
            if command.startswith(('PlayerControl(', 'SetProperty(XCMate.NativeStopAck41,')):
                native(command, wait=wait)
        self.xbmc.executebuiltin = post
        self.xbmc.log = lambda message, *a: self.logs.append(message)
        self.xbmc.LOGINFO = 1

    def tick(self):
        self.jobs.poll()
        if self.jobs._thread is not None:
            self.jobs._thread.join(2)
            self.assertFalse(self.jobs._thread.is_alive())

    def request(self):
        self.assertTrue(self.jobs.request(self.m.player, reason='USER_BACK'))
        value = self.jobs.state()
        value['not_before'] = 0
        self.jobs.save(value)
        self.tick()

    def pump(self, deinit=True):
        """Explicit native MAIN queue model; no automatic mock ACK on post."""
        while self.queue and not self.main_hang:
            command = self.queue.pop(0)
            self.executed.append(command)
            if command == 'ActivateWindow(Videos)':
                if deinit and not self.modal and self.dialog in (0, 9999):
                    self.screen, self.visible = 10025, False
            elif command == 'PlayerControl(Stop)':
                self.stop_entered = True
                if self.native_hang or self.visible:
                    self.main_hang = True
                    return
                self.m.player.stop()
            elif command.startswith('SetProperty('):
                key, value, _ = command[len('SetProperty('):-1].split(',')
                self.m.properties[key] = value

    def release(self):
        self.pump()
        self.tick()

    def timeout(self):
        value = self.jobs.state()
        value['deadline'] = 0
        self.jobs.save(value)
        self.tick()

    def test_explicit_opt_in_defaults_false_without_writing_existing_settings(self):
        root = Path(__file__).resolve().parents[1]
        nodes = list(ET.parse(root/'src/plugin.video.xtreammate/resources/settings.xml').iter('setting'))
        node = next(n for n in nodes if n.get('id') == self.compat.SETTING)
        self.assertEqual(node.get('default'), 'false')
        self.m.options.clear()
        self.request()
        self.assertEqual(self.jobs.state()['strategy42'], 'direct41')
        self.assertEqual(self.queue[0], 'PlayerControl(Stop)')
        self.assertEqual(self.m.options, {})

    def test_strategy_a_041_native_stop_in_fullscreen_reproduces_no_return(self):
        self.m.options[self.compat.SETTING] = False
        self.request(); self.pump(); self.timeout()
        self.assertTrue(self.main_hang)
        self.assertEqual(self.jobs.state()['phase'], 'timeout')
        self.assertTrue(self.jobs.blocked())
        self.assertNotIn(self.native.ACK, self.m.properties)
        self.assertFalse(any('PLAYER_STOP_DONE' in s for s in self.logs))

    def test_strategy_b_native_fullscreen_deinit_precedes_stop_and_completion(self):
        self.request()
        self.assertEqual(self.queue[0], 'ActivateWindow(Videos)')
        self.assertEqual(self.jobs.state()['phase'], 'pending')
        self.assertFalse(self.stop_entered)
        self.release()
        self.assertFalse(self.stop_entered)
        self.assertEqual(self.jobs.state()['phase'], 'running')
        self.assertEqual(self.queue[0], 'PlayerControl(Stop)')
        self.assertTrue(self.jobs.blocked())
        self.release()
        self.assertEqual(self.jobs.state()['phase'], 'complete')
        self.assertEqual(self.m.stops, 1)
        self.assertFalse(self.jobs.blocked())

    def test_prepare_ack_is_not_stop_done_or_permission_to_return_home(self):
        self.m.exit.request(self.m.nav); self.m.ready(); self.m.exit._poll(self.m.nav)
        value = self.jobs.state(); value['not_before'] = 0; self.jobs.save(value)
        self.tick(); self.pump(); self.tick()
        self.m.exit._poll(self.m.nav)
        self.assertTrue(self.jobs.blocked())
        self.assertNotIn(self.native.ACK, self.m.properties)
        self.assertFalse(any('HOME_REQUESTED' in s or 'stage=STOP_DONE' in s for s in self.logs))
        self.assertFalse(any('action=xcmate_home' in s for s in self.queue))

    def test_home_and_focus_return_only_after_confirmed_stop_and_no_playback(self):
        self.m.exit.request(self.m.nav); self.m.ready(); self.m.exit._poll(self.m.nav)
        value = self.jobs.state(); value['not_before'] = 0; self.jobs.save(value)
        self.tick(); self.release(); self.release()
        self.m.exit._poll(self.m.nav); self.m.exit._poll(self.m.nav)
        self.assertEqual(self.m.exit.state()['phase'], 'complete')
        self.assertFalse(self.m.playing)
        self.assertEqual(self.m.stops, 1)
        self.assertEqual(sum('action=xcmate_home' in s for s in self.queue), 1)

    def test_native_deadlock_after_deinit_stays_failure_no_fake_success(self):
        self.native_hang = True
        self.request(); self.release(); self.pump(); self.timeout()
        self.assertTrue(self.main_hang)
        self.assertEqual(self.jobs.state()['phase'], 'timeout')
        self.assertTrue(self.jobs.blocked())
        self.assertFalse(any('PLAYER_STOP_DONE' in s or 'HOME_REQUESTED' in s for s in self.logs))
        self.assertEqual(self.executed.count('PlayerControl(Stop)'), 1)

    def test_main_queue_never_free_no_stop_no_retry_and_late_prepare_no_success(self):
        self.main_hang = True
        self.request(); self.timeout()
        self.assertTrue(self.jobs.blocked())
        for _ in range(20):
            self.assertFalse(self.jobs.request(self.m.player, manual=True))
            self.tick()
        self.assertFalse(self.stop_entered)
        self.assertEqual(len(self.queue), 2)
        self.main_hang = False
        self.pump(); self.tick()
        self.assertEqual(self.jobs.state()['phase'], 'timeout')
        self.assertFalse(self.jobs.blocked())
        self.assertFalse(self.stop_entered)
        self.assertTrue(any('LATE_FULLSCREEN_RETURN' in s for s in self.logs))

    def test_unmatched_prepare_nonce_never_releases_pending_job(self):
        self.request()
        self.screen, self.visible = 10025, False
        self.m.properties[self.compat.ACK] = 'f'*32
        self.tick()
        self.assertEqual(self.jobs.state()['phase'], 'pending')
        self.assertFalse(self.stop_entered)

    def test_ack_while_fullscreen_still_visible_does_not_start_stop(self):
        self.request(); self.pump(deinit=False); self.tick()
        self.assertTrue(self.jobs.state()['prepare_done42'])
        self.assertEqual(self.jobs.state()['phase'], 'pending')
        self.assertFalse(self.stop_entered)

    def test_foreign_modal_before_prepare_is_never_closed(self):
        self.modal, self.dialog = True, 10100
        self.request()
        self.assertFalse(self.queue)
        self.timeout()
        self.assertFalse(self.stop_entered)

    def test_foreign_modal_after_prepare_barrier_holds_stop(self):
        self.request(); self.pump()
        self.modal, self.dialog = True, 10100
        self.tick()
        self.assertFalse(self.queue)
        self.assertFalse(self.stop_entered)
        self.assertEqual(self.jobs.state()['phase'], 'pending')

    def test_modal_arriving_while_main_queue_waits_vetoes_native_window_change(self):
        self.request()
        self.modal, self.dialog = True, 10100
        self.pump()
        self.assertEqual(self.screen, 12005)
        self.assertTrue(self.visible)
        self.tick()
        self.assertFalse(self.stop_entered)
        # Even after the unrelated modal closes: ACK without window release
        # is not enough, and the preparation action is never repeated.
        self.modal, self.dialog = False, 9999
        self.tick(); self.timeout()
        self.assertEqual(self.jobs.state()['phase'], 'timeout')
        self.assertEqual(self.executed.count('ActivateWindow(Videos)'), 1)

    def test_foreign_item_before_preparation_receives_no_window_or_stop(self):
        self.jobs.request(self.m.player)
        value = self.jobs.state(); value['not_before'] = 0; self.jobs.save(value)
        self.m.tag = 'foreign'
        self.tick()
        self.assertEqual(self.jobs.state()['result'], 'PREP_OWNER_CHANGED')
        self.assertFalse(self.queue)

    def test_owner_change_after_prepare_barrier_prevents_stop(self):
        self.request(); self.pump()
        self.m.tag = 'foreign'
        self.tick()
        self.assertEqual(self.jobs.state()['phase'], 'failed')
        self.assertFalse(self.stop_entered)

    def test_post_guard_rechecks_gui_between_preparation_and_stop_worker(self):
        self.request(); self.pump()
        value = self.jobs.state()
        self.compat.observe(value)
        self.assertTrue(self.compat.prepare(value))
        value.update(phase='running', stop_started=True); self.jobs.save(value)
        self.modal, self.dialog = True, 10100
        self.assertFalse(self.native.post(tuple(value['token'])))
        self.assertFalse(self.queue)

    def test_unrelated_window_after_deinit_prevents_stop_and_home(self):
        self.request(); self.pump(); self.screen = 10016; self.tick()
        self.assertEqual(self.jobs.state()['result'], 'PREP_WINDOW_CHANGED')
        self.assertFalse(self.stop_entered)

    def test_pending_prepare_blocks_new_foreign_or_media_requests(self):
        self.request(); self.timeout()
        other = ('media', dict(self.m.session, nonce='different', kind='vod'))
        with mock.patch('playback_exit.identity', return_value=other):
            self.assertFalse(self.jobs.request(self.m.player, expected=other))
        self.assertEqual(self.jobs.state()['token'][0], 'live')

    def test_queue_post_raises_after_first_command_stays_quarantined(self):
        post = self.xbmc.executebuiltin
        def broken(command, wait=False):
            if command.startswith('SetProperty('+self.compat.ACK):
                raise RuntimeError('queue unavailable')
            post(command, wait=wait)
        with mock.patch.object(self.xbmc, 'executebuiltin', side_effect=broken):
            self.request()
        self.assertEqual(self.jobs.state()['phase'], 'timeout')
        self.assertTrue(self.jobs.blocked())
        self.assertFalse(self.jobs.request(self.m.player, manual=True))
        self.assertEqual(len(self.queue), 1)

    def test_early_playback_callback_cannot_replace_native_stop_barrier(self):
        self.request(); self.release()
        self.m.playing = False
        self.tick()
        self.assertTrue(self.jobs.blocked())
        self.assertEqual(self.jobs.state()['phase'], 'running')

    def test_late_native_stop_return_remains_timeout_no_auto_home(self):
        self.request(); self.release(); self.timeout()
        self.pump(); self.tick()
        self.assertFalse(self.jobs.blocked())
        self.assertEqual(self.jobs.state()['phase'], 'timeout')
        self.assertTrue(any('LATE_NATIVE_RETURN' in s for s in self.logs))
        self.assertFalse(any('HOME_REQUESTED' in s for s in self.logs))

    def test_repeated_back_cannot_double_stop_or_reset_deadline(self):
        self.request(); deadline = self.jobs.state()['deadline']
        for _ in range(50):
            self.jobs.request(self.m.player, expected=('live', self.m.session))
            self.tick()
        self.assertEqual(self.jobs.state()['deadline'], deadline)
        self.assertEqual(len(self.queue), 2)
        self.release(); self.release()
        self.assertEqual(self.m.stops, 1)

    def test_kodi_shutdown_does_not_post_a_prepare_or_stop(self):
        self.xbmc.Monitor = lambda: mock.Mock(abortRequested=lambda: True)
        self.request()
        self.assertFalse(self.queue)
        self.timeout()
        self.assertFalse(self.jobs.blocked())

    def test_unsupported_host_is_rejected_without_global_decoder_write(self):
        for android, version in ((False, '21.3'), (True, '21.2'), (True, '22.0'), (True, '21.30')):
            self.jobs.save(dict(token=['live', self.m.session], phase='pending',
                                at=self.m.session['at'], deadline=999999999999,
                                not_before=0, stop_started=False, worker_done=False))
            self.android, self.build = android, version
            self.tick()
            self.assertEqual(self.jobs.state()['result'], 'PREP_UNSUPPORTED_HOST')
            self.assertFalse(self.queue)

    def test_settings_read_failure_no_native_call_or_profile_write(self):
        with mock.patch('utils.setting_bool', side_effect=OSError('disk full')):
            self.request()
        self.assertFalse(self.queue)
        self.assertEqual(self.jobs.state()['phase'], 'failed')
        self.assertEqual(self.jobs.state()['result'], 'PREP_UNCONFIRMED')

    def test_media_job_keeps_original_synchronous_owned_exit_implementation(self):
        media = ('media', dict(self.m.session, kind='vod'))
        with mock.patch('playback_exit.identity', return_value=media), \
             mock.patch('playback_exit.stop_owned', return_value=True) as stop, \
             mock.patch.object(self.compat, 'prepare', side_effect=AssertionError('Live only')):
            self.request()
        stop.assert_called_once()
        self.assertEqual(self.jobs.state()['phase'], 'complete')
        self.assertFalse(self.queue)

    def test_diagnostics_never_contain_private_item_ids_or_urls(self):
        self.request(); self.release(); self.release()
        text = '\n'.join(self.logs)
        self.assertIn('FULLSCREEN_READY', text)
        for private in ('https://', 'SECRET', 'provider.invalid', 'nonce=own', 'pid=p', 'sid=1'):
            self.assertNotIn(private, text)

    def test_strategy_does_not_change_when_setting_is_toggled_in_flight(self):
        self.request(); self.m.options[self.compat.SETTING] = False
        self.release()
        self.assertEqual(self.jobs.state()['strategy42'], 'fullscreen42')
        self.release()
        self.assertEqual(self.jobs.state()['phase'], 'complete')

    def test_already_safe_gui_needs_no_fullscreen_action(self):
        self.screen, self.visible = 10025, False
        self.request()
        self.assertEqual(self.queue[0], 'PlayerControl(Stop)')
        self.release()
        self.assertEqual(self.jobs.state()['phase'], 'complete')

    def test_twenty_opt_in_native_lifecycle_cycles_each_stop_once(self):
        for i in range(20):
            self.jobs._thread = None
            self.m.properties.pop(self.jobs.KEY, None)
            self.m.session = dict(self.m.session, nonce='cycle'+str(i))
            self.m.tag = json.dumps(self.m.session)
            self.m.properties[self.m.exit.SESSION] = self.m.tag
            self.m.playing, self.visible, self.screen = True, True, 12005
            self.request(); self.release(); self.release()
            self.assertEqual(self.jobs.state()['phase'], 'complete')
        self.assertEqual(self.m.stops, 20)
        self.assertEqual(self.executed.count('ActivateWindow(Videos)'), 20)
        self.assertEqual(self.executed.count('PlayerControl(Stop)'), 20)

    def test_failed_prepare_never_becomes_live_home_success_on_early_callback(self):
        self.m.exit.request(self.m.nav); self.m.ready(); self.m.exit._poll(self.m.nav)
        value = self.jobs.state(); value['not_before'] = 0; self.jobs.save(value)
        self.build = '21.2'; self.tick(); self.m.playing = False
        self.m.exit._poll(self.m.nav)
        self.assertEqual(self.m.exit.state()['phase'], 'failed')
        self.assertFalse(any('HOME_REQUESTED' in s for s in self.logs))

    def test_no_player_mutex_queries_during_native_hang_or_after_timeout(self):
        self.native_hang = True
        self.request(); self.release(); self.pump()
        with mock.patch.object(self.m.player, 'isPlayingVideo', side_effect=AssertionError('native mutex')):
            self.timeout()
            for _ in range(20):
                self.tick()
                self.assertTrue(self.jobs.blocked())
                self.assertFalse(self.jobs.request(self.m.player, manual=True))

    def test_memory_pressure_before_prepare_posts_no_native_command(self):
        with mock.patch('utils.setting_bool', side_effect=MemoryError):
            self.request()
        self.assertEqual(self.jobs.state()['phase'], 'failed')
        self.assertFalse(self.queue)
        self.assertFalse(self.jobs.blocked())

    def test_deadline_passed_before_poll_never_accepts_native_ack_as_on_time(self):
        self.request(); self.release(); self.pump()
        value = self.jobs.state(); value['deadline'] = 0; self.jobs.save(value)
        self.tick()
        self.assertEqual(self.jobs.state()['phase'], 'timeout')
        self.assertFalse(self.jobs.blocked())
        self.assertFalse(any('PLAYER_STOP_DONE' in s for s in self.logs))

    def test_prepare_survives_interpreter_restart_without_duplicate_gui_action(self):
        self.request()
        self.jobs = importlib.reload(self.jobs)
        self.tick()
        self.assertEqual(len(self.queue), 2)
        self.release(); self.release()
        self.assertEqual(self.jobs.state()['phase'], 'complete')
        self.assertEqual(self.m.stops, 1)
