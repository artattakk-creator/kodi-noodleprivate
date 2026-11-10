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
   if name not in ('xml/IncludesHomeWidgets.xml','xml/IncludesVariables.xml'):self.assertEqual(new[name],old[name])
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
