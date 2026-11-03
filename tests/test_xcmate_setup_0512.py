"""Regression: 0.5.11 owned BINGIE widgets, single-button UI, reboot marker."""
import ast
import os
from pathlib import Path
import sys
import tempfile
import unittest

ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/"src/script.gsmedia.setup/resources/lib"
sys.path.insert(0,str(LIB))
import setup_bingie_apply as bingie
from setup_finish_0512 import read, mark_restart_pending, finish


def inv():
    return {"code":"READY","addons":{
        "skin.titan.bingie.mod":{"version":"2.2.3","enabled":True},
        "script.skinshortcuts":{"version":"2.1.0","enabled":True}}}


class WidgetRecoveryTests(unittest.TestCase):
    def test_legacy_exact_files_are_upgraded_without_replacing_menu(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/"script.skinshortcuts"
            dest.mkdir()
            legacy=bingie.render(legacy=True)
            for k,v in legacy.items():
                (dest/k).write_bytes(v)
            self.assertEqual(bingie.inspect_new_profile(dest,inv()),"OWNED_UPGRADE_READY")
            self.assertEqual(bingie.apply_new_profile(dest,inv(),True),"UPGRADED")
            self.assertEqual(bingie.inspect_new_profile(dest,inv()),"ALREADY_APPLIED")
            self.assertEqual((dest/bingie.MENU_FILENAME).read_bytes(),legacy[bingie.MENU_FILENAME])
            self.assertEqual((dest/(bingie.PROPS_FILENAME+".xcmate-0511.bak")).read_bytes(),
                             legacy[bingie.PROPS_FILENAME])
            props=ast.literal_eval((dest/bingie.PROPS_FILENAME).read_text())
            self.assertTrue(any(p[1]=="mp3echo" and "plugin.audio.m3sr2019" in str(p[3]) for p in props))
            self.assertTrue(any(p[1]=="radio" and "plugin.audio.shoutcast" in str(p[3]) for p in props))
            self.assertEqual(bingie.apply_new_profile(dest,inv(),True),"ALREADY_APPLIED")

    def test_custom_properties_are_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/"script.skinshortcuts"
            dest.mkdir()
            for k,v in bingie.render(legacy=True).items():
                (dest/k).write_bytes(v)
            p=dest/bingie.PROPS_FILENAME
            p.write_bytes(b"personal customised property list")
            self.assertEqual(bingie.inspect_new_profile(dest,inv()),"EXISTING_SKIN_DATA_PRESERVED")
            self.assertEqual(bingie.apply_new_profile(dest,inv(),True),"EXISTING_SKIN_DATA_PRESERVED")
            self.assertEqual(p.read_bytes(),b"personal customised property list")
            self.assertFalse((dest/(bingie.PROPS_FILENAME+".xcmate-0511.bak")).exists())

    def test_kodi_reserialized_semantically_matching_files_are_accepted(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest=Path(tmp)/"script.skinshortcuts"
            dest.mkdir()
            generated=bingie.render()
            (dest/bingie.MENU_FILENAME).write_bytes(generated[bingie.MENU_FILENAME])
            props=ast.literal_eval(generated[bingie.PROPS_FILENAME].decode())
            props.reverse()
            props.append(["mainmenu","personal","thumb","user-art.png"])
            (dest/bingie.PROPS_FILENAME).write_text(repr(props))
            self.assertEqual(bingie.inspect_new_profile(dest,inv()),"ALREADY_APPLIED")


class MinimalUIAndRestartTests(unittest.TestCase):
    def test_only_primary_action_and_error_onscreen(self):
        ui=(ROOT/"src/script.gsmedia.setup/default.py").read_text(encoding="utf-8")
        self.assertIn('choices = ["Installation starten"]',ui)
        self.assertIn('choices.append("Fehlerprotokoll anzeigen")',ui)
        for forbidden in ("Installationspilot (3 Pakete", "Komplettinstallation 0.4.0",
                          '"Beenden",', '"Aktuelle Kodi-Add-ons inventarisieren"'):
            self.assertNotIn(forbidden,ui)

    def test_single_reboot_prompt_not_android_restartapp(self):
        ui=(LIB/"setup_auto_ui50.py").read_text(encoding="utf-8")
        self.assertIn("Um die Installation abzuschließen, muss Kodi neu",ui)
        self.assertIn('xbmc.executebuiltin("Quit")',ui)
        self.assertNotIn('xbmc.executebuiltin("RestartApp")',ui)
        self.assertIn("mark_restart_pending(profile)",ui)
        self.assertIn('completion["stage"] = "done"',ui)
        self.assertIn("WIDGETS_",ui)

    def test_reboot_marker_lifecycle(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"script.gsmedia.setup"
            mark_restart_pending(folder)
            self.assertEqual(read(folder)["status"],"restart_pending")
            self.assertEqual(read(folder)["before_pid"],str(os.getpid()))
            finish(folder,"complete")
            self.assertEqual(read(folder)["status"],"complete")
            with self.assertRaises(ValueError):
                finish(folder,"complete")

    def test_service_has_real_postboot_validation(self):
        s=(ROOT/"src/script.gsmedia.setup/service.py").read_text(encoding="utf-8")
        for expected in ("POSTBOOT_TMDB_XVAULT_NOT_VERIFIED","POSTBOOT_WIDGETS_",
                         "POSTBOOT_BINGIE_NOT_ACTIVE","ActivateWindow(Home)",
                         'marker["before_pid"] == str(os.getpid())'):
            self.assertIn(expected,s)


if __name__=="__main__":
    unittest.main()
