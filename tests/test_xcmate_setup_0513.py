"""Kodi 21.3 XC Mate userdata recovery without destroying existing Skin Shortcuts."""
import ast
import json
from pathlib import Path
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
LIB = ROOT / "src/script.gsmedia.setup/resources/lib"
sys.path.insert(0, str(LIB))
import setup_bingie_apply as bingie
import setup_bingie_merge_0513 as merge


def inv():
    return {"code": "READY", "addons": {
        "skin.titan.bingie.mod": {"version": "2.2.3", "enabled": True},
        "script.skinshortcuts": {"version": "2.1.0", "enabled": True}}}


def seed(folder, menu=None, props=None):
    folder.mkdir(parents=True)
    (folder / bingie.MENU_FILENAME).write_bytes(
        menu or b'<shortcuts><shortcut><defaultID>movies</defaultID><label>Filme privat</label><action>ActivateWindow(Videos,"plugin://personal/",return)</action></shortcut></shortcuts>')
    (folder / bingie.PROPS_FILENAME).write_bytes(props if props is not None else
                                                 repr([["mainmenu", "movies", "widgetPath", "plugin://personal/"]]).encode())


class MergeTests(unittest.TestCase):
    def test_existing_unrelated_menu_and_widgets_preserved_and_extended(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"script.skinshortcuts"
            seed(folder)
            menu_old=(folder/bingie.MENU_FILENAME).read_bytes()
            props_old=(folder/bingie.PROPS_FILENAME).read_bytes()
            self.assertEqual(bingie.inspect_new_profile(folder, inv()),"SAFE_MERGE_READY")
            self.assertEqual((folder/bingie.MENU_FILENAME).read_bytes(),menu_old)
            self.assertEqual(bingie.apply_new_profile(folder,inv(),True),"MERGED")
            self.assertEqual(bingie.inspect_new_profile(folder,inv()),"ALREADY_APPLIED")
            self.assertEqual((folder/(bingie.MENU_FILENAME+merge.BACKUP_SUFFIX)).read_bytes(),menu_old)
            self.assertEqual((folder/(bingie.PROPS_FILENAME+merge.BACKUP_SUFFIX)).read_bytes(),props_old)
            root=ET.fromstring((folder/bingie.MENU_FILENAME).read_bytes())
            ids={el.findtext("defaultID"):el.findtext("action") for el in root.findall("shortcut")}
            self.assertIn("movies",ids)
            self.assertIn("personal",ids["movies"])
            self.assertIn("xcmate",ids)
            self.assertIn("mp3echo",ids)
            prop=ast.literal_eval((folder/bingie.PROPS_FILENAME).read_text())
            self.assertIn(["mainmenu","movies","widgetPath","plugin://personal/"],prop)
            self.assertTrue(any(x[1]=="mp3echo" and "plugin.audio.m3sr2019" in x[3] for x in prop if x[2].startswith("widgetPath")))
            self.assertTrue(any(x[1]=="radio" and "plugin.audio.shoutcast" in x[3] for x in prop if x[2].startswith("widgetPath")))
            self.assertEqual(bingie.apply_new_profile(folder,inv(),True),"ALREADY_APPLIED")

    def test_conflicting_id_uses_namespaced_alias_without_touching_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"script.skinshortcuts"
            menu=b'<shortcuts><shortcut><defaultID>xcmate</defaultID><label>My menu</label><action>ActivateWindow(Home)</action></shortcut></shortcuts>'
            props=repr([["mainmenu","xcmate","widgetPath","plugin://my-private-widget/"]]).encode()
            seed(folder,menu,props)
            self.assertEqual(bingie.inspect_new_profile(folder,inv()),"SAFE_MERGE_READY")
            self.assertEqual(bingie.apply_new_profile(folder,inv(),True),"MERGED")
            root=ET.fromstring((folder/bingie.MENU_FILENAME).read_bytes())
            ids={row.findtext("defaultID"):row for row in root.findall("shortcut")}
            self.assertEqual(ids["xcmate"].findtext("action"),"ActivateWindow(Home)")
            self.assertIn("xcmate_auto_xcmate",ids)
            existing=ast.literal_eval((folder/bingie.PROPS_FILENAME).read_text())
            self.assertIn(["mainmenu","xcmate","widgetPath","plugin://my-private-widget/"],existing)
            self.assertTrue(any(v[1]=="xcmate_auto_xcmate" and "widget_live_start_group" in v[3] for v in existing))
            self.assertEqual(bingie.inspect_new_profile(folder,inv()),"ALREADY_APPLIED")

    def test_same_action_custom_label_preserved_not_duplicated(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"script.skinshortcuts"
            generated=bingie.render()
            root=ET.fromstring(generated[bingie.MENU_FILENAME])
            for row in root.findall("shortcut"):
                if row.findtext("defaultID")=="filme":
                    row.find("label").text="Meine Filme"
            seed(folder,ET.tostring(root),generated[bingie.PROPS_FILENAME])
            self.assertEqual(bingie.inspect_new_profile(folder,inv()),"ALREADY_APPLIED")

    def test_does_not_replace_nonparseable_existing_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"script.skinshortcuts"
            seed(folder, props=b"not valid Python literal")
            before=(folder/bingie.PROPS_FILENAME).read_bytes()
            self.assertTrue(bingie.inspect_new_profile(folder,inv()).startswith("EXISTING_SKIN_DATA_PRESERVED"))
            self.assertTrue(bingie.apply_new_profile(folder,inv(),True).startswith("EXISTING_SKIN_DATA_PRESERVED"))
            self.assertEqual((folder/bingie.PROPS_FILENAME).read_bytes(),before)
            self.assertFalse((folder/(bingie.PROPS_FILENAME+merge.BACKUP_SUFFIX)).exists())

    def test_foreign_alias_conflict_is_blocked_instead_of_overwritten(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"script.skinshortcuts"
            seed(folder,menu=(b'<shortcuts><shortcut><defaultID>xcmate</defaultID><action>RunPlugin(foo)</action></shortcut>'
                              b'<shortcut><defaultID>xcmate_auto_xcmate</defaultID><action>RunPlugin(bar)</action></shortcut></shortcuts>'))
            self.assertIn("CONFLICT",bingie.inspect_new_profile(folder,inv()))
            self.assertIn("CONFLICT",bingie.apply_new_profile(folder,inv(),True))

    def test_do_not_overwrite_preexisting_backup(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder=Path(tmp)/"script.skinshortcuts"
            seed(folder)
            backup=folder/(bingie.MENU_FILENAME+merge.BACKUP_SUFFIX)
            backup.write_bytes(b"user owns this backup")
            self.assertEqual(bingie.apply_new_profile(folder,inv(),True),"EXISTING_BACKUP_PRESERVED")
            self.assertEqual(backup.read_bytes(),b"user owns this backup")

    def test_production_ids_and_one_button_remain_stable(self):
        ui=(LIB/"setup_auto_ui50.py").read_text()
        self.assertIn('"SAFE_MERGE_READY"',ui)
        self.assertIn('"MERGED"',ui)
        self.assertNotIn('if state.get("stage") == "done":\n        dialog.ok',ui[:ui.index("def _apply_skin")])
        with self.subTest("Kodi user-facing"):
            basic=(ROOT/"src/script.gsmedia.setup/default.py").read_text()
            self.assertIn('choices = ["Installation starten"]',basic)
            self.assertIn("Fehlerprotokoll anzeigen",basic)
            self.assertNotIn("Installationspilot (3 Pakete",basic)


if __name__=="__main__":
    unittest.main()
