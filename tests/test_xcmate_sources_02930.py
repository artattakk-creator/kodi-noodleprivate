"""Storage root list and exact backend/ENOSYS attribution; no hardware PASS."""
import importlib,json,os,sys,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture


class Sources30Tests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('storage_sources','storage_diagnostics','download_targets','download_target_ui'):sys.modules.pop(name,None)
        self.sources=importlib.import_module('storage_sources');self.diag=importlib.import_module('storage_diagnostics')
        self.dialog.browseSingle=mock.Mock(return_value='');self.logs=[]
        sys.modules['xbmc'].LOGINFO=1;sys.modules['xbmc'].log=lambda value,*a:self.logs.append(value)

    def test_first_dialog_lists_three_storage_classes_before_any_folder_browser(self):
        self.dialog.select.return_value=-1;before=dict(self.options)
        self.assertIsNone(self.sources.choose('DOWNLOAD'))
        self.assertEqual(len(self.dialog.select.call_args.args[1]),3);self.dialog.browseSingle.assert_not_called()
        self.assertEqual(self.options,before);self.assertIn('PICKER_ROOT_LISTED','\n'.join(self.logs))

    def test_existing_kodi_smb_source_is_used_as_root_without_internal_default(self):
        uri='smb://PRIVATE_SERVER/share/folder'
        sys.modules['xbmc'].executeJSONRPC=mock.Mock(return_value=json.dumps(dict(result=dict(sources=[dict(label='Private NAS',file=uri),dict(label='Plugin',file='plugin://unrelated/')]))))
        self.dialog.select.side_effect=[2,0];self.dialog.browseSingle.return_value=uri+'/selected'
        with mock.patch('capture_ui.work',side_effect=lambda fn:fn()):self.assertEqual(self.sources.choose(),uri+'/selected')
        self.assertEqual(self.dialog.browseSingle.call_args.kwargs['defaultt'],uri)
        for private in ('PRIVATE_SERVER','Private NAS',uri):self.assertNotIn(private,'\n'.join(self.logs))

    def test_usb_category_browses_selected_volume_and_cancellation_keeps_settings(self):
        self.dialog.select.side_effect=[1,0]
        with mock.patch.object(self.sources,'external_sources',return_value=[dict(path='/storage/ABCD',label='USB')]),mock.patch('capture_ui.work',side_effect=lambda fn:fn()):self.assertIsNone(self.sources.choose())
        self.assertEqual(self.dialog.browseSingle.call_args.kwargs['defaultt'],'/storage/ABCD')
        self.assertNotIn('downloads_folder',self.options)

    def test_record_route_does_not_call_download_backend_or_offer_internal_replacement(self):
        import home_menu
        uri='smb://PRIVATE_SERVER/share'
        self.options['recordings_folder']='/old/record'
        sys.modules['xbmcvfs'].translatePath=lambda value:value
        with mock.patch.object(self.sources,'choose',return_value=uri),mock.patch('capture_ui.work',side_effect=lambda fn:fn()),mock.patch('download_targets.assess',side_effect=AssertionError('recording is separate')):
            home_menu.recording_folder()
        self.assertEqual(self.options['recordings_folder'],'/old/record');self.dialog.yesno.assert_not_called()
        text='\n'.join(self.logs);self.assertIn('PICKER_ACTION=RECORD',text);self.assertIn('PROBE_BACKEND=NATIVE',text);self.assertNotIn('PRIVATE_SERVER',text)

    def test_internal_stage_can_use_exclusive_fsynced_parts_without_link_or_rename(self):
        import atomic_media
        targets=importlib.import_module('download_targets')
        with mock.patch.object(atomic_media,'probe',side_effect=atomic_media.StorageFailure('TARGET_ATOMIC_PUBLISH_UNAVAILABLE','LINK',38)),mock.patch.object(atomic_media.os,'link',side_effect=AssertionError('stage must not hardlink')):
            root=targets.stage_root()
        self.assertEqual(root,str(self.folder/'download_staging'))
        self.assertIn('INTERNAL_STAGE_EXCLUSIVE','\n'.join(self.logs));self.assertIn('errno=38','\n'.join(self.logs))
        self.assertEqual(list(Path(root).iterdir()),[])

    def test_stage_still_requires_real_file_fsync_and_preserves_error_phase(self):
        import atomic_media
        targets=importlib.import_module('download_targets')
        with mock.patch.object(atomic_media,'probe',side_effect=atomic_media.StorageFailure('TARGET_ATOMIC_PUBLISH_UNAVAILABLE','LINK',38)),mock.patch.object(targets.os,'fsync',side_effect=OSError(38,'PRIVATE')):
            with self.assertRaises(targets.Failure) as raised:targets.stage_root()
        self.assertEqual((raised.exception.code,raised.exception.step,raised.exception.number),('STAGING_UNAVAILABLE','INTERNAL_STAGE_FSYNC_FILE',38))
        self.assertNotIn('PRIVATE','\n'.join(self.logs))

    def test_diagnostics_reject_untrusted_strings(self):
        self.diag.mark('DOWNLOAD','FAILED','SMB','SMB2',type('Failure',(),dict(code='https://PRIVATE',step='/PRIVATE',number=38))())
        self.assertNotIn('PRIVATE','\n'.join(self.logs));self.assertIn('errno=38','\n'.join(self.logs))


if __name__=='__main__':unittest.main()
