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

    def test_snapshot_reads_are_attributed_through_public_portal_accessors(self):
        with patch.dict(sys.modules):
            sys.modules.pop("portals", None)
            import portals
            import service_runtime
            from types import ModuleType

            portals.save_all([{"id": "fixture", "type": "m3u"}])
            worker = ModuleType("widget_fast69")
            worker.__dict__["get_active"] = portals.get_active
            exec("def prepare():\n    return get_active()", worker.__dict__)
            before = service_runtime.counters()
            self.assertEqual(worker.prepare()[0]["id"], "fixture")
            after = service_runtime.counters()
            self.assertEqual(after["portal_calls"], before["portal_calls"] + 1)
            self.assertEqual(after["portal_disk_reads"], before["portal_disk_reads"])
            self.assertEqual(after["callers"].get("WIDGET", 0), before["callers"].get("WIDGET", 0) + 1)

    def test_field_projection_cannot_mutate_profile_and_observes_replacement(self):
        with patch.dict(sys.modules):
            sys.modules.pop("portals", None)
            import portals

            portals.save_all([{"id": "fixture", "type": "xtream", "xc_user": "first", "state": {"active": True}}])
            fields = ("xc_user", "state")
            saved = portals.get_fields("fixture", fields)
            self.assertEqual(saved, {"xc_user": "first", "state": {"active": True}})
            saved["state"]["active"] = False
            self.assertTrue(portals.get_fields("fixture", fields)["state"]["active"])
            Path(portals._db_path()).unlink()
            self.assertIsNone(portals.get_fields("fixture", fields))
            portals.save_all([{"id": "fixture", "type": "xtream", "xc_user": "second"}])
            self.assertEqual(portals.get_fields("fixture", fields), {"xc_user": "second"})
