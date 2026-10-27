"""Explicit entry, refresh, shortcut, temporary pause and ownership contracts."""
import importlib,json,sys,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture

class Entry38(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.dialog.input.return_value='6666'  # Explicit .45 experimental authorization for legacy behavior tests.;self.entry=importlib.import_module('app_entry')
        previous=sys.modules['xbmc'].getCondVisibility
        sys.modules['xbmc'].getCondVisibility=lambda c:c=='Window.IsActive(videos)' or previous(c)
        self.portal['autoplay_start']=True;self.options['autoplay_diagnostics_safe']=True
        sys.modules['xbmc'].Player=lambda:types.SimpleNamespace(isPlayingVideo=lambda:False,isPlaying=lambda:False)

    def test_legacy_diagnostic_default_does_not_override_explicit_portal_choice(self):
        self.assertTrue(self.entry.enter(self.router,self.portal));self.assertEqual(len(self.builtins),1)
        self.assertIn('action=play_start_direct',self.builtins[0]);self.assertTrue(self.options['autoplay_diagnostics_safe'])

    def test_twenty_refreshes_and_more_than_old_cooldown_still_start_once(self):
        self.assertTrue(self.entry.enter(self.router,self.portal))
        for i in range(20):
            with mock.patch.object(self.entry.time,'time',return_value=1000000+i*60):self.assertFalse(self.entry.enter(self.router,self.portal))
        self.assertEqual(len(self.builtins),1)

    def test_compatible_home_and_app_open_shortcuts_share_intent(self):
        for action in ('xcmate_home','portal_home','app_open'):
            with self.subTest(action=action):
                self.properties.clear();self.builtins.clear();self.router._params={'action':action}
                self.assertTrue(self.entry.enter(self.router,self.portal));self.assertFalse(self.entry.enter(self.router,self.portal));self.assertEqual(len(self.builtins),1)

    def test_disabled_or_unconfigured_portal_does_not_start(self):
        for change in ({'autoplay_start':False},{'enabled':False},{'include_live':False},{'start_stream_id':''}):
            self.properties.clear();self.assertFalse(self.entry.enter(self.router,dict(self.portal,**change)))
        self.assertFalse(self.builtins)

    def test_foreign_player_never_replaced(self):
        sys.modules['xbmc'].Player=lambda:types.SimpleNamespace(isPlayingVideo=lambda:True,isPlaying=lambda:True)
        self.assertFalse(self.entry.enter(self.router,self.portal));self.assertFalse(self.builtins)

    def test_background_return_and_navigation_do_not_arm_autoplay(self):
        for params in ({'action':'global_search'},{'action':'xcmate_home','entry':'return'},{'action':'root','nav':'a'*32},{'action':'root','widget':'1'}):
            self.router._params=params;self.assertFalse(self.entry.enter(self.router,self.portal))
        self.assertFalse(self.builtins)

    def test_temporary_pause_expires_without_changing_saved_flags(self):
        self.properties[self.entry.PAUSE]=str(self.entry.time.time()+600)
        self.assertFalse(self.entry.enter(self.router,self.portal));self.assertTrue(self.entry.paused())
        self.properties.clear();self.properties[self.entry.PAUSE]='1'
        self.assertTrue(self.entry.enter(self.router,self.portal));self.assertTrue(self.portal['autoplay_start'])

    def test_replayed_queued_resolver_and_player_race_are_rejected(self):
        self.entry.enter(self.router,self.portal);value=self.entry.read();params=dict(pid='p',autoplay_entry=value['nonce'])
        self.assertTrue(self.entry.accept_play(params));self.assertFalse(self.entry.accept_play(params))
        self.properties.clear();self.entry.enter(self.router,self.portal);params['autoplay_entry']=self.entry.read()['nonce']
        sys.modules['xbmc'].Player=lambda:types.SimpleNamespace(isPlayingVideo=lambda:True,isPlaying=lambda:True)
        self.assertFalse(self.entry.accept_play(params))

    def test_observed_departure_rearms_next_explicit_open_not_background_service(self):
        self.entry.enter(self.router,self.portal)
        life=importlib.import_module('window_lifecycle')
        with mock.patch.object(life,'state',return_value=dict(modal=False)),mock.patch.object(life,'lease',return_value=''):
            with mock.patch.object(sys.modules['xbmc'],'getInfoLabel',return_value='plugin://plugin.video.xtreammate/?action=root'):self.entry.observe()
            with mock.patch.object(sys.modules['xbmc'],'getInfoLabel',return_value='videodb://movies/'):
                self.entry.observe();value=self.entry.read();value['outside']-=1;self.properties[self.entry.KEY]=json.dumps(value);self.entry.observe()
        self.assertIsNone(self.entry.read());self.assertEqual(len(self.builtins),1)
        self.assertTrue(self.entry.enter(self.router,self.portal));self.assertEqual(len(self.builtins),2)

    def test_diagnostic_directory_route_finishes_without_opening_root_or_player(self):
        self.router._params={'action':'autoplay_diagnostic_mode'}
        import importlib.util
        from xcmate027_fixture import ADDON
        spec=importlib.util.spec_from_file_location('main38_entry_test',ADDON/'resources/lib/main.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        router=module.Router(['plugin://plugin.video.xtreammate','7','?action=autoplay_diagnostic_mode'])
        with mock.patch.object(self.entry,'toggle_pause') as toggle:router.dispatch()
        toggle.assert_called_once();self.assertEqual(len(self.ends),1);self.assertFalse(self.added);self.assertFalse(self.builtins)

    def test_background_root_widget_does_not_consume_the_next_explicit_entry(self):
        with mock.patch.object(sys.modules['xbmc'],'getCondVisibility',return_value=False):
            self.assertFalse(self.entry.enter(self.router,self.portal));self.assertIsNone(self.entry.read())
        self.assertTrue(self.entry.enter(self.router,self.portal))

    def test_autoplay_ownership_and_preference_rechecked_after_resolver_work(self):
        self.entry.enter(self.router,self.portal);params=dict(pid='p',autoplay_entry=self.entry.read()['nonce'])
        self.assertTrue(self.entry.accept_play(params));self.assertTrue(self.entry.still_allowed(params))
        self.portal['autoplay_start']=False;self.assertFalse(self.entry.still_allowed(params))
        self.portal['autoplay_start']=True
        sys.modules['xbmc'].Player=lambda:types.SimpleNamespace(isPlayingVideo=lambda:True,isPlaying=lambda:True)
        self.assertFalse(self.entry.still_allowed(params))

    def test_legacy_setting_is_hidden_and_new_pause_is_a_visible_action(self):
        import xml.etree.ElementTree as ET
        from xcmate027_fixture import ADDON
        nodes={n.get('id'):n for n in ET.parse(ADDON/'resources/settings.xml').iter('setting')}
        self.assertEqual(nodes['autoplay_diagnostics_safe'].get('default'),'false');self.assertEqual(nodes['autoplay_diagnostics_safe'].get('visible'),'false')
        self.assertIn('action=autoplay_diagnostic_mode',nodes['autoplay_pause_action'].get('action'))
