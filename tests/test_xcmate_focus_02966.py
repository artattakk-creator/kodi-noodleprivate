"""Exact four-file opt-in patch, local native geometry and reversible settings."""
import importlib,unittest
import xml.etree.ElementTree as E
from xcmate050_fixture import Fixture50
class Focus66(Fixture50,unittest.TestCase):
 def prepare66(self):
  plan=self.skinmod.prepare(self.skin)
  self.skinmod.apply(plan['id'],self.skin,confirmed=True)
  return plan
 def test_preview_without_confirmation_writes_no_skin_or_widget_bindings(self):
  before=self.skin_bytes();properties=self.prop.read_bytes();menu=self.menu.read_bytes()
  plan=self.skinmod.prepare(self.skin)
  self.assertEqual(self.skin_bytes(),before)
  with self.assertRaises(PermissionError):self.skinmod.apply(plan['id'],self.skin,confirmed=False)
  self.assertEqual(self.skin_bytes(),before);self.assertEqual(self.prop.read_bytes(),properties);self.assertEqual(self.menu.read_bytes(),menu)
 def test_every_foreign_poster_and_square_frame_uses_its_focused_control(self):
  self.prepare66();root=E.parse(self.skin/'xml/IncludesHomeWidgets.xml').getroot();count=0
  for layout in root.iter('focusedlayout'):
   for group in layout.iter('control'):
    if group.get('type')!='group':continue
    for image in group.findall('control'):
     includes=[n.text for n in image.findall('include')]
     if image.get('type')!='image' or 'thumbsborder_focused' not in includes:continue
     self.assertIn('Control.HasFocus($PARAM[widgetid])',image.findtext('visible'))
     self.assertEqual(image.findtext('width'),group.findtext('width'));self.assertEqual(image.findtext('height'),group.findtext('height'));count+=1
  self.assertGreaterEqual(count,2)
 def test_absolute_global_frames_are_hidden_when_any_actual_widget_has_focus(self):
  self.prepare66();root=E.parse(self.skin/'xml/IncludesHomeBingie.xml').getroot();count=0
  for group in root.iter('control'):
   if any((n.get('content') or n.text or '').startswith('Bingie_Screens_Fixed_Focus_Frame') for n in group.findall('include')):
    self.assertIn('!ControlGroup(77777).HasFocus()',[v.text for v in group.findall('visible')]);count+=1
  self.assertGreaterEqual(count,2)
 def test_widget_position_is_published_before_current_identity_without_dead_condition(self):
  self.prepare66();root=E.parse(self.skin/'xml/IncludesHomeWidgets.xml').getroot()
  actions=root.find("include[@name='XCMate66.VerticalFocus']").findall('onfocus')
  self.assertIn('SetProperty(CurrentWidgetPos,',actions[1].text)
  self.assertIn('SetProperty(CurrentWidgetID,',actions[2].text)
  self.assertIsNone(actions[1].get('condition'))
 def test_native_plot_has_bounded_height_without_autogrowing_into_next_heading(self):
  self.prepare66();root=E.parse(self.skin/'xml/IncludesHomeBingie.xml').getroot()
  plot=root.find(".//control[@id='90009']")
  self.assertEqual(plot.findtext('height'),'84');self.assertNotIn('max',plot.find('height').attrib)
  self.assertEqual(plot.findtext('autoscroll'),'false')
 def test_065_upgrade_requires_new_consent_and_restores_065_exactly(self):
  from widget_skin66 import previous_candidate
  from widget_transaction50 import prepare,apply,sha
  paths=[self.skin/name for name in self.skinmod.FILES]
  old=prepare('skin',[(p,previous_candidate(n,p.read_bytes())) for n,p in zip(self.skinmod.FILES,paths)],dict(skin=str(self.skin.resolve()),meta_sha=sha((self.skin/'addon.xml').read_bytes())))
  apply(old['id'],'skin',paths,confirmed=True);before=self.skin_bytes();properties=self.prop.read_bytes();menu=self.menu.read_bytes()
  plan=self.prepare66();self.skinmod.apply(plan['id'],self.skin,confirmed=True,restore=True)
  self.assertEqual(self.skin_bytes(),before);self.assertEqual(self.prop.read_bytes(),properties);self.assertEqual(self.menu.read_bytes(),menu)
 def test_unknown_private_skin_edit_is_blocked_without_reset_or_overwrite(self):
  path=self.skin/'xml/IncludesHomeBingie.xml';path.write_bytes(path.read_bytes()+b'<!-- customized -->')
  before=self.skin_bytes()
  with self.assertRaises(ValueError):self.skinmod.prepare(self.skin)
  self.assertEqual(self.skin_bytes(),before)
