"""Cumulative EPG/series/pixel source and retained-test protection."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02952 import without_stabilization52
ROOT=Path(__file__).resolve().parents[1]

class Scope52(unittest.TestCase):
    def test_all_577_existing_files_retained_with_only_reviewed_epg_series_pixel_deltas(self):
        baseline=json.loads((ROOT/'tests/fixtures/xcmate_02952_protection.json').read_text())
        hooks=json.loads((ROOT/'tests/fixtures/xcmate_02952_reviewed_hooks.json').read_text())['modules']
        self.assertEqual(baseline['base'],'2a9a47736384e6af8e1384fddd5d719092cea9cb')
        self.assertEqual(len(baseline['source_sha256']),577);self.assertEqual(len(hooks),19)
        self.assertEqual({Path(p).name for p in hooks},set(['addon.xml', 'app_services.py', 'catalog_delta.py', 'changelog.txt', 'epg.py', 'group_selection.py', 'guide_grid_diagnostics.py', 'guide_publish44.py', 'guide_store.py', 'guide_window.py', 'infobar45.py', 'library_index.py', 'local_epg.py', 'media_window.py', 'programme_flow48.py', 'programme_index46.py', 'programme_snapshot47.py', 'stream_details.py', 'stream_epg.py']))
        for path,digest in baseline['source_sha256'].items():
            raw=(ROOT/path).read_bytes()
            self.assertEqual(hashlib.sha256(without_stabilization52(raw,path)).hexdigest(),digest,path)
            if path not in hooks:self.assertEqual(hashlib.sha256(raw).hexdigest(),digest,path)
    def test_all_2116_old_methods_retained_without_new_skips(self):
        base=json.loads((ROOT/'tests/fixtures/xcmate_02952_protection.json').read_text());count=0
        for path,cases in base['test_methods'].items():
            nodes={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            for case in cases:
                self.assertIn(tuple(case),nodes,path)
                self.assertEqual([ast.unparse(d) for d in nodes[tuple(case)].decorator_list if 'skip' in ast.unparse(d)],base['existing_skip_conditions'][path+'|'+case[0]+'|'+case[1]])
            count+=len(cases)
        self.assertEqual(count,2116)
