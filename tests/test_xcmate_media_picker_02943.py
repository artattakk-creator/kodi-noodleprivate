"""Owned dialog, explicit Save, cancellation, focus and identity boundaries."""
import importlib,threading,types,unittest
from concurrent.futures import Future
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ADDON
from test_xcmate_media_choices_02943 import image


class Picker43(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.mod=importlib.import_module('media_picker43')
        self.parent=self.media_window();self.parent._details(self.parent.rows[0]);self.settle(self.parent)
        self.p=self.mod.ArtworkPicker('XCMateArtwork43.xml',str(ADDON),'Default','720p');self.p.configure(self.parent)
        self.addCleanup(self.p.close)
        self.jobs=[]
        def submit(fn,apply):self.jobs.append((fn,apply))
        self.p._submit=submit
        with mock.patch.object(self.p,'_source'):self.p.show()
        self.candidate=dict(source='provider',url='',name='Choice',role='poster',attribution='Provider',metadata={'plot':'Chosen'})
        self.p._results([self.candidate])
    def drain(self):
        while self.jobs:
            fn,ready=self.jobs.pop(0);ready(fn())
    def test_cancel_preview_and_return_to_source_do_not_create_profile_or_change_parent(self):
        before=dict(self.parent.selected);self.p._preview(fetch=False)
        self.p.native(92);self.assertEqual(self.p.mode,'list');self.assertEqual(self.p.getFocusId(),200)
        self.p.close();self.assertFalse((self.folder/'media_choices43').exists());self.assertEqual(self.parent.selected,before)
    def test_image_requires_use_then_explicit_save_and_has_separate_metadata(self):
        self.p._preview(fetch=False);self.p.image=image()
        store=importlib.import_module('media_overrides43')
        with mock.patch.object(store,'save',return_value=True) as save:
            self.p.onClick(503);self.assertFalse(self.jobs)
            self.p.onClick(501);save.assert_not_called();self.assertEqual(self.p.getFocusId(),503)
            self.p.onClick(503);save.assert_not_called();self.drain()
            save.assert_called_once();self.assertNotIn('metadata',save.call_args.kwargs)
            self.assertEqual(save.call_args.args,('p','vod',self.p.sid));self.assertTrue(self.p.changed)
    def test_every_visible_button_is_remote_reachable_without_hidden_focus_targets(self):
        self.p._preview(fetch=False)
        for armed,metadata in ((False,False),(True,False),(True,True)):
            self.p.getControl(503).setVisible(armed);self.p.getControl(508).setVisible(metadata);self.p._navigation()
            self.p.setFocusId(501);seen=set()
            for _ in range(12):seen.add(self.p.getFocusId());self.p.native(4)
            expected={n for n in range(501,509) if self.p.getControl(n).visible}
            self.assertEqual(seen,expected)
        self.p.setFocusId(501);self.p.native(3);self.assertEqual(self.p.getFocusId(),401)
        self.p.native(2);self.assertEqual(self.p.getFocusId(),402)
    def test_role_change_disarms_save_without_writing_or_touching_metadata(self):
        self.p._preview(fetch=False);self.p.image=image();self.p.onClick(501)
        self.dialog.select.return_value=1;self.p.onClick(502)
        self.assertEqual(self.p.role,'fanart');self.assertFalse(self.p.armed);self.assertFalse(self.p.getControl(503).visible);self.assertFalse(self.jobs)
    def test_metadata_fields_are_selected_and_confirmed_separately_without_identity_change(self):
        self.p.selected=self.candidate;self.dialog.multiselect=mock.Mock(return_value=[0]);self.dialog.yesno.return_value=True
        store=importlib.import_module('media_overrides43')
        with mock.patch.object(store,'save',return_value=True) as save:
            self.p._metadata();self.assertFalse(self.p.changed);self.drain()
            self.assertEqual(save.call_args.kwargs['metadata'],{'plot':'Chosen'});self.assertNotIn('image',save.call_args.kwargs)
            self.assertEqual(self.parent.selected['sid'],self.p.sid)
    def test_actor_or_cancelled_metadata_never_auto_replace_work_metadata(self):
        self.p.selected=dict(self.candidate,media_type='person');self.p._metadata();self.assertFalse(self.jobs)
        self.p.selected=self.candidate;self.dialog.multiselect=mock.Mock(return_value=None);self.p._metadata();self.drain()
        self.assertFalse(self.p.changed);self.assertFalse((self.folder/'media_choices43').exists())
    def test_closed_owner_ignores_late_worker_result(self):
        future=Future();self.p._future=future;apply=mock.Mock();self.p._apply=apply
        future.set_running_or_notify_cancel();self.p.close();future.set_result(image());self.p.pump();apply.assert_not_called()
    def test_owner_guard_rejects_foreign_thread_gui_calls(self):
        errors=[]
        def work():
            try:self.p.pump()
            except RuntimeError as exc:errors.append(str(exc))
        thread=threading.Thread(target=work);thread.start();thread.join(2)
        self.assertEqual(errors,['CHOICE_OWNER_THREAD'])
    def test_request_is_deferred_and_does_not_open_in_callback(self):
        with mock.patch.object(self.mod,'ArtworkPicker') as window:
            self.mod.request(self.parent);window.assert_not_called()
        self.assertEqual(self.parent._picker_requested43,('p','vod',self.p.sid))
    def test_stale_portal_identity_and_foreign_dialog_never_open_picker(self):
        self.mod.request(self.parent);self.parent.portal=dict(self.parent.portal,id='other')
        with mock.patch.object(self.mod,'ArtworkPicker') as window:self.mod.open_pending(self.parent);window.assert_not_called()
        self.parent.portal['id']='p';self.mod.request(self.parent)
        with mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=10101),mock.patch.object(self.mod,'ArtworkPicker') as window:
            self.mod.open_pending(self.parent);window.assert_not_called()
    def test_failure_displays_fixed_code_and_keeps_sources_available(self):
        from media_sources43 import SourceError
        f=Future();f.set_exception(SourceError('HTTP_AUTH'));self.p._future=f;self.p._apply=mock.Mock();self.p.pump()
        self.assertIn('HTTP_AUTH',self.p.getControl(103).label);self.assertTrue(self.p.getControl(402).visible);self.assertFalse(self.p.changed)
    def test_local_import_validates_on_worker_preserves_original_and_requires_save(self):
        path=self.folder/'original.png';data=image();path.write_bytes(data)
        self.dialog.browseSingle=mock.Mock(return_value=str(path))
        with mock.patch('xbmcvfs.translatePath',side_effect=lambda p:p,create=True):self.p.onClick(404)
        self.assertIsNone(self.p.image);self.assertFalse((self.folder/'media_choices43').exists());self.drain()
        self.assertEqual(self.p.image,data);self.assertEqual(path.read_bytes(),data);self.assertFalse(self.p.changed)
    def test_provider_rating_text_is_converted_to_validated_numeric_field(self):
        from media_sources43 import provider
        values=provider(dict(self.parent.selected,rating='8.5',plot='Text'))
        self.assertEqual(values[0]['metadata']['rating'],8.5)
