import unittest,xml.etree.ElementTree as E
from unittest import mock
class UI81(unittest.TestCase):
 def setUp(self):
  from test_xcmate_skin_02978 import Skin78
  self.h=Skin78(methodName='runTest');self.h.setUp();self.addCleanup(self.h.doCleanups)
 def test_exact_owned_upgrade_is_idempotent_both_rows_fit_and_foreign_shortcuts_survive(self):
  import widget_skin81 as adapter
  with mock.patch.object(adapter,'upgrade',side_effect=lambda x:dict(x)):old=self.h.m.build(self.h.original)
  new=adapter.upgrade(old);self.assertEqual(adapter.upgrade(new),new)
  root=self.h.m.parse(new['xml/IncludesHomeWidgets.xml'])
  self.assertEqual(root.find(".//control[@id='296751']/height").text,'520')
  self.assertEqual(root.find(".//control[@id='296783']/aspectratio").text,'keep')
  self.assertEqual(root.find("include[@name='XCMate80.MediaRow']/control/height").text,'268')
  self.assertEqual(root.find("include[@name='XCMate81.PosterRow']/focusedlayout/control[last()]/visible").text,'Control.HasFocus($PARAM[widgetid])')
  self.assertEqual(new['shortcuts/template.xml'],old['shortcuts/template.xml']);self.assertEqual(new['shortcuts/overrides.xml'],old['shortcuts/overrides.xml'])
  self.assertIn('Neu im Kino',self.h.prop.read_text())
 def test_unknown_own_graph_is_blocked_before_any_write(self):
  import widget_skin81 as adapter
  with mock.patch.object(adapter,'upgrade',side_effect=lambda x:dict(x)):old=self.h.m.build(self.h.original)
  old['xml/IncludesHomeWidgets.xml']=old['xml/IncludesHomeWidgets.xml'].replace(b'<height>480</height>',b'<height>479</height>',1)
  with self.assertRaises(ValueError):adapter.upgrade(old)
