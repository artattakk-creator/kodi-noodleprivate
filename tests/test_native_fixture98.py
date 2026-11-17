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
  for body,window,heading,control in [('Another installed add-on',10100,'Disabled add-ons','No'),('Catalog73 synthetic GUI contract',12000,'Select','No'),('Catalog73 synthetic GUI contract',10100,'Delete profile?','No'),('Catalog73 synthetic GUI contract',10100,'Disabled add-ons','Yes')]:
   with self.subTest(body=body,window=window,heading=heading):self.assertEqual(invoke(body,window,heading,control),(False,[]))
  result,calls=invoke('Would you like to enable this add-on? Catalog73 synthetic GUI contract')
  self.assertTrue(result);self.assertEqual(len(calls),1)
 def test_focus_receipt_requires_matching_owner_dialog_and_requested_control(self):
  helper=self.helper()
  self.assertEqual(helper.focus_receipt(13001,'mini',200,'mini',200),dict(dialog=13001,owner='mini',control=200))
  for window,owner,control in [(10100,'',200),(13001,'grid',200),(13001,'mini',405),(0,'mini',200)]:
   with self.subTest(window=window,owner=owner,control=control):
    self.assertIsNone(helper.focus_receipt(window,owner,control,'mini',200))
if __name__=='__main__':unittest.main()
