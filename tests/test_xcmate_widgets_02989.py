import importlib,json,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
class Widgets89(Fixture,unittest.TestCase):
 def test_existing_global_hook_is_preserved_but_own_update_uses_private_hook(self):
  from widget_reload78 import candidate
  from widget_hooks45 import sources,isolated89
  foreign=b'<content>plugin://plugin.audio.example/?reload=$INFO[Window(Home).Property(widgetreload)]</content>'
  own=b'<content>plugin://plugin.video.xtreammate/?action=widget_recent_vod&amp;pid=p&amp;reload=$INFO[Window(Home).Property(widgetreload)]</content>'
  value=candidate(b'<includes>'+own+foreign+b'</includes>')
  self.assertIn(foreign,value);self.assertIn(b'reload=$INFO[Window(Home).Property(widgetreload)]',value)
  self.assertIn(b'xcmate_reload45=$INFO[Window(Home).Property(XCMate.Widget45.Reload.vod)]',value)
  self.assertEqual(isolated89(sources(value.decode())[0]['hooks']),['XCMate.Widget45.Reload.vod']);self.assertEqual(candidate(value),value)
 def test_foreign_saved_rows_are_traced_to_actual_native_ids_without_modification(self):
  from widget_audit89 import inventory
  profile=self.folder/'testprofile';skin=self.folder/'testskin';folder=profile/'addon_data/script.skinshortcuts';folder.mkdir(parents=True);(skin/'xml').mkdir(parents=True)
  rows=[['mainmenu','10000','widgetPath.12','plugin://plugin.audio.example/?foo=1'],['mainmenu','10000','widgetName.12','Personal audio']]
  prop=folder/'skin.titan.bingie.mod.properties';prop.write_text(repr(rows));before=prop.read_bytes()
  generated=skin/'xml/script-skinshortcuts-includes.xml';generated.write_text('<includes><include content="widget_base"><param name="widgetPath" value="plugin://plugin.audio.example/?foo=1"/><param name="widgetid" value="3580"/></include></includes>')
  value=inventory(profile,skin);self.assertEqual(len(value),1);self.assertEqual(value[0]['ids'],[3580]);self.assertTrue(value[0]['external']);self.assertEqual(value[0]['state'],'GENERATED_PRESENT');self.assertEqual(prop.read_bytes(),before)
  generated.write_text('<includes/>');self.assertEqual(inventory(profile,skin)[0]['state'],'SAVED_NOT_GENERATED');self.assertEqual(prop.read_bytes(),before)
 def test_unexposed_native_list_does_not_perform_24_invalid_index_calls(self):
  import time
  m=__import__('widget_patch85');runtime=__import__('widget_runtime79');profile=__import__('epg_handoff63').profile_scope()
  runtime._plans[('p','vod')]=dict(scope=profile,at=time.monotonic(),slot='source',ids=[1520])
  item=dict(label='Movie',url='plugin://plugin.video.xtreammate/?action=media_detail',props={'XCMate.Source85':'verified'},art={})
  record=dict(profile=profile,pid='p',kind='vod',signature='new',source='source',at=time.time(),items=[item])
  self.properties[m.slot('p','vod',profile)]=json.dumps(record);control=mock.Mock();control.size.return_value=0
  with mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=0),mock.patch('xbmc.getCondVisibility',return_value=False),mock.patch('home_runtime77.control',return_value=control),mock.patch('xbmc.getInfoLabel',return_value='1'),mock.patch('gui_guard86.note') as note:
   self.assertFalse(m.apply('p','vod','new'))
  control.getListItem.assert_not_called();note.assert_called_once();self.assertEqual(note.call_args.kwargs['count'],0)
