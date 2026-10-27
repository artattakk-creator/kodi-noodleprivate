"""Native left menu, explicit downloads and existing poster retry contracts."""
import importlib,os,sys,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture


class DetailMenuTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('download_sources','downloads','downloads_ui','download_store','capture_target','direct_ts'):
            sys.modules.pop(name,None)

    def detail(self,kind='vod'):
        w=self.media_window(kind);w._details(w.rows[0]);self.settle(w);return w

    def test_left_opens_native_panel_and_back_or_right_restores_same_detail_focus(self):
        for back in (92,2):
            w=self.detail();before=dict(w.selected);focus=w.getFocusId()
            w.native(1);self.assertTrue(w._detail_menu_open);self.assertEqual(w.getFocusId(),810)
            self.assertEqual(w._valid_focus(),[810]);self.assertEqual(w.getControl(810).size(),6)
            w.native(back);self.assertFalse(w._detail_menu_open);self.assertEqual(w.getFocusId(),focus)
            self.assertEqual(w.selected,before);self.assertEqual(w.mode,'detail');self.assertFalse(self.builtins)

    def test_navigation_and_cancel_cannot_enqueue_or_start_any_provider(self):
        w=self.detail();downloads=importlib.import_module('downloads')
        with mock.patch.object(downloads,'enqueue') as enqueue:
            w.native(1);w.native(4);w.native(3);self.dialog.yesno.return_value=False
            w.getControl(810).selectItem(0);w.native(7);self.settle(w)
            enqueue.assert_not_called()
        self.assertFalse(w._detail_menu_open);self.assertEqual(w.mode,'detail')

    def test_movie_download_is_deferred_to_worker_with_exact_current_identity(self):
        w=self.detail();self.dialog.yesno.return_value=True
        downloads=importlib.import_module('downloads')
        with mock.patch.object(downloads,'enqueue',return_value='own') as enqueue:
            w.native(1);w.native(7);enqueue.assert_not_called();self.settle(w)
        enqueue.assert_called_once();portal,kind,sid,series=enqueue.call_args.args
        self.assertEqual((portal['id'],kind,sid,series),('p','vod',w.selected['sid'],''))

    def test_series_download_selects_real_episode_without_altering_autoplay(self):
        w=self.detail('series');self.dialog.select.return_value=1;self.dialog.yesno.return_value=True
        expected=w.episodes[1];downloads=importlib.import_module('downloads')
        with mock.patch.object(downloads,'enqueue',return_value='own') as enqueue:
            w.native(1);w.native(7);self.settle(w)
        self.assertEqual(enqueue.call_args.args[1:],('episode',expected['sid'],w.selected['sid']))
        self.assertEqual(w.mode,'detail');self.assertFalse(self.builtins)

    def test_cancel_episode_picker_never_enqueues(self):
        w=self.detail('series');self.dialog.select.return_value=-1;self.dialog.yesno.return_value=True
        downloads=importlib.import_module('downloads')
        with mock.patch.object(downloads,'enqueue') as enqueue:
            w.native(1);w.native(7);self.settle(w);enqueue.assert_not_called()

    def test_poster_retry_uses_existing_single_poster_job_and_does_not_delete_cache(self):
        w=self.detail();art=importlib.import_module('media_art')
        with mock.patch.object(art,'retry_poster',return_value='PENDING') as retry:
            w.native(1);w.getControl(810).selectItem(2);w.native(7);retry.assert_not_called();self.settle(w)
        retry.assert_called_once_with(w.selected);self.assertFalse(w._detail_menu_open)

    def test_shared_folder_is_recordings_setting_even_when_old_download_setting_exists(self):
        self.options.update(recordings_folder=str(self.folder/'recorded'),downloads_folder='/ignored/old')
        with mock.patch.object(sys.modules['xbmcvfs'],'translatePath',side_effect=lambda p:p,create=True):
            self.assertEqual(importlib.import_module('downloads').folder(),self.options['recordings_folder'])

    def test_service_is_lazy_and_shutdown_rejects_new_workers(self):
        api=importlib.import_module('downloads')
        with mock.patch.object(api.threading,'Thread') as thread:api.poll();api.shutdown();api.poll();thread.assert_not_called()

    def test_partial_download_is_not_playable_and_management_can_pause_running_job(self):
        store=importlib.import_module('download_store');api=importlib.import_module('downloads')
        target=self.folder/'media';target.mkdir()
        ident=store.enqueue(dict(pid='p',kind='vod',sid='1',title='Film',target=str(target)))
        row=store.get(ident)
        with self.assertRaises(Exception):api.playable(row)
        self.dialog.select.side_effect=[0,0]
        with mock.patch('capture_ui.work',side_effect=lambda fn:fn()):importlib.import_module('downloads_ui').manage()
        self.assertEqual(store.get(ident)['state'],'PAUSED')


if __name__=='__main__':unittest.main()
