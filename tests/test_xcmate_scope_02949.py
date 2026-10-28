"""Minimal hotfix: all published .48 data/player/widget implementations frozen."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02949 import without_widget49
ROOT=Path(__file__).resolve().parents[1]

class Scope49(unittest.TestCase):
    def baseline(self):return json.loads((ROOT/'tests/fixtures/xcmate_02949_protection.json').read_text())
    def test_all_565_published_sources_retained_with_only_seven_exact_routing_and_label_changes(self):
        data=self.baseline();self.assertEqual(len(data['source_sha256']),565)
        hooks=json.loads((ROOT/'tests/fixtures/xcmate_02949_reviewed_hooks.json').read_text())['modules']
        self.assertEqual({Path(p).name for p in hooks},{'addon.xml','changelog.txt','strings.po','app_routes.py','widget_ui45.py','window_navigation.py'})
        self.assertEqual(len(hooks),7)
        for path,digest in data['source_sha256'].items():
            raw=(ROOT/path).read_bytes()
            self.assertEqual(hashlib.sha256(without_widget49(raw,path)).hexdigest(),digest,path)
            if path not in hooks:self.assertEqual(hashlib.sha256(raw).hexdigest(),digest,path)
    def test_all_2021_existing_tests_retained_without_any_new_skip(self):
        count=0;baseline=self.baseline()
        for path,cases in baseline['test_methods'].items():
            actual={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            for case in cases:
                self.assertIn(tuple(case),actual,path)
                skip=[ast.unparse(d) for d in actual[tuple(case)].decorator_list if 'skip' in ast.unparse(d)]
                self.assertEqual(skip,baseline['existing_skip_conditions'].get(path+'|'+case[0]+'|'+case[1],[]))
            count+=len(cases)
        self.assertEqual(count,2021)
