"""Identical target capability checks precede UI acceptance and resolver IO."""
import importlib,os,sys,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture


class TargetTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('capture_target','direct_ts','capture_ui','capture_service','capture_store'):sys.modules.pop(name,None)
        self.target=importlib.import_module('capture_target')

    def test_real_target_roundtrips_link_and_leaves_existing_files_untouched(self):
        keep=self.folder/'existing.ts';keep.write_bytes(b'KEEP')
        result=self.target.probe(str(self.folder))
        self.assertGreater(result['free'],0);self.assertEqual(list(self.folder.glob('*.probe*')),[])
        self.assertEqual(keep.read_bytes(),b'KEEP')

    def test_hardlink_errno_and_operation_are_reported_without_private_path(self):
        with mock.patch('atomic_media._rename_noreplace',side_effect=OSError(95,'unsupported')),mock.patch.object(self.target.os,'link',side_effect=OSError(95,'secret/path')),mock.patch.object(self.target,'mark') as mark:
            with self.assertRaises(self.target.TargetFailure) as raised:self.target.probe(str(self.folder))
        self.assertEqual((raised.exception.code,raised.exception.step,raised.exception.number),('TARGET_ATOMIC_PUBLISH_UNAVAILABLE','LINK',95))
        self.assertNotIn('secret',str(mark.call_args_list));self.assertFalse(list(self.folder.glob('*.probe*')))

    def test_readonly_permission_and_reserve_fail_differently(self):
        for number,code in [(13,'TARGET_PERMISSION'),(30,'TARGET_READ_ONLY'),(28,'DISK_FULL')]:
            with mock.patch.object(self.target.os,'open',side_effect=OSError(number,'private')):
                with self.assertRaises(self.target.TargetFailure) as raised:self.target.probe(str(self.folder))
            self.assertEqual(raised.exception.code,code)
        with mock.patch.object(self.target.os,'fstatvfs',return_value=types.SimpleNamespace(f_bavail=1,f_frsize=4096)):
            with self.assertRaises(self.target.TargetFailure) as raised:self.target.probe(str(self.folder))
        self.assertEqual(raised.exception.code,'DISK_FULL')

    def test_symlink_and_nonlocal_targets_are_rejected(self):
        link=self.folder/'link';link.symlink_to(self.folder,target_is_directory=True)
        for path in (str(link),'smb://private/folder','relative'):
            with self.assertRaises(self.target.TargetFailure):self.target.probe(path)

    def test_service_never_resolves_provider_when_target_probe_fails(self):
        store=importlib.import_module('capture_store');service=importlib.import_module('capture_service')
        store.add(self.portal,dict(sid='1'),str(self.folder/'captures'),120)
        monitor=types.SimpleNamespace(abortRequested=lambda:False,waitForAbort=lambda n:True)
        with mock.patch('atomic_media._rename_noreplace',side_effect=OSError(95,'unsupported')),mock.patch.object(self.target.os,'link',side_effect=OSError(95,'private')),\
             mock.patch.object(service,'resolve') as resolve,\
             mock.patch.object(sys.modules['xbmc'],'Monitor',return_value=monitor):
            service._run()
        resolve.assert_not_called();row=store.rows()[0]
        self.assertEqual((row['status'],row['bytes'],row['code'].split('@')[0]),('failed',0,'TARGET_ATOMIC_PUBLISH_UNAVAILABLE'))

    def test_ui_rejects_bad_target_without_enqueuing_or_silent_setting_change(self):
        ui=importlib.import_module('capture_ui');store=importlib.import_module('capture_store')
        self.dialog.input.return_value='Channel';self.dialog.select.side_effect=[0,0]
        self.dialog.yesno.side_effect=[True,False]
        with mock.patch.object(ui,'work',side_effect=lambda fn:fn()),\
             mock.patch.object(self.target,'configured',return_value=str(self.folder)),\
             mock.patch.object(self.target,'probe',side_effect=self.target.TargetFailure('TARGET_ATOMIC_PUBLISH_UNAVAILABLE','LINK',95)),\
             mock.patch.object(self.target,'compatible_default',return_value=str(self.folder/'alternative')),\
             mock.patch.object(store,'add') as add:
            ui.start(self.portal)
        add.assert_not_called();self.assertNotIn('recordings_folder',self.options)

    def test_default_is_probed_persistent_directory_and_never_temporary_cache(self):
        target=self.target.compatible_default()
        self.assertEqual(target,str(self.folder/'recordings'));self.assertTrue(os.path.isdir(target))


if __name__=='__main__':unittest.main()
