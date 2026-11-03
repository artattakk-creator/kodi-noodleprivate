"""Atomic legacy imports, valid action/directory contracts and companion ZIP."""
import importlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest import mock
import zipfile

import test_xcmate_setup_0294 as old
ROOT=Path(__file__).resolve().parents[1]


class Legacy71(unittest.TestCase):
    def setUp(self):
        self.m=old.StorageTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.p=self.m.portals;self.legacy=importlib.import_module('legacy_setup71')
    def settings(self):
        import utils
        values={}
        for n in range(1,4):
            values.update({f'playlist{n}_name':f'List {n}',f'playlist{n}_xc_host':'https://synthetic.invalid',
                           f'playlist{n}_xc_user':'synthetic-user',f'playlist{n}_xc_pass':'SECRET'})
        patches=[mock.patch.object(utils,'setting',side_effect=lambda key:values.get(key,''),create=True),
                 mock.patch.object(utils,'setting_bool',return_value=True,create=True),
                 mock.patch.object(utils,'setting_int',return_value=2,create=True)]
        for p in patches:p.start();self.addCleanup(p.stop)
    def test_all_legacy_slots_are_published_with_one_atomic_write_and_repeat_is_noop(self):
        self.p.save_all([]);self.settings()
        with mock.patch.object(self.p,'save_all',wraps=self.p.save_all) as save:
            for _ in range(3):self.p.import_from_settings()
        self.assertEqual(save.call_count,1)
        rows=self.p.load_all();self.assertEqual(len(rows),3)
        self.assertEqual(len({p['id'] for p in rows}),3)
        self.assertTrue(all(p['xc_pass']=='SECRET' for p in rows))
    def test_partial_write_failure_does_not_hide_remaining_legacy_slots_on_retry(self):
        self.p.save_all([]);self.settings();save=self.p.save_all;attempt=[0]
        def fail(rows):
            attempt[0]+=1
            save(rows)
            if attempt[0]==1:raise OSError('synthetic post-write failure')
        with mock.patch.object(self.p,'save_all',side_effect=fail):
            with self.assertRaises(OSError):self.p.import_from_settings()
        self.assertEqual(self.p.load_all(),[])
        self.assertTrue(self.p.import_from_settings());self.assertEqual(len(self.p.load_all()),3)
    def test_existing_portals_never_import_duplicate_slots_or_rewrite_configuration(self):
        self.settings()
        with mock.patch.object(self.p,'save_all',wraps=self.p.save_all) as save:
            self.assertFalse(self.p.import_from_settings())
        save.assert_not_called();self.assertEqual(self.p.load_all(),[self.m.portal])
    def test_positive_handle_renders_once_without_refresh_or_autoplay(self):
        router=types.SimpleNamespace(_handle=7,_root=mock.Mock())
        with mock.patch('xbmc.executebuiltin') as builtin:
            self.legacy.run(router)
        router._root.assert_called_once_with(_legacy71=True);builtin.assert_not_called()
    def test_runplugin_has_no_directory_completion_or_foreign_container_navigation(self):
        router=types.SimpleNamespace(_handle=-1,_root=mock.Mock())
        with mock.patch('xbmc.executebuiltin') as builtin,mock.patch('xbmcplugin.endOfDirectory') as end:
            self.legacy.run(router)
        router._root.assert_not_called();builtin.assert_not_called();end.assert_not_called()

    def test_real_entry_renders_valid_directory_on_three_manual_import_calls(self):
        from test_xcmate_0281_boot import BootTests
        model=BootTests(methodName='runTest');model.setUp();self.addCleanup(model.doCleanups)
        before=model.portal_file.read_bytes()
        for _ in range(3):model.run_entry('import_legacy_settings')
        self.assertEqual(len(model.ends),3);self.assertTrue(model.items)
        self.assertFalse(any('START_FAILED' in line for line in model.logs))
        self.assertFalse(any('Refresh' in command for command in model.calls))
        self.assertTrue(all(kw.get('succeeded',True) for args,kw in model.ends))
        self.assertEqual(model.portal_file.read_bytes(),before)

    def test_successful_action_updates_only_own_parent_to_canonical_root(self):
        router=types.SimpleNamespace(_handle=-1,_root=mock.Mock(),url=lambda **kw:'plugin://plugin.video.xtreammate/?action=root')
        with mock.patch.object(self.p,'import_from_settings',return_value=True),\
             mock.patch('xbmc.getInfoLabel',return_value='plugin://plugin.video.xtreammate/?action=root',create=True),\
             mock.patch('xbmc.executebuiltin') as builtin,mock.patch('xbmcplugin.endOfDirectory') as end:
            self.legacy.run(router)
        end.assert_not_called();builtin.assert_called_once_with('Container.Update(plugin://plugin.video.xtreammate/?action=root,replace)')


class Companion352(unittest.TestCase):
    @classmethod
    def module(cls,name,path):
        spec=importlib.util.spec_from_file_location(name,ROOT/path);mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod);return mod
    def test_companion_build_is_repeatable_closes_local_imports_and_preserves_installer_modules(self):
        builder=self.module('build_setup352_update','tools/build_setup352_update.py')
        with tempfile.TemporaryDirectory() as a,tempfile.TemporaryDirectory() as b:
            one=builder.build(a);two=builder.build(b);self.assertEqual(one['sha256'],two['sha256'])
            self.assertEqual(one['import_closure'],'PASS')
            with zipfile.ZipFile(builder.BASE) as oldzip,zipfile.ZipFile(Path(a)/'script.gsmedia.setup-0.5.20.zip') as newzip:
                for name in oldzip.namelist():
                    if name.endswith('/') or name.endswith(('/addon.xml','/service.py')):continue
                    self.assertEqual(oldzip.read(name),newzip.read(name),name)
    def test_bingie_readiness_waits_for_two_stable_gui_samples_without_setting_changes(self):
        mod=self.module('postboot71','tools/gsmedia_setup352/setup_postboot71.py')
        calls=[];state=[0]
        def rpc(raw):
            request=json.loads(raw);calls.append(request['method'])
            state[0]+=1
            if request['method']=='Settings.GetSettingValue':return json.dumps(dict(result=dict(value='skin.titan.bingie.mod')))
            return json.dumps(dict(result=dict(skin=dict(id='skin.estuary' if state[0]<4 else 'skin.titan.bingie.mod'))))
        xbmc=types.SimpleNamespace(executeJSONRPC=rpc,getCondVisibility=lambda key:key=='Window.IsActive(home)')
        monitor=types.SimpleNamespace(abortRequested=lambda:False,waitForAbort=lambda n:False)
        self.assertTrue(mod.wait_active(xbmc,monitor))
        self.assertTrue(all(n in ('GUI.GetProperties','Settings.GetSettingValue') for n in calls))
        self.assertGreaterEqual(calls.count('GUI.GetProperties'),3)
    def test_foreign_skin_or_abort_cannot_claim_bingie_ready(self):
        mod=self.module('postboot71b','tools/gsmedia_setup352/setup_postboot71.py')
        xbmc=types.SimpleNamespace(executeJSONRPC=lambda raw:json.dumps(dict(result=dict(value='skin.estuary',skin=dict(id='skin.estuary')))),getCondVisibility=lambda key:False)
        monitor=types.SimpleNamespace(abortRequested=lambda:False,waitForAbort=lambda n:True)
        self.assertFalse(mod.wait_active(xbmc,monitor))
        monitor.abortRequested=lambda:True
        self.assertFalse(mod.wait_active(xbmc,monitor))
