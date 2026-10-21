"""Real bundled PO + strict native UI models, without Kodi language mutations."""
import ast
import hashlib
import importlib
import json
from pathlib import Path
import re
import sys
import tempfile
import unittest
from unittest import mock
import xml.etree.ElementTree as ET

from xcmate027_fixture import Fixture,ADDON,LIB,ROOT


class LocalizationTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.l10n=importlib.import_module('localization')
        self.home=importlib.import_module('home_menu')

    def labels(self): return [item.label for _,item,_ in self.added]

    def show_home(self):
        self.added.clear();self.home.show(self.router,self.portal)
        return self.labels()

    def test_english_and_german_have_exact_six_home_items(self):
        for locale,expected in (
            ('en_gb',['Start channel','Live TV','EPG','Movies','Series','Settings']),
            ('de_de',['Startkanal','Live-TV','EPG','Filme','Serien','Einstellungen'])):
            self.ui_locale=locale
            self.assertEqual(self.show_home(),expected)
            self.assertEqual(len({url for url,_,_ in self.added}),6)

    def test_ten_settings_categories_in_both_languages_with_identical_destinations(self):
        urls=[]
        for locale,first,last in (('en_gb','Accounts & portals','About XCMate & licences'),
                                  ('de_de','Accounts & Portale','Über XCMate & Lizenzen')):
            self.ui_locale=locale;self.added.clear();self.home.settings(self.router,self.portal)
            self.assertEqual(len(self.added),10)
            self.assertEqual((self.labels()[0],self.labels()[-1]),(first,last))
            urls.append([u for u,_,_ in self.added])
        self.assertEqual(*urls)

    def test_same_imported_home_module_does_not_cache_translated_menu_labels(self):
        self.assertEqual(self.show_home()[3],'Filme')
        self.ui_locale='en_gb';self.assertEqual(self.show_home()[3],'Movies')
        self.ui_locale='de_de';self.assertEqual(self.show_home()[3],'Filme')

    def test_german_upgrade_preserves_profile_language_filter_and_portal_data(self):
        # A German Kodi profile is an existing user choice. No migration or
        # writing a new English preference is allowed when opening these views.
        self.options.update(lang_priority='de',recordings_folder='existing-folder',recent_keep='72')
        before=json.dumps((self.options,self.portal,self.properties),sort_keys=True)
        self.assertEqual(self.show_home()[5],'Einstellungen')
        for section in ('accounts','startup','epg','groups','remote','player','storage','appearance','maintenance','about'):
            self.added.clear();self.home.settings(self.router,self.portal,section)
        self.assertEqual(json.dumps((self.options,self.portal,self.properties),sort_keys=True),before)
        self.assertEqual(self.builtins,[])

    def test_english_install_uses_english_ui_even_when_content_filter_is_german(self):
        self.ui_locale='en_gb';self.options['lang_priority']='de'
        self.assertEqual(self.show_home()[3:6],['Movies','Series','Settings'])
        self.assertEqual(self.options,{'lang_priority':'de'})
        self.assertEqual(ET.parse(ADDON/'addon.xml').findtext('.//defaultlanguage'),'resource.language.en_gb')

    def test_missing_one_german_translation_falls_back_only_that_message(self):
        self.translations['de_de'].pop(32403)
        self.assertEqual(self.show_home(),['Startkanal','Live-TV','EPG','Movies','Serien','Einstellungen'])
        self.assertEqual(self.ui_locale,'de_de');self.assertFalse(self.options)

    def test_unavailable_kodi_translation_uses_bundled_english_without_language_change(self):
        self.ui_locale='fr_fr'
        self.assertEqual(self.show_home()[3:6],['Movies','Series','Settings'])
        self.assertEqual(self.ui_locale,'fr_fr');self.assertFalse(self.options)

    def test_empty_translation_and_native_lookup_failure_have_english_fallback(self):
        self.translations['de_de'][32403]=''
        self.assertEqual(self.l10n.tr(32403),'Movies')
        addon=sys.modules['xbmcaddon']
        with mock.patch.object(addon,'Addon',side_effect=RuntimeError('language lookup unavailable')):
            self.assertEqual(self.l10n.tr(32403),'Movies')

    def test_invalid_placeholder_falls_back_before_real_resume_action_formats(self):
        self.translations['de_de'][32514]='Fortsetzen {unknown}'
        self.state.save_progress(dict(pid='p',kind='vod',sid='1'),1050,2700)
        w=self.media_window();w.native(7);self.settle(w)
        labels=dict((action,label) for label,action in w.actions)
        self.assertEqual(labels['resume'],'Resume from 00:17:30')
        self.assertEqual(labels['restart'],'Neu starten')

    def test_reordered_named_placeholders_work_and_format_spec_mismatch_falls_back(self):
        with mock.patch.object(self.l10n,'english',return_value={32990:'{name}: {count:02d}'}):
            self.translations['de_de'][32990]='{count:02d} · {name}'
            self.assertEqual(self.l10n.tr(32990,name='Titel',count=3),'03 · Titel')
            self.translations['de_de'][32990]='{name}: {count:04d}'
            self.assertEqual(self.l10n.tr(32990,name='Titel',count=3),'Titel: 03')

    def test_english_media_window_controls_actions_and_native_navigation(self):
        self.ui_locale='en_gb'
        w=self.media_window()
        self.assertEqual(w.getControl(400).label,'Search')
        self.assertIn('Back: one level',w.getControl(501).label)
        self.assertEqual(w.getControl(120).label,'Movies / Categories')
        w.native(3);w.native(7);self.settle(w);w.native(1);w.native(2)
        self.assertEqual((w.mode,w._cols),('grid',6))
        w.native(7);self.settle(w)
        self.assertIn(('Play','play'),w.actions)
        self.assertIn(('Add to favourites','favourite'),w.actions)
        self.assertIn('Rating',w.getControl(102).label)
        self.assertIn('Actual plot',w.getControl(320).text)
        self.assertNotIn('Anbieter',w.getControl(102).label)

    def test_english_series_actions_seasons_and_watched_labels(self):
        self.ui_locale='en_gb';w=self.media_window('series');w.native(7);self.settle(w)
        self.assertIn(('Seasons and episodes','seasons'),w.actions)
        w.getControl(300).selectItem(next(i for i,(_,key) in enumerate(w.actions) if key=='seasons'))
        w.native(7)
        self.assertEqual(w.getControl(330).items[0].label,'Season 1 · 0/2 · Unwatched')
        w.native(7)
        self.assertIn('Unwatched',w.getControl(330).items[0].label)
        self.assertEqual(self.builtins,[])

    def test_english_guide_day_buttons_empty_status_and_group_focus(self):
        self.ui_locale='en_gb';self.options['epg_days']=10
        w=self.guide_window()
        self.assertEqual(w.getControl(310).label,'Previous day')
        self.assertEqual(w.getControl(311).label,'Next day')
        self.assertEqual(w.getControl(312).label,'EPG status')
        self.assertIn('No real programme data',w.getControl(220).items[0].label)
        self.assertIn('Day 1/10',w.getControl(102).label)
        w.native(1);self.assertEqual(w.focus,200)
        w.native(2);self.assertEqual(w.focus,210)
        w.onClick(311);self.settle(w)
        self.assertIn('Day 2/10',w.getControl(102).label)
        sys.modules['utils'].http_get.assert_not_called()

    def test_search_and_widgets_are_english_without_translating_provider_titles(self):
        self.ui_locale='en_gb';self.router._params.update(action='global_search',q='house of dragon')
        self.routes.dispatch(self.router)
        self.assertEqual(self.labels(),['LIVE TV · 1 match','MOVIES · 100 matches','SERIES · 3 matches'])
        self.added.clear();self.router._params['action']='widget_recent_vod';self.routes.dispatch(self.router)
        self.assertIn('House of Dragon',self.added[0][1].label)
        self.assertIn('New ·',self.added[0][1].props['XCMate.AddedStatus'])
        self.assertIn('Show all',self.labels()[-1])
        self.added.clear();self.router._params['action']='widget_live_start_group'
        self.cache={'xml':[dict(name='Originaltitel',start_timestamp=self.now-100,stop_timestamp=self.now+100)]}
        self.routes.dispatch(self.router)
        self.assertIn('Now ',self.added[0][1].info['plot'])
        self.assertIn('Originaltitel',self.added[0][1].info['plot'])
        self.assertNotIn('Jetzt',self.added[0][1].info['plot'])
        self.assertIn('Now 12:00: Originaltitel',self.routes.guide_plot(dict(now='Originaltitel',now_time='12:00')))
        self.assertEqual(self.routes.guide_plot({}),'No EPG data currently available.')
        sys.modules['utils'].http_get.assert_not_called()

    def test_widget_setup_and_recording_diagnostics_are_english(self):
        self.ui_locale='en_gb'
        text=self.routes.widget_instructions(self.router,self.portal)
        self.assertIn('optional widget setup',text);self.assertIn('Latest movies',text)
        self.assertIn('pid=p',text);self.assertNotIn('SECRET',text)
        probe=importlib.import_module('recording_probe')
        with mock.patch.object(probe.shutil,'which',return_value=None): text=probe.report()
        self.assertIn('no executable candidate',text)
        self.assertIn('not yet implemented',text)

    def test_reminder_state_is_localized_for_display_but_durable_state_stays_canonical(self):
        timers=importlib.import_module('guide_timers')
        event=dict(start=self.now+600,stop=self.now+1200,title='Sendung unverändert')
        timers.add('p','1','Sender unverändert',event)
        for locale,label in (('en_gb','Pending'),('de_de','Ausstehend')):
            self.ui_locale=locale;timers.manage('p')
            displayed=self.dialog.select.call_args.args[1]
            self.assertIn(label,displayed[0]);self.assertIn('Sendung unverändert',displayed[0])
        self.assertEqual(timers.list_timers('p')[0]['state'],'pending')

    def test_fallback_catalog_is_loaded_once_not_on_each_remote_event(self):
        self.ui_locale='unavailable';self.l10n.english()
        with mock.patch('builtins.open',side_effect=AssertionError('catalog reread during navigation')):
            for _ in range(20): self.assertEqual(self.l10n.tr(32403),'Movies')

    def test_guide_reactivation_keeps_selected_date_channel_and_focus(self):
        self.ui_locale='en_gb';w=self.guide_window()
        w.onClick(311);self.settle(w);w.native(2)
        before=(w.day,w.sid,w.focus,w.getControl(101).label)
        w.onInit()  # WindowXML's real WINDOW_INIT on reactivation, not WindowDialog.
        self.assertEqual((w.day,w.sid,w.focus,w.getControl(101).label),before)


class CatalogContractTests(unittest.TestCase):
    def setUp(self):
        patch=mock.patch.object(sys,'path',[str(LIB)]+sys.path);patch.start();self.addCleanup(patch.stop)
        self.l10n=importlib.import_module('localization')
        self.catalogs={locale:self.l10n.read_catalog(ADDON/'resources/language'/('resource.language.'+locale)/'strings.po')
                       for locale in ('en_gb','de_de')}

    def test_old_026_po_bytes_and_existing_setting_definitions_are_preserved(self):
        frozen=json.loads((ROOT/'tests/fixtures/xcmate_026_languages.json').read_text())
        for locale,record in frozen['catalogs'].items():
            data=(ADDON/'resources/language'/('resource.language.'+locale)/'strings.po').read_bytes()
            self.assertEqual(hashlib.sha256(data[:record['bytes']]).hexdigest(),record['sha256'])
        settings={n.get('id'):dict(n.attrib) for n in ET.parse(ADDON/'resources/settings.xml').iter('setting')}
        for ident,attributes in frozen['settings'].items(): self.assertEqual(settings[ident],attributes,ident)

    def test_both_catalogs_have_every_new_id_and_matching_format_fields(self):
        en,de=self.catalogs['en_gb'],self.catalogs['de_de']
        self.assertEqual(set(en),set(de))
        self.assertTrue(set(range(32400,32607)).issubset(en))
        for ident in (i for i in en if i>=32400):
            self.assertTrue(en[ident].strip());self.assertTrue(de[ident].strip())
            self.assertEqual(self.l10n.fields(en[ident]),self.l10n.fields(de[ident]),ident)

    def test_all_new_python_string_references_exist_in_both_catalogs(self):
        used=set()
        for file in LIB.glob('*.py'):
            tree=ast.parse(file.read_text())
            for n in ast.walk(tree):
                if isinstance(n,ast.Call) and isinstance(n.func,ast.Name) and n.func.id=='tr':
                    if n.args and isinstance(n.args[0],ast.Constant) and isinstance(n.args[0].value,int):
                        used.add(n.args[0].value)
        self.assertGreater(len(used),170)
        for locale,entries in self.catalogs.items(): self.assertFalse(used-set(entries),locale)

    def test_new_python_ui_has_no_hardcoded_german_or_translated_route_keys(self):
        for name in ('home_menu','app_routes','media_window','guide_window','guide_store',
                     'guide_timers','media_data','media_progress','recording_probe'):
            for n in ast.walk(ast.parse((LIB/(name+'.py')).read_text())):
                if isinstance(n,ast.Constant) and isinstance(n.value,str):
                    self.assertIsNone(re.search(r'[äöüÄÖÜß]|\b(Startkanal|Filme|Serien|Gesehen|Begonnen|Ungesehen)\b',n.value),
                                      (name,n.lineno,n.value))

    def test_new_xml_labels_are_assigned_by_addon_localization_not_global_kodi_ids(self):
        for name in ('XCMateMedia.xml','XCMateGuide.xml'):
            root=ET.parse(ADDON/'resources/skins/Default/720p'/name)
            for label in root.iter('label'):
                self.assertTrue(not label.text or label.text.startswith('$INFO['),(name,label.text))
            self.assertIsNotNone(root.find('.//control[@id="501"]'))
        category=ET.parse(ADDON/'resources/settings.xml').find('.//category[@label="32592"]')
        self.assertIsNotNone(category)
        for control in category:
            self.assertIn(int(control.get('label')),self.catalogs['en_gb'])

    def test_duplicate_and_incomplete_po_entries_fail_validation(self):
        valid='msgctxt "#32400"\nmsgid "Start channel"\nmsgstr "Startkanal"\n'
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'strings.po'
            for data in (valid+'\n'+valid,'msgctxt "#32400"\nmsgid "Start"\n'):
                path.write_text(data)
                with self.assertRaises(ValueError): self.l10n.read_catalog(path)

    def test_multiline_po_keeps_quotes_newlines_and_unicode(self):
        with tempfile.TemporaryDirectory() as temp:
            path=Path(temp)/'strings.po'
            path.write_text('msgctxt "#32400"\nmsgid "Folder"\nmsgstr "Ordner \\\"A\\\"\\n"\n"Überblick"\n')
            self.assertEqual(self.l10n.read_catalog(path)[32400],'Ordner "A"\nÜberblick')
