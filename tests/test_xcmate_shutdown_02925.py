"""Optional service cancellation does not begin later stages or block Kodi."""
import importlib
import sys
import threading
import time
import types
import unittest
from unittest import mock
from xcmate027_fixture import Fixture


class ShutdownTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        sys.modules.pop('app_services',None)
        self.service=importlib.import_module('app_services')
        self.addCleanup(self.service._stop.set)

    def test_abort_during_maintenance_prevents_following_local_and_network_work(self):
        aborted=threading.Event()
        sys.modules['xbmc'].Monitor=lambda:types.SimpleNamespace(abortRequested=aborted.is_set,waitForAbort=lambda n:aborted.is_set())
        db=importlib.import_module('artwork_db')
        # .82 automatically inspects read-only, after Home/network admission.
        # Cancellation at that boundary must still prevent all later stages;
        # invoking the old mutating maintenance API would be a regression.
        timer=threading.Timer(2,aborted.set);timer.start()
        try:
            with mock.patch.object(db,'maintain',side_effect=AssertionError('automatic repair')), mock.patch.object(db,'inspect_readonly82',side_effect=lambda **kw:aborted.set()) as inspect, mock.patch('startup48.suspended',return_value=False), mock.patch('startup48.Phases.network',return_value=True), mock.patch('home_schedule75.rest_allowed',return_value=True), mock.patch.object(self.service,'refresh_local') as refresh:
                self.service._run()
                inspect.assert_called_once()
        finally:timer.cancel()
        refresh.assert_not_called()

    def test_shutdown_has_bounded_join_and_never_restarts_worker(self):
        released=threading.Event();worker=threading.Thread(target=lambda:released.wait(2))
        worker.start();self.service._worker=worker
        try:
            before=time.monotonic();self.assertFalse(self.service.shutdown())
            self.assertLess(time.monotonic()-before,.7)
            with mock.patch.object(self.service.threading,'Thread') as factory:self.service.poll()
            factory.assert_not_called()
        finally:released.set();worker.join()

    def test_refresh_cancelled_before_first_portal_does_not_touch_catalogue(self):
        with mock.patch.object(importlib.import_module('library_index'),'refresh') as refresh:
            self.service.refresh_local(cancel=lambda:True)
        refresh.assert_not_called()


if __name__=='__main__':unittest.main()
