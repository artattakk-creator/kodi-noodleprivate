"""70/30 geometry and a nontrivial personal layout remain protected together."""
import importlib,json,unittest
from unittest import mock
from test_xcmate_skin_02986 import Skin86
class Skin87(Skin86):
 # Inherit the four existing graph regressions; add exact foreign-source cases.
 def foreign(self):
  names=[('MP3 Streams Echoed','plugin.audio.m3sr2019'),('SHOUTcast','plugin.audio.shoutcast'),('Im Kino','plugin.video.foreign.cinema'),('Neu im Kino','plugin.video.foreign.cinema'),('Frisch im Kino','plugin.video.foreign.cinema'),('Diese Woche aktuell','plugin.video.foreign.trends'),('Meine Serien','plugin.video.foreign.series'),('Mein Wetter','plugin.video.foreign.weather'),('Meine Nachrichten','plugin.video.foreign.news')]
  rows=[]
  for i,(name,addon) in enumerate(names):
   suffix='.'+str(i) if i else ''
   for k,v in dict(widgetName=name,widgetPath='plugin://'+addon+'/?category='+str(i),widgetEnabled='true',widgetStyle='poster').items():rows.append(['mainmenu','10000',k+suffix,v])
  self.prop.write_text(repr(rows));return rows
 def test_nine_saved_foreign_widget_rows_are_not_replaced_by_three_xcmate_sources(self):
  self.foreign();m=__import__('widget_inventory87');before=m.collect(self.profile,self.skin);raw=self.prop.read_bytes(),self.menu.read_bytes()
  graph=self.graph.build(self.original);self.assertTrue(__import__('widget_skin87').verify(graph))
  self.assertEqual((self.prop.read_bytes(),self.menu.read_bytes()),raw);self.assertTrue(m.compare(self.profile,before));self.assertEqual(len(before['widgets']),9);self.assertTrue(all(v['external'] for v in before['widgets']))
  from widget_skin80 import _node

  with mock.patch('widget_skin87.upgrade',side_effect=lambda files:dict(files)):baseline87=self.graph.build(self.original)
  a,b,_=_node(baseline87['xml/IncludesHomeWidgets.xml'],'include','name','widget_layout_poster');c,d,_=_node(graph['xml/IncludesHomeWidgets.xml'],'include','name','widget_layout_poster')
  self.assertEqual(baseline87['xml/IncludesHomeWidgets.xml'][a['start']:b],graph['xml/IncludesHomeWidgets.xml'][c['start']:d])
 def test_widget_name_order_path_enablement_and_slots_are_all_integrity_checked(self):
  rows=self.foreign();m=__import__('widget_inventory87');receipt=m.collect(self.profile,self.skin)
  for index,new in [(0,'Changed name'),(1,'plugin://plugin.video.xtreammate/?action=widget_recent_vod'),(2,'false')]:
   changed=[list(v) for v in rows];changed[index][3]=new;self.prop.write_text(repr(changed))
   with self.assertRaisesRegex(ValueError,'SKIN_MIGRATION_BLOCKED'):m.compare(self.profile,receipt)
  self.prop.write_text(repr(list(reversed(rows))))
  with self.assertRaisesRegex(ValueError,'SKIN_MIGRATION_BLOCKED'):m.compare(self.profile,receipt)
 def test_unknown_widget_format_blocks_before_any_skin_or_profile_write(self):
  self.prop.write_text('unsupported private format')
  with self.assertRaisesRegex(ValueError,'SKIN_MIGRATION_BLOCKED'):__import__('widget_inventory87').collect(self.profile,self.skin)
 def test_fixed_hero_image_table_and_attribution_bounds_at_both_resolutions(self):
  with mock.patch('widget_skin88.upgrade',side_effect=lambda files:dict(files)):graph=self.graph.build(self.original)
  node=self.graph.parse(graph['xml/IncludesHomeWidgets.xml']).find("include[@name='XCMate50.Hero']")
  for scale in (1,2/3):
   panel=node.find(".//control[@id='296750']");self.assertAlmostEqual(540/1620,1/3)
   self.assertLessEqual((int(panel.findtext('left'))+int(panel.findtext('width')))*scale,1920*scale)
   self.assertEqual(int(node.find(".//control[@id='296751']/height").text)*scale,620*scale)
   for item in panel.findall('control'):
    self.assertLessEqual((int(item.findtext('top','0'))+int(item.findtext('height','0')))*scale,620*scale)
  status=node.find(".//control[@id='296887']");self.assertGreaterEqual(int(status.findtext('left')),1350);self.assertEqual(node.find(".//control[@id='296785']/visible").text,'false')
 def test_foreign_headers_keep_their_native_labels_and_are_not_globally_hidden_on_home(self):
  with mock.patch('widget_skin88.upgrade',side_effect=lambda files:dict(files)):graph=self.graph.build(self.original)
  node=self.graph.parse(graph['xml/IncludesHomeWidgets.xml']).find("include[@name='widget_header_multi']")
  self.assertIn('XCMate.WidgetKind41',node.find('control/visible').text)
  self.assertTrue(node.find('control/visible').text.startswith('!Window.IsActive(Home) | !['))
  self.assertTrue(any(c.text=='$PARAM[widgetName]' for c in node.iter('label')))
 def test_profile_switch_is_detected_even_with_identical_foreign_widget_definitions(self):
  self.foreign();m=__import__('widget_inventory87');receipt=m.collect(self.profile,self.skin)
  receipt['profile']=str(self.folder/'other-profile')
  with self.assertRaisesRegex(ValueError,'SKIN_MIGRATION_BLOCKED'):m.compare(self.profile,receipt)
