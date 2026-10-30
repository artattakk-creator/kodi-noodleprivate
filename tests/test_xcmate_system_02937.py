"""Read-only diagnostics, wizard handoff and installed Home route models."""
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import time
import types
import unittest
from unittest import mock
from xcmate027_fixture import Fixture,ADDON


class System37(Fixture,unittest.TestCase):
    def test_device_firmware_and_sdk_mismatch_does_not_invent_advertised_ram(self):
        info=importlib.import_module('device_info')
        def proc(path,keys):return dict(MemTotal='2048000 kB',MemAvailable='512000 kB') if path.endswith('meminfo') else dict(Hardware='RK3528')
        with mock.patch.object(info,'proc_values',side_effect=proc),mock.patch.object(info,'android_properties',return_value={'ro.build.version.sdk':'34','ro.build.version.release':'16'}),mock.patch.object(sys.modules['xbmcvfs'],'translatePath',return_value=str(self.folder),create=True),mock.patch.object(sys.modules['xbmc'],'getInfoLabel',return_value='21.3 Omega'):
            result=info.collect()
        self.assertEqual(result['ram_total_bytes'],2048000*1024);self.assertTrue(result['firmware_mismatch'])
        self.assertEqual(result['android_expected_from_sdk'],'14');self.assertIn('UNVERIFIED',result['advertised_ram_flash'])
        self.assertNotIn(str(self.folder),json.dumps(result))

    def test_wizard_root_is_deferred_while_save_window_owns_gui(self):
        spec=importlib.util.spec_from_file_location('main37',ADDON/'resources/lib/main.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        nav=importlib.import_module('setup_navigation')
        self.properties[nav.ACTIVE]=str(time.time())
        router=module.Router(['plugin://plugin.video.xtreammate','7','?action=root'])
        # .48 requires the real cross-interpreter owner, not a stale timestamp.
        with importlib.import_module('window_navigation').ownership() as acquired:
            self.assertTrue(acquired);router.dispatch()
        self.assertEqual(len(self.ends),1);self.assertFalse(self.added);self.assertFalse(self.builtins)

    def test_saved_wizard_cannot_navigate_before_native_release_or_foreign_modal(self):
        nav=importlib.import_module('setup_navigation');nav._queue('return',pid='p',closed='13001')
        value=json.loads(self.properties[nav.KEY]);value['at']-=1;self.properties[nav.KEY]=json.dumps(value)
        life=importlib.import_module('window_lifecycle')
        with mock.patch.object(life,'state',return_value=dict(window=13001,dialog=0,modal=False,updating=False)):
            nav.poll();self.assertFalse(self.builtins)
        with mock.patch.object(life,'state',return_value=dict(window=10025,dialog=999,modal=True,updating=False)):
            nav.poll();self.assertFalse(self.builtins)
        with mock.patch.object(life,'state',return_value=dict(window=10025,dialog=0,modal=False,updating=False)):
            nav.poll();nav.poll()
        self.assertEqual(len(self.builtins),1);self.assertIn('action=xcmate_home',self.builtins[0])

    def test_existing_profile_does_not_automatically_reopen_wizard(self):
        config=importlib.import_module('artwork_config');self.assertEqual(config.initialize()['mode'],'internal')
        nav=importlib.import_module('setup_navigation');nav.maybe_fresh(self.router)
        self.assertFalse(self.properties.get(nav.KEY))

    def test_fast_home_matches_existing_six_items_icon_and_completion_without_catalogue(self):
        home=importlib.import_module('home_entry')
        with mock.patch.dict(sys.modules,{'main':None}):
            self.assertTrue(home.dispatch(['plugin://plugin.video.xtreammate','7','?action=xcmate_home&pid=p']))
        self.assertEqual(len(self.added),8);self.assertEqual(len(self.ends),1)
        self.assertTrue(any('action=guide_grid' in row[0] for row in self.added))
        self.assertTrue(any('action=home_start' in row[0] for row in self.added));self.client._get_json.assert_not_called()

    def test_nonhome_route_falls_back_to_full_router_without_side_effects(self):
        home=importlib.import_module('home_entry')
        self.assertFalse(home.dispatch(['plugin://plugin.video.xtreammate','7','?action=media_play&pid=p']))
        self.assertFalse(self.added);self.assertFalse(self.ends)

    def test_xtream_new_group_requests_delta_without_forcing_existing_groups(self):
        groups=importlib.import_module('group_selection');sync=importlib.import_module('catalog_delta')
        cats=[dict(category_id='a',category_name='A'),dict(category_id='b',category_name='B')]
        groups.save('p',['a'],'live',known=['a','b'],auto_new=False)
        self.dialog.select.side_effect=[1,6]
        with mock.patch.object(sync,'request') as request:
            self.assertTrue(groups.choose_groups(self.portal,'live',categories=cats,allow_refresh=False))
        self.assertEqual(request.call_count,1)
        self.assertEqual(request.call_args.args[1:3],('live','b'));self.assertFalse(request.call_args.kwargs)
        self.assertEqual(groups.load('p'),{'a','b'})

    def test_wizard_unknown_duration_progress_is_visible_without_false_percentage(self):
        import test_xcmate_setup_0294 as model
        m=model.SetupThreadTests(methodName='runTest');m.setUp();self.addCleanup(m.doCleanups)
        m.show();m.window.busy=True;m.window.status(None,'EPG 1/4')
        self.assertTrue(m.window.getControl(4).isVisible());self.assertEqual(m.window.getControl(4).percent,0)
        m.window.pump();self.assertIn('EPG 1/4',m.window.getControl(3).text)
        self.assertFalse(m.violations)

    def test_cancelled_worker_keeps_only_data_not_native_window_reference(self):
        import gc,weakref,threading
        ui=importlib.import_module('setup_window');release=threading.Event();entered=threading.Event()
        window=ui.WorkWindow('XCMateSetup.xml',str(ADDON),'Default','720p');window.configure_work()
        pool=window._pool
        def job():entered.set();release.wait(3);return None
        window.work(job,lambda result:None);self.assertTrue(entered.wait(1))
        reference=weakref.ref(window)
        try:
            window.close();del window;gc.collect()
            self.assertIsNone(reference())
        finally:release.set();pool.shutdown(wait=True)
