"""Keep all .49 data/player/widget implementations except six exact entry deltas."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02950 import without_widget50
ROOT=Path(__file__).resolve().parents[1]

class Scope50(unittest.TestCase):
    def test_all_566_published_files_are_retained_and_560_remain_byte_identical(self):
        base=json.loads((ROOT/'tests/fixtures/xcmate_02950_protection.json').read_text())
        hooks=json.loads((ROOT/'tests/fixtures/xcmate_02950_reviewed_hooks.json').read_text())['modules']
        self.assertEqual(base['base'],'bc278a32a0e9a3bc8763189c09ffa9195d4dddf3');self.assertEqual(len(base['source_sha256']),566)
        self.assertEqual(len(hooks),6);self.assertEqual({Path(p).name for p in hooks},{'addon.xml','changelog.txt','strings.po','app_routes.py','widget_entry46.py'})
        for path,digest in base['source_sha256'].items():
            raw=(ROOT/path).read_bytes();self.assertEqual(hashlib.sha256(without_widget50(raw,path)).hexdigest(),digest,path)
            if path not in hooks:self.assertEqual(hashlib.sha256(raw).hexdigest(),digest,path)
    def test_all_2035_existing_methods_remain_without_new_skips(self):
        baseline=json.loads((ROOT/'tests/fixtures/xcmate_02950_protection.json').read_text());count=0
        for path,cases in baseline['test_methods'].items():
            present={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            for case in cases:
                self.assertIn(tuple(case),present,path)
                self.assertEqual([ast.unparse(d) for d in present[tuple(case)].decorator_list if 'skip' in ast.unparse(d)],baseline['existing_skip_conditions'].get(path+'|'+case[0]+'|'+case[1],[]))
            count+=len(cases)
        self.assertEqual(count,2035)
