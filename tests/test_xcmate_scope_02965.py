"""All .64 source files and historic methods survive the .65 release."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02965 import without_stabilization65
ROOT=Path(__file__).resolve().parents[1]
class Scope65(unittest.TestCase):
 def baseline(self):return json.loads((ROOT/'tests/fixtures/xcmate_02965_protection.json').read_text())
 def test_all_644_prior_source_files_are_preserved_with_only_reviewed_deltas(self):
  values=self.baseline();self.assertEqual(len(values['source_sha256']),644)
  for path,digest in values['source_sha256'].items():self.assertEqual(hashlib.sha256(without_stabilization65((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
 def test_all_2618_historic_methods_and_skip_conditions_remain(self):
  base=self.baseline();count=0
  for path,cases in base['test_methods'].items():
   methods={(cls.name,fn.name):fn for cls in ast.parse((ROOT/path).read_bytes()).body if isinstance(cls,ast.ClassDef) for fn in cls.body if isinstance(fn,ast.FunctionDef) and fn.name.startswith('test_')}
   for case in cases:
    node=methods[tuple(case)];self.assertEqual([ast.unparse(d) for d in node.decorator_list if 'skip' in ast.unparse(d)],base['existing_skip_conditions'].get(path+'|'+case[0]+'|'+case[1],[]))
   count+=len(cases)
  self.assertEqual(count,2618)
