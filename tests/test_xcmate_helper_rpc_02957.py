"""Bounded Kodi-worker calls; no accumulating timeout replacements."""
import importlib,json,threading,time,unittest
from concurrent.futures import ThreadPoolExecutor
from xcmate027_fixture import Fixture


class Rpc57(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.rpc=importlib.import_module('helper_rpc57')
        self.assertTrue(self.rpc._active is None or self.rpc._active['done'].is_set())

    def run_call(self,**kwargs):
        with ThreadPoolExecutor(1) as pool:
            return pool.submit(self.rpc.call,'Addons.GetAddonDetails',{'addonid':'plugin.video.themoviedb.helper'},**kwargs).result(2)

    def test_actual_rpc_executes_on_its_single_background_thread(self):
        owners=[]
        def execute(raw):
            owners.append((threading.get_ident(),threading.current_thread().name));request=json.loads(raw)
            return json.dumps(dict(jsonrpc='2.0',id=request['id'],result={'addon':{'version':'6.19.4'}}))
        self.assertEqual(self.run_call(execute=execute)['addon']['version'],'6.19.4')
        self.assertTrue(all(identity!=threading.get_ident() and name=='XCMate-helper-rpc57' for identity,name in owners))

    def test_gui_owner_cannot_start_a_lookup(self):
        with self.assertRaises(self.rpc.Error) as exc:self.rpc.call('Files.GetDirectory',{},execute=lambda raw:None)
        self.assertEqual(exc.exception.code,'HELPER_BACKGROUND_UNAVAILABLE')

    def test_player_window_and_settings_rpc_commands_are_not_allowed(self):
        for method in ('Player.Open','GUI.ActivateWindow','Addons.SetAddonEnabled','Settings.SetSettingValue','JSONRPC.NotifyAll'):
            with ThreadPoolExecutor(1) as pool:
                with self.assertRaises(self.rpc.Error):pool.submit(self.rpc.call,method,{}).result(1)

    def test_timeout_allows_no_new_rpc_until_the_only_native_call_finishes(self):
        entered=threading.Event();release=threading.Event();calls=[]
        def slow(raw):
            calls.append(raw);entered.set();release.wait(2)
            return json.dumps(dict(jsonrpc='2.0',id=57,result={'late':True}))
        try:
            started=time.monotonic()
            with self.assertRaises(self.rpc.Error) as exc:self.run_call(execute=slow,timeout=.02)
            self.assertEqual(exc.exception.code,'HELPER_TIMEOUT');self.assertLess(time.monotonic()-started,1)
            self.assertTrue(entered.is_set())
            for _ in range(5):
                with self.assertRaises(self.rpc.Error) as busy:self.run_call(execute=slow)
                self.assertEqual(busy.exception.code,'HELPER_BACKGROUND_UNAVAILABLE')
            self.assertEqual(len(calls),1)
        finally:release.set();self.assertTrue(self.rpc._active['done'].wait(1))

    def test_cancelled_wait_discards_result_without_spawning_replacements(self):
        entered=threading.Event();release=threading.Event();cancel=threading.Event()
        def execute(raw):entered.set();release.wait(2);return json.dumps(dict(jsonrpc='2.0',id=57,result={}))
        try:
            with ThreadPoolExecutor(1) as pool:
                future=pool.submit(self.rpc.call,'Files.GetDirectory',{},cancel.is_set,execute=execute)
                self.assertTrue(entered.wait(1));cancel.set()
                with self.assertRaises(self.rpc.Error) as exc:future.result(1)
                self.assertEqual(exc.exception.code,'CANCELLED')
        finally:release.set();self.assertTrue(self.rpc._active['done'].wait(1))

    def test_malformed_oversize_wrong_id_and_native_errors_have_fixed_private_safe_codes(self):
        replies=['not json',json.dumps(dict(jsonrpc='2.0',id=1,result={})),json.dumps(dict(jsonrpc='2.0',id=57,result=[])),
                 json.dumps(dict(jsonrpc='2.0',id=57,error={'message':'PRIVATE_PROVIDER_PASSWORD'})), 'x'*(self.rpc.MAX_REPLY+1)]
        for reply in replies:
            with self.assertRaises(self.rpc.Error) as exc:self.run_call(execute=lambda raw:reply)
            self.assertEqual(str(exc.exception),'HELPER_BACKGROUND_UNAVAILABLE')
        def broken(raw):raise OSError('PRIVATE_PROVIDER_PASSWORD')
        with self.assertRaises(self.rpc.Error) as exc:self.run_call(execute=broken)
        self.assertNotIn('PRIVATE',str(exc.exception))
