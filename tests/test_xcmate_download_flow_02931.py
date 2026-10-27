"""Origin-specific confirmation/retry and actual tiny storage writes, no provider."""
import hashlib,importlib,json,os,subprocess,sys,unittest
from pathlib import Path
from unittest import mock
from test_xcmate_download_targets_02929 import TargetsFixture,SMB_FIXTURE


class DownloadFlow31Tests(TargetsFixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.dialog.input.return_value='6666'  # Explicit .45 experimental authorization for legacy behavior tests.
        for name in ('download_trust','download_trust_ui','download_target_test'):sys.modules.pop(name,None)
        self.trust=importlib.import_module('download_trust');self.ui=importlib.import_module('download_trust_ui')
        self.source='https://provider.invalid';self.cdn='https://cdn.invalid'
        self.work=mock.patch('capture_ui.work',side_effect=lambda fn:fn());self.work.start();self.addCleanup(self.work.stop)

    def denied(self,sid='one'):
        target=self.folder/'media';target.mkdir(exist_ok=True)
        ident=self.store.enqueue(self.make_media(str(target),sid));job=self.store.claim()
        self.assertEqual(job['id'],ident)
        self.trust.remember(ident,'p',self.source,self.cdn)
        self.store.finish(ident,job['owner'],'FAILED','REDIRECT_UNTRUSTED_TARGET')
        return self.store.get(ident)

    def test_unverified_default_choice_keeps_denial_and_never_starts_dns_or_retry(self):
        row=self.denied();self.dialog.select.return_value=0
        with mock.patch('download_redirect.addresses') as dns:self.assertFalse(self.ui.approve(row))
        dns.assert_not_called();self.assertEqual(self.trust.grants('p'),[])
        self.assertEqual(self.store.get(row['id'])['state'],'FAILED')

    def test_explicit_verified_origin_grant_and_second_retry_only_requeues_this_job(self):
        row=self.denied();other=self.denied('two');self.dialog.select.return_value=1;self.dialog.yesno.side_effect=[True,True]
        with mock.patch('download_redirect.addresses',return_value=['93.184.216.34']):self.assertTrue(self.ui.approve(row))
        self.assertEqual(self.store.get(row['id'])['state'],'QUEUED');self.assertEqual(self.store.get(other['id'])['state'],'FAILED')
        self.assertTrue(self.trust.allowed('p',self.source,self.cdn));self.assertFalse(self.trust.allowed('foreign',self.source,self.cdn))
        self.assertFalse(self.trust.allowed('p','https://other.invalid',self.cdn))

    def test_cancel_between_retry_review_and_queue_commit_wins(self):
        row=self.denied();self.dialog.select.return_value=1;self.dialog.yesno.side_effect=[True,True]
        original=self.store.get
        def cancelled(ident):
            value=original(ident);self.assertTrue(self.store.command(ident,'cancel'));return value
        with mock.patch('download_redirect.addresses',return_value=['93.184.216.34']),mock.patch.object(self.store,'get',side_effect=cancelled):
            self.assertTrue(self.ui.approve(row))
        self.assertEqual(self.store.get(row['id'])['state'],'CANCELLED')

    def test_changed_pending_target_during_confirmation_is_never_granted(self):
        row=self.denied();self.dialog.select.return_value=1
        def change(*args,**kwargs):self.trust.remember(row['id'],'p',self.source,'https://new.invalid');return True
        self.dialog.yesno.side_effect=change
        with mock.patch('download_redirect.addresses',return_value=['93.184.216.34']):self.assertFalse(self.ui.approve(row))
        self.assertEqual(self.trust.grants('p'),[]);self.assertEqual(self.store.get(row['id'])['state'],'FAILED')

    def test_loopback_stays_blocked_even_after_explicit_lan_confirmation(self):
        row=self.denied();self.dialog.select.return_value=1;self.dialog.yesno.return_value=True
        failure=importlib.import_module('download_sources').DownloadFailure('REDIRECT_PRIVATE_ADDRESS')
        with mock.patch('download_redirect.addresses',side_effect=failure):
            with self.assertRaisesRegex(Exception,'REDIRECT_PRIVATE_ADDRESS'):self.ui.approve(row)
        self.assertEqual(self.trust.grants('p'),[])

    def test_revoke_removes_only_selected_portal_connection(self):
        self.trust.grant(dict(pid='p',source=self.source,target=self.cdn))
        self.trust.grant(dict(pid='other',source=self.source,target=self.cdn))
        self.dialog.select.return_value=0;self.dialog.yesno.return_value=True;self.ui.manage('p')
        self.assertFalse(self.trust.allowed('p',self.source,self.cdn));self.assertTrue(self.trust.allowed('other',self.source,self.cdn))

    def test_failed_redirect_job_shows_review_action_before_blind_retry(self):
        self.denied();self.dialog.select.side_effect=[0,-1]
        importlib.import_module('downloads_ui').manage()
        options=self.dialog.select.call_args_list[-1].args[1]
        tr=importlib.import_module('localization').tr
        self.assertEqual(options[0].getLabel(),tr(34600));self.assertEqual(options[1].getLabel(),tr(34215))
        self.assertIn(tr(35000),self.dialog.select.call_args_list[0].args[1][0].getLabel())

    def test_tiny_local_target_proves_actual_bytes_and_hash_and_preserves_existing_files(self):
        root=self.folder/'target';root.mkdir();foreign=root/'keep.mp4';foreign.write_bytes(b'KEEP')
        probe=importlib.import_module('download_target_test')
        with mock.patch('download_sources.resolve',side_effect=AssertionError('no provider')):result=probe.run(str(root))
        self.assertEqual(result['sha256'],hashlib.sha256(probe.PAYLOAD).hexdigest());self.assertTrue(result['removed'])
        self.assertEqual(list(root.iterdir()),[foreign]);self.assertEqual(foreign.read_bytes(),b'KEEP')

    def test_source_redirect_denial_is_not_logged_as_target_copy_failure(self):
        import types
        row_target=self.folder/'target';row_target.mkdir()
        ident=self.store.enqueue(self.make_media(str(row_target)))
        logger=mock.Mock();sys.modules['xbmc'].log=logger;sys.modules['xbmc'].LOGINFO=1
        failure=importlib.import_module('download_sources').DownloadFailure('REDIRECT_UNTRUSTED_TARGET')
        self.worker.run_one(resolver=lambda media:('https://fixture.invalid/file.mp4',{}),opener=mock.Mock(side_effect=failure))
        self.assertEqual(self.store.get(ident)['state'],'FAILED')
        text='\n'.join(str(call.args[0]) for call in logger.call_args_list)
        self.assertIn('SOURCE_REDIRECT_DENIED',text);self.assertNotIn('TARGET_COPY_FAILED',text)
        self.assertNotIn('fixture.invalid',text);self.assertIn('bytes=0',text)

    def test_cancelled_target_test_never_writes(self):
        probe=importlib.import_module('download_target_test');self.dialog.yesno.return_value=False
        with mock.patch.object(probe,'run') as run:probe.show()
        run.assert_not_called()

    def test_target_inode_replacement_is_not_deleted(self):
        root=self.folder/'target';root.mkdir();probe=importlib.import_module('download_target_test');original=os.stat
        def replaced(path,*args,**kwargs):
            value=original(path,*args,**kwargs)
            if '.xcmate-target-test-' in str(path):
                import types
                return types.SimpleNamespace(st_dev=value.st_dev,st_ino=value.st_ino+1)
            return value
        with mock.patch.object(probe.os,'stat',side_effect=replaced):
            with self.assertRaisesRegex(Exception,'TARGET_CHANGED'):probe.run(str(root))
        self.assertEqual(len(list(root.iterdir())),1)


@unittest.skipUnless(SMB_FIXTURE,'host impacket unavailable')
class TargetWire31Tests(TargetsFixture,unittest.TestCase):
    def test_selected_signed_smb_target_really_receives_and_reads_tiny_file(self):
        share=self.folder/'share';share.mkdir();foreign=share/'keep.mp4';foreign.write_bytes(b'KEEP')
        helper=Path(__file__).parent/'fixtures/smb29_server.py'
        server=subprocess.Popen([sys.executable,str(helper),str(share)],stdout=subprocess.PIPE,stderr=subprocess.DEVNULL,text=True)
        def cleanup():server.terminate();server.wait(timeout=5);server.stdout.close()
        self.addCleanup(cleanup);port=json.loads(server.stdout.readline())['port'];uri='smb://127.0.0.1:'+str(port)+'/MEDIA'
        smb=importlib.import_module('download_smb');smb.credentials(uri,('fixture','fixture-password',''));self.targets.approved(uri,save=True)
        probe=importlib.import_module('download_target_test');result=probe.run(uri)
        self.assertEqual(result['backend'],'SMB2_STAGE_VERIFY');self.assertEqual(result['bytes'],len(probe.PAYLOAD))
        self.assertEqual(list(share.iterdir()),[foreign]);self.assertEqual(foreign.read_bytes(),b'KEEP')


if __name__=='__main__':unittest.main()
