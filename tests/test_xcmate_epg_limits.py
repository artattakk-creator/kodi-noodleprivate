"""Exercise real cache/HTTP/XMLTV paths with bounded synthetic inputs."""
import ast
import gzip
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import threading
import time
import types
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from unittest import mock

LIB = Path(__file__).resolve().parents[1] / 'src/plugin.video.xtreammate/resources/lib'
sys.path.insert(0, str(LIB))
from network_io import read_http_chunks
from epg_io import XMLTVReader


def load(name, file):
    spec = importlib.util.spec_from_file_location(name, LIB/file)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LocalVFS:
    def __init__(self, root):
        self.root = root
        self.denied = set()
        self.refuse_writes = set()
    def translatePath(self, path):
        return path.replace('special://userdata/addon_data/plugin.video.xtreammate/', self.root+'/')
    def exists(self, path): return os.path.exists(path)
    def mkdirs(self, path):
        os.makedirs(path, exist_ok=True)
        return True
    def delete(self, path):
        os.unlink(path)
        return True
    def File(self, path, mode='r'):
        if mode=='w' and os.path.dirname(path) in self.denied:
            raise PermissionError('permission revoked')
        stream = open(path,mode,encoding='utf-8')
        class File:
            def __enter__(inner): return inner
            def __exit__(inner,*args): stream.close()
            def read(inner): return stream.read()
            def write(inner,text):
                if os.path.dirname(path) in self.refuse_writes: return False
                stream.write(text)
                return True
        return File()


class CacheAndEPGTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.root = Path(temp.name)
        self.vfs = LocalVFS(str(self.root/'profile'))
        self.prefs = {}
        self.logs = []
        xbmc = types.ModuleType('xbmc')
        xbmc.LOGDEBUG,xbmc.LOGINFO,xbmc.LOGWARNING,xbmc.LOGERROR = range(4)
        xbmc.log = lambda message,**kwargs:self.logs.append(message)
        xbmc.sleep = lambda *_:None
        addon = types.ModuleType('xbmcaddon')
        addon.Addon = lambda:types.SimpleNamespace(
            getAddonInfo=lambda name:'plugin.video.xtreammate',
            getSetting=lambda key:self.prefs.get(key,''))
        gui=types.ModuleType('xbmcgui')
        gui.NOTIFICATION_INFO='info'
        patch = mock.patch.dict(sys.modules,dict(xbmc=xbmc,xbmcaddon=addon,
            xbmcgui=gui,xbmcvfs=self.vfs))
        patch.start()
        self.addCleanup(patch.stop)
        self.utils = load('limits_utils','utils.py')
        patch2 = mock.patch.dict(sys.modules,dict(utils=self.utils))
        patch2.start()
        self.addCleanup(patch2.stop)
        self.epg = load('limits_epg','epg.py')
        self.sources = load('limits_sources','epg_sources.py')

    def select_folder(self):
        path = str(self.root/'selected')
        os.mkdir(path)
        self.prefs['cache_dir'] = path
        return path

    def test_existing_unwritable_folder_uses_private_cache(self):
        selected = self.select_folder()
        self.vfs.denied.add(selected)
        self.assertEqual(Path(self.utils.cache_dir()),self.root/'profile/cache')
        self.assertTrue(self.utils.cache_set('a'*32,{'title':'kept'}))
        self.assertEqual(self.utils.cache_get('a'*32),{'title':'kept'})
        self.assertEqual(self.prefs['cache_dir'],selected)
        self.assertEqual(os.listdir(selected),[])

    def test_permission_revoked_after_probe_retries_private_write(self):
        selected = self.select_folder()
        self.assertEqual(self.utils.cache_dir(),selected)
        self.assertEqual(os.listdir(selected),[])
        self.vfs.denied.add(selected)
        self.assertTrue(self.utils.cache_set('b'*32,[1,2]))
        self.assertTrue((self.root/'profile/cache'/('b'*32+'.json')).is_file())
        self.assertNotIn(selected,self.utils._CACHE_WRITABLE)

    def test_vfs_false_write_also_falls_back_and_private_failure_is_reported(self):
        selected = self.select_folder()
        self.vfs.refuse_writes.add(selected)
        self.assertEqual(Path(self.utils.cache_dir()),self.root/'profile/cache')
        self.assertEqual(os.listdir(selected),[])
        self.vfs.denied.add(str(self.root/'profile/cache'))
        self.assertFalse(self.utils.cache_set('c'*32,{}))

    def test_sources_and_mappings_survive_cache_failure_and_module_reload(self):
        selected = self.select_folder()
        self.sources.add_source('p','Example','https://example.invalid/guide.xml')
        self.sources.set_mapping('p','1','station.id')
        config = Path(self.sources._file_path()).read_bytes()
        self.vfs.denied.add(selected)
        self.utils.cache_set('d'*32,{'data':'cache'})
        other = load('reloaded_sources','epg_sources.py')
        self.assertEqual(other.configuration('p')['mappings'],{'1':'station.id'})
        self.assertEqual(Path(other._file_path()).read_bytes(),config)

    @staticmethod
    def programme(start='20261018120000 +0200', stop='20261018130000 +0200'):
        return f'<programme channel="one" start="{start}" stop="{stop}"><title>Film</title></programme>'

    def test_invalid_dates_offsets_missing_fields_and_intervals_are_isolated(self):
        invalid = [('20261318120000 +0200','20261018130000 +0200'),
                   ('20261018120000 +0260','20261018130000 +0200'),
                   ('','20261018130000 +0200'),
                   ('20261018120000 +0200','20261018110000 +0200')]
        content = '<tv>'+self.programme()+''.join(self.programme(a,b) for a,b in invalid)+'</tv>'
        channels,guide = self.epg.parse_xmltv(content.encode())
        self.assertEqual(len(guide['one']),1)
        self.assertTrue(any('skipped 4' in log for log in self.logs))
        self.assertEqual(self.epg._parse_xmltv_ts('20261018100000 +0000'),guide['one'][0]['start_timestamp'])

    def test_gzip_bomb_plain_size_programme_count_and_channels_are_bounded(self):
        with mock.patch.object(self.epg,'MAX_XML_BYTES',256):
            for content in [b'<tv>'+b' '*1000+b'</tv>',gzip.compress(b'<tv>'+b' '*10000+b'</tv>')]:
                with self.assertRaises(ValueError): self.epg.parse_xmltv(content)
        with mock.patch.object(self.epg,'MAX_PROGRAMMES',1):
            with self.assertRaises(ValueError):
                self.epg.parse_xmltv(('<tv>'+self.programme()*2+'</tv>').encode())
        with mock.patch.object(self.epg,'MAX_CHANNELS',1):
            with self.assertRaises(ValueError):
                self.epg.parse_xmltv(b'<tv><channel id="a"/><channel id="b"/></tv>')

    def test_entity_declaration_after_long_comment_is_rejected(self):
        payload=b'<!--'+b' '*17000+b'--><!DOCTYPE tv [<!ENTITY x "expanded">]><tv/>'
        with self.assertRaises(ValueError): self.epg.parse_xmltv(payload)

    def test_failed_or_oversize_refresh_preserves_previous_working_guide(self):
        cached={'one':[{'name':'Existing'}]}
        self.epg._save_disk('p',cached)
        self.epg._mem_set('p',cached)
        with mock.patch.object(self.epg,'http_get',side_effect=ValueError('size exceeded')):
            self.epg._refresh_portal_epg('p',{'id':'p','type':'m3u','epg_url':'https://example.invalid/a'})
        self.assertEqual(self.epg.load_cache('p'),cached)

    def test_combined_sources_have_budget_and_keep_provider_and_mapping(self):
        self.sources.add_source('p','A','https://example.invalid/a')
        self.sources.add_source('p','B','https://example.invalid/b')
        self.sources.set_mapping('p','1','native')
        with mock.patch.object(self.sources,'_read_source',side_effect=[b'a',b'b']), mock.patch.object(self.sources,'MAX_PROGRAMMES',2):
            result,ok,failed=self.sources.merge_sources('p',{'native':[{'name':'provider'}]},
                lambda raw:({raw.decode():raw.decode()},{raw.decode():[{'name':'external'}]}))
        self.assertEqual((ok,failed),(1,1))
        self.assertEqual(result['1'][0]['name'],'provider')
        self.assertNotIn('b',result)

    def test_manual_refresh_closes_directory_then_schedules_worker(self):
        tree=ast.parse((LIB/'main.py').read_text())
        router=next(n for n in tree.body if isinstance(n,ast.ClassDef) and n.name=='Router')
        method=next(n for n in router.body if isinstance(n,ast.FunctionDef) and n.name=='_refresh_epg')
        events=[]
        module=types.ModuleType('epg')
        module.warmup_async=lambda *a,**kw:events.append('scheduled')
        portals=types.ModuleType('portals')
        portals.get_by_id=lambda _:dict(id='p')
        ns=dict(notify=lambda *a,**kw:events.append('notified'),
                xbmcplugin=types.SimpleNamespace(endOfDirectory=lambda *a,**kw:events.append('closed')))
        exec(compile(ast.Module(body=[method],type_ignores=[]),'main refresh','exec'),ns)
        with mock.patch.dict(sys.modules,dict(epg=module,portals=portals)):
            ns['_refresh_epg'](types.SimpleNamespace(_params={'pid':'p'},_handle=7))
        self.assertEqual(events,['closed','scheduled','notified'])

    def test_http_backends_function_against_local_streaming_server(self):
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args): pass
            def do_GET(self):
                body=b'<tv/>' if self.path=='/plain' else gzip.compress(b'<tv/>')
                if self.path=='/large': body=b'x'*1000
                self.send_response(200)
                if self.path=='/gzip': self.send_header('Content-Encoding','gzip')
                self.send_header('Content-Length',str(len(body)))
                self.end_headers()
                self.wfile.write(body)
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True)
        thread.start()
        try:
            backends=[False,True] if self.utils.HAVE_HTTPX else [False]
            for backend in backends:
                with self.subTest(httpx=backend), mock.patch.object(self.utils,'HAVE_HTTPX',backend):
                    base=f'http://127.0.0.1:{server.server_port}'
                    for path in ['/plain','/gzip']:
                        data,_=self.utils.http_get(base+path,max_bytes=64,max_seconds=5)
                        self.assertEqual(data,b'<tv/>')
                    with self.assertRaises(ValueError):
                        self.utils.http_get(base+'/large',max_bytes=32,max_seconds=5)
        finally:
            server.shutdown()
            server.server_close()
            thread.join(timeout=2)


class HTTPBudgetTests(unittest.TestCase):
    def test_stops_consuming_oversize_chunks(self):
        consumed=[]
        def chunks():
            for i in range(100):
                consumed.append(i)
                yield b'x'*16
        with self.assertRaises(ValueError):
            read_http_chunks(chunks(),{},32,time.monotonic()+5)
        self.assertEqual(consumed,[0,1,2])

    def test_http_gzip_is_bounded_before_full_expansion(self):
        with self.assertRaises(ValueError):
            read_http_chunks([gzip.compress(b'x'*1000000)],{'Content-Encoding':'gzip'},1024,time.monotonic()+5)
        self.assertEqual(read_http_chunks([gzip.compress(b'hello')],{'Content-Encoding':'gzip'},100,time.monotonic()+5),b'hello')

    def test_truncated_gzip_and_expired_budget_fail(self):
        with self.assertRaises(ValueError):
            read_http_chunks([gzip.compress(b'hello')[:-5]],{'Content-Encoding':'gzip'},100,time.monotonic()+5)
        with self.assertRaises(TimeoutError):
            read_http_chunks([b'hello'],{},100,time.monotonic()-1)

    def test_xmltv_deadline_and_split_declaration(self):
        reader=XMLTVReader(b'<!DOCTYPE tv><tv/>')
        self.addCleanup(reader.close)
        self.assertEqual(reader.read(5),b'<!DOC')
        with self.assertRaises(ValueError):reader.read(100)
        reader=XMLTVReader(b'<tv/>')
        self.addCleanup(reader.close)
        reader._deadline=0
        with self.assertRaises(TimeoutError):reader.read(1)


if __name__=='__main__': unittest.main()
