"""Mandatory xVAULT and verifiable Kodi 21 BINGIE activation guards."""
import json
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src/script.gsmedia.setup/resources/lib"))
from setup_skin_activate_0511 import activate, SKIN_ID


def inventory():
    return {"code": "READY", "addons": {
        SKIN_ID: {"enabled": True, "version": "2.2.3"},
        "script.skinshortcuts": {"enabled": True, "version": "2.1.0"}}}


class FakeKodi:
    def __init__(self, skin="skin.estuary", reject=False, revert=False, bad_gui=False):
        self.skin = skin
        self.reject = reject
        self.revert = revert
        self.bad_gui = bad_gui
        self.writes = 0

    def execute(self, req):
        data = json.loads(req)
        method = data["method"]
        if method == "Settings.GetSettingValue":
            result = {"value": self.skin}
        elif method == "Settings.SetSettingValue":
            self.writes += 1
            if self.reject:
                result = False
            else:
                self.skin = data["params"]["value"]
                result = True
        elif method == "GUI.GetProperties":
            result = {"skin": {"id": "skin.estuary" if self.bad_gui else self.skin,
                               "name": "Titan BINGIE MOD"}}
        else:
            return json.dumps({"jsonrpc": "2.0", "id": 51011,
                               "error": {"code": -32601, "message": "Not found"}})
        return json.dumps({"jsonrpc": "2.0", "id": 51011, "result": result})

    def wait(self, secs):
        if self.revert:
            self.skin = "skin.estuary"


class SkinActivationTests(unittest.TestCase):
    def run_activate(self, kodi, inv=None, patch=None, shortcuts="ALREADY_APPLIED"):
        return activate(kodi.execute, inv or inventory(),
                        patch or {"code": "READY", "pending": ()},
                        shortcuts, kodi.wait)

    def test_verified_switch(self):
        kodi = FakeKodi()
        self.assertEqual(self.run_activate(kodi), "ACTIVE_AND_VERIFIED")
        self.assertEqual(kodi.skin, SKIN_ID)
        self.assertEqual(kodi.writes, 1)

    def test_idempotent_and_gui_verified(self):
        kodi = FakeKodi(SKIN_ID)
        self.assertEqual(self.run_activate(kodi), "ALREADY_ACTIVE")
        self.assertEqual(kodi.writes, 0)
        self.assertEqual(self.run_activate(FakeKodi(SKIN_ID, bad_gui=True)), "SKIN_GUI_NOT_ACTIVE")

    def test_kodi_user_can_decline_switch(self):
        self.assertEqual(self.run_activate(FakeKodi(revert=True)), "SKIN_SWITCH_NOT_CONFIRMED")
        self.assertEqual(self.run_activate(FakeKodi(reject=True)), "SKIN_SWITCH_REJECTED")

    def test_modified_skin_and_missing_widget_stop_without_writes(self):
        kodi = FakeKodi()
        self.assertEqual(self.run_activate(kodi, patch={"code": "READY", "pending": ("xml/template.xml",)}),
                         "BINGIE_PATCH_NOT_VERIFIED")
        self.assertEqual(self.run_activate(kodi, shortcuts="EXISTING_SKIN_DATA_PRESERVED"),
                         "BINGIE_WIDGET_FILES_NOT_VERIFIED")
        self.assertEqual(kodi.writes, 0)

    def test_user_requested_default_player_is_hard_gate(self):
        ui=(ROOT/"src/script.gsmedia.setup/resources/lib/setup_auto_ui50.py").read_text(encoding="utf-8")
        self.assertIn('reason = "TMDB_XVAULT_MANDATORY_UNMET:" + code_', ui)
        self.assertIn('reason = "TMDB_XVAULT_MANDATORY_UNMET:" + player_result', ui)
        self.assertIn('"BINGIE_NOT_ACTIVE:" + skin_result', ui)
        self.assertIn("setup_skin_activate_0511", ui)
        self.assertIn('def _activate_bingie_runtime(', ui)
        self.assertNotIn("Bestehender TMDB-Standardplayer wurde geschützt", ui)

    def test_exact_display_names_and_stable_ids(self):
        import xml.etree.ElementTree as ET
        addon=ET.parse(ROOT/"src/script.gsmedia.setup/addon.xml").getroot()
        self.assertEqual(addon.get("id"), "script.gsmedia.setup")
        self.assertEqual(addon.get("version"), "0.5.16")
        self.assertEqual(addon.get("name"), "XCMate Media Center Setup – v0.5.16 – Kodi 21.3 Omega")
        b=(ROOT/"tools/build_gsmedia_pilot050.py").read_text(encoding="utf-8")
        self.assertIn('PILOT_ID = "repository.gsmedia.pilot"', b)
        self.assertIn('PILOT_VERSION = "1.9.9"', b)
        self.assertIn('xcMate Repository – Test v1.9.9 – Kodi 21.3 Omega',b)


if __name__ == "__main__":
    unittest.main()
