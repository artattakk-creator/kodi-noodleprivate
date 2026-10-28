"""Cumulative EPG/preview/wizard source and retained-test protection."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02953 import without_stabilization53
ROOT=Path(__file__).resolve().parents[1]

class Scope53(unittest.TestCase):
    def test_all_580_existing_files_retained_with_only_reviewed_epg_preview_wizard_deltas(self):
        baseline=json.loads((ROOT/'tests/fixtures/xcmate_02953_protection.json').read_text())
        hooks=json.loads((ROOT/'tests/fixtures/xcmate_02953_reviewed_hooks.json').read_text())['modules']
        self.assertEqual(baseline['base'],'e17c2b2311481fa83f6f9f8ee560837eb369ce6e')
        self.assertEqual(len(baseline['source_sha256']),580);self.assertEqual(len(hooks),19)
        self.assertEqual({Path(p).name for p in hooks},set(['XCMateMapping48.xml', 'XCMateSetup.xml', 'addon.xml', 'changelog.txt', 'epg.py', 'epg_sources.py', 'guide_grid_window.py', 'guide_mapping48.py', 'main.py', 'service.py', 'settings.xml', 'setup_draft.py', 'setup_epg48.py', 'setup_window.py', 'setup_wizard.py', 'stream_epg.py', 'strings.po', 'update_notice41.py']))
        for path,digest in baseline['source_sha256'].items():
            raw=(ROOT/path).read_bytes()
            self.assertEqual(hashlib.sha256(without_stabilization53(raw,path)).hexdigest(),digest,path)
            if path not in hooks:self.assertEqual(hashlib.sha256(raw).hexdigest(),digest,path)
    def test_all_2168_old_methods_retained_without_new_skips(self):
        base=json.loads((ROOT/'tests/fixtures/xcmate_02953_protection.json').read_text());count=0
        for path,cases in base['test_methods'].items():
            nodes={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            for case in cases:
                self.assertIn(tuple(case),nodes,path)
                self.assertEqual([ast.unparse(d) for d in nodes[tuple(case)].decorator_list if 'skip' in ast.unparse(d)],base['existing_skip_conditions'][path+'|'+case[0]+'|'+case[1]])
            count+=len(cases)
        self.assertEqual(count,2168)
