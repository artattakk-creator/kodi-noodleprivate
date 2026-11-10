"""C/E: real BINGIE XML graph, own-node guards, native user rows unchanged."""
import base64,importlib,json,lzma,unittest
from unittest import mock
from xcmate050_fixture import Fixture50
from xcmate027_fixture import ROOT
class Skin86(Fixture50,unittest.TestCase):
 def setUp(self):
  super().setUp();self.m=importlib.import_module('widget_skin86');self.graph=importlib.import_module('widget_skin78')
  extra=json.loads(lzma.decompress(base64.b64decode((ROOT/'tests/fixtures/bingie223_graph78.json.xz.b64').read_bytes())))
  for name,text in extra.items():(self.skin/name).write_text(text)
  self.original={name:(self.skin/name).read_bytes() for name in self.graph.FILES}
  with mock.patch('widget_skin86.upgrade',side_effect=lambda files:dict(files)):self.previous=self.graph.build(self.original)
 def test_all_user_row_template_overrides_and_bindings_remain_byte_exact(self):
  before=self.menu.read_bytes(),self.prop.read_bytes();after=self.m.upgrade(self.previous)
  for name in self.graph.FILES:
   if name not in ('xml/IncludesHomeWidgets.xml','xml/IncludesVariables.xml'):self.assertEqual(after[name],self.previous[name],name)
  from widget_skin80 import _node
  name='xml/IncludesHomeWidgets.xml';a,b,_=_node(self.previous[name],'include','name','XCMate50.Hero');c,d,_=_node(after[name],'include','name','XCMate50.Hero')
  self.assertEqual(self.previous[name][:a['start']]+self.previous[name][b:],after[name][:c['start']]+after[name][d:])
  self.assertEqual((self.menu.read_bytes(),self.prop.read_bytes()),before)
 def test_real_include_graph_compiles_with_separate_poster_and_preload_status_controls(self):
  after=self.m.upgrade(self.previous);self.assertTrue(self.graph.verify(after));self.assertTrue(self.m.verify(after))
  root=self.graph.parse(after['xml/IncludesHomeWidgets.xml'])
  poster=root.find(".//control[@id='296783']");self.assertEqual(poster.findtext('aspectratio'),'keep');self.assertGreater(int(poster.findtext('height')),500);self.assertEqual(poster.findtext('left'),'270');self.assertEqual(poster.findtext('width'),'1080')
  self.assertIn('official_poster',poster.findtext('visible'));self.assertEqual(root.find(".//control[@id='296751']/height").text,'620')
  status=root.find(".//control[@id='296887']");self.assertLessEqual(int(status.findtext('top'))+int(status.findtext('height')),640)
 def test_unknown_owned_hero_change_is_rejected_without_touching_profile(self):
  bad=dict(self.previous);bad['xml/IncludesHomeWidgets.xml']=bad['xml/IncludesHomeWidgets.xml'].replace(b'<width>1620</width>',b'<width>1619</width>',1)
  before=self.prop.read_bytes()
  with self.assertRaisesRegex(ValueError,'UNVERIFIED_86_HERO'):self.m.upgrade(bad)
  self.assertEqual(self.prop.read_bytes(),before)
 def test_second_upgrade_is_idempotent_and_never_duplicates_native_rows(self):
  after=self.m.upgrade(self.previous);self.assertEqual(self.m.upgrade(after),after)
  self.assertEqual(after['xml/IncludesHomeWidgets.xml'].count(b'id="296886"'),1)
