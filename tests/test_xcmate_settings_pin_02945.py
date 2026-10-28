"""Seven categories, exact 6666 gate, safe deep links and unchanged setting IDs."""
import ast,importlib,json,sys,types,unittest,xml.etree.ElementTree as ET
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,LIB,ADDON

class SettingsPIN45(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.p=importlib.import_module('experimental45');self.s=importlib.import_module('settings_sections45')
  self.token=self.p._active.set(False);self.addCleanup(lambda:self.p._active.reset(self.token))
  self.dialog=types.SimpleNamespace(input=mock.Mock(return_value=''),notification=mock.Mock(),select=mock.Mock(return_value=-1))
  patch=mock.patch.object(sys.modules['xbmcgui'],'Dialog',return_value=self.dialog);patch.start();self.addCleanup(patch.stop)
 def test_seven_canonical_sections_exactly_match_native_categories(self):
  self.assertEqual([k for _,k in self.s.SECTIONS],['accounts','live','epg','media','appearance','system','experimental'])
  self.assertEqual([n.get('label') for n in ET.parse(ADDON/'resources/settings.xml').getroot()],[str(n) for n,_ in self.s.SECTIONS])
 def test_only_four_sixes_allow_entry_and_nested_calls_prompt_once(self):
  self.dialog.input.return_value='6666';calls=[]
  self.p.run(lambda:self.p.run(lambda:calls.append(self.p.active())))
  self.assertEqual(calls,[True]);self.assertFalse(self.p.active());self.dialog.input.assert_called_once()
 def test_three_wrong_pins_cancel_spaces_and_three_sixes_never_call_action(self):
  for value in ('1111','1234','666','', ' 6666','6666 ','６６６６'):
   self.dialog.input.return_value=value;action=mock.Mock();self.p.run(action);action.assert_not_called();self.assertFalse(self.p.active())
 def test_reentry_always_prompts_again_and_never_persists_pin(self):
  self.dialog.input.return_value='6666';self.p.run(lambda:None);self.p.run(lambda:None)
  self.assertEqual(self.dialog.input.call_count,2);self.assertFalse(self.p.active());self.assertEqual(self.options,{});self.assertFalse(self.properties)
 def test_exception_does_not_leave_an_unlocked_context(self):
  self.dialog.input.return_value='6666'
  with self.assertRaises(RuntimeError):self.p.run(lambda:(_ for _ in ()).throw(RuntimeError('synthetic')))
  self.assertFalse(self.p.active())
 def test_every_protected_direct_route_stops_before_portal_read(self):
  for action in sorted(self.p.ACTIONS):
   self.router._params=dict(action=action,pid='p');self.dialog.input.return_value='666'
   with mock.patch.object(self.routes,'portal_for',side_effect=AssertionError('read before PIN')):self.routes.dispatch(self.router)
   self.assertFalse(self.p.active())
 def test_legacy_router_guard_covers_clear_cache_and_old_diagnostics(self):
  tree=ast.parse((LIB/'main.py').read_text());cls=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Router');fn=next(n for n in cls.body if isinstance(n,ast.FunctionDef) and n.name=='dispatch')
  namespace={};exec(compile(ast.Module(body=[fn],type_ignores=[]),'legacy Router dispatch','exec'),namespace)
  for action in ('clear_cache','popup_probe','service_recover','remote_diagnostics','autoplay_diagnostic_mode'):
   router=types.SimpleNamespace(_params={'action':action},_handle=-1);router.dispatch=types.MethodType(namespace['dispatch'],router)
   self.dialog.input.return_value='';router.dispatch();self.assertFalse(self.p.active())
 def test_pin_is_not_bypassed_by_query_flags_or_experimental_native_group(self):
  for params in [dict(action='native_options45',group='experimental',pin='6666',unlocked='1'),dict(action='settings_section',section='experimental',authorized='true')]:
   self.assertTrue(self.p.protected(params));self.router._params=params
   with mock.patch.object(self.routes,'portal_for',side_effect=AssertionError('bypass')):self.routes.dispatch(self.router)
 def test_bookmarked_directory_is_released_before_pin_and_handle_restored(self):
  self.router._handle=17;self.dialog.input.side_effect=lambda **kw:'6666'
  def enter(*args,**kw):self.assertTrue(self.ends);self.assertEqual(self.router._handle,-1);return '6666'
  self.dialog.input.side_effect=enter;callback=mock.Mock(return_value='done')
  self.assertEqual(self.p.route(self.router,callback),'done');self.assertEqual(self.router._handle,17);self.assertFalse(self.p.active())
 def test_cancel_returns_without_container_update_or_data_files(self):
  before=set(self.folder.iterdir());self.p.route(self.router,mock.Mock());self.assertFalse(self.builtins);self.assertEqual(set(self.folder.iterdir()),before)
 def test_unreleased_actions_only_in_pin_submenus_and_aliases_are_safe(self):
  for name,rows in self.s.ROWS.items():
   self.assertFalse(any(action in self.p.ACTIONS for _,action,_ in rows),name)
  for alias in ('startup','groups','remote','player','storage','maintenance','about','designs'):self.assertIn(alias,self.s.ALIASES)
  all_actions={a for rows in self.s.EXPERIMENTAL.values() for _,a,_ in rows}
  self.assertTrue({'record_now','recordings_manage','download_folder','guide_timers','clear_cache','popup_probe','remote_diagnostics'}<=all_actions)
 def test_native_experimental_fields_are_hidden_and_open_action_is_gated(self):
  root=ET.parse(ADDON/'resources/settings.xml').getroot();cat=root[-1]
  self.assertEqual(cat.get('label'),'36006')
  for n in cat:
   if n.get('id')!='experimental_open45':self.assertEqual(n.get('visible'),'false')
  launch=cat.find("setting[@id='experimental_open45']");self.assertIn('section=experimental',launch.get('action'))
 def test_clear_or_global_retry_requires_separate_nondefault_confirmation(self):
  self.dialog.input.return_value='6666';self.dialog.select.return_value=0
  self.assertFalse(self.p.run(self.p.confirm));self.assertEqual(self.dialog.select.call_args.kwargs['preselect'],0)
  self.dialog.select.return_value=1;self.assertTrue(self.p.run(self.p.confirm));self.assertFalse(self.p.active())
 def test_existing_native_setting_ids_types_defaults_are_exact(self):
  expected=json.loads((Path(__file__).parent/'fixtures/xcmate_02945_settings_baseline.json').read_text())
  actual={n.get('id'):dict(n.attrib) for n in ET.fromstring(__import__('stabilization_contract_02953').without_stabilization53((ADDON/'resources/settings.xml').read_bytes(),'src/plugin.video.xtreammate/resources/settings.xml')).iter('setting')}
  self.assertTrue(set(expected)<=set(actual))
  for key,value in expected.items():
   for field in ('type','default','values','range','option','action'):
    self.assertEqual(actual[key].get(field),value.get(field),(key,field))
 def test_normal_settings_navigation_does_not_prompt_or_write_values(self):
  for section in ['']+[v for _,v in self.s.SECTIONS if v!='experimental']:
   self.added.clear();self.s.render(self.router,self.portal,section);self.assertTrue(self.added)
  self.dialog.input.assert_not_called();self.assertEqual(self.options,{})
 def test_direct_download_ui_and_recording_ui_are_gated_before_any_jobs(self):
  self.dialog.input.return_value=''
  for module,entry,args in [('downloads_ui','request',(types.SimpleNamespace(),)),('downloads_ui','manage',()),('capture_ui','start',(self.portal,)),('capture_ui','manage',())]:
   m=importlib.import_module(module)
   with mock.patch.object(m,'_'+entry+'45',side_effect=AssertionError('unguarded UI')):getattr(m,entry)(*args)
 def test_manual_timer_entry_does_not_create_database_without_pin(self):
  m=importlib.import_module('guide_timers')
  with mock.patch.object(m,'add',side_effect=AssertionError('ungated timer')):m.request_add45('p',{})
 def test_nested_native_option_action_uses_released_handle_and_restores_parameters(self):
  editor=importlib.import_module('settings_options45');before=dict(self.router._params);self.router._handle=17
  self.dialog.select.side_effect=[0,-1];observed=[]
  row=dict(id='synthetic_action',type='action',label='36017',action='RunPlugin(plugin://plugin.video.xtreammate/?action=guide_status&pid=p)')
  addon=sys.modules['xbmcaddon'].Addon();addon.getSetting=lambda key:self.options.get(key,'')
  with mock.patch.object(sys.modules['xbmcaddon'],'Addon',return_value=addon),mock.patch.object(editor,'definitions',return_value=[row]),mock.patch.object(self.router,'dispatch',create=True,side_effect=lambda:observed.append((self.router._handle,dict(self.router._params)))):
   editor.show(self.router,'epg')
  self.assertEqual(observed,[(-1,dict(action='guide_status',pid='p'))]);self.assertEqual(self.router._handle,17);self.assertEqual(self.router._params,before);self.assertFalse(self.options)
