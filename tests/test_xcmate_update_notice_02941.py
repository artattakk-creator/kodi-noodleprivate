"""Actual install versions, safe GUI dispatch, per-profile durable acknowledgment."""
import importlib,json,sys,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture

class UpdateNotice41(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.notice=importlib.import_module('update_notice41');self.notice._next=0
        self.current='0.1.29.41'
        sys.modules['xbmcaddon'].Addon=lambda *a:types.SimpleNamespace(getAddonInfo=lambda k:self.current if k=='version' else str(self.folder))
        sys.modules['xbmcgui'].getCurrentWindowId=lambda:10000
        sys.modules['xbmcgui'].getCurrentWindowDialogId=lambda:9999
    def baseline(self,v='0.1.29.40'):self.notice.save(dict(current=v,seen=[],pending=''))
    def test_fresh_install_is_baseline_not_false_upgrade_and_no_dialog(self):
        with mock.patch.object(self.notice,'legacy',return_value=''):
            self.assertFalse(self.notice.detect())
        self.assertEqual(self.notice.read()['current'],self.current);self.assertFalse(self.notice.show());self.dialog.ok.assert_not_called()
    def test_real_upgrade_shows_actual_installed_version_once_after_ok(self):
        self.baseline();self.assertTrue(self.notice.detect());self.assertTrue(self.notice.show())
        self.assertIn(self.current,self.dialog.ok.call_args.args[1]);self.assertFalse(self.notice.show());self.dialog.ok.assert_called_once()
    def test_back_also_acknowledges_and_two_restarts_do_not_repeat(self):
        self.baseline();self.notice.detect();self.dialog.ok.return_value=False;self.assertTrue(self.notice.show())
        for _ in range(2):
            self.properties.clear();self.notice.detect();self.assertFalse(self.notice.show())
        self.dialog.ok.assert_called_once()
    def test_old_service_build_witness_handles_first_actual_upgrade_from_40(self):
        with mock.patch.object(self.notice,'legacy',return_value='0.1.29.40'):self.assertTrue(self.notice.detect())
        self.assertEqual(self.notice.read()['pending'],'0.1.29.41');self.assertTrue(self.notice.show())
    def test_service_schedules_runplugin_but_never_opens_a_dialog(self):
        self.baseline();self.notice.detect();self.notice.schedule()
        self.assertEqual(len(self.builtins),1);self.assertIn('action=update_notice',self.builtins[0]);self.dialog.ok.assert_not_called()
        self.notice.schedule();self.assertEqual(len(self.builtins),1)
    def test_playback_modal_owner_or_stop_defers_without_using_player_stop(self):
        self.baseline();self.notice.detect()
        for cond in ('Player.HasMedia','System.HasActiveModalDialog','Container.IsUpdating'):
            with mock.patch.object(sys.modules['xbmc'],'getCondVisibility',side_effect=lambda c:c==cond):self.assertFalse(self.notice.show())
        with mock.patch('exit_jobs.blocked',return_value=True):self.assertFalse(self.notice.show())
        self.dialog.ok.assert_not_called();self.assertTrue(self.notice.read()['pending'])
    def test_no_notice_on_repository_publish_or_same_installed_version(self):
        self.baseline(self.current)
        for _ in range(5):self.assertFalse(self.notice.detect());self.assertFalse(self.notice.show())
        self.dialog.ok.assert_not_called()
    def test_numeric_versions_downgrade_and_skipped_updates_are_correct(self):
        self.baseline('0.1.29.9');self.assertTrue(self.notice.detect());self.notice.show()
        self.current='0.1.29.10';self.assertFalse(self.notice.detect());self.assertFalse(self.notice.show())
        self.current='0.1.29.52';self.assertTrue(self.notice.detect());self.assertTrue(self.notice.show())
        self.assertEqual(self.dialog.ok.call_count,2);self.assertIn('52',self.dialog.ok.call_args.args[1])
    def test_power_loss_before_display_retries_pending_but_bad_marker_is_baseline(self):
        self.baseline();self.notice.detect();self.properties.clear();self.assertTrue(self.notice.detect());self.assertTrue(self.notice.show())
        (self.folder/'xcmate_update_notice.json').write_text('{broken')
        with mock.patch.object(self.notice,'legacy',return_value=''):self.assertFalse(self.notice.detect())
    def test_failed_dialog_never_acknowledges_and_is_rate_limited(self):
        self.baseline();self.notice.detect();self.dialog.ok.side_effect=RuntimeError('native failure')
        self.assertFalse(self.notice.show());self.assertFalse(self.notice.show());self.dialog.ok.assert_called_once()
        self.assertTrue(self.notice.read()['pending']);self.assertFalse(self.notice.read()['seen'])
    def test_persistent_marker_does_not_change_existing_profile_files(self):
        p=self.folder/'portals.json';p.write_text('unchanged');before=p.read_bytes()
        self.baseline();self.notice.detect();self.notice.show();self.assertEqual(p.read_bytes(),before)
    def test_parallel_gui_presenter_cannot_show_twice(self):
        self.baseline();self.notice.detect()
        with self.notice.lease() as acquired:
            self.assertTrue(acquired);self.assertFalse(self.notice.show())
        self.dialog.ok.assert_not_called();self.assertTrue(self.notice.show())
    def test_valid_json_with_invalid_optional_marker_fields_is_safe_and_not_spam(self):
        self.notice.save(dict(current=self.current,pending=['bad'],seen=[None,{},'bad'],retry_at='invalid'))
        self.assertFalse(self.notice.detect());self.assertFalse(self.notice.show());self.dialog.ok.assert_not_called()
