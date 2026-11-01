"""Verified adapter upgrade, tile-relative bounds, source and LiveRow protection."""
import importlib,unittest
import xml.etree.ElementTree as E
from xcmate050_fixture import Fixture50
from xcmate027_fixture import ADDON
class Layout64(Fixture50,unittest.TestCase):
 def test_known_063_adapter_upgrades_only_after_confirmation_and_restores_exactly(self):
  skin64=importlib.import_module('widget_skin64');paths=[self.skin/name for name in self.skinmod.FILES]
  original=self.skin_bytes();saved=self.prop.read_bytes();menu=self.menu.read_bytes()
  from widget_transaction50 import prepare,apply,sha
  old=prepare('skin',[(p,skin64.previous_candidate(n,p.read_bytes())) for n,p in zip(self.skinmod.FILES,paths)],dict(skin=str(self.skin.resolve()),meta_sha=sha((self.skin/'addon.xml').read_bytes())))
  apply(old['id'],'skin',paths,confirmed=True);legacy=self.skin_bytes()
  plan=self.skinmod.prepare(self.skin);self.assertEqual(self.skin_bytes(),legacy)
  with self.assertRaises(PermissionError):self.skinmod.apply(plan['id'],self.skin,confirmed=False)
  self.skinmod.apply(plan['id'],self.skin,confirmed=True)
  tree=E.parse(self.skin/'xml/IncludesHomeWidgets.xml')
  own=[n for n in tree.iter('control') if n.get('type')=='image' and 'programme55/focus.png' in (n.findtext('texture') or '') and n.findtext('width')=='240']
  self.assertTrue(own);self.assertGreaterEqual(sum(n.findtext('height')=='330' for n in own),2)
  self.assertEqual(self.prop.read_bytes(),saved);self.assertEqual(self.menu.read_bytes(),menu)
  self.skinmod.apply(plan['id'],self.skin,confirmed=True,restore=True);self.assertEqual(self.skin_bytes(),legacy)
  self.skinmod.apply(old['id'],self.skin,confirmed=True,restore=True);self.assertEqual(self.skin_bytes(),original)
 def test_live_row_only_hides_inactive_frame_and_reuses_original_space_asset(self):
  a=E.parse(ADDON/'resources/bingie64/IncludesXCMate64.xml').find("include[@name='XCMate50.LiveRow']")
  b=E.parse(ADDON/'resources/bingie63/IncludesXCMate63.xml').find("include[@name='XCMate50.LiveRow']")
  frames=[n for n in a.iter('control') if 'programme55/focus.png' in (n.findtext('texture') or '')]
  self.assertEqual(len(frames),1);visible=frames[0].find('visible')
  self.assertEqual(visible.text,'Control.HasFocus($PARAM[widgetid])');frames[0].remove(visible)
  a.tail=b.tail=None;E.indent(a);E.indent(b);self.assertEqual(E.tostring(a),E.tostring(b))
  tree=E.parse(ADDON/'resources/bingie64/IncludesXCMate64.xml')
  image=tree.find("variable[@name='XCMate64.Image']")
  self.assertTrue(image[-1].text.endswith('resources/media/lightweight_splash.jpg'))
 def test_unknown_skin_modifications_still_block(self):
  target=self.skin/'xml/IncludesHomeWidgets.xml';target.write_bytes(target.read_bytes()+b'\n<!-- private customization -->')
  original=self.skin_bytes()
  with self.assertRaises(ValueError):self.skinmod.prepare(self.skin)
  self.assertEqual(self.skin_bytes(),original)
