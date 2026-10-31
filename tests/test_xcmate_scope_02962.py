"""Cumulative .60 inventory plus raw protection of widget sources/player/data."""
import ast,hashlib,json,unittest
from pathlib import Path
from stabilization_contract_02962 import without_stabilization62
ROOT=Path(__file__).resolve().parents[1]
class Scope62(unittest.TestCase):
 def baseline(self):return json.loads((ROOT/'tests/fixtures/xcmate_02962_protection.json').read_text())
 def test_all_621_source_files_and_reviewed_deltas(self):
  base=self.baseline();self.assertEqual(base['base'],'dfe59e98305aa73cfcf3e0c7c7e49dcfb0dbf9ca');self.assertEqual(len(base['source_sha256']),621)
  for path,digest in base['source_sha256'].items():self.assertEqual(hashlib.sha256(without_stabilization62((ROOT/path).read_bytes(),path)).hexdigest(),digest,path)
 def test_all_2536_previous_methods_and_skip_conditions_are_preserved(self):
  base=self.baseline();count=0
  for path,cases in base['test_methods'].items():
   methods={(c.name,n.name):n for c in ast.parse((ROOT/path).read_bytes()).body if isinstance(c,ast.ClassDef) for n in c.body if isinstance(n,ast.FunctionDef) and n.name.startswith('test_')}
   for case in cases:
    node=methods[tuple(case)];self.assertEqual([ast.unparse(d) for d in node.decorator_list if 'skip' in ast.unparse(d)],base['existing_skip_conditions'][path+'|'+case[0]+'|'+case[1]])
   count+=len(cases)
  self.assertEqual(count,2536)
 def test_sources_bindings_player_epg_and_user_data_code_are_raw_unchanged(self):
  allowed={'addon.xml','changelog.txt','strings.po','widget_home50.py','widget_manager50.py','tmdb_access61.py','tmdb_token61.py'}
  for path,digest in self.baseline()['source_sha256'].items():
   if Path(path).name not in allowed:self.assertEqual(hashlib.sha256((ROOT/path).read_bytes()).hexdigest(),digest,path)
