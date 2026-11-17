"""A late test-addon prompt cannot silently count as mapping focus proof."""
import importlib.util,sys,unittest
from pathlib import Path
from unittest import mock
HOST=Path(__file__).resolve().parents[1]/'tools/kodi_epg94_host'
sys.path.insert(0,str(HOST))
class Fixture98(unittest.TestCase):
 def helper(self):
  self.assertIsNotNone(importlib.util.find_spec('bootstrap98'))
  import bootstrap98
  return bootstrap98
 def test_only_exact_own_disabled_test_addon_prompt_is_acknowledged(self):
  helper=self.helper()
  def invoke(body,window=10100,heading='Disabled add-ons',control='No'):
   def answer(method,params=None):
    if method=='GUI.GetProperties':return dict(currentwindow=dict(id=window),currentcontrol=dict(label=control))
    if method=='XBMC.GetInfoLabels':return {key:(heading if key=='Control.GetLabel(1)' else body) for key in params['labels']}
    if method=='Input.Select':return 'OK'
    self.fail(method)
   rpc=mock.Mock(side_effect=answer);result=helper.settle_fixture_prompt(rpc)
   return result,[c for c in rpc.call_args_list if c.args[0]=='Input.Select']
  for body,window,heading,control in [('Would you like to enable this add-on? Foreign add-on referencing Catalog73 synthetic GUI contract',10100,'Disabled add-ons','No'),('Another installed add-on',10100,'Disabled add-ons','No'),('Catalog73 synthetic GUI contract',12000,'Select','No'),('Catalog73 synthetic GUI contract',10100,'Delete profile?','No'),('Catalog73 synthetic GUI contract',10100,'Disabled add-ons','Yes')]:
   with self.subTest(body=body,window=window,heading=heading):self.assertEqual(invoke(body,window,heading,control),(False,[]))
  result,calls=invoke('Would you like to enable this add-on? Catalog73 synthetic GUI contract')
  self.assertTrue(result);self.assertEqual(len(calls),1)
 def test_post_screenshot_receipt_observes_focus_loss_without_resetting_it(self):
  import ast
  source=ast.parse((HOST/'mapping482.py').read_text())
  function=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='mapping_shot98')
  receipt=dict(dialog=13001,owner='mini',control=200)
  focus=mock.Mock(return_value=receipt);observe=mock.Mock(return_value=None)
  namespace=dict(mapping_focus98=focus,read_mapping_focus98=observe,shot=lambda name:name+'.png')
  exec(compile(ast.Module(body=[function],type_ignores=[]),'native_mapping_observer','exec'),namespace)
  with self.assertRaisesRegex(AssertionError,'FOCUS_CHANGED_DURING_SCREENSHOT'):
   namespace['mapping_shot98'](object(),200,'frame')
  focus.assert_called_once();observe.assert_called_once()
 def test_empty_receipts_cannot_be_counted_as_stable_focus(self):
  import ast
  source=ast.parse((HOST/'mapping482.py').read_text())
  function=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='mapping_shot98')
  namespace=dict(mapping_focus98=lambda *a:None,read_mapping_focus98=lambda *a:None,shot=lambda name:name+'.png')
  exec(compile(ast.Module(body=[function],type_ignores=[]),'native_mapping_observer','exec'),namespace)
  with self.assertRaisesRegex(AssertionError,'FOCUS_CHANGED_DURING_SCREENSHOT'):
   namespace['mapping_shot98'](object(),200,'frame')
 def test_select_requires_valid_unchanged_top_dialog_focus_after_settle(self):
  import ast,types
  source=ast.parse((HOST/'mapping482.py').read_text())
  function=next(n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='select_control482')
  receipt=dict(dialog=13001,owner='mini',control=200)
  for before,after in [(None,None),(receipt,None),(receipt,dict(dialog=13002,owner='grid',control=200)),(receipt,receipt)]:
   with self.subTest(before=before,after=after):
    execute=mock.Mock();namespace=dict(mapping_focus98=lambda *a:before,read_mapping_focus98=lambda *a:after,xbmc=types.SimpleNamespace(sleep=lambda ms:None,executebuiltin=execute))
    exec(compile(ast.Module(body=[function],type_ignores=[]),'native_mapping_input','exec'),namespace)
    if before and before==after:
     namespace['select_control482'](object(),200);execute.assert_called_once_with('Action(Select)',wait=False)
    else:
     with self.assertRaisesRegex(AssertionError,'INPUT_FOCUS_NOT_STABLE'):namespace['select_control482'](object(),200)
     execute.assert_not_called()
 def test_focus_receipt_requires_matching_owner_dialog_and_requested_control(self):
  helper=self.helper()
  self.assertEqual(helper.focus_receipt(13001,'mini',200,'mini',200),dict(dialog=13001,owner='mini',control=200))
  for window,owner,control in [(10100,'',200),(13001,'grid',200),(13001,'mini',405),(0,'mini',200)]:
   with self.subTest(window=window,owner=owner,control=control):
    self.assertIsNone(helper.focus_receipt(window,owner,control,'mini',200))
if __name__=='__main__':unittest.main()
