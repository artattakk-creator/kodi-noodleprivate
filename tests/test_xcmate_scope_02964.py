"""All 638 source files and 2593 historic test methods stay protected."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02964 import without_stabilization64
ROOT=Path(__file__).resolve().parents[1]
class Scope64(unittest.TestCase):
 def data(self):return json.loads((ROOT/'tests/fixtures/xcmate_02964_protection.json').read_text())
 def test_complete_063_source_inventory_and_exact_reviewed_edits(self):
  baseline=self.data();self.assertEqual(len(baseline['source_sha256']),638)
  for path,digest in baseline['source_sha256'].items():self.assertEqual(hashlib.sha256(without_stabilization64((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
 def test_all_2593_historic_test_methods_and_skip_conditions_remain(self):
  base=self.data();count=0
  for path,cases in base['test_methods'].items():
   methods={(cls.name,fn.name):fn for cls in ast.parse((ROOT/path).read_bytes()).body if isinstance(cls,ast.ClassDef) for fn in cls.body if isinstance(fn,ast.FunctionDef) and fn.name.startswith('test_')}
   for case in cases:
    node=methods[tuple(case)];self.assertEqual([ast.unparse(d) for d in node.decorator_list if 'skip' in ast.unparse(d)],base['existing_skip_conditions'].get(path+'|'+case[0]+'|'+case[1],[]))
   count+=len(cases)
  self.assertEqual(count,2593)
