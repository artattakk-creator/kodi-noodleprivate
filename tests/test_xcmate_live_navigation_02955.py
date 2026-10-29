"""Regression of the orphaned handoff gate, not a claimed Android repair proof."""
import json,sys,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture
import test_xcmate_live_guide_02935 as guide_model


class LiveGate55(guide_model.LiveGuideFixture,unittest.TestCase):

    def test_disappearing_intent_releases_service_gate_without_player_or_gui_work(self):
        self.assertTrue(self.module.request(self.nav,destination='settings_home'))
        self.properties.pop(self.module.KEY)
        self.assertFalse(self.module.poll(self.nav));self.assertFalse(self.nav._guide_handoff)
        self.nav.suspend_for_guide.assert_not_called();self.assertFalse(self.builtins)
        self.player.play.assert_not_called();self.player.stop.assert_not_called()

    def test_corrupt_or_oversized_state_does_not_permanently_disable_input(self):
        for raw in ('{','x'*8193,'{}'):
            self.nav._guide_handoff=True;self.properties[self.module.KEY]=raw
            self.module.reconcile_input(self.nav)
            self.assertFalse(self.nav._guide_handoff)
            self.assertEqual(self.properties[self.module.KEY],raw)

    def test_new_owner_cannot_clear_another_owners_intent(self):
        self.module.request(self.nav);value=self.module._state();value['owner']='foreign';self.module._save(value)
        original=self.properties[self.module.KEY];self.module.reconcile_input(self.nav)
        self.assertFalse(self.nav._guide_handoff);self.assertEqual(self.properties[self.module.KEY],original)

    def test_valid_queue_still_rejects_double_click_and_select(self):
        self.assertTrue(self.module.request(self.nav,destination='settings_home'))
        self.module.reconcile_input(self.nav)
        self.assertTrue(self.nav._guide_handoff)
        self.assertFalse(self.module.request(self.nav,destination='settings_home'))
        self.assertFalse(self.builtins)

    def test_back_cancels_own_queued_intent_without_stopping_or_closing_stream(self):
        self.module.request(self.nav)
        self.assertTrue(self.module.cancel_pending(self.nav));self.assertIsNone(self.module._state())
        self.assertFalse(self.nav._guide_handoff);self.nav.suspend_for_guide.assert_not_called()
        self.player.stop.assert_not_called();self.assertFalse(self.builtins)

    def test_back_never_cancels_foreign_modal_or_already_dispatched_window(self):
        self.module.request(self.nav);self.dialog_id=10103
        self.assertFalse(self.module.cancel_pending(self.nav));self.assertTrue(self.nav._guide_handoff)
        self.dialog_id=13007;self.module.poll(self.nav);self.module.poll(self.nav)
        self.assertFalse(self.module.cancel_pending(self.nav));self.assertEqual(self.module._state()['phase'],'DISPATCHED')

    def test_settings_after_lost_request_can_be_queued_again_once(self):
        self.module.request(self.nav,destination='settings_home');self.properties.pop(self.module.KEY)
        self.assertTrue(self.module.request(self.nav,destination='settings_home'))
        self.assertEqual(self.module._state()['destination'],'settings_home')
        self.assertFalse(self.module.request(self.nav,destination='settings_home'))

    def test_actual_overlay_input_gate_recovers_before_remote_and_control_dispatch(self):
        self.module.request(self.nav);self.properties.pop(self.module.KEY)
        self.assertTrue(self.live.LiveNavigator._accept_input(self.nav))
        self.assertFalse(self.nav._guide_handoff)
        self.player.stop.assert_not_called();self.player.play.assert_not_called()

    def test_fullscreen_stop_and_movie_exit_implementations_are_not_changed(self):
        from pathlib import Path
        import hashlib,json
        root=Path(__file__).resolve().parents[1]
        base=json.loads((root/'tests/fixtures/xcmate_02955_protection.json').read_text())['source_sha256']
        for path,digest in base.items():
            if Path(path).name in ('native_stop41.py','native_stop42.py','live_exit.py','exit_jobs.py','playback_exit.py','autoplay.py'):
                self.assertEqual(hashlib.sha256((root/path).read_bytes()).hexdigest(),digest,path)
