"""Exercise the real native restart collector against partial JSON writes."""
import ast,json,unittest
from pathlib import Path
from types import SimpleNamespace
ROOT=Path(__file__).resolve().parents[1]
class Receipt88(unittest.TestCase):
 def loop(self,values):
  source=ast.parse((ROOT/'tools/kodi_home75_host/restart75.py').read_text())
  loop=next(n for n in source.body if isinstance(n,ast.For) and 'gui_budget87' in ast.unparse(n.iter))
  reads=[];sleeps=[]
  class File:
   def __init__(self,path):self.path=path
   def exists(self):return False
   def read_text(self,**kwargs):
    reads.append(kwargs);return values[min(len(reads)-1,len(values)-1)]
  ns=dict(Path=File,json=json,time=SimpleNamespace(sleep=lambda seconds:sleeps.append(seconds)),gui_budget87=1)
  exec(compile(ast.Module(body=[loop],type_ignores=[]),'actual-native-receipt','exec'),ns)
  return ns,reads,sleeps
 def test_empty_then_partial_then_complete_receipt_is_read_once_as_complete(self):
  ns,reads,sleeps=self.loop(['','{"status":',json.dumps(dict(status='PASS',actual_restart=True))])
  self.assertEqual(ns['result']['status'],'PASS');self.assertEqual(len(reads),3);self.assertEqual(len(sleeps),2)
  self.assertTrue(all(r==dict(encoding='utf-8') for r in reads))
 def test_reported_failure_is_never_retried_as_success(self):
  with self.assertRaisesRegex(RuntimeError,'POST75_REPORTED_FAILURE'):self.loop([json.dumps(dict(status='FAIL'))])
 def test_incomplete_receipt_retains_the_existing_bounded_timeout(self):
  with self.assertRaisesRegex(RuntimeError,'POST75_GUI_TIMEOUT'):self.loop([''])
