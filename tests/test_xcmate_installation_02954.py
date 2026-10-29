"""Successful installed version and release changes; no first-run omissions."""
import hashlib,importlib,json,sys,types,unittest
from pathlib import Path
from unittest import mock
import xml.etree.ElementTree as E
import test_xcmate_update_notice_02941 as old
from xcmate027_fixture import ADDON

class Installation54(unittest.TestCase):
    def setUp(self):
        self.m=old.UpdateNotice41(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.m.current='0.1.29.54';self.m.options['xcmate_ui_language']='de_de';self.n=self.m.notice
    def test_fresh_54_install_shows_success_version_and_actual_changes(self):
        with mock.patch.object(self.n,'legacy',return_value=''):self.assertTrue(self.n.detect())
        self.assertTrue(self.n.show());heading,text=self.m.dialog.ok.call_args.args
        self.assertEqual(heading,'Installation erfolgreich')
        for word in ('Version 0.1.29.54','Änderungen:','Portal vor','EPG-Quellen','Passwörter','Hintergrund'):self.assertIn(word,text)
        self.assertNotIn('SECRET',text)
    def test_53_to_54_update_shows_same_success_and_does_not_repeat_after_restarts(self):
        self.m.baseline('0.1.29.53');self.assertTrue(self.n.detect());self.assertTrue(self.n.show())
        for _ in range(2):self.m.properties.clear();self.assertFalse(self.n.detect());self.assertFalse(self.n.show())
        self.m.dialog.ok.assert_called_once()
    def test_fresh_install_popup_waits_for_native_safe_state_without_touching_player(self):
        self.n.detect()
        with mock.patch.object(self.n,'safe',return_value=False):self.assertFalse(self.n.show())
        self.assertTrue(self.n.read()['pending']);self.m.dialog.ok.assert_not_called()
        self.assertTrue(self.n.show())
    def test_english_installation_success_and_password_limit_remain_explicit(self):
        self.m.options['xcmate_ui_language']='en_gb';self.n.detect();self.n.show()
        heading,text=self.m.dialog.ok.call_args.args;self.assertEqual(heading,'Installation successful')
        self.assertIn('unsaved password',text);self.assertIn('new Kodi/Python session',text)
    def test_addon_fanart_reuses_regular_lightweight_asset_and_original_icons(self):
        tree=E.parse(ADDON/'addon.xml');fanart=tree.findtext('.//assets/fanart');self.assertEqual(fanart,'resources/media/lightweight_splash.jpg')
        self.assertTrue((ADDON/fanart).is_file())
        base=json.loads((Path(__file__).parent/'fixtures/xcmate_02954_protection.json').read_text())['source_sha256']
        for name in ('icon.png','icon-81da1003a2753ec6.png','resources/media/lightweight_splash.jpg','fanart.jpg'):
            self.assertEqual(hashlib.sha256((ADDON/name).read_bytes()).hexdigest(),base['src/plugin.video.xtreammate/'+name])
    def test_unknown_saved_success_does_not_claim_empty_epg_was_verified(self):
        module=importlib.import_module('epg_report53');portal=dict(self.m.portal,provider_epg_enabled=True)
        row=dict(id='provider',key='provider',name='Provider',enabled=True,rank=0)
        with mock.patch.object(module,'configured',return_value=[row]),mock.patch.object(module,'history',return_value=[]),mock.patch.object(module,'statistics',return_value=dict(code='READY',sources=[],programmes=0)),mock.patch('epg_status.read',return_value={'provider':dict(code='READY')}):
            value=module.overview(portal)[0]
        self.assertEqual(value['code'],'NO_SAVED_PROGRAMMES');self.assertNotIn('Erfolgreich',module.meaning(value['code']))
    def test_long_running_wizard_keeps_actual_owner_instead_of_two_hour_expiry(self):
        nav=importlib.import_module('setup_navigation');self.m.properties[nav.ACTIVE]=str(__import__('time').time()-10800)
        with mock.patch('setup_liveness48.owner_alive',return_value=True):self.assertTrue(nav.active())
        with mock.patch('setup_liveness48.owner_alive',return_value=False):self.assertFalse(nav.active())
