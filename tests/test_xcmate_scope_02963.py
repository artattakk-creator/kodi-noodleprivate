"""Exact .62 baseline and reviewed .63 hooks; VOD/player/settings stay protected."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02963 import without_stabilization63
ROOT=Path(__file__).resolve().parents[1]

class Scope63(unittest.TestCase):
 def data(self):return json.loads((ROOT/'tests/fixtures/xcmate_02963_protection.json').read_text())
 def test_all_624_previous_source_files_and_only_exact_reviewed_deltas(self):
  base=self.data();self.assertEqual(base['base'],'7b76bd0fdfe7dcbfdac1d936490d409d719b630c');self.assertEqual(len(base['source_sha256']),624)
  for path,digest in base['source_sha256'].items():self.assertEqual(hashlib.sha256(without_stabilization63((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
 def test_all_2553_previous_methods_and_skip_conditions_remain(self):
  base=self.data();count=0
  for path,cases in base['test_methods'].items():
   methods={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
   for case in cases:
    node=methods[tuple(case)];self.assertEqual([ast.unparse(d) for d in node.decorator_list if 'skip' in ast.unparse(d)],base['existing_skip_conditions'][path+'|'+case[0]+'|'+case[1]])
   count+=len(cases)
  self.assertEqual(count,2553)
 def test_unreviewed_edits_are_rejected_and_nonhook_sources_are_raw_unchanged(self):
  hooks=json.loads((ROOT/'tests/fixtures/xcmate_02963_reviewed_hooks.json').read_text())['modules']
  for path,digest in self.data()['source_sha256'].items():
   raw=(ROOT/path).read_bytes()
   if path not in hooks:self.assertEqual(hashlib.sha256(raw).hexdigest(),digest,path)
   else:
    with self.assertRaises(AssertionError):without_stabilization63(raw+b'\nunreviewed63\n',path)
