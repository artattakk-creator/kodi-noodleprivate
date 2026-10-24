"""Real profile IO/versioning, bounded scheduling, pressure and private metrics."""
import importlib,json,os,sys,tempfile,threading,types,unittest
from pathlib import Path
from unittest import mock

LIB=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/lib'


class Stability30Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup);self.root=Path(self.temp.name)
        patch=mock.patch.object(sys,'path',[str(LIB)]+sys.path);patch.start();self.addCleanup(patch.stop)
        patch=mock.patch.dict(sys.modules);patch.start();self.addCleanup(patch.stop)
        self.logs=[]
        sys.modules['utils']=types.SimpleNamespace(addon_data_dir=lambda:str(self.root),error=lambda *a:None,info=lambda *a:None,debug=lambda *a:None)
        sys.modules['xbmcvfs']=types.SimpleNamespace()
        sys.modules['xbmc']=types.SimpleNamespace(LOGINFO=1,log=lambda msg,*a:self.logs.append(msg),Monitor=lambda:types.SimpleNamespace(abortRequested=lambda:False,waitForAbort=lambda n:False))
        for name in ('portals','portal_snapshot','service_runtime','profile_transaction','stability_monitor','app_services'):sys.modules.pop(name,None)
        self.portals=importlib.import_module('portals');self.runtime=importlib.import_module('service_runtime')
        self.file=self.root/'portals.json';self.value=[dict(id='p',type='xtream',xc_pass='SECRET',groups=['one'])]
        self.file.write_text(json.dumps(self.value))

    def test_twenty_thousand_calls_parse_once_and_mutable_callers_cannot_change_snapshot(self):
        with mock.patch.object(json,'loads',wraps=json.loads) as loads:
            for _ in range(20000):self.assertEqual(self.portals.get_by_id('p')['id'],'p')
        self.assertEqual(loads.call_count,1);self.assertEqual(self.runtime.counters()['portal_disk_reads'],1)
        result=self.portals.load_all();result[0]['groups'].append('MUTATED');result[0]['xc_pass']='changed'
        self.assertEqual(self.portals.load_all(),self.value)

    def test_atomic_same_size_same_mtime_replacement_and_writer_immediately_invalidate(self):
        self.portals.load_all();before=self.file.stat();new=self.root/'new'
        changed=[dict(self.value[0],xc_pass='OTHER!')];new.write_text(json.dumps(changed))
        os.utime(new,ns=(before.st_atime_ns,before.st_mtime_ns));os.replace(new,self.file)
        self.assertEqual(self.portals.get_by_id('p')['xc_pass'],'OTHER!')
        self.portals.update('p',dict(xc_pass='LATEST',groups=['two']))
        self.assertEqual(self.portals.get_by_id('p')['xc_pass'],'LATEST')
        self.assertEqual(self.portals.get_by_id('p')['groups'],['two'])

    def test_oom_backoff_never_returns_empty_or_retries_parsing_in_a_tight_loop(self):
        before=self.file.read_bytes()
        with mock.patch.object(json,'loads',side_effect=MemoryError()) as loads:
            for _ in range(100):
                with self.assertRaises(self.portals.PortalReadError):self.portals.load_all()
        self.assertEqual(loads.call_count,1);self.assertEqual(self.runtime.counters()['portal_oom'],1)
        self.assertEqual(self.file.read_bytes(),before)
        self.portals._snapshot.retry=0
        self.assertEqual(self.portals.load_all(),self.value)

    def test_corrupt_read_not_permanently_cached_and_missing_file_reappears(self):
        self.file.write_text('{bad')
        with self.assertRaises(self.portals.PortalReadError):self.portals.load_all()
        self.file.write_text(json.dumps(self.value));self.assertEqual(self.portals.load_all(),self.value)
        self.file.unlink();self.assertEqual(self.portals.load_all(),[])
        self.file.write_text(json.dumps(self.value));self.assertEqual(self.portals.load_all(),self.value)

    def test_concurrent_readers_share_one_parse_and_save_verification_is_reentrant(self):
        failures=[]
        def read():
            try:
                for _ in range(100):self.assertEqual(self.portals.load_all(),self.value)
            except Exception as exc:failures.append(type(exc).__name__)
        threads=[threading.Thread(target=read) for _ in range(4)]
        for thread in threads:thread.start()
        for thread in threads:thread.join(3);self.assertFalse(thread.is_alive())
        self.assertEqual(failures,[]);self.assertEqual(self.runtime.counters()['portal_disk_reads'],1)
        from profile_transaction import writing
        with writing():self.portals.save_all(self.value)
        self.assertEqual(self.portals.load_all(),self.value)

    def test_service_io_timeout_and_stop_are_scoped_and_never_retry_cancelled_chunks(self):
        from network_io import read_http_chunks
        self.assertEqual(self.runtime.timeout(15),15)
        with self.runtime.scope():
            self.assertEqual(self.runtime.timeout(15),2);self.runtime.stop()
            with self.assertRaises(InterruptedError):read_http_chunks([b'PRIVATE'],{},100,9999999999)
        self.assertFalse(self.runtime.cancelled())
        self.runtime.install()
        self.assertEqual(self.runtime.timeout(15),15)  # Preserve foreground/autoplay deadlines.

    def test_optional_preparation_does_not_repeat_on_each_fast_catalogue_tick(self):
        ticks=[0];monitor=types.SimpleNamespace(abortRequested=lambda:False)
        def wait(seconds):ticks[0]+=1;return ticks[0]>=20
        monitor.waitForAbort=wait;sys.modules['xbmc'].Monitor=lambda:monitor
        maintenance=mock.Mock();prefetch=mock.Mock();prepare=mock.Mock();catalog=mock.Mock(return_value=True)
        for name,value in [('artwork_db',types.SimpleNamespace(maintain=maintenance)),('art_store',types.SimpleNamespace(prefetch_selected=prefetch)),('startup_preload',types.SimpleNamespace(prepare=prepare)),('catalog_sync',types.SimpleNamespace(run_next=catalog)),('guide_timers',types.SimpleNamespace(poll=lambda:None))]:sys.modules[name]=value
        service=importlib.import_module('app_services')
        with mock.patch.object(service,'refresh_local') as refresh,mock.patch.object(self.runtime,'pressure',return_value=False),mock.patch.object(self.runtime,'emit'),mock.patch.object(self.runtime.time,'monotonic',side_effect=lambda:ticks[0]*.1):service._run()
        self.assertEqual(maintenance.call_count,1);self.assertEqual(prefetch.call_count,1);self.assertEqual(prepare.call_count,1);self.assertEqual(refresh.call_count,1)
        self.assertGreaterEqual(catalog.call_count,10)

    def test_shutdown_interrupts_owned_socket_read_without_closing_foreign_io(self):
        import socket
        one,two=socket.socketpair();self.addCleanup(one.close);self.addCleanup(two.close)
        received=[];waiting=threading.Event()
        def read():waiting.set();received.append(one.recv(1))
        thread=threading.Thread(target=read);thread.start();waiting.wait(1)
        with self.runtime.scope():self.runtime.track_socket(one);self.runtime.stop()
        thread.join(1);self.assertFalse(thread.is_alive());self.assertEqual(received,[b''])
        self.assertGreaterEqual(one.fileno(),0)

    def test_numeric_monitor_is_bounded_and_never_contains_credentials_or_paths(self):
        monitor=importlib.import_module('stability_monitor');self.portals.load_all()
        value=monitor.sample();text=json.dumps(value)
        for private in ('SECRET',str(self.root),'xc_pass','groups'):self.assertNotIn(private,text)
        self.assertEqual(value['pointer_bits'],8*__import__('struct').calcsize('P'))
        monitor.path('samples.jsonl').write_bytes(b'x'*(513*1024));monitor.append(value)
        self.assertLess(monitor.path('samples.jsonl').stat().st_size,4096)
        self.assertTrue(monitor.path('samples.previous.jsonl').exists())
        before=self.file.read_bytes();session=monitor.start(4);self.assertGreaterEqual(session['end']-session['start'],4*3600-1)
        self.assertEqual(self.file.read_bytes(),before)


if __name__=='__main__':unittest.main()
