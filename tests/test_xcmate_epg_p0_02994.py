"""Real profile/SQLite regressions; never Android acceptance."""
import ast,importlib,sys,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from xcmate027_fixture import Fixture,LIB


class EPG94(Fixture,unittest.TestCase):
 def real_sources(self):
  sys.modules.pop('epg_status',None)
  sys.modules.pop('epg_sources',None)
  return importlib.import_module('epg_sources')
 def test_new_xtream_defaults_to_actual_provider_xmltv_without_external_choice(self):
  self.client.get_xmltv_epg_url=lambda:'https://provider.invalid/xmltv.php'
  draft=importlib.import_module('setup_draft').Draft(self.portal)
  self.addCleanup(draft.dispose)
  self.assertTrue(draft.provider_epg)
 def test_adding_dach_enables_only_known_implicit_global_disable(self):
  self.portal.update(epg_show=False,epg_opt_out94=False)
  import portals
  with mock.patch.object(portals,'update',side_effect=lambda pid,v:self.portal.update(v) or True):
   sources=self.real_sources();sources.add_presets('p',['de_master','de_epgshare','at_epgshare','ch_epgshare'])
  self.assertTrue(self.portal['epg_show'])
  self.assertEqual(len(sources.configuration('p')['sources']),4)
  self.assertEqual(sources.add_presets('p',['de_master']),[])
 def test_adding_source_never_silently_overrides_explicit_optout(self):
  self.portal.update(epg_show=False,epg_opt_out94=True)
  sources=self.real_sources();sources.add_presets('p',['de_master'])
  self.assertFalse(self.portal['epg_show'])
 def test_full_index_missing_selected_group_also_requests_targeted_rows(self):
  tree=ast.parse((LIB/'live_overlay.py').read_text())
  cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='LiveNavigator')
  node=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='_list_content')
  ns={'CHANNEL_PAGE_SIZE':100};exec(compile(ast.Module(body=[node],type_ignores=[]),'real-list-content','exec'),ns)
  channels=[SimpleNamespace(name='Unterhaltung '+str(i),extra={'stream_id':str(i)}) for i in range(137)]
  nav=SimpleNamespace(mode='channels',category_id='b',enabled={'a','b'},index=SimpleNamespace(selection=lambda *a:([],{})),_catalog_partial46=False,_catalog_ready=True,_highlight={'channels':0},_scroll_to_current=False)
  with mock.patch('live_group93.rows',return_value=channels) as read:
   labels=ns['_list_content'](nav)
  self.assertEqual(len(nav.visible_channels),137);self.assertEqual(len(labels),100);read.assert_called_once()
