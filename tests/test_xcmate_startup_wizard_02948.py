"""P0 startup/single-flight and real wizard entry/authentication regressions."""
import importlib
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import types
import unittest
from unittest import mock
from xcmate027_fixture import Fixture,ADDON,LIB

class StartupWizard48(Fixture,unittest.TestCase):
    def test_service_singleton_is_os_held_and_releases_without_deleting_any_profile(self):
        s=importlib.import_module('startup48');before=dict(self.options)
        with s.singleton() as acquired:
            self.assertTrue(acquired)
            with s.singleton() as duplicate:self.assertFalse(duplicate)
            lock=self.folder/'.service48.lock'
            code='import fcntl,sys; f=open(sys.argv[1]);\ntry: fcntl.flock(f,fcntl.LOCK_EX|fcntl.LOCK_NB)\nexcept BlockingIOError: sys.exit(23)'
            result=subprocess.run([sys.executable,'-c',code,str(lock)],capture_output=True)
            self.assertEqual(result.returncode,23)
        with s.singleton() as acquired:self.assertTrue(acquired)
        self.assertEqual(self.options,before)
    def test_startup_network_is_deferred_and_setup_and_stop_hold_it(self):
        s=importlib.import_module('startup48');clock=mock.Mock(return_value=0);phases=s.Phases(clock)
        self.assertFalse(phases.network());clock.return_value=16
        with mock.patch('setup_navigation.active',return_value=False),mock.patch('exit_jobs.blocked',return_value=False):self.assertTrue(phases.network())
        with mock.patch('setup_navigation.active',return_value=True):self.assertFalse(phases.network())
        with mock.patch('setup_navigation.active',return_value=False),mock.patch('exit_jobs.blocked',return_value=True):self.assertFalse(phases.network())
    def test_maintenance_has_no_every_tick_rescan_and_timer_is_finite(self):
        clock=mock.Mock(return_value=0);phases=importlib.import_module('startup48').Phases(clock)
        self.assertTrue(phases.due('maintenance',300))
        for i in range(300):clock.return_value=i;self.assertFalse(phases.due('maintenance',300))
        clock.return_value=300;self.assertTrue(phases.due('maintenance',300))
    def test_fresh_and_legacy_artwork_modes_are_not_changed_by_singleton(self):
        config=importlib.import_module('artwork_config')
        for key in ('artwork.sqlite','portals.json'):
            (self.folder/key).write_bytes(b'legacy')
        self.assertEqual(config.initialize()['mode'],'internal')
        with importlib.import_module('startup48').singleton():pass
        self.assertEqual(config.read()['mode'],'internal')
        self.assertEqual((self.folder/'portals.json').read_bytes(),b'legacy')
    def test_wizard_directory_entry_does_not_import_router_or_reenter_root(self):
        from home_entry import HomeRouter
        router=HomeRouter(['plugin://plugin.video.xtreammate','7','?action=setup_wizard'])
        entry=importlib.import_module('setup_entry48')
        with mock.patch('setup_navigation.active',return_value=False),mock.patch('setup_navigation._queue') as queued,mock.patch('setup_navigation.run') as run:
            self.assertTrue(entry.dispatch(router));run.assert_not_called();queued.assert_called_once()
        self.assertFalse(self.builtins);self.assertEqual(len(self.ends),1)
    def test_wizard_action_entry_calls_existing_owner_flow(self):
        from home_entry import HomeRouter
        entry=importlib.import_module('setup_entry48');router=HomeRouter(['plugin://plugin.video.xtreammate','-1','?action=setup_wizard'])
        with mock.patch('setup_navigation.run') as run:self.assertTrue(entry.dispatch(router));run.assert_called_once_with(router)
    def test_xtream_authentication_performs_exactly_one_actual_request(self):
        spec=importlib.util.spec_from_file_location('real_xtream48',LIB/'xtream.py');x=importlib.util.module_from_spec(spec);spec.loader.exec_module(x);response={'user_info':{'auth':1}}
        with mock.patch.object(x,'http_get',return_value=(json.dumps(response).encode(),{})) as get:
            client=x.XtreamClient('https://provider.invalid','u','SECRET');self.assertEqual(client.authenticate(),response);self.assertEqual(client.authenticate(),response)
        self.assertEqual(get.call_count,1)
    def test_discovery_context_limits_timeout_retries_and_restores_normal_policy(self):
        wizard=importlib.import_module('wizard_deadline48');seen=[]
        class Draft:
            pid='synthetic'
            @wizard.discovery
            def discover(self,cancel,status):
                seen.append(wizard.policy(30,60,3));self_bytes=wizard.byte_limit(80*1024*1024)
                assert self_bytes==2*1024*1024
                return 'ready'
        self.assertEqual(Draft().discover(),'ready')
        self.assertLessEqual(seen[0][0],15);self.assertLessEqual(seen[0][1],60);self.assertEqual(seen[0][2],1)
        self.assertEqual(wizard.policy(30,60,3),(30,60,3));self.assertFalse(wizard.active())
    def test_discovery_cancelled_before_network_never_calls_adapter(self):
        wizard=importlib.import_module('wizard_deadline48');called=[]
        class Draft:
            @wizard.discovery
            def discover(self,*args):called.append(1)
        with self.assertRaises(InterruptedError):Draft().discover(cancel=lambda:True)
        self.assertFalse(called);self.assertFalse(wizard.active())
    def test_deadline_expiry_is_error_not_auth_or_success(self):
        wizard=importlib.import_module('wizard_deadline48')
        class Draft:
            @wizard.discovery
            def discover(self,*args):
                wizard._local.deadline=0;wizard.check()
        # .54 deliberately removes the aggregate deadline; request limits remain.
        Draft().discover()
        self.assertFalse(wizard.active())
    def test_cancelled_dns_worker_cannot_create_unbounded_parallel_discoveries(self):
        wizard=importlib.import_module('wizard_deadline48');wizard._slot.acquire()
        self.addCleanup(wizard._slot.release)
        class Draft:
            @wizard.discovery
            def discover(self,*args):raise AssertionError('network must not run')
        with self.assertRaises(OSError):Draft().discover()
    def test_legacy_epg_configuration_dictionary_contract_remains_compatible(self):
        c=importlib.import_module('epg_sources').configuration('p')
        self.assertEqual(c,dict(sources=[],mappings={}))
    def test_setup_has_finite_native_window_initialization_deadline(self):
        module=importlib.import_module('setup_window')
        window=module.WorkWindow('XCMateSetup.xml',str(ADDON),'Default','720p');window.configure_work()
        with mock.patch.object(window,'show'),mock.patch('time.monotonic',side_effect=[0,0,11]),mock.patch('setup_trace.mark') as mark:
            window.run()
        self.assertTrue(window._closed);self.assertTrue(window.cancel.is_set())
        mark.assert_called_with('NATIVE_INIT_TIMEOUT48')
    def test_required_image_decoder_is_declared_on_clean_kodi_install(self):
        import xml.etree.ElementTree as E
        dep=E.parse(ADDON/'addon.xml').find("requires/import[@addon='script.module.pil']")
        self.assertNotEqual(dep.get('optional'),'true')

    def test_stale_wizard_timestamp_without_owner_does_not_block_restart(self):
        navigation=importlib.import_module('setup_navigation');self.properties[navigation.ACTIVE]=str(time.time())
        self.assertFalse(navigation.active())
        from window_navigation import ownership
        with ownership() as acquired:
            self.assertTrue(acquired);self.assertTrue(navigation.active())
        self.assertFalse(navigation.active())
    def test_manual_wizard_directory_continues_from_settings_without_root_reload(self):
        from home_entry import HomeRouter
        import setup_entry48,setup_navigation
        self.current_folder='plugin://plugin.video.xtreammate/?action=settings_home&pid=p'
        router=HomeRouter(['plugin://plugin.video.xtreammate','7','?action=setup_wizard'])
        setup_entry48.dispatch(router)
        value=json.loads(self.properties[setup_navigation.KEY]);self.assertTrue(value['direct48']);value['at']-=1;self.properties[setup_navigation.KEY]=json.dumps(value)
        setup_navigation.poll();setup_navigation.poll()
        self.assertEqual(self.builtins,['RunPlugin(plugin://plugin.video.xtreammate?action=setup_wizard)'])
    def test_direct_wizard_continuation_still_waits_for_foreign_modal(self):
        import setup_navigation
        setup_navigation._queue('launch',url='plugin://plugin.video.xtreammate/?action=setup_wizard',direct48=True)
        value=json.loads(self.properties[setup_navigation.KEY]);value['at']-=1;self.properties[setup_navigation.KEY]=json.dumps(value)
        with mock.patch('window_lifecycle.state',return_value=dict(window=10025,dialog=10103,modal=True,updating=False)):
            setup_navigation.poll()
        self.assertFalse(self.builtins);self.assertIn(setup_navigation.KEY,self.properties)

    def test_cold_service_defers_auto_scan_images_and_maintenance_but_serves_explicit_jobs(self):
        import threading
        service=importlib.import_module('app_services')
        class Monitor:
            def abortRequested(self):return False
            def waitForAbort(self,seconds):return True
        with mock.patch.object(sys.modules['xbmc'],'Monitor',Monitor),mock.patch.object(service,'_stop',threading.Event()),mock.patch('startup48.suspended',return_value=False),mock.patch('startup48.Phases.network',return_value=False),mock.patch('service_runtime.pressure',return_value=False),mock.patch.object(service,'refresh_local') as refresh,mock.patch('artwork_db.maintain') as maintenance,mock.patch('media_art.ensure_worker') as images,mock.patch('catalog_sync.run_next',return_value=True) as explicit,mock.patch('catalog_delta.run_next',return_value=False),mock.patch('genre_search.run_next',return_value=False),mock.patch('guide_timers.poll') as timers:
            service._run()
        refresh.assert_not_called();maintenance.assert_not_called();images.assert_not_called();explicit.assert_called_once();timers.assert_called_once()
