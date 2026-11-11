"""Current cinematic geometry plus archived layout protection, no Android claim."""
import hashlib,json,unittest
from unittest import mock
from test_xcmate_skin_02986 import Skin86
class Skin88(Skin86):
 def test_cinematic_home_is_full_width_left_gradient_not_right_panel(self):
  files=self.graph.build(self.original);m=__import__('widget_skin88');self.assertTrue(m.verify(files));self.assertEqual(m.upgrade(files),files)
  hero=self.graph.parse(files['xml/IncludesHomeWidgets.xml']).find("include[@name='XCMate50.Hero']")
  self.assertEqual(hero.find(".//control[@id='296751']/aspectratio").get('align'),'right')
  self.assertEqual(hero.find(".//control[@id='296750']/left").text,'150')
  self.assertEqual(hero.find(".//control[@id='296750']/control[@type='image']/visible").text,'false')
  for scale in (1,2/3):
   image=hero.find(".//control[@id='296751']");self.assertEqual(int(image.findtext('height'))*scale,620*scale)
   self.assertLessEqual((int(image.findtext('left'))+int(image.findtext('width')))*scale,1920*scale)
 def test_only_released_owned_hero_changes_no_native_or_foreign_rows(self):
  with mock.patch('widget_skin88.upgrade',side_effect=lambda value:dict(value)):old=self.graph.build(self.original)
  new=__import__('widget_skin88').upgrade(old)
  for name in self.graph.FILES:
   if name not in ('xml/IncludesHomeWidgets.xml','xml/IncludesVariables.xml','xml/IncludesBingie.xml'):self.assertEqual(new[name],old[name])
  from widget_skin80 import _node
  name='xml/IncludesHomeWidgets.xml';a,b,_=_node(old[name],'include','name','XCMate50.Hero');c,d,_=_node(new[name],'include','name','XCMate50.Hero')
  self.assertEqual(old[name][:a['start']]+old[name][b:],new[name][:c['start']]+new[name][d:])
  bad=dict(old);bad[name]=old[name].replace(b'<width>1620</width>',b'<width>1618</width>',1)
  with self.assertRaisesRegex(ValueError,'SKIN_MIGRATION_BLOCKED'):__import__('widget_skin88').upgrade(bad)
 def test_existing_logo_asset_is_byte_exact_and_brand_patch_is_reversible(self):
  from xcmate027_fixture import ROOT,ADDON
  from PIL import Image
  asset=ADDON/'resources/media/hero88/xcmate_logo.png';receipt=json.loads(asset.with_suffix('.provenance.json').read_bytes())
  self.assertEqual(hashlib.sha256(asset.read_bytes()).hexdigest(),receipt['sha256'])
  with Image.open(asset) as image:self.assertIn('A',image.mode)
  m=__import__('branding88');raw=b'<includes><include name="HeaderLogo"><control type="image"><texture>bingie_mod_logo.png</texture></control><control type="image"><texture>home/bingie_mod_logo.png</texture></control></include><include name="user"><label>unchanged</label></include></includes>'
  patched=m.candidate(raw);self.assertEqual(patched.count(m.NEW.encode()),2);self.assertIn(b'<include name="user"><label>unchanged</label></include>',patched)
  (self.skin/'xml/IncludesHeader.xml').write_bytes(raw);plan=m.prepare(self.skin)
  with self.assertRaises(PermissionError):m.apply(plan['id'],self.skin)
  m.apply(plan['id'],self.skin,True);self.assertEqual((self.skin/'xml/IncludesHeader.xml').read_bytes(),patched)
  m.apply(plan['id'],self.skin,True,True);self.assertEqual((self.skin/'xml/IncludesHeader.xml').read_bytes(),raw)
 def test_gradient_keeps_text_legible_and_right_subject_untinted(self):
  from PIL import Image
  from xcmate027_fixture import ADDON
  with Image.open(ADDON/'resources/media/hero88/left-gradient.png') as im:
   self.assertGreaterEqual(im.getpixel((20,1))[3],240)
   self.assertEqual(im.getpixel((760,1))[3],0)
   self.assertGreater(im.getpixel((420,1))[3],im.getpixel((600,1))[3])
 def test_released_87_adapter_is_offered_for_88_without_silent_skin_write(self):
  with mock.patch('widget_skin88.upgrade',side_effect=lambda value:dict(value)):old=self.graph.build(self.original)
  for name,raw in old.items():(self.skin/name).write_bytes(raw)
  self.assertTrue(__import__('widget_skin88').previous_owned(self.skin));self.assertFalse(self.graph.installed(self.skin))
  before={name:(self.skin/name).read_bytes() for name in self.graph.FILES};user=self.prop.read_bytes()
  m=__import__('skin_upgrade63');m._done=False;m._pending=None;m._next=0
  self.options['bingie_hero63_notice']='0.1.29.78'
  with mock.patch('widget_manager50.runtime',return_value=(self.profile,self.skin)),mock.patch('widget_skin50.applied',return_value=False):m.prepare()
  self.assertIsNotNone(m._pending);self.assertFalse(m._pending['automatic78'])
  self.assertEqual({name:(self.skin/name).read_bytes() for name in self.graph.FILES},before);self.assertEqual(self.prop.read_bytes(),user)
  plan=m._pending['plan'];self.graph.apply(plan['id'],self.skin,confirmed=True)
  self.assertTrue(self.graph.installed(self.skin));self.assertEqual(self.prop.read_bytes(),user)
  m._pending=None;m._done=False

 def test_bingie_navigation_has_larger_own_glyphs_and_english_aliases_without_foreign_changes(self):
  with mock.patch('widget_skin88.upgrade',side_effect=lambda v:dict(v)):old=self.graph.build(self.original)
  new=__import__('widget_skin88').upgrade(old)
  from widget_skin80 import _node
  name='xml/IncludesBingie.xml';a,b,_=_node(old[name],'include','name','Bingie_Menu_Icon_Defs');c,d,icons=_node(new[name],'include','name','Bingie_Menu_Icon_Defs')
  self.assertEqual((icons.findtext('width'),icons.findtext('height')),('48','48'))
  self.assertEqual(old[name][:a['start']]+old[name][b:],new[name][:c['start']]+new[name][d:])
  menu=self.graph.parse(new['xml/IncludesVariables.xml']).find("variable[@name='XCMate75.MenuIcon']")
  self.assertTrue(any('Live TV' in n.get('condition','') and 'device-tv-normal.png' in n.text for n in menu.findall('value')))
  self.assertEqual(menu.findall('value')[-1].text,'$INFO[ListItem.Icon]')
