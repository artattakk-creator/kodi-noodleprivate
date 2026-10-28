"""Actual native owner path: distinct auth, groups, catalog save and EPG."""
import importlib,sys,threading,types,unittest
from concurrent.futures import wait
from pathlib import Path
from unittest import mock
import test_xcmate_setup_0294 as old
from xcmate027_fixture import ADDON,Control

class Phases54(unittest.TestCase):
    def setUp(self):
        self.m=old.StorageTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.d=self.m.draft;self.d.phased54=True;self.ui=importlib.import_module('setup_window')
        p=mock.patch.object(Control,'setPercent',lambda c,v:setattr(c,'percent',v),create=True);p.start();self.addCleanup(p.stop)
    def window(self):
        w=self.ui.SetupWindow('XCMateSetup.xml',str(ADDON),'Default','720p');w.configure(self.d)
        self.addCleanup(w._pool.shutdown,wait=True,cancel_futures=True);self.addCleanup(w.close);w.show();return w
    def finish(self,w):
        self.assertTrue(wait([w._future],timeout=5).done);w.pump()
    def groups(self,w):self.finish(w);self.finish(w);self.assertEqual(w.stage,'groups')
    def test_real_auth_success_notification_precedes_automatic_categories(self):
        events=[];self.d.adapter.authenticate=lambda *a:events.append('auth') or True
        self.d.adapter.categories=lambda kind,remote:events.append(kind) or [dict(category_id=kind+'-1',category_name=kind+' group')]
        w=self.window();self.finish(w)
        self.assertIn('Verbindung erfolgreich. Zugangsdaten bestätigt.',str(self.m.dialog.notification.call_args))
        self.finish(w);self.assertEqual(events,['auth','live','vod','series']);self.assertEqual(w.stage,'groups')
        self.assertIsNone(w.result);self.assertFalse(self.d.saved)
    def test_auth_failure_keeps_all_inputs_and_exposes_edit_retry_later_password(self):
        self.d.adapter.authenticate=mock.Mock(side_effect=ValueError('authentication failed'))
        w=self.window();self.finish(w);self.assertEqual(w.stage,'failed')
        for cid in (16,17,18,19):self.assertTrue(w.getControl(cid).visible)
        self.assertEqual(w.getControl(19).label,'Passwort anzeigen/ausblenden');self.assertEqual(self.d.data['xc_pass'],'SECRET')
        self.assertNotIn('SECRET',w.getControl(3).text)
        self.d.adapter.authenticate=mock.Mock(return_value=True);w.onClick(17);self.groups(w);self.assertEqual(self.d.adapter.authenticate.call_count,1)
    def test_catalog_summary_save_publishes_before_optional_epg_and_epg_cancel_keeps_result(self):
        w=self.window();self.groups(w);self.d.provider_epg=True
        with mock.patch.object(self.d,'_scan_epg',side_effect=AssertionError('before publication')):
            w.onClick(17);self.finish(w)
        self.assertEqual(w.stage,'summary');self.assertFalse(self.d.saved)
        w.onClick(17);self.finish(w);self.assertEqual(w.stage,'epg_pending');self.assertTrue(self.d.saved)
        self.assertEqual(self.m.portals.get_by_id(w.result['id'])['id'],self.d.pid)
        import wizard_epg54
        entered=threading.Event();release=threading.Event()
        def epg(portal,cancel,status):entered.set();release.wait(3);raise InterruptedError('user cancel')
        with mock.patch.object(wizard_epg54,'run',side_effect=epg):
            w.onClick(17);self.assertTrue(entered.wait(2));future=w._future;w.onClick(18);release.set();wait([future],timeout=5)
        self.assertTrue(w._closed);self.assertEqual(w.result['id'],self.d.pid);self.assertIsNotNone(self.m.portals.get_by_id(self.d.pid))
    def test_successful_catalog_without_epg_goes_directly_to_usable_portal(self):
        w=self.window();self.groups(w);w.onClick(17);self.finish(w);w.onClick(17);self.finish(w)
        self.assertEqual(w.stage,'epg_ready');self.assertEqual(w.getControl(17).label,'Zu XCMate')
        w.onClick(17);self.assertTrue(w._closed);self.assertEqual(w.result['id'],self.d.pid)
    def test_active_twenty_minute_job_has_no_total_or_idle_auto_cancel_and_still_accepts_back(self):
        w=self.ui.WorkWindow('XCMateSetup.xml',str(ADDON),'Default','720p');w.configure_work();w._initialized=True;w.stage='discover'
        release=threading.Event();self.addCleanup(w._pool.shutdown,wait=True,cancel_futures=True);self.addCleanup(w.close)
        w.work(lambda:release.wait(3),lambda result:None)
        try:
            w._job_started-=1500;w._data_state.progress_at-=1500;w.pump()
            self.assertFalse(w._closed);self.assertIn('1500',w.getControl(20).label);self.assertFalse(w.cancel.is_set())
            w.onAction(types.SimpleNamespace(getId=lambda:92));self.assertTrue(w.cancel.is_set())
        finally:release.set()
    def test_discovery_request_limits_are_per_operation_with_no_aggregate_deadline(self):
        import wizard_deadline48 as budget
        class Job:
            @budget.discovery
            def discover(self,cancel,status):
                budget._local.deadline=0;budget.check();return budget.policy(30,60,3)
        self.assertEqual(Job().discover(),(15,60,1));self.assertFalse(budget.active())
    def test_new_ram_password_can_be_revealed_or_hidden_and_edited_after_failure(self):
        wizard=importlib.import_module('setup_wizard');self.m.dialog.input.return_value='changed synthetic';self.m.dialog.yesno.return_value=False
        self.d.data['_password_new54']=True
        result=wizard.input_data(self.m.dialog,3,dict(self.d.data,_edit53='xc_pass'))
        self.assertEqual(self.m.dialog.input.call_args.kwargs['defaultt'],'SECRET');self.assertEqual(self.m.dialog.input.call_args.kwargs['option'],0)
        self.assertEqual(result['xc_pass'],'changed synthetic')
    def test_saved_secret_is_never_revealed_as_keyboard_default_even_on_explicit_edit(self):
        wizard=importlib.import_module('setup_wizard');self.m.dialog.input.return_value='new synthetic';self.m.dialog.yesno.return_value=True
        result=wizard.input_data(self.m.dialog,3,dict(self.d.data,_edit53='xc_pass'))
        self.assertNotIn('defaultt',self.m.dialog.input.call_args.kwargs);self.assertEqual(result['xc_pass'],'new synthetic')
    def test_partial_auth_draft_password_remains_only_in_current_interpreter_ram(self):
        resume=importlib.import_module('wizard_resume53');memory=importlib.import_module('wizard_memory54');s=resume.Session();s.input(dict(self.d.data,_password_new54=True),'credentials');memory.remember(s)
        self.assertEqual(memory.current().data['xc_pass'],'SECRET');self.assertNotIn('SECRET',Path(resume.root(),'current.json').read_text())
        memory=importlib.reload(memory);self.assertIsNone(memory.current());cold=resume.Session.load();self.assertNotIn('xc_pass',cold.data)
    def test_group_count_tab_lines_list_and_progress_have_disjoint_rectangles(self):
        import xml.etree.ElementTree as E
        t=E.parse(ADDON/'resources/skins/Default/720p/XCMateSetup.xml')
        n=lambda cid:t.find("./controls/control[@id='%s']"%cid)
        count=n(5);top=int(count.findtext('top'));bottom=top+int(count.findtext('height'))
        for cid in (110,111,112):
            line=n(cid);self.assertLessEqual(int(line.findtext('top'))+int(line.findtext('height')),top)
        self.assertLessEqual(bottom,int(n(100).findtext('top')))
        self.assertEqual(n(3).findtext('font'),'font16')
    def test_pending_epg_wizard_reentry_uses_existing_portal_without_credentials_or_new_save(self):
        resume=importlib.import_module('wizard_resume53');s=resume.Session();s.state['choice']=3;s.live=self.d;self.d.resume53=s
        self.d.epg_sources=[dict(id='pending',uri='https://public.invalid/a.xml',name='Pending',enabled=True)]
        s.checkpoint(self.d,'groups',categories=True);self.d.scan();portal=self.d.save();s.checkpoint(self.d,'epg_pending');s.live=None
        self.m.dialog.select.return_value=0
        flow=importlib.import_module('wizard_flow53')
        with mock.patch('wizard_ui54.open_published',return_value=portal) as reopened:
            result=flow.run(self.m.dialog,mock.Mock(side_effect=AssertionError('no credentials')),mock.Mock(side_effect=AssertionError('no second portal')),RuntimeError)
        self.assertEqual(result['id'],portal['id']);reopened.assert_called_once_with(portal);self.assertEqual(len(self.m.portals.load_all()),2)
    def test_dns_tls_http_auth_and_socket_timeouts_are_distinguished_without_private_exception_text(self):
        import socket,ssl
        from urllib.error import URLError,HTTPError
        cases=[(URLError(socket.gaierror(-2,'private.example.invalid')),'XM-SETUP-DNS'),(URLError(ssl.SSLError('private.example.invalid')),'XM-SETUP-TLS'),(HTTPError('https://private.invalid/password',403,'SECRET',{},None),'XM-SETUP-AUTH'),(HTTPError('https://private.invalid/token',502,'SECRET',{},None),'XM-SETUP-HTTP'),(TimeoutError('SECRET'),'XM-SETUP-TIMEOUT')]
        for error,expected in cases:
            code,text=self.ui._failure_details(error);self.assertEqual(code,expected);self.assertNotIn('SECRET',text);self.assertNotIn('private',text)
