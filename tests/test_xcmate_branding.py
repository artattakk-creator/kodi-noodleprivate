"""XCMate is a display-name rebrand; the Kodi addon ID must stay stable."""
import pathlib
import unittest
import xml.etree.ElementTree as ET

ROOT=pathlib.Path(__file__).resolve().parents[1]/"src/plugin.video.xtreammate"

class XCMateBrandingTests(unittest.TestCase):
    def test_display_name_and_version(self):
        addon=ET.parse(ROOT/"addon.xml").getroot()
        self.assertEqual(addon.get("name"),"XCMate")
        self.assertEqual(addon.get("version"),"0.1.29.5")
        self.assertEqual(addon.get("id"),"plugin.video.xtreammate")
        self.assertTrue(all("XCMate" in (node.text or "")
                            for node in addon.findall(".//summary")))
    def test_recovery_keeps_epg_dialog_and_startup_nonblocking(self):
        entry=(ROOT/"default.py").read_text(encoding="utf-8")
        main=(ROOT/"resources/lib/main.py").read_text(encoding="utf-8")
        self.assertIn("mark('START_FAILED', error=type(exc).__name__)",entry)
        self.assertNotIn('traceback.format_tb',entry)  # Source lines can contain secrets.
        self.assertIn("XCMate – Startfehler",entry)
        epg=main.split("    def _epg_sources(self):",1)[1].split("    def _refresh_epg(self):",1)[0]
        self.assertIn("xbmcplugin.endOfDirectory",epg)
        self.assertLess(epg.index("xbmcplugin.endOfDirectory"),epg.index("manage(portal)"))
        root=main.split("    def _root(self):",1)[1].split("    def _maybe_autoplay_start(self",1)[0]
        self.assertIn("self._maybe_autoplay_start(portal)",root)

    def test_kodi_settings_and_languages(self):
        settings=(ROOT/"resources/settings.xml").read_text(encoding="utf-8")
        self.assertIn("XCMate: Android-Fernbedienung anlernen",settings)
        self.assertNotIn('label="XtreamMate:',settings)
        for language in ("de_de","en_gb"):
            p=ROOT/("resources/language/resource.language."+language+"/strings.po")
            self.assertIn('msgstr "XCMate"',p.read_text(encoding="utf-8"))
    def test_internal_communication_and_saved_ids_unchanged(self):
        overlay=(ROOT/"resources/lib/live_overlay.py").read_text(encoding="utf-8")
        self.assertIn("SESSION_KEY = 'XtreamMate.LiveSession'",overlay)
        self.assertIn("'channels':'LIVE-TV'",overlay)
        remote=(ROOT/"resources/lib/remote_control.py").read_text(encoding="utf-8")
        self.assertIn("COMMAND_KEY = 'XtreamMate.RemoteCommand'",remote)
        data=(ROOT/"resources/lib/group_selection.py").read_text(encoding="utf-8")
        self.assertIn("'xtreammate_groups.json'",data)

if __name__=="__main__":
    unittest.main()
