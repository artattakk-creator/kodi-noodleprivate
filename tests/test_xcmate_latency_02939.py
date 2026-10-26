"""Blocked data IO must not block a GUI callback; no measured Android claims."""
import importlib,sys,threading,time,unittest
from concurrent.futures import Future
from unittest import mock
import test_xcmate_kodi21_overlay as model


class Latency39(unittest.TestCase):
    def setUp(self):
        self.m=model.OverlayLifecycleTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)

    def test_pending_catalogue_allows_native_capture_before_2905_rows_finish(self):
        catalogue=importlib.import_module('live_catalog');future=Future()
        with mock.patch.object(catalogue,'prepare',return_value=future):
            o=self.m.module.LiveNavigator(self.m.portal,'1');self.addCleanup(o.close)
            o.show();self.assertTrue(o._drawn);self.assertFalse(o._catalog_ready)
            for _ in range(20):o.handle_command('left');o.handle_command('back')
            self.m.player.stop.assert_not_called()
            future.set_result(catalogue.read(self.m.portal,self.m.client));o.refresh_from_cache()
            self.assertTrue(o._catalog_ready);self.assertEqual(len(o.channels),4)

    def test_focus_ownership_and_performance_callbacks_do_not_write_diagnostic_files(self):
        diag=importlib.import_module('live_diagnostics')
        with mock.patch.object(diag,'_save',side_effect=AssertionError('GUI profile write')):
            for _ in range(20):
                diag.record('focus','OBSERVED',focus_id=42);diag.record('ownership','ITEM_IDENTITY',video=True)
                diag.record('performance','CHANNELS',render_ms=1)

    def test_slow_background_diagnostic_sink_never_holds_callback_inbox_lock(self):
        diag=importlib.import_module('live_diagnostics');entered=threading.Event();release=threading.Event();accepted=threading.Event()
        diag.record('focus','OBSERVED',focus_id=42)
        def save(*args,**kw):entered.set();release.wait(2);return True
        try:
            with mock.patch.object(diag,'_save',side_effect=save):
                diag.flush_input(background=True);self.assertTrue(entered.wait(1))
                producer=threading.Thread(target=lambda:(diag.record('focus','OBSERVED',focus_id=43),accepted.set()))
                producer.start();self.assertTrue(accepted.wait(.5));release.set();producer.join(1);diag._flush_thread.join(1)
        finally:release.set()

    def test_latency_trace_is_numeric_and_does_not_claim_first_decoded_frame(self):
        helper=importlib.import_module('ui_latency39');helper._last.clear();o=self.m.overlay
        log=mock.Mock();sys.modules['xbmc'].LOGINFO=1
        with mock.patch.object(sys.modules['xbmc'],'log',log,create=True),mock.patch.object(sys.modules['xbmcgui'],'getCurrentWindowDialogId',return_value=13001,create=True):
            helper.begin(o,1);helper.mark(o,'OWNER_BEGIN');helper.mark(o,'OWNER_READY');helper.mark(o,'GUI_APPLIED');helper.finish(o)
        text=log.call_args.args[0];self.assertIn('OWNER_READY=',text);self.assertIn('GUI_APPLIED=',text)
        self.assertNotIn('provider',text);self.assertNotIn('FIRST_FRAME',text)
