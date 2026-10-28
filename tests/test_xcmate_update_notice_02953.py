"""Requested visible .53 release changes, accurate password promise and old gates."""
import importlib,unittest
from unittest import mock
import test_xcmate_update_notice_02941 as old


class Notice53(unittest.TestCase):
    def setUp(self):
        self.m=old.UpdateNotice41(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.m.options['xcmate_ui_language']='de_de'
        self.m.current='0.1.29.53';self.m.baseline('0.1.29.52');self.n=self.m.notice
    def test_real_upgrade_popup_shows_epg_wizard_and_password_changes(self):
        self.assertTrue(self.n.detect());self.assertTrue(self.n.show());text=self.m.dialog.ok.call_args.args[1]
        for phrase in ('0.1.29.53','EPG-Manager','Live-Vorschau','24 Stunden','Gruppen','Passwort','Kodi-Neustart'):self.assertIn(phrase,text)
        self.assertIn('erneut eingegeben',text);self.assertNotIn('SECRET',text)
    def test_ack_and_two_restarts_do_not_repeat_release_details(self):
        self.n.detect();self.n.show()
        for _ in range(2):self.m.properties.clear();self.n.detect();self.assertFalse(self.n.show())
        self.m.dialog.ok.assert_called_once()
    def test_english_translation_and_unknown_version_fallback_are_accurate(self):
        self.m.options['xcmate_ui_language']='en_gb';message=importlib.import_module('update_notes53').message
        self.assertIn('source comparison',message('0.1.29.53'));self.assertIn('unsaved password',message('0.1.29.53'))
        self.assertIn('0.1.29.54',message('0.1.29.54'));self.assertNotIn('source comparison',message('0.1.29.54'))
    def test_active_player_still_defers_popup_without_acknowledging(self):
        self.n.detect()
        with mock.patch('update_notice41.safe',return_value=False):self.assertFalse(self.n.show())
        self.assertTrue(self.n.read()['pending']);self.m.dialog.ok.assert_not_called()

    def test_future_installed_release_automatically_uses_its_local_changelog_only(self):
        module=importlib.import_module('update_notes53');file=self.m.folder/'changes.txt'
        file.write_text('0.1.29.55\n- Neue freigegebene Funktion\n\n0.1.29.53\n- Nicht als .55 ausgeben\n')
        with mock.patch.object(module,'changelog_path',return_value=file):text=module.message('0.1.29.55')
        self.assertIn('Neue freigegebene Funktion',text);self.assertNotIn('Nicht als .55',text)
