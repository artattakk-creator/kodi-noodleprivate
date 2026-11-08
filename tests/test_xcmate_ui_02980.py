"""Actual generated own adapter geometry and preservation of foreign nodes."""
import importlib,unittest,xml.etree.ElementTree as E
from unittest import mock
from xcmate050_fixture import Fixture50

class Skin80(unittest.TestCase):
 def setUp(self):
  import test_xcmate_skin_02978 as old
  self.h=old.Skin78(methodName='runTest');self.h.setUp();self.addCleanup(self.h.doCleanups)
 def legacy(self):
  with mock.patch('widget_skin80.upgrade',side_effect=lambda files:dict(files)):return self.h.m.build(self.h.original)
 def test_actual_full_bleed_and_contain_fallback_and_idempotence(self):
  import widget_skin80 as adapter
  old=self.legacy();new=adapter.upgrade(old);root=self.h.m.parse(new['xml/IncludesHomeWidgets.xml'])
  main=root.find(".//control[@id='296751']");self.assertEqual(main.findtext('width'),'1620');self.assertEqual(main.findtext('height'),'480')
  portrait=root.find(".//control[@id='296783']");self.assertEqual(portrait.findtext('aspectratio'),'keep');self.assertEqual(adapter.upgrade(new),new)
 def test_own_rows_have_no_unfocused_fade_foreign_definitions_and_settings_survive(self):
  import widget_skin80 as adapter
  old=self.legacy();new=adapter.upgrade(old);root=self.h.m.parse(new['xml/IncludesHomeWidgets.xml']);prior=self.h.m.parse(old['xml/IncludesHomeWidgets.xml'])
  self.assertEqual(E.tostring(root.find("include[@name='widget_base_normal']")),E.tostring(prior.find("include[@name='widget_base_normal']")))
  own=root.find("include[@name='XCMate80.BaseBingie']");self.assertFalse(any(n.get('content')=='BingieUnfocusedWidgetFade' for n in own.iter('include')))
  self.assertEqual(new['shortcuts/template.xml'],old['shortcuts/template.xml']);self.assertEqual(new['shortcuts/overrides.xml'],old['shortcuts/overrides.xml'])
  self.assertIn('Neu im Kino',self.h.prop.read_text())
 def test_unknown_own_hero_is_blocked_without_overwriting_skin(self):
  import widget_skin80 as adapter
  old=self.legacy();old['xml/IncludesHomeWidgets.xml']=old['xml/IncludesHomeWidgets.xml'].replace(b'<width>1080</width>',b'<width>1079</width>',1)
  with self.assertRaises(ValueError):adapter.upgrade(old)

class Guide80(unittest.TestCase):
 def setUp(self):
  # Use the actual common fixture, without opening a device or provider.
  from xcmate027_fixture import Fixture
  class Model(Fixture,unittest.TestCase):pass
  self.h=Model();self.h.setUp();self.addCleanup(self.h.doCleanups)
 def test_explicit_grid_channel_overrides_start_sender_without_portal_mutation(self):
  import guide_grid_data as grid
  h=self.h;portal=dict(h.portal,start_stream_id='1',start_group_id='a');before=dict(portal)
  reader=mock.Mock();reader.groups.return_value=[dict(cid='a',title='A')]
  reader.get.return_value=dict(sid='9',category_id='a')
  reader.position.return_value=17
  with mock.patch('library_index.Reader',return_value=reader),mock.patch.object(grid,'page',side_effect=lambda portal,offset,*a,**k:dict(rows=[],groups=[],offset=offset)) as page:
   result=grid.initial(portal,h.now,selected_sid80='9')
  self.assertEqual(result['row'],1);self.assertEqual(result['offset'],16);self.assertEqual(portal,before)
  reader.get.assert_called_once_with('live','9')


class FocusAsset80(unittest.TestCase):
 def test_original_gray_blue_frame_is_reproducible_and_transparent(self):
  from pathlib import Path
  import sys,io
  sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
  from build_guide_focus80 import build
  from PIL import Image
  target=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/media/guide_focus80.png'
  self.assertEqual(target.read_bytes(),build())
  im=Image.open(io.BytesIO(build())).convert('RGBA')
  self.assertEqual(im.getpixel((64,27)),(0,0,0,0));self.assertEqual(im.getpixel((64,2)),(58,75,91,255))
