"""Retain the complete fixed .66 source and every historic test/skip condition."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02967 import without_stabilization67
ROOT=Path(__file__).resolve().parents[1]
class Scope67(unittest.TestCase):
 def baseline(self):return json.loads((ROOT/'tests/fixtures/xcmate_02967_protection.json').read_text())
 def test_all_653_previous_source_files_match_after_exact_reviewed_deltas(self):
  data=self.baseline();self.assertEqual(len(data['source_sha256']),653)
  for path,digest in data['source_sha256'].items():self.assertEqual(hashlib.sha256(without_stabilization67((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
 def test_all_2719_old_methods_and_skip_conditions_remain(self):
  data=self.baseline();total=0
  for path,cases in data['test_methods'].items():
   methods={(cls.name,fn.name):fn for cls in ast.parse((ROOT/path).read_bytes()).body if isinstance(cls,ast.ClassDef) for fn in cls.body if isinstance(fn,ast.FunctionDef) and fn.name.startswith('test_')}
   for case in cases:
    node=methods[tuple(case)];self.assertEqual([ast.unparse(d) for d in node.decorator_list if 'skip' in ast.unparse(d)],data['existing_skip_conditions'].get(path+'|'+case[0]+'|'+case[1],[]))
   total+=len(cases)
  self.assertEqual(total,2719)
