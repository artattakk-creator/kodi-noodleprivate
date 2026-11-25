"""The no-provider state is cheap and recovers as soon as the profile changes."""
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] /
                       "src/plugin.video.xtreammate/resources/lib"))
from xcmate027_fixture import Fixture


class ServicePortalStateTests(Fixture, unittest.TestCase):
    def test_fresh_profile_backs_off_then_discovers_committed_portal(self):
        with patch.dict(sys.modules):
            sys.modules.pop("portals", None)
            import portals
            import service_runtime
            clock = [100]
            with patch.object(service_runtime.time, "monotonic", lambda: clock[0]):
                old_count = service_runtime.counters()["portal_calls"]
                for _ in range(100):
                    self.assertFalse(service_runtime.portals_ready())
                self.assertEqual(service_runtime.counters()["portal_calls"] - old_count, 1)
                portals.save_all([{"id": "fixture", "type": "m3u"}])
                clock[0] += 5
                self.assertTrue(service_runtime.portals_ready())
