"""All own menu surfaces use existing focusable rows and local registry assets."""
import ast,hashlib,importlib,sys,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,LIB,ADDON

class MenuIcons45(Fixture,unittest.TestCase):
 def setUp(self):super().setUp();self.m=importlib.import_module('menu_icons45');self.layout=importlib.import_module('menu_layout45')
 def test_every_semantic_role_has_distinct_nonempty_local_transparent_png(self):
  from PIL import Image
  values=[]
  for role in self.m.ROLES:
   for full in (False,True):
    path=Path(self.m.icon(role,full=full));self.assertTrue(path.is_file(),role)
    with Image.open(path) as im:self.assertEqual(im.mode,'RGBA');self.assertEqual(im.size,(96,96));self.assertTrue(im.getbbox());self.assertEqual(im.getpixel((0,0))[3],0)
   values.append(Path(self.m.icon(role)).read_bytes())
  self.assertEqual(len(values),len(set(values)))
 def test_seven_settings_and_every_nested_row_have_function_icons(self):
  from settings_sections45 import SECTIONS,ROWS,EXPERIMENTAL
  for _,key in SECTIONS:self.assertTrue(Path(self.m.icon('settings_section',{'section':key})).is_file())
  for rows in list(ROWS.values())+list(EXPERIMENTAL.values()):
   for _,action,params in rows:self.assertTrue(Path(self.m.icon(action,params)).is_file(),action)
 def test_function_mapping_matches_user_table_in_multiple_contexts(self):
  expected={'home_start':'tv','movies_home':'movie','series_home':'series','global_search':'search','favourites':'star','epg_sources':'database','refresh_epg':'refresh','portal_manager':'user','add_portal_from_settings':'plus','groups_manager':'list','ui_language':'globe','widget_setup':'grid','record_now':'record','download_folder':'drive','guide_backup44':'shield','xcmate_licenses':'document'}
  for action,role in expected.items():self.assertEqual(self.m.role(action),role)
  self.assertEqual(self.m.role('settings_section',{'section':'experimental'}),'flask-lock')
 def test_native_select_adds_glyphs_without_focus_entries_or_network(self):
  dialog=mock.Mock();dialog.select.return_value=1
  result=self.m.select(dialog,'Actions',['Hinzufügen','Bearbeiten','Zurück'])
  self.assertEqual(result,1);items=dialog.select.call_args.args[1];self.assertEqual(len(items),3)
  self.assertEqual([v.label for v in items],['Hinzufügen','Bearbeiten','Zurück']);self.assertTrue(all(v.art.get('icon') for v in items));self.assertTrue(dialog.select.call_args.kwargs['useDetails'])
  sys.modules['utils'].http_get.assert_not_called()
 def test_existing_listitem_and_real_media_poster_are_not_overwritten(self):
  li=sys.modules['xbmcgui'].ListItem('Real');li.setArt({'icon':'/real/image.png'})
  self.assertIs(self.m.entries([li])[0],li)
  self.assertEqual(self.m.for_url('plugin://plugin.video.xtreammate/?action=media_detail&kind=vod','/real/poster.png'),'/real/poster.png')
 def test_owned_xml_icons_preserve_every_control_id_navigation_and_hit_rectangle(self):
  for name in self.layout.FILES:
   tree=ET.parse(ADDON/'resources/skins/Default/720p'/name)
   def contract():return {n.get('id'):{k:n.findtext(k) for k in ('left','top','width','height','onleft','onright','onup','ondown')} for n in tree.iter('control') if n.get('id')}
   before=contract();self.layout.apply(tree,name);self.assertEqual(contract(),before,name)
   self.assertTrue(list(tree.iterfind('.//control[@xcmate-menu45="true"]')),name)
   self.assertFalse(any(n.get('id') for n in tree.iter('control') if n.get('xcmate-menu45')))
 def test_original_search_xml_and_app_icon_bytes_unchanged(self):
  import json
  baseline=json.loads((Path(__file__).parent/'fixtures/xcmate_02944_protection.json').read_text())['source_sha256']
  for path in ('icon.png','resources/skins/Default/720p/XCMateMedia.xml'):
   self.assertEqual(hashlib.sha256((ADDON/path).read_bytes()).hexdigest(),baseline['src/plugin.video.xtreammate/'+path])
 def test_media_detail_submenu_and_actions_expose_icons_without_new_focus_ids(self):
  w=self.media_window();w._details(w.rows[0]);self.settle(w)
  self.assertTrue(all(v.art.get('icon') for v in w.getControl(300).items));w._detail_menu_show()
  self.assertEqual(len(w.getControl(810).items),7);self.assertTrue(all(v.art.get('icon') for v in w.getControl(810).items));self.assertEqual(w.getFocusId(),810)
 def test_all_owned_native_select_calls_are_decorated_or_already_icon_listitems(self):
  exceptions={'menu_icons45.py','stream_details.py'}
  for p in LIB.glob('*.py'):
   if p.name in exceptions:continue
   for n in ast.walk(ast.parse(p.read_text())):
    if not isinstance(n,ast.Call) or not isinstance(n.func,ast.Attribute) or n.func.attr not in ('select','multiselect'):continue
    v=n.func.value
    own=isinstance(v,ast.Call) and isinstance(v.func,ast.Attribute) and v.func.attr=='Dialog' or isinstance(v,ast.Name) and v.id in ('d','dialog','dlg')
    self.assertFalse(own,(p.name,n.lineno))
