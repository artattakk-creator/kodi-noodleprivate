"""Actual 2.2.3 XML / 2.1.0 compiler, private preparation and reversible apply."""
import copy,hashlib,json,sys,types,unittest,xml.etree.ElementTree as E
from pathlib import Path
from unittest import mock
from xcmate050_fixture import Fixture50
from xcmate027_fixture import ROOT,ListItem

class Skin50(Fixture50,unittest.TestCase):
    def test_preparation_never_changes_installed_skin_and_tests_backup_restore_privately(self):
        before=self.skin_bytes();plan=self.skinmod.prepare(self.skin)
        self.assertEqual(self.skin_bytes(),before);self.assertEqual(len(plan['entries']),4)
        root=self.tx.folder()/plan['id']
        for i,name in enumerate(self.skinmod.FILES):self.assertEqual((root/('restore-check.'+str(i))).read_bytes(),before[name])
    def test_skin_apply_needs_explicit_approval_and_restores_all_four_originals(self):
        before=self.skin_bytes();plan=self.skinmod.prepare(self.skin)
        with self.assertRaises(PermissionError):self.skinmod.apply(plan['id'],self.skin)
        self.assertEqual(self.skin_bytes(),before)
        self.skinmod.apply(plan['id'],self.skin,confirmed=True);self.assertTrue(self.skinmod.applied(self.skin))
        self.skinmod.apply(plan['id'],self.skin,confirmed=True,restore=True);self.assertEqual(self.skin_bytes(),before)
    def test_failure_before_or_after_each_native_file_replace_rolls_back_without_loss(self):
        for fail in range(4):
            for after in (False,True):
                with self.subTest(fail=fail,after=after):
                    before=self.skin_bytes();plan=self.skinmod.prepare(self.skin);original=self.tx.replace;paths=[self.skin/n for n in self.skinmod.FILES];failed=[False]
                    def replace(path,data,expected,mode=0o600):
                        hit=Path(path)==paths[fail] and data!=before[self.skinmod.FILES[fail]] and not failed[0]
                        if hit:
                            failed[0]=True
                            if after:original(path,data,expected,mode)
                            raise OSError('synthetic interrupted write')
                        return original(path,data,expected,mode)
                    with mock.patch.object(self.tx,'replace',side_effect=replace),self.assertRaises(OSError):self.skinmod.apply(plan['id'],self.skin,confirmed=True)
                    self.assertTrue(failed[0]);self.assertEqual(self.skin_bytes(),before)
    def test_process_interruption_between_files_remains_explicitly_recoverable(self):
        class Crash(BaseException):pass
        for fail in range(4):
            before=self.skin_bytes();plan=self.skinmod.prepare(self.skin);original=self.tx.replace;target=self.skin/self.skinmod.FILES[fail]
            def replace(path,data,expected,mode=0o600):
                original(path,data,expected,mode)
                if Path(path)==target:raise Crash()
            with mock.patch.object(self.tx,'replace',side_effect=replace),self.assertRaises(Crash):self.skinmod.apply(plan['id'],self.skin,confirmed=True)
            self.skinmod.apply(plan['id'],self.skin,confirmed=True,restore=True);self.assertEqual(self.skin_bytes(),before)
    def test_foreign_skin_change_blocks_entire_apply_or_restore_without_overwrite(self):
        original=self.skin_bytes()
        for restore in (False,True):
            plan=self.skinmod.prepare(self.skin)
            if restore:self.skinmod.apply(plan['id'],self.skin,confirmed=True)
            target=self.skin/self.skinmod.FILES[2];target.write_bytes(target.read_bytes()+b'\n');changed=self.skin_bytes()
            with self.assertRaisesRegex(ValueError,'TARGET_CHANGED_NO_OVERWRITE'):self.skinmod.apply(plan['id'],self.skin,confirmed=True,restore=restore)
            self.assertEqual(self.skin_bytes(),changed)
            for name,raw in original.items():(self.skin/name).write_bytes(raw)
    def test_unknown_layout_or_skin_version_does_not_get_a_best_guess_patch(self):
        before=self.skin_bytes();p=self.skin/'shortcuts/template.xml';p.write_bytes(p.read_bytes()+b'\n')
        with self.assertRaisesRegex(ValueError,'UNVERIFIED_SKIN_FILE'):self.skinmod.prepare(self.skin)
        p.write_bytes(before['shortcuts/template.xml']);p=self.skin/'addon.xml';p.write_bytes(p.read_bytes().replace(b'2.2.3',b'2.2.4'))
        with self.assertRaisesRegex(ValueError,'UNVERIFIED_SKIN_VERSION'):self.skinmod.prepare(self.skin)
        self.assertEqual(self.skin_bytes(),before)
    def test_known_previous_programme_card_adapter_is_preserved_as_an_additive_variant(self):
        import widget_adapter46
        p=self.skin/'xml/IncludesHomeWidgets.xml';old,count=widget_adapter46.patch(p.read_bytes());self.assertEqual(count,12);p.write_bytes(old)
        plan=self.skinmod.prepare(self.skin);self.skinmod.apply(plan['id'],self.skin,confirmed=True)
        self.assertEqual(p.read_bytes().count(b'xcmate-programme46='),12)
        self.skinmod.apply(plan['id'],self.skin,confirmed=True,restore=True);self.assertEqual(p.read_bytes(),old)
    def test_original_native_widget_registry_exposes_three_direct_candidates_with_real_urls(self):
        self.skinmod.apply(self.skinmod.prepare(self.skin)['id'],self.skin,confirmed=True)
        module=self.native_reference();module.DATA=types.SimpleNamespace(_get_overrides_skin=lambda:E.parse(self.skin/'shortcuts/overrides.xml'),local=lambda v:[v,v,v])
        module.xbmc.getCondVisibility=lambda v:False;library=module.LibraryFunctions();library.dictionaryGroupings={'widgets-classic':[]}
        def create(values):
            item=ListItem(values[1]);item.setProperty('Path',values[0]);return item
        library._create=create;library.addToDictionary=lambda key,items:setattr(library,'items',items);library.widgets()
        items=[i for i in library.items if i.getProperty('widget').startswith('xcmate50.')]
        self.assertEqual(len(items),3)
        for i,kind in zip(items,('live','vod','series')):
            self.assertEqual(i.getProperty('widgetTarget'),'videos');self.assertIn('action='+self.binding.ROUTES[kind],i.getProperty('widgetPath'))
            self.assertNotIn('home_live',i.getProperty('widgetPath'));self.assertEqual(library.addWidgetReload(i.getProperty('widgetPath')),i.getProperty('widgetPath'))
    def test_original_native_template_compiler_keeps_media_parameters_and_registers_live_in_all_eight_slots(self):
        module=self.native_reference();compiler=module.Template()
        old=E.parse(self.skin/'shortcuts/template.xml').getroot().find('other/controls')
        patched=E.fromstring(self.skinmod.patch('shortcuts/template.xml',(self.skin/'shortcuts/template.xml').read_bytes())).find('other/controls')
        for live_position in range(1,9):
            props=dict(id='2',submenuid='10000',multiWidgets='true')
            for i in range(1,9):
                for name in ('widgetTarget','contentStyle','widgetPath','widgetName','widgetTags','widgetStyle','widgetSortBy','widgetSortOrder','widgetLimit','widgetInfoPanel','widgetFixedFocus'):
                    props[name+str(i)]=''
                props.update({k+str(i):v for k,v in dict(widgetPath=self.binding.source('live' if i==live_position else 'vod','p'),widgetStyle='poster',widgetFixedFocus='disabled',widgetLimit='25',widgetTarget='videos',contentStyle='normal').items()})
            a=copy.deepcopy(old);b=copy.deepcopy(patched)
            compiler.replaceElements(a,None,None,[],props);compiler.replaceElements(b,None,None,[],props)
            native_a=[n for n in a if n.tag=='include' and n.get('content')=='widget_base'];native_b=[n for n in b if n.tag=='include' and n.get('content')=='widget_base'];live=[n for n in b if n.tag=='include' and n.get('content')=='XCMate50.LiveRow']
            self.assertEqual(len(native_a),8);self.assertEqual(len(native_b),8);self.assertEqual(len(live),8)
            for original,kept in zip(native_a,native_b):
                self.assertEqual([E.tostring(p) for p in original],[E.tostring(p) for p in kept])
                self.assertIn(original.get('condition'),kept.get('condition'))
            chosen=live[live_position-1];self.assertIn('home50=1',chosen.find("param[@name='widgetPath']").get('value'))
            self.assertIn('String.StartsWith',chosen.get('condition'));self.assertIn('XCMate50.LiveRow',[n.get('content') for n in b])
    def test_home_hero_uses_native_focused_item_properties_above_small_logos_without_player_hooks(self):
        from widget_skin50 import reference
        data=(ROOT/'src/plugin.video.xtreammate/resources/bingie50/IncludesXCMate50.xml').read_bytes();root=E.fromstring(data)
        row=root.find("include[@name='XCMate50.LiveRow']/control");self.assertEqual(row.get('id'),'$PARAM[widgetid]')
        self.assertIsNone(row.find('content').get('limit'));self.assertEqual(row.findtext('orientation'),'horizontal')
        self.assertEqual(row.find('itemlayout').get('width'),'142')
        self.assertEqual(row.findtext('onback'),'900');self.assertNotIn('PlayerControl',data.decode());self.assertNotIn('RunPlugin',data.decode())
        image=root.find("include[@name='XCMate50.Hero']//control[texture='$INFO[ListItem.Property(XCMate.ProgrammeImage46)]']")
        self.assertIsNotNone(image);self.assertLess(int(image.findtext('top'))+int(image.findtext('height')),571)
        self.assertIn('XCMate.Home50',root.findtext("include[@name='XCMate50.Hero']/control/visible"))
    def test_no_skin_changes_are_applied_when_user_declines_reviewed_preview(self):
        import widget_manager50 as ui
        before=self.skin_bytes();self.dialog.yesno.return_value=False
        with mock.patch.object(ui,'runtime',return_value=(self.profile,self.skin)):ui.skin_setup()
        self.assertEqual(self.skin_bytes(),before);self.assertFalse(self.builtins)
        self.dialog.textviewer.assert_called_once();self.assertEqual(self.dialog.yesno.call_args.kwargs['defaultbutton'],10)
    def test_checked_reference_files_and_archive_have_explicit_provenance(self):
        proof=json.loads((ROOT/'tests/fixtures/bingie223_reference50.json').read_text())
        self.assertEqual(proof['version'],'2.2.3');self.assertEqual(proof['shortcuts_version'],'2.1.0')
        self.assertEqual(hashlib.sha256((ROOT/'tests/fixtures/bingie223_reference50.zip').read_bytes()).hexdigest(),proof['fixture_archive_sha256'])
        self.assertEqual(hashlib.sha256((ROOT/'tests/fixtures/skinshortcuts210_reference50.py').read_bytes()).hexdigest(),proof['method_excerpt_sha256'])
