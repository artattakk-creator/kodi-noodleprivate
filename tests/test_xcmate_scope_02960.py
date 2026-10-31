"""Cumulative .59 source/test inventory and user data/route boundaries."""
import ast
import hashlib
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path
from stabilization_contract_02960 import without_stabilization60

ROOT = Path(__file__).resolve().parents[1]
LIB = 'src/plugin.video.xtreammate/resources/lib/'

class Scope60(unittest.TestCase):
    def baseline(self):
        return json.loads((ROOT / 'tests/fixtures/xcmate_02960_protection.json').read_text())

    def test_all_612_source_files_are_retained_with_exact_reviewed_deltas(self):
        base = self.baseline()
        self.assertEqual(base['base'], '551a69a327f0bf2e54e594edadd384d2c16ae215')
        self.assertEqual(len(base['source_sha256']), 612)
        for path, digest in base['source_sha256'].items():
            self.assertEqual(hashlib.sha256(without_stabilization60((ROOT / path).read_bytes(), path)).hexdigest(), digest, path)

    def test_all_2491_previous_methods_and_skip_conditions_remain(self):
        base = self.baseline()
        count = 0
        for path, cases in base['test_methods'].items():
            methods = {(c.name, n.name): n for c in ast.parse((ROOT / path).read_bytes()).body if isinstance(c, ast.ClassDef) for n in c.body if isinstance(n, ast.FunctionDef) and n.name.startswith('test_')}
            for case in cases:
                node = methods[tuple(case)]
                self.assertEqual([ast.unparse(d) for d in node.decorator_list if 'skip' in ast.unparse(d)], base['existing_skip_conditions'][path + '|' + case[0] + '|' + case[1]])
            count += len(cases)
        self.assertEqual(count, 2491)

    def test_saved_urls_routing_player_wizard_and_provider_media_are_raw_frozen(self):
        names = {'default.py', 'main.py', 'home_entry.py', 'home_menu.py', 'app_routes.py', 'window_navigation.py', 'widget_sources49.py', 'widget_binding50.py', 'widget_transaction50.py', 'widget_data41.py', 'widget_items45.py', 'widget_render47.py', 'widget_query44.py', 'live_exit.py', 'live_return59.py', 'native_stop41.py', 'live_stop42.py', 'exit_jobs.py', 'playback_exit.py', 'media_autoplay.py', 'media_progress.py', 'epg.py', 'epg_manager53.py', 'stream_epg.py', 'epg_report53.py'}
        for path, digest in self.baseline()['source_sha256'].items():
            if Path(path).name in names or Path(path).name.startswith(('setup_', 'wizard_', 'XCMateSetup')):
                self.assertEqual(hashlib.sha256(without_stabilization60((ROOT / path).read_bytes(),path)).hexdigest(), digest, path)

    def test_tmdb_is_optional_hidden_and_reachable_without_shared_token(self):
        tree = ET.parse(ROOT / 'src/plugin.video.xtreammate/resources/settings.xml')
        for ident in ('programme_tmdb46', 'tmdb_research43'):
            self.assertEqual(tree.find(".//setting[@id='" + ident + "']").get('default'), 'false')
        token = tree.find(".//setting[@id='tmdb_read_token43']")
        self.assertEqual(token.get('default'), '')
        self.assertEqual(token.get('option'), 'hidden')
        action = tree.find(".//setting[@id='tmdb_test60']")
        self.assertEqual(action.get('type'), 'action')
        self.assertIn('action=native_options45', action.get('action'))
        self.assertIn('group=tmdb_test60', action.get('action'))
        self.assertIn('not endorsed or certified', (ROOT / (LIB + 'tmdb_connection60.py')).read_text())

    def test_experiments_are_not_imported_and_no_new_player_or_profile_operations(self):
        for name in ('live_view60.py', 'programme_tvmaze59.py'):
            self.assertFalse((ROOT / LIB / name).exists())
        for name in ('tmdb_connection60.py', 'tmdb_epg60.py', 'widget_skin60.py'):
            for node in ast.walk(ast.parse((ROOT / LIB / name).read_text())):
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    self.assertNotIn(node.func.attr, ('setSetting', 'stop', 'play', 'unlink', 'rmtree', 'remove', 'replace', 'write_bytes', 'write_text'))
