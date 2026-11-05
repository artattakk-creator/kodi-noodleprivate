"""Released source, existing repository channel and all previous tests retained."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02974 import without_stabilization74
ROOT=Path(__file__).resolve().parents[1]
class Scope74(unittest.TestCase):
    def test_released_source_kept_with_only_exact_reviewed_changes(self):
        data=json.loads((ROOT/'tests/fixtures/xcmate_02974_protection.json').read_text())
        for path,digest in data['source_sha256'].items():
            self.assertEqual(hashlib.sha256(without_stabilization74((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
    def test_all_published_pilot_indexes_packages_and_checksums_unchanged(self):
        data=json.loads((ROOT/'tests/fixtures/xcmate_02974_protection.json').read_text())
        from channel_contract_02975 import verify
        for path in data['channel_sha256']:verify(path)
    def test_no_previous_test_method_or_skip_contract_removed(self):
        data=json.loads((ROOT/'tests/fixtures/xcmate_02974_protection.json').read_text())
        for path,cases in data['test_methods'].items():
            nodes={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
            for c,n in cases:
                self.assertIn((c,n),nodes,path)
                self.assertEqual([ast.unparse(d) for d in nodes[(c,n)].decorator_list if 'skip' in ast.unparse(d)],data['existing_skip_conditions'][path+'|'+c+'|'+n])
