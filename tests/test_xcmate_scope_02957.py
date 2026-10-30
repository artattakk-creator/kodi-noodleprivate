"""Exact cumulative .56 baseline, routing/Wizard/player freeze and no secrets."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02957 import without_stabilization57
ROOT=Path(__file__).resolve().parents[1];LIB='src/plugin.video.xtreammate/resources/lib/'


class Scope57(unittest.TestCase):
    def baseline(self):return json.loads((ROOT/'tests/fixtures/xcmate_02957_protection.json').read_text())
    def test_all_602_previous_sources_are_present_with_only_exact_reviewed_deltas(self):
        base=self.baseline();self.assertEqual(base['base'],'34e7e17aff797e736447cae3760667a2ffa9563a')
        self.assertEqual(len(base['source_sha256']),602)
        for path,digest in base['source_sha256'].items():
            self.assertEqual(hashlib.sha256(without_stabilization57((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)

    def test_all_2369_previous_test_methods_and_skip_conditions_remain(self):
        base=self.baseline();count=0
        for path,cases in base['test_methods'].items():
            methods={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            for case in cases:
                self.assertIn(tuple(case),methods,path)
                self.assertEqual([ast.unparse(d) for d in methods[tuple(case)].decorator_list if 'skip' in ast.unparse(d)],base['existing_skip_conditions'][path+'|'+case[0]+'|'+case[1]])
            count+=len(cases)
        self.assertEqual(count,2369)

    def test_routing_widget_sources_wizard_stop_navigation_and_skin_remain_raw_identical(self):
        base=self.baseline()['source_sha256'];count=0
        names={'main.py','home_entry.py','home_menu.py','app_routes.py','widget_home50.py','widget_sources49.py','widget_entry46.py','widget_binding50.py','window_navigation.py',
               'live_navigation.py','live_overlay.py','live_stop42.py','native_stop41.py','native_stop42.py','live_exit.py','exit_jobs.py','playback_exit.py',
               'stream_epg.py','xmltv_stream.py','epg_schedule53.py','source_adapters.py','media_autoplay.py','media_progress.py','widget_skin50.py'}
        for path,digest in base.items():
            name=Path(path).name
            if name in names or name.startswith(('setup_','wizard_','XCMateSetup')) or '/bingie50/' in path or '/skins/' in path:
                self.assertEqual(hashlib.sha256(__import__('stabilization_contract_02958').without_stabilization58((ROOT/path).read_bytes(),path)).hexdigest(),digest,path);count+=1
        self.assertEqual(count,60)

    def test_new_adapter_modules_use_only_public_kodi_metadata_rpc_no_private_helper_import_or_player(self):
        for name in ('helper_rpc57.py','programme_helper57.py','programme_catalog57.py','programme_sources57.py'):
            raw=(ROOT/LIB/name).read_text();tree=ast.parse(raw)
            for node in ast.walk(tree):
                if isinstance(node,ast.ImportFrom):self.assertFalse((node.module or '').startswith(('tmdbhelper','resources.tmdbhelper')))
                if isinstance(node,ast.Call) and isinstance(node.func,ast.Attribute):self.assertNotIn(node.func.attr,('getSetting','setSetting','executebuiltin','Player','Dialog','show','doModal'))
            self.assertNotIn('TMDB_KEY',raw);self.assertNotIn('settings.xml',raw)
