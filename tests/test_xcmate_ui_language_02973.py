"""Real saved BINGIE properties, exact rollback and validated locale resources."""
import ast
import importlib
import sys
import time
import unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ADDON,ROOT
from xcmate050_fixture import Fixture50


class Widgets73(Fixture50,unittest.TestCase):
    def setUp(self):super().setUp();self.repair=importlib.import_module('widget_repair73')
    def test_only_own_reload_hook_added_with_backed_up_byte_exact_rollback(self):
        before=self.prop.read_bytes();plan=self.repair.prepare_hook(self.ctx(),'vod','p',0)
        self.assertEqual(self.prop.read_bytes(),before)
        with self.assertRaises(PermissionError):self.repair.apply_hook(plan['id'],self.profile,self.skin)
        self.repair.apply_hook(plan['id'],self.profile,self.skin,confirmed=True)
        rows=ast.literal_eval(self.prop.read_text())
        self.assertEqual([r for r in rows if r[:3]!=['mainmenu','10000','widgetPath']], [r for r in self.saved if r[:3]!=['mainmenu','10000','widgetPath']])
        value=next(r[3] for r in rows if r[:3]==['mainmenu','10000','widgetPath'])
        self.assertTrue(value.startswith(self.saved[4][3]));self.assertIn('XCMate.Widget45.Reload.vod',value)
        self.assertEqual(dict(self.native_properties())['widgetPath'],value)
        self.binding.apply(plan['id'],self.profile,self.skin,confirmed=True,restore=True)
        self.assertEqual(self.prop.read_bytes(),before)
    def test_foreign_slot_or_changed_profile_never_gets_modified(self):
        with self.assertRaises(ValueError):self.repair.prepare_hook(self.ctx(),'live','p',0)
        plan=self.repair.prepare_hook(self.ctx(),'vod','p',0);self.prop.write_bytes(self.prop.read_bytes()+b'\n')
        changed=self.prop.read_bytes()
        with self.assertRaises(ValueError):self.repair.apply_hook(plan['id'],self.profile,self.skin,confirmed=True)
        self.assertEqual(self.prop.read_bytes(),changed)
    def test_existing_link_diagnoses_stale_generated_home_and_only_rebuilds_after_consent(self):
        with mock.patch('widget_hooks45.probe',return_value=dict(bindings=[])):
            self.assertEqual(self.repair.diagnose(self.profile,self.skin,'vod','p'),'HOME_BUILD_STALE')
        manager=importlib.import_module('widget_manager50');before=self.prop.read_bytes()
        with mock.patch('widget_hooks45.probe',return_value=dict(bindings=[])),mock.patch.object(sys.modules['xbmcgui'],'Dialog',return_value=mock.Mock(yesno=lambda *a,**kw:False)),mock.patch.object(manager,'rebuild') as rebuild:
            self.repair.existing(self.profile,self.skin,'vod','p',0)
            rebuild.assert_not_called()
        self.assertEqual(self.prop.read_bytes(),before)
    def test_repair_never_creates_standalone_widget_or_changes_skin_files(self):
        before=self.skin_bytes();plan=self.repair.prepare_hook(self.ctx(),'series','p',1)
        self.repair.apply_hook(plan['id'],self.profile,self.skin,confirmed=True)
        self.assertEqual(self.skin_bytes(),before)
        self.assertEqual(len(ast.literal_eval(self.prop.read_text())),len(self.saved))


class Languages73(Fixture,unittest.TestCase):
    def setUp(self):super().setUp();self.l=importlib.import_module('localization')
    def test_17_bundled_locales_all_new_workflow_keys_and_placeholders_valid(self):
        locales=[k for k,_ in self.l.LANGUAGES if k!='kodi'];self.assertEqual(len(locales),17)
        base=self.l.english();critical={i for i in base if 38000<=i<38100}
        sys.path.insert(0,str(ROOT/'tools'))
        from validate_kodi_po import validate
        for locale in locales:
            with self.subTest(locale=locale):
                values=self.l.bundled(locale);self.assertTrue(critical<=values.keys())
                for key,value in values.items():self.assertEqual(self.l.fields(value),self.l.fields(base[key]),(locale,key))
                p=ADDON/'resources/language'/('resource.language.'+locale)/'strings.po'
                validate(p.read_text())
        self.assertIn('تحديث',self.l.bundled('ar_sa')[38000])
    def test_explicit_language_changes_only_own_setting_and_english_fallback_remains(self):
        self.options['xcmate_ui_language']='fr_fr'
        self.assertEqual(self.l.tr(32403),'Films')
        self.assertEqual(self.l.tr(32587),self.l.english()[32587])
        self.assertEqual(self.options,dict(xcmate_ui_language='fr_fr'))
        self.assertEqual(self.l.bundled('../../private'),{})
    def test_old_language_menu_indices_and_existing_choice_remain_compatible(self):
        self.assertEqual([k for k,_ in self.l.LANGUAGES[:3]],['de_de','en_gb','kodi'])
        self.options.update(xcmate_ui_language='de_de',lang_priority='de')
        with mock.patch('menu_icons45.select',return_value=2):self.l.choose_language()
        self.assertEqual(self.options,dict(xcmate_ui_language='kodi',lang_priority='de'))
    def test_country_names_use_selected_language_without_provider_changes(self):
        self.options['xcmate_ui_language']='fr_fr';epg=importlib.import_module('international_epg73')
        self.assertEqual(next(r['label'] for r in epg.countries() if r['code']=='DE'),'Allemagne')


class Progress73(Fixture,unittest.TestCase):
    def test_waiting_is_waiting_no_provider_requests_no_focus_or_notification_flood(self):
        self.setUpCalled=True
        p=importlib.import_module('catalog_progress73');p._snapshot=dict(id='a',state='WAITING',updated=1,group='Synthetic',processed=25,code='WRITER_BUSY');p._dialog=None;p._last=None
        bg=mock.Mock();dialog=mock.Mock()
        with mock.patch.object(sys.modules['xbmcgui'],'DialogProgressBG',return_value=bg,create=True),mock.patch.object(sys.modules['xbmcgui'],'Dialog',return_value=dialog):
            p.poll();p.poll()
            bg.create.assert_not_called();bg.update.assert_not_called()
            self.options['catalog_status81']=True;p.poll()
            self.assertIn('Wartet',sys.modules['xbmcgui'].Window(10000).getProperty('XCMate.Catalog81.Text'));dialog.notification.assert_not_called()
            self.assertFalse(self.builtins)
