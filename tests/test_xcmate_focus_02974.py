"""Versioned opt-in adapter: local geometry, exact baseline and full restore."""
import hashlib,importlib,unittest
import xml.etree.ElementTree as E
from unittest import mock
from xcmate050_fixture import Fixture50
class Focus74(Fixture50,unittest.TestCase):
 def prepare(self):
  value=self.skinmod.prepare(self.skin);self.skinmod.apply(value['id'],self.skin,confirmed=True);return value
 def test_pristine_and_exact_66_upgrade_have_same_candidate_bytes(self):
  import widget_skin66,widget_skin74
  for name,data in self.skin_bytes().items():self.assertEqual(widget_skin74.candidate(name,data),widget_skin74.candidate(name,widget_skin66.candidate(name,data)),name)
 def test_frame_origin_and_size_are_item_local_not_global_offsets(self):
  self.prepare();root=E.parse(self.skin/'xml/IncludesHomeWidgets.xml').getroot();frames=[]
  for layout in root.iter('focusedlayout'):
   for group in layout.findall("control[@type='group']"):
    for frame in group.findall("control[@type='image']"):
     if frame.findtext('description')!='XCMate74.ItemFocus':continue
     self.assertEqual(frame.findtext('left'),'0');self.assertEqual(frame.findtext('top'),'0')
     for axis in ('width','height'):self.assertEqual(frame.findtext(axis),group.findtext(axis))
     self.assertEqual(frame.findtext('visible'),'Control.HasFocus($PARAM[widgetid])');frames.append(frame)
  self.assertGreaterEqual(len(frames),4)
 def test_native_vertical_navigation_is_restored_without_python_focus_emulation(self):
  self.prepare();text=(self.skin/'xml/IncludesHomeWidgets.xml').read_text();self.assertNotIn('XCMate66.VerticalFocus',text);self.assertIn('SetFixedVerticalNavigationProps',text)
 def test_apply_requires_consent_and_restores_every_original_byte(self):
  before=self.skin_bytes();menu=self.menu.read_bytes();properties=self.prop.read_bytes();plan=self.skinmod.prepare(self.skin)
  self.assertEqual(self.skin_bytes(),before)
  with self.assertRaises(PermissionError):self.skinmod.apply(plan['id'],self.skin,confirmed=False)
  self.skinmod.apply(plan['id'],self.skin,confirmed=True);self.skinmod.apply(plan['id'],self.skin,confirmed=True,restore=True)
  self.assertEqual(self.skin_bytes(),before);self.assertEqual(self.menu.read_bytes(),menu);self.assertEqual(self.prop.read_bytes(),properties)
 def test_private_skin_modification_fails_closed(self):
  path=self.skin/'xml/IncludesHomeWidgets.xml';path.write_bytes(path.read_bytes()+b'<!-- private edit -->');before=self.skin_bytes()
  with self.assertRaises(ValueError):self.skinmod.prepare(self.skin)
  self.assertEqual(self.skin_bytes(),before)
