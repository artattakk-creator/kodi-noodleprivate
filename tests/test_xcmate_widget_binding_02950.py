"""Native saved profile readback, explicit approval and data-preserving rollback."""
import ast,json,os,stat,sys,unittest
from pathlib import Path
from unittest import mock
from xcmate050_fixture import Fixture50

class Binding50(Fixture50,unittest.TestCase):
    def test_three_choices_are_actions_not_group_folder_fallbacks(self):
        self.router._params['action']='widget_setup';self.routes.dispatch(self.router)
        self.assertEqual([i.label for _,i,_ in self.added],['Live-TV','Filme','Serien'])
        self.assertEqual(len(self.ends),1)
        for url,item,folder in self.added:
            self.assertFalse(folder);self.assertEqual(item.getProperty('IsPlayable'),'false')
            self.assertIn('action=widget_link50',url);self.assertIn('kind=',url)
        self.assertFalse(self.builtins)
    def test_new_slot_saves_and_fresh_original_native_reader_loads_exact_widget_binding(self):
        before=self.prop.read_bytes();plan=self.bind_plan();self.assertEqual(self.prop.read_bytes(),before)
        self.binding.apply(plan['id'],self.profile,self.skin,confirmed=True)
        values=dict(self.native_properties());self.assertEqual(values['widgetPath.2'],self.binding.source('live','p'))
        self.assertEqual(values['widgetTarget.2'],'videos');self.assertEqual(values['widgetName.2'],'Live-TV')
        self.assertEqual(values['widgetPath'],self.saved[4][3]);self.assertEqual(values['widgetPath.1'],self.saved[7][3])
        self.assertEqual(dict(self.native_properties())['widgetPath.2'],values['widgetPath.2'])
    def test_explicit_approval_is_required_and_prepare_only_creates_private_backups(self):
        before=self.prop.read_bytes();plan=self.bind_plan()
        with self.assertRaises(PermissionError):self.binding.apply(plan['id'],self.profile,self.skin)
        self.assertEqual(before,self.prop.read_bytes());root=self.tx.folder()/plan['id']
        self.assertEqual((root/'original.0').read_bytes(),before);self.assertEqual((root/'restore-check.0').read_bytes(),before)
        self.assertEqual(stat.S_IMODE((root/'original.0').stat().st_mode),0o600)
    def test_existing_movie_and_series_slots_cannot_be_replaced(self):
        before=self.prop.read_bytes()
        for kind,slot in [('live',0),('live',1),('series',0),('vod',1)]:
            with self.assertRaisesRegex(ValueError,'OCCUPIED_SLOT'):self.binding.candidate(self.ctx(),kind,'p',slot,'New')
        self.assertEqual(self.prop.read_bytes(),before)
    def test_existing_own_movie_and_series_keep_custom_names_and_reload_hooks(self):
        before=self.prop.read_bytes()
        for kind,slot in [('vod',0),('series',1)]:
            plan=self.bind_plan(kind,slot);self.assertEqual(plan['code'],'ALREADY_LINKED')
        self.assertEqual(self.prop.read_bytes(),before)
    def test_only_explicit_own_live_upgrade_is_allowed_and_custom_title_is_kept(self):
        rows=self.saved+[['mainmenu','10000','widgetPath.3','plugin://plugin.video.xtreammate/?action=widget_live_start_group&pid=p&reload=old'],['mainmenu','10000','widgetName.3','My television']]
        self.prop.write_text(repr(rows));plan=self.bind_plan('live',3)
        self.binding.apply(plan['id'],self.profile,self.skin,confirmed=True)
        values=dict(self.native_properties());self.assertIn('home50=1',values['widgetPath.3']);self.assertEqual(values['widgetName.3'],'My television')
        self.assertEqual(values['widgetPath'],self.saved[4][3]);self.assertEqual(values['widgetPath.1'],self.saved[7][3])
    def test_original_bytes_are_restored_exactly_after_verified_save(self):
        original=self.prop.read_bytes();plan=self.bind_plan();self.binding.apply(plan['id'],self.profile,self.skin,confirmed=True)
        self.binding.apply(plan['id'],self.profile,self.skin,confirmed=True,restore=True)
        self.assertEqual(self.prop.read_bytes(),original)
    def test_later_foreign_profile_change_is_never_overwritten_by_restore(self):
        plan=self.bind_plan();self.binding.apply(plan['id'],self.profile,self.skin,confirmed=True)
        self.prop.write_bytes(self.prop.read_bytes()+b'\n# later external editor\n');changed=self.prop.read_bytes()
        with self.assertRaisesRegex(ValueError,'TARGET_CHANGED_NO_OVERWRITE'):self.binding.apply(plan['id'],self.profile,self.skin,confirmed=True,restore=True)
        self.assertEqual(self.prop.read_bytes(),changed)
    def test_profile_race_between_preview_and_save_is_rejected(self):
        plan=self.bind_plan();self.prop.write_bytes(self.prop.read_bytes()+b'\n');changed=self.prop.read_bytes()
        with self.assertRaisesRegex(ValueError,'TARGET_CHANGED_NO_OVERWRITE'):self.binding.apply(plan['id'],self.profile,self.skin,confirmed=True)
        self.assertEqual(self.prop.read_bytes(),changed)
    def test_mainmenu_change_invalidates_the_profile_plan_before_any_write(self):
        plan=self.bind_plan();before=self.prop.read_bytes();self.menu.write_bytes(self.menu.read_bytes()+b'\n')
        with self.assertRaisesRegex(ValueError,'PROFILE_CHANGED'):self.binding.apply(plan['id'],self.profile,self.skin,confirmed=True)
        self.assertEqual(self.prop.read_bytes(),before)
    def test_tampered_original_or_candidate_is_rejected(self):
        for filename in ('original.0','candidate.0'):
            plan=self.bind_plan();before=self.prop.read_bytes();p=self.tx.folder()/plan['id']/filename;p.write_bytes(p.read_bytes()+b' ')
            with self.assertRaisesRegex(ValueError,'CANDIDATE_VERIFY_FAILED|BACKUP_VERIFY_FAILED'):self.binding.apply(plan['id'],self.profile,self.skin,confirmed=True)
            self.assertEqual(self.prop.read_bytes(),before)
    def test_saved_profile_is_required_and_skin_defaults_are_never_created_automatically(self):
        self.prop.unlink();before=self.menu.read_bytes()
        with self.assertRaisesRegex(ValueError,'NO_SAVED_BINGIE_PROFILE'):self.ctx()
        self.assertFalse(self.prop.exists());self.assertEqual(self.menu.read_bytes(),before)
    def test_unknown_home_id_duplicate_properties_and_code_in_properties_are_blocked(self):
        original=self.prop.read_bytes()
        for raw,code in [(repr(self.saved+[self.saved[0]]).encode(),'DUPLICATE_PROPERTIES'),(b"__import__('os').getcwd()",'INVALID_PROPERTIES'),(b' '*524289,'PROFILE_BUDGET')]:
            self.prop.write_bytes(raw)
            with self.assertRaisesRegex(ValueError,code):self.ctx()
        self.prop.write_bytes(original);self.menu.write_bytes(self.menu.read_bytes().replace(b'<label>10000</label>',b'<label>Renamed</label>'))
        with self.assertRaisesRegex(ValueError,'HOME_ID_UNVERIFIED'):self.ctx()
    def test_symlink_profile_target_and_unknown_skin_are_blocked(self):
        original=self.prop.read_bytes();self.prop.unlink();target=self.folder/'outside';target.write_bytes(original);self.prop.symlink_to(target)
        with self.assertRaisesRegex(ValueError,'UNSAFE_TARGET'):self.ctx()
        self.assertEqual(target.read_bytes(),original)
    def test_ui_cancel_does_not_write_binding_or_rebuild_home(self):
        import widget_manager50 as ui
        self.router._params.update(action='widget_link50',kind='vod');self.saved[4][3]='plugin://foreign.movies/';self.prop.write_text(repr(self.saved));before=self.prop.read_bytes()
        self.dialog.select.return_value=0;self.dialog.yesno.return_value=False
        with mock.patch.object(ui,'runtime',return_value=(self.profile,self.skin)):self.routes.dispatch(self.router)
        self.assertEqual(self.prop.read_bytes(),before);self.assertFalse(self.builtins)
        self.assertEqual(self.dialog.yesno.call_args.kwargs['defaultbutton'],10)
    def test_ui_confirmation_saves_only_one_slot_and_requests_the_original_native_builder(self):
        import widget_manager50 as ui
        self.router._params.update(action='widget_link50',kind='vod');self.saved[4][3]='plugin://foreign.movies/';self.prop.write_text(repr(self.saved));self.dialog.select.return_value=0;self.dialog.yesno.return_value=True
        with mock.patch.object(ui,'runtime',return_value=(self.profile,self.skin)):self.routes.dispatch(self.router)
        self.assertEqual(dict(self.native_properties())['widgetPath.2'],self.binding.source('vod','p'))
        self.assertEqual(self.builtins,['RunScript(script.skinshortcuts,type=buildxml&mainmenuID=900&group=mainmenu|powermenu)'])
        self.assertNotIn('PlayerControl',str(self.builtins));self.assertNotIn('Reset',str(self.builtins))
    def test_live_binding_without_active_approved_layout_is_not_silently_saved(self):
        import widget_manager50 as ui
        self.router._params.update(action='widget_link50',kind='live');before=self.prop.read_bytes();self.dialog.yesno.return_value=False
        with mock.patch.object(ui,'runtime',return_value=(self.profile,self.skin)):self.routes.dispatch(self.router)
        self.assertEqual(self.prop.read_bytes(),before);self.assertFalse(self.builtins)

    def test_single_widget_home_is_not_silently_changed_to_multiple_widgets(self):
        self.prop.write_text(repr(self.saved+[['mainmenu','10000','multiwidget','single']]))
        before=self.prop.read_bytes()
        with self.assertRaisesRegex(ValueError,'SINGLE_WIDGET_HOME'):self.ctx()
        self.assertEqual(self.prop.read_bytes(),before)
    def test_restore_cannot_write_a_profile_that_is_no_longer_active(self):
        import widget_manager50 as ui
        plan=self.bind_plan();self.binding.apply(plan['id'],self.profile,self.skin,confirmed=True)
        before=self.prop.read_bytes();self.dialog.select.return_value=0;self.dialog.yesno.return_value=True
        with mock.patch.object(ui,'runtime',side_effect=[(self.profile,self.skin),(self.folder/'other-profile',self.skin)]):ui.restore()
        self.assertEqual(self.prop.read_bytes(),before);self.assertFalse(self.builtins)
        self.assertIn('PROFILE_CHANGED',self.dialog.ok.call_args.args[1])
    def test_native_assistance_is_only_opened_after_explicit_confirmation(self):
        import widget_manager50 as ui
        before=self.prop.read_bytes();self.dialog.yesno.return_value=False
        ui.error(ValueError('NO_SAVED_BINGIE_PROFILE'));self.assertFalse(self.builtins)
        self.dialog.yesno.return_value=True
        with mock.patch.object(ui,'runtime',return_value=(self.profile,self.skin)):ui.error(ValueError('NO_SAVED_BINGIE_PROFILE'))
        self.assertEqual(self.builtins,['RunScript(script.skinshortcuts,type=manage&group=mainmenu)'])
        self.assertEqual(self.prop.read_bytes(),before)
    def test_native_runtime_guards_foreign_skin_player_and_busy_editor_before_writes(self):
        import widget_manager50 as ui,types
        xbmc=sys.modules['xbmc'];addon=sys.modules['xbmcaddon'];vfs=sys.modules['xbmcvfs']
        before=self.prop.read_bytes()
        def info(name=''):
            return types.SimpleNamespace(getAddonInfo=lambda key:('2.2.3' if name=='skin.titan.bingie.mod' else '2.1.0') if key=='version' else str(self.skin))
        for skinid,visible,code in [('skin.other','', 'UNSUPPORTED_SKIN'),('skin.titan.bingie.mod','Player.HasMedia','PLAYER_ACTIVE'),('skin.titan.bingie.mod','Window.IsVisible(script-skinshortcuts.xml)','NATIVE_EDITOR_BUSY')]:
            with mock.patch.object(xbmc,'getSkinDir',return_value=skinid,create=True),mock.patch.object(xbmc,'getCondVisibility',side_effect=lambda value:value==visible),mock.patch.object(addon,'Addon',side_effect=info):
                with self.assertRaisesRegex(ValueError,code):ui.runtime()
        self.assertEqual(self.prop.read_bytes(),before)

    def test_non_ascii_prefix_and_comments_preserve_exact_unrelated_native_values(self):
        rows=[['mainmenu','other','caption','ÄÖÜ 🛰️']]+self.saved
        self.prop.write_text('# existing comment\n'+repr(rows))
        plan=self.bind_plan();self.binding.apply(plan['id'],self.profile,self.skin,confirmed=True)
        self.assertTrue(self.prop.read_text().startswith('# existing comment\n'))
        self.assertEqual(ast.literal_eval(self.prop.read_text())[0],rows[0])
        self.assertEqual(dict(self.native_properties())['widgetPath.2'],self.binding.source('live','p'))

    def test_explicit_legacy_live_group_binding_can_be_replaced_but_no_other_account(self):
        for action in ('home_live','live_groups','widget_groups'):
            rows=self.saved+[['mainmenu','10000','widgetPath.3','plugin://plugin.video.xtreammate/?action='+action+'&pid=p']]
            self.prop.write_text(repr(rows));plan=self.bind_plan('live',3)
            self.assertEqual(plan['metadata']['state'],'UPGRADE_OWN_LIVE')
            self.binding.apply(plan['id'],self.profile,self.skin,confirmed=True)
            values=dict(self.native_properties());self.assertEqual(values['widgetPath.3'],self.binding.source('live','p'))
            self.assertEqual(values['widgetPath'],self.saved[4][3]);self.assertEqual(values['widgetPath.1'],self.saved[7][3])
        self.prop.write_text(repr(self.saved+[['mainmenu','10000','widgetPath.3','plugin://plugin.video.xtreammate/?action=home_live&pid=other']]))
        with self.assertRaisesRegex(ValueError,'OCCUPIED_SLOT'):self.bind_plan('live',3)
