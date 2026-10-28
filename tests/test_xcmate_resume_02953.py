"""Private nonsecret restart data, real staging/save and existing native GUI."""
import importlib,json,os,stat,sys,threading,time,types,unittest
from pathlib import Path
from unittest import mock
from concurrent.futures import wait
import test_xcmate_setup_0294 as storage
from xcmate027_fixture import ADDON,Control


class Resume53(unittest.TestCase):
    def setUp(self):
        self.m=storage.StorageTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.mod=importlib.import_module('wizard_resume53');self.s=self.mod.Session();self.s.state['choice']=3
        self.d=self.m.draft;self.d.resume53=self.s;self.s.live=self.d;self.s.authenticated53=True
        self.assertTrue(self.s.checkpoint(self.d,'groups',categories=True))
    def restored(self):
        s=self.mod.Session.load();self.assertIsNotNone(s)
        d=s.restore(dict(s.data,xc_pass='NEW_SYNTHETIC'));d.resume53=s
        return s,d
    def window(self):
        ui=importlib.import_module('setup_window')
        p=mock.patch.object(Control,'setPercent',lambda c,v:setattr(c,'percent',v),create=True);p.start();self.addCleanup(p.stop)
        w=ui.SetupWindow('XCMateSetup.xml',str(ADDON),'Default','720p');w.configure(self.d);w.show()
        self.addCleanup(w._pool.shutdown,wait=True,cancel_futures=True);self.addCleanup(w.close);return w
    def finish(self,w):
        self.assertTrue(wait([w._future],timeout=5).done);w.pump()
    def test_checkpoint_retains_nonsecret_data_and_groups_but_never_password(self):
        raw=Path(self.mod.root(),'current.json').read_text()
        self.assertNotIn('SECRET',raw);self.assertNotIn('xc_pass',raw)
        s=self.mod.Session.load();self.assertEqual(s.data['xc_host'],self.d.data['xc_host']);self.assertEqual(s.data['xc_user'],'user')
        self.assertEqual(s.state['selected']['series'],['series-1'])
    def test_private_modes_and_symlink_rejection(self):
        root=Path(self.mod.root());file=root/'current.json'
        self.assertEqual(stat.S_IMODE(root.stat().st_mode),0o700);self.assertEqual(stat.S_IMODE(file.stat().st_mode),0o600)
        file.unlink();outside=self.m.folder/'foreign.json';outside.write_text('protected');file.symlink_to(outside)
        self.assertFalse(self.s.persist());self.assertEqual(outside.read_text(),'protected');self.assertIsNone(self.mod.Session.load())
    def test_state_write_failure_keeps_ram_input_and_never_claims_restart_safety(self):
        with mock.patch.object(self.mod,'write_file',side_effect=OSError('synthetic denied')):
            self.assertFalse(self.s.input(dict(self.d.data,xc_user='changed'),'xc_user'))
        self.assertEqual(self.s.data['xc_user'],'changed');self.assertEqual(self.s.error,'DRAFT_STORAGE_UNAVAILABLE')
    def test_restore_keeps_original_staging_uuid_categories_and_selection(self):
        s,d=self.restored();self.assertEqual(d.pid,self.d.pid);self.assertEqual(d.folder,self.d.folder)
        self.assertEqual(d.selected,self.d.selected);self.assertEqual(d.categories,self.d.categories)
        self.assertEqual(d.data['xc_pass'],'NEW_SYNTHETIC');self.assertIsNone(self.m.portals.get_by_id(d.pid))
    def test_completed_scan_restores_summary_without_reimporting_staged_content(self):
        self.d.scan();self.s.checkpoint(self.d,'summary')
        s,d=self.restored();self.assertTrue(d.scanned);self.assertEqual(d.report['live'],2400)
        self.assertEqual(self.m.index.Reader(d.pid,d.index).page('series')[1],9)
        self.assertEqual(Path(self.m.portals._db_path()).read_bytes(),self.m.old)
    def test_corrupt_or_expired_staging_requires_scan_but_keeps_group_selection(self):
        self.d.scan();self.s.checkpoint(self.d,'summary');Path(self.d.index).write_bytes(b'corrupt')
        s,d=self.restored();self.assertFalse(d.scanned);self.assertEqual(d.selected['live'],{'live-1'})
        self.s.state['updated']=time.time()-2*86400;self.s.persist()
    def test_failed_save_keeps_scan_selection_and_can_be_retried(self):
        self.d.scan();self.s.checkpoint(self.d,'summary');original=self.d._copy
        with mock.patch.object(self.d,'_copy',side_effect=OSError('synthetic')):
            with self.assertRaises(OSError):self.d.save()
        self.s.checkpoint(self.d,'summary');s,d=self.restored()
        self.assertTrue(d.scanned);self.assertEqual(d.selected,self.d.selected)
        portal=d.save();self.assertEqual(self.m.index.Reader(portal['id']).page('live')[1],2400)
        self.assertEqual(self.m.portals.get_by_id('p'),self.m.portal)
    def test_back_from_groups_keeps_intent_and_staging_not_discarded(self):
        w=self.window();w.onAction(types.SimpleNamespace(getId=lambda:92))
        self.assertTrue(w._closed);self.assertEqual(self.s.action,'back');self.assertTrue(Path(self.d.folder).is_dir())
        self.assertEqual(self.mod.Session.load().state['selected']['vod'],['vod-1'])
    def test_native_toggle_persists_selected_group_without_losing_other_tabs(self):
        w=self.window();w.getControl(100).selectItem(1);w.onClick(100)
        self.assertEqual(self.mod.Session.load().state['selected']['live'],['live-1','live-2'])
        self.assertEqual(self.mod.Session.load().state['selected']['series'],['series-1'])
        self.assertEqual(w.getControl(100).getSelectedPosition(),1)
    def test_summary_back_and_forward_reuse_verified_scan(self):
        self.d.scan();self.s.checkpoint(self.d,'summary');w=self.window();self.assertEqual(w.stage,'summary')
        w.onClick(16);self.assertEqual(w.stage,'groups')
        with mock.patch.object(self.d,'scan',side_effect=AssertionError('must reuse current staged scan')):w.onClick(17)
        self.assertEqual(w.stage,'summary');self.assertFalse(w.busy)
    def test_discard_requires_explicit_confirmation(self):
        w=self.window();before=Path(self.mod.root(),'current.json').read_bytes()
        self.m.dialog.yesno.return_value=False;w.onClick(19);self.assertFalse(w._closed)
        self.assertEqual(Path(self.mod.root(),'current.json').read_bytes(),before)
        self.m.dialog.yesno.return_value=True;w.onClick(19);self.assertTrue(w._closed)
        self.assertIsNone(self.mod.Session.load());self.assertEqual(self.m.portals.load_all(),[self.m.portal])
    def test_scan_failure_keeps_groups_and_native_retry_back_later_controls(self):
        w=self.window();entries=self.d.adapter.entries
        self.d.adapter.entries=mock.Mock(side_effect=OSError('synthetic'))
        w.onClick(17);self.finish(w)
        self.assertEqual(w.stage,'groups');self.assertEqual(self.d.selected['series'],{'series-1'})
        for cid in (16,17,18,19):self.assertTrue(w.getControl(cid).visible)
        self.assertEqual(w.getControl(17).label,'Erneut versuchen')
        self.d.adapter.entries=entries;w.onClick(17);self.finish(w);self.assertEqual(w.stage,'summary')
    def test_url_password_not_in_nonsecret_json_and_plain_public_epg_url_retained(self):
        data=dict(self.d.data,m3u_url='https://source.invalid/get.php?username=u&password=SECRET&type=m3u',epg_url='https://public.invalid/guide.xml')
        self.s.input(data,'credentials');raw=Path(self.mod.root(),'current.json').read_text();self.assertNotIn('SECRET',raw)
        value=self.mod.Session.load().data;self.assertEqual(value['epg_url'],data['epg_url']);self.assertTrue(value['m3u_url_needs_input53'])
        self.assertIn('username=u',value['m3u_url_public53']);self.assertNotIn('password',value['m3u_url_public53'])
    def test_saved_portal_marks_resume_complete_and_preserves_old_portal(self):
        self.d.scan();self.d.save();self.d.dispose();self.assertIsNone(self.mod.Session.load())
        self.assertEqual(self.m.portals.get_by_id('p'),self.m.portal)
    def test_crash_after_publication_resume_returns_existing_id_without_second_save(self):
        self.d.scan();self.s.checkpoint(self.d,'summary');portal=self.d.save()
        flow=importlib.import_module('wizard_flow53');self.m.dialog.select.return_value=0
        opened=mock.Mock(side_effect=AssertionError('already published'))
        got=flow.run(self.m.dialog,mock.Mock(),opened,RuntimeError)
        self.assertEqual(got['id'],portal['id']);self.assertEqual(len(self.m.portals.load_all()),2)
    def test_foreign_staging_path_and_changed_provider_are_not_reused(self):
        self.s.state['folder']='../outside';self.s.persist();self.assertIsNone(self.mod.Session.load().folder())
        self.s.state['folder']=os.path.basename(self.d.folder);self.s.persist();s=self.mod.Session.load()
        d=s.restore(dict(s.data,xc_host='https://different.invalid',xc_pass='new'))
        self.assertNotEqual(d.pid,self.d.pid);self.assertFalse(d.scanned)
    def test_kodi_restart_input_asks_only_missing_password_not_host_user_or_name(self):
        self.s.input(self.d.data,'name');self.s.state['choice']=3;self.s.persist()
        wizard=importlib.import_module('setup_wizard');self.m.dialog.select.return_value=0
        self.m.dialog.input.side_effect=['NEW_SYNTHETIC'];self.m.dialog.yesno.return_value=False
        with mock.patch('setup_window.open_setup',return_value={'id':'new'}) as opened:self.assertEqual(wizard.setup(),{'id':'new'})
        self.assertEqual(self.m.dialog.input.call_count,1);self.assertEqual(opened.call_args.args[0]['xc_user'],'user')
        self.assertEqual(opened.call_args.args[0]['xc_pass'],'NEW_SYNTHETIC')
    def test_new_password_visible_by_default_and_optional_hidden_without_prefill(self):
        wizard=importlib.import_module('setup_wizard');gui=sys.modules['xbmcgui'];gui.ALPHANUM_HIDE_INPUT=2
        initial=dict(type='xtream',xc_host='https://synthetic.invalid',xc_user='user')
        for hidden,expected in ((False,0),(True,2)):
            self.m.dialog.yesno.return_value=hidden;self.m.dialog.input.reset_mock();self.m.dialog.input.side_effect=None;self.m.dialog.input.return_value='new-only'
            value=wizard.input_data(self.m.dialog,3,initial);self.assertEqual(value['xc_pass'],'new-only')
            self.assertEqual(self.m.dialog.input.call_args.kwargs,{'option':expected});self.assertNotIn('SECRET',str(self.m.dialog.input.call_args))
    def test_saved_password_never_opens_native_input_or_appears_in_summary(self):
        wizard=importlib.import_module('setup_wizard');self.m.dialog.input.reset_mock()
        result=wizard.input_data(self.m.dialog,3,self.d.data);self.m.dialog.input.assert_not_called();self.assertEqual(result['xc_pass'],'SECRET')
        self.d.scan();self.s.checkpoint(self.d,'summary');w=self.window()
        for control in w.controls.values():self.assertNotIn('SECRET',str(getattr(control,'text',''))+str(getattr(control,'label','')))
    def test_no_duplicate_wizard_while_previous_worker_lease_is_held(self):
        flow=importlib.import_module('wizard_flow53');release=importlib.import_module('wizard_session51').acquire()
        try:
            values=mock.Mock(side_effect=AssertionError('must not edit while old worker owns state'))
            self.assertIsNone(flow.run(self.m.dialog,values,mock.Mock(),RuntimeError));values.assert_not_called()
        finally:release()
    def test_first_input_cancel_retains_already_confirmed_origin(self):
        wizard=importlib.import_module('setup_wizard');self.m.dialog.input.side_effect=['https://new.invalid','']
        with self.assertRaises(wizard.Cancelled):wizard.input_data(self.m.dialog,3,checkpoint=self.s.input)
        self.assertEqual(self.mod.Session.load().data['xc_host'],'https://new.invalid')
    def test_cancel_during_worker_never_calls_native_controls_from_checkpoint_thread(self):
        self.s.authenticated53=False;ui=importlib.import_module('setup_window');entered=threading.Event();release=threading.Event()
        def auth(*a):entered.set();release.wait(3);return True
        self.d.adapter.authenticate=auth
        p=mock.patch.object(Control,'setPercent',lambda c,v:None,create=True);p.start();self.addCleanup(p.stop)
        w=ui.SetupWindow('XCMateSetup.xml',str(ADDON),'Default','720p');w.configure(self.d)
        w.show();self.assertTrue(entered.wait(2));future=w._future;w.onClick(18)
        release.set();self.assertTrue(wait([future],timeout=5).done);w._pool.shutdown(wait=True)
        self.assertTrue(w._closed);self.assertIsNone(w.result);self.assertIsNotNone(self.mod.Session.load())
        self.assertEqual(self.m.portals.load_all(),[self.m.portal])

    def test_corrupt_intent_is_not_silently_reset_without_confirmation(self):
        file=Path(self.mod.root(),'current.json');file.write_text('{broken');before=file.read_bytes()
        flow=importlib.import_module('wizard_flow53');self.m.dialog.select.return_value=0
        fields=mock.Mock(side_effect=AssertionError('corrupt intent must not be overwritten'))
        self.assertIsNone(flow.run(self.m.dialog,fields,mock.Mock(),RuntimeError))
        self.assertEqual(file.read_bytes(),before);fields.assert_not_called()

    def test_valid_old_scan_is_revalidated_after_24_hours_but_selection_remains(self):
        self.d.scan();self.s.checkpoint(self.d,'summary');file=Path(self.mod.root(),'current.json');value=json.loads(file.read_text())
        value['updated']=time.time()-2*86400;self.mod.write_file(str(file),value)
        s,d=self.restored();self.assertTrue(s.state['revalidate53']);self.assertFalse(d.scanned)
        self.assertEqual(d.selected['series'],{'series-1'})

    def test_abrupt_process_exit_after_checkpoint_survives_in_fresh_session(self):
        import subprocess
        code="import sys,types,os;sys.path.insert(0,sys.argv[1]);u=types.ModuleType('utils');u.addon_data_dir=lambda:sys.argv[2];sys.modules['utils']=u;from wizard_resume53 import Session;s=Session.load();s.state['selected']['series'].append('series-2');assert s.persist();os._exit(23)"
        result=subprocess.run([sys.executable,'-c',code,str(ADDON/'resources/lib'),str(self.m.folder)],capture_output=True,timeout=10)
        self.assertEqual(result.returncode,23);self.assertEqual(self.mod.Session.load().state['selected']['series'],['series-1','series-2'])

    def test_only_owned_private_staging_is_cleaned_after_explicit_discard(self):
        unrelated=self.m.folder/'xcmate-setup-unrelated';unrelated.mkdir();(unrelated/'keep').write_text('keep')
        self.s.state['staging53'].append(dict(folder=unrelated.name,pid='not-owned'))
        self.s.discard(confirmed=True);self.d.dispose()
        self.assertEqual((unrelated/'keep').read_text(),'keep');self.assertFalse(Path(self.d.folder).exists())

    def test_back_allows_correcting_password_without_showing_previous_value(self):
        wizard=importlib.import_module('setup_wizard');self.m.dialog.select.side_effect=[0,2]
        self.m.dialog.yesno.return_value=False;self.m.dialog.input.side_effect=['first-new','second-new']
        calls=[]
        def opened(data):
            calls.append(dict(data));s=self.mod.current()
            if len(calls)==1:s.action='back';return None
            return {'id':'new'}
        with mock.patch('setup_window.open_setup',side_effect=opened):self.assertEqual(wizard.setup(),{'id':'new'})
        self.assertEqual(calls[-1]['xc_pass'],'second-new')
        for call in self.m.dialog.input.call_args_list:self.assertNotIn('SECRET',str(call))
