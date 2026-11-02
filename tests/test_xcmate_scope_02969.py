"""Protect all 670 .68 source files and 2805 historic test methods."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02969 import without_stabilization69
ROOT=Path(__file__).resolve().parents[1]
class Scope69(unittest.TestCase):
 def data(self):return json.loads((ROOT/'tests/fixtures/xcmate_02969_protection.json').read_text())
 def test_every_previous_source_file_is_retained_or_exact_reviewed_delta(self):
  data=self.data();self.assertEqual(len(data['source_sha256']),670)
  for path,digest in data['source_sha256'].items():
   self.assertEqual(hashlib.sha256(without_stabilization69((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
 def test_all_previous_methods_and_skip_conditions_are_retained(self):
  data=self.data();count=0
  for path,cases in data['test_methods'].items():
   methods={(cls.name,fn.name):fn for cls in ast.parse((ROOT/path).read_bytes()).body if isinstance(cls,ast.ClassDef) for fn in cls.body if isinstance(fn,ast.FunctionDef) and fn.name.startswith('test_')}
   for case in cases:
    node=methods[tuple(case)]
    self.assertEqual([ast.unparse(d) for d in node.decorator_list if 'skip' in ast.unparse(d)],data['existing_skip_conditions'].get(path+'|'+case[0]+'|'+case[1],[]))
   count+=len(cases)
  self.assertEqual(count,2805)
