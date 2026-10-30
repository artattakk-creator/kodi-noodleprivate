"""Cumulative 0.1.29.59 release-gate: keep every .58 protection in force."""
import ast
import hashlib
import importlib
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
LIB=ROOT/'src/plugin.video.xtreammate/resources/lib'

class Scope59(unittest.TestCase):
    def test_version_and_previous_version_preserved(self):
        addon=ROOT/'src/plugin.video.xtreammate/addon.xml'
        self.assertEqual(ET.parse(addon).getroot().get('version'),'0.1.29.59')
        from stabilization_contract_02959 import without_stabilization59
        old=without_stabilization59(addon.read_text(encoding='utf-8'),
                                     'src/plugin.video.xtreammate/addon.xml')
        self.assertEqual(ET.fromstring(old).get('version'),'0.1.29.58')

    def test_approved_deltas_strip_exactly_to_frozen_58(self):
        from stabilization_contract_02959 import without_stabilization59
        from stabilization_contract_02958 import without_stabilization58
        import json
        fixture=json.loads((ROOT/'tests/fixtures/xcmate_02958_protection.json').read_text())
        paths=[
            'src/plugin.video.xtreammate/addon.xml',
            'src/plugin.video.xtreammate/resources/lib/app_routes.py',
            'src/plugin.video.xtreammate/resources/lib/settings_sections45.py',
            'src/plugin.video.xtreammate/resources/lib/experimental45.py',
            'src/plugin.video.xtreammate/resources/lib/menu_icons45.py',
            'src/plugin.video.xtreammate/resources/language/resource.language.de_de/strings.po',
            'src/plugin.video.xtreammate/resources/language/resource.language.en_gb/strings.po',
        ]
        for path in paths:
            src=(ROOT/path).read_bytes()
            restored=without_stabilization59(src,path)
            self.assertNotEqual(src,restored,path)
            self.assertEqual(hashlib.sha256(without_stabilization58(restored,path)).hexdigest(),
                             fixture['source_sha256'][path],path)

    def test_p0_modules_are_not_changed_in_this_scope(self):
        # Scope protection: keep all previously frozen media/exit/binding bytes.
        from stabilization_contract_02959 import without_stabilization59
        for name in ('live_exit.py','live_stop42.py','live_stop58.py',
                     'widget_binding50.py','widget_skin50.py','widget_home50.py',
                     'widget_sources49.py','widget_data41.py'):
            path='src/plugin.video.xtreammate/resources/lib/'+name
            data=(ROOT/path).read_bytes()
            self.assertEqual(without_stabilization59(data,path),data)

    def test_no_player_api_or_skin_file_writer_in_new_view(self):
        tree=ast.parse((LIB/'live_view60.py').read_text(encoding='utf-8'))
        forbidden={'Player','setResolvedUrl','executebuiltin','setSetting','request_refresh',
                   'unlink','rmtree','remove','open'}
        for node in ast.walk(tree):
            if isinstance(node,ast.Call):
                if isinstance(node.func,ast.Attribute):
                    self.assertNotIn(node.func.attr,forbidden)
                if isinstance(node.func,ast.Name):
                    self.assertNotIn(node.func.id,forbidden)
        self.assertNotIn('PlayerControl(', (LIB/'live_view60.py').read_text())

    def test_live_view_remains_experimental_not_home(self):
        routes=(LIB/'app_routes.py').read_text()
        exp=(LIB/'experimental45.py').read_text()
        menu=(LIB/'settings_sections45.py').read_text()
        self.assertIn("if action=='live_view60':",routes)
        self.assertIn("'live_view60'",exp)
        self.assertIn("'experimental':[(36720,'live_view60',{})",menu)
        self.assertNotIn('skin.titan.bingie.mod', (LIB/'live_view60.py').read_text())

if __name__=='__main__':
    unittest.main()
