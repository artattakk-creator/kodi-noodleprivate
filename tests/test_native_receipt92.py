"""Exercise the real native fixture publisher, without launching Kodi/RPC."""
import ast
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

class NativeReceipt92(unittest.TestCase):
 def setUp(self):
  source=Path(__file__).resolve().parents[1]/'tools/kodi_home90_host/picker_check90.py'
  function=next(n for n in ast.parse(source.read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='write_receipt90')
  namespace=dict(Path=Path,json=json)
  exec(compile(ast.Module(body=[function],type_ignores=[]),str(source),'exec'),namespace)
  self.publish=namespace['write_receipt90']
  folder=tempfile.TemporaryDirectory();self.addCleanup(folder.cleanup);self.folder=Path(folder.name)
 def test_complete_json_becomes_visible_only_by_atomic_replace(self):
  target=self.folder/'receipt.json';original=Path.replace;seen=[]
  def boundary(path,dest):
   self.assertFalse(target.exists());seen.append(json.loads(path.read_text()));return original(path,dest)
  with mock.patch.object(Path,'replace',boundary):self.publish(target,dict(status='PASS',rows=88))
  self.assertEqual(seen,[dict(status='PASS',rows=88)]);self.assertEqual(json.loads(target.read_text()),seen[0]);self.assertFalse(list(self.folder.glob('*.writing')))
 def test_failed_publication_never_replaces_last_complete_report(self):
  target=self.folder/'receipt.json';old=dict(status='OLD',rows=24);target.write_text(json.dumps(old))
  with mock.patch.object(Path,'replace',side_effect=OSError('synthetic publication failure')),self.assertRaises(OSError):
   self.publish(target,dict(status='PASS',rows=88))
  self.assertEqual(json.loads(target.read_text()),old)
