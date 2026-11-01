"""Retain every .65 file and old test/skip contract; no runtime normalization."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02966 import without_stabilization66
ROOT=Path(__file__).resolve().parents[1]
class Scope66(unittest.TestCase):
 def data(self):return json.loads((ROOT/'tests/fixtures/xcmate_02966_protection.json').read_text())
 def test_all_647_previous_source_files_match_after_exact_reviewed_deltas(self):
  data=self.data();self.assertEqual(len(data['source_sha256']),647)
  for path,digest in data['source_sha256'].items():self.assertEqual(hashlib.sha256(without_stabilization66((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
 def test_all_2665_historic_methods_and_skip_conditions_are_retained(self):
  data=self.data();total=0
  for path,cases in data['test_methods'].items():
   methods={(cls.name,fn.name):fn for cls in ast.parse((ROOT/path).read_bytes()).body if isinstance(cls,ast.ClassDef) for fn in cls.body if isinstance(fn,ast.FunctionDef) and fn.name.startswith('test_')}
   for case in cases:
    node=methods[tuple(case)];self.assertEqual([ast.unparse(d) for d in node.decorator_list if 'skip' in ast.unparse(d)],data['existing_skip_conditions'].get(path+'|'+case[0]+'|'+case[1],[]))
   total+=len(cases)
  self.assertEqual(total,2665)
