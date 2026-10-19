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

    def test_atomic_failed_cache_write_keeps_previous_bytes_and_reports_epg_failure(self):
        self.epg._save_disk('p',{'old':[{'name':'Previous'}]})
        path=self.root/'profile/cache'/(self.epg._disk_ck('p')+'.json')
        previous=path.read_bytes()
        self.vfs.refuse_writes.add(str(path.parent))
        with self.assertRaises(OSError): self.epg._save_disk('p',{'new':[]})
        self.assertEqual(path.read_bytes(),previous)
        self.assertFalse(list(path.parent.glob('.xcmate-cache-*')))

    def test_private_fallback_wins_over_older_custom_cache_and_survives_reload(self):
        selected=self.select_folder()
        self.utils.cache_set('e'*32,{'name':'old'})
        self.vfs.refuse_writes.add(selected)
        self.assertTrue(self.utils.cache_set('e'*32,{'name':'new'}))
        self.vfs.refuse_writes.clear()
        other=load('fresh_cache_reader','utils.py')
        self.assertEqual(other.cache_get('e'*32),{'name':'new'})

    def test_expired_refresh_ttl_keeps_valid_old_epg_without_marking_it_fresh(self):
        import json
        old={'x':[{'name':'Retained'}]}
        self.epg._save_disk('p',old)
        path=self.root/'profile/cache'/(self.epg._disk_ck('p')+'.json')
        raw=json.loads(path.read_text())
        raw['ts']-=2*86400
        path.write_text(json.dumps(raw))
        self.epg._mem_clear('p')
        self.assertEqual(self.epg.load_cache('p'),old)
        self.assertFalse(self.epg._is_fresh('p'))

    def test_eight_day_old_ten_day_guide_stays_available_to_frozen_infobar(self):
        import json
        now=time.time()
        retained={'x':[dict(name='Still current',start_timestamp=now-60,stop_timestamp=now+1800)]}
        self.epg._save_disk('p',retained)
        path=self.root/'profile/cache'/(self.epg._disk_ck('p')+'.json')
        raw=json.loads(path.read_text());raw['ts']-=8*86400;path.write_text(json.dumps(raw))
        self.epg._mem_clear('p')
        self.assertEqual(self.epg.load_cache('p'),retained)
        self.assertFalse(self.epg._is_fresh('p'))
        raw['ts']-=3*86400;path.write_text(json.dumps(raw));self.epg._mem_clear('p')
        self.assertEqual(self.epg.load_cache('p'),{})

    def test_obsolete_but_valid_xmltv_never_overwrites_working_cache(self):
        old={'old':[{'name':'Retained'}]}
        self.epg._save_disk('p',old)
        raw=b'<tv><programme channel="one" start="20200101120000 +0000" stop="20200101130000 +0000"><title>Old</title></programme></tv>'
        with mock.patch.object(self.epg,'http_get',return_value=(raw,{})):
            result=self.epg._refresh_portal_epg('p',dict(id='p',type='m3u',epg_url='https://example.invalid'))
        self.assertEqual(result,{})
        self.epg._mem_clear('p')
        self.assertEqual(self.epg.load_cache('p'),old)

    def test_real_programme_on_day_nine_is_a_usable_guide_not_obsolete(self):
        start=time.time()+8*86400
        stamp=lambda ts:time.strftime('%Y%m%d%H%M%S +0000',time.gmtime(ts))
        raw=('<tv><programme channel="one" start="'+stamp(start)+'" stop="'+stamp(start+3600)+'"><title>Day nine</title></programme></tv>').encode()
        with mock.patch.object(self.epg,'http_get',return_value=(raw,{})):
            self.epg._refresh_portal_epg('p',dict(id='p',type='m3u',epg_url='https://example.invalid'))
        self.epg._mem_clear('p')
        self.assertEqual(self.epg.load_cache('p')['one'][0]['name'],'Day nine')

    def test_import_mapping_persistence_to_real_local_tv_snapshot(self):
        from epg_status import read
        self.sources.add_source('p','Test','https://example.invalid/guide')
        self.sources.set_mapping('p','7','one')
        now=time.time()
        stamp=lambda ts:time.strftime('%Y%m%d%H%M%S +0000',time.gmtime(ts))
        raw=('<tv><channel id="one"><display-name>Station</display-name></channel>'+
             self.programme(stamp(now-600),stamp(now+600))+self.programme(stamp(now+600),stamp(now+1800))+'</tv>').encode()
        client=types.SimpleNamespace(_get_json=mock.Mock(side_effect=AssertionError('manual mapping must win')))
        logos=types.ModuleType('logo_cache');logos.request=lambda _:None
        with mock.patch.dict(sys.modules,{'epg':self.epg,'epg_sources':self.sources,'logo_cache':logos}), \
             mock.patch.object(self.sources,'_read_source',return_value=gzip.compress(raw)):
            self.epg._refresh_portal_epg('p',dict(id='p',type='m3u'))
            self.epg._mem_clear('p')
            data=load('end_to_end_tv_data','tv_data.py')
            snapshot=data.GuideSnapshot(dict(id='p',type='xtream'),client)
            snapshot.request([types.SimpleNamespace(name='Station',tvg_id='wrong',logo='',extra={'stream_id':'7'})])
            snapshot.refresh()
            info=snapshot.get('7')
        self.assertEqual((info['now'],info['next']),('Film','Film'))
        self.assertEqual(info['mapping'],'MANUAL')
        self.assertTrue(0<info['progress']<1)
        self.assertEqual(self.sources.configuration('p')['mappings'],{'7':'one'})
        status=read('p')
        self.assertEqual(status['cache']['code'],'READY')

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

    def test_external_failures_distinguish_download_gzip_xml_and_empty_guide(self):
        first = self.sources.add_source('p','Disabled','https://example.invalid/disabled')
        self.sources.edit_source('p',first['id'],'toggle')
        self.sources.add_source('p','Active','https://private.invalid/token')
        config = Path(self.sources._file_path()).read_bytes()
        diagnostic = types.ModuleType('live_diagnostics')
        diagnostic.record = mock.Mock()
        payloads = [(gzip.compress(b'<tv/>')[:-5], 'GZIP_INVALID', 'EOFError'),
                    (b'<tv><programme>', 'INVALID_XMLTV', 'ParseError'),
                    (b'<tv/>', 'EMPTY_GUIDE', 'EmptyGuideError')]
        with mock.patch.dict(sys.modules, {'live_diagnostics':diagnostic}):
            for raw, code, exception in payloads:
                with self.subTest(code=code), mock.patch.object(self.sources,'_read_source',return_value=raw):
                    diagnostic.record.reset_mock()
                    result,ok,failed = self.sources.merge_sources('p',{'old':[{'name':'Kept'}]},
                                                                 self.epg.parse_xmltv)
                    self.assertEqual((ok,failed),(0,1))
                    self.assertIn('old',result)
                    calls = diagnostic.record.call_args_list
                    self.assertEqual(calls[0].args,('epg_source','READ'))
                    self.assertEqual(calls[-1].args,('epg_source',code))
                    self.assertEqual(calls[-1].kwargs['failure_stage'],'PARSE')
                    self.assertEqual(calls[-1].kwargs['source_index'],2)
                    self.assertEqual(calls[-1].kwargs['exception_class'],exception)
                    self.assertEqual(calls[-1].kwargs['bytes'],len(raw))
            with mock.patch.object(self.sources,'_read_source',side_effect=OSError('private://secret')):
                self.sources.merge_sources('p',{},self.epg.parse_xmltv)
            self.assertEqual(diagnostic.record.call_args.args,('epg_source','DOWNLOAD_FAILED'))
            self.assertEqual(diagnostic.record.call_args.kwargs['failure_stage'],'DOWNLOAD')
        self.assertEqual(Path(self.sources._file_path()).read_bytes(),config)
        self.assertFalse(any('private://' in log or '/token' in log for log in self.logs))

    def test_provider_limit_reason_and_no_new_guide_keep_old_cache(self):
        old = {'old':[{'name':'Cached'}]}
        self.epg._save_disk('p',old)
        self.epg._mem_set('p',old)
        diagnostic = types.ModuleType('live_diagnostics')
        diagnostic.record = mock.Mock()
        diagnostic.checkpoint = lambda:None
        raw = ('<tv>'+self.programme()*2+'</tv>').encode()
        with mock.patch.dict(sys.modules,{'live_diagnostics':diagnostic}), \
             mock.patch.object(self.epg,'http_get',return_value=(raw,{})), \
             mock.patch.object(self.epg,'MAX_PROGRAMMES',1):
            self.epg._refresh_portal_epg('p',dict(id='p',type='m3u',epg_url='https://example.invalid'))
        limit = next(c for c in diagnostic.record.call_args_list if c.args[1]=='PROVIDER_LIMIT')
        self.assertEqual(limit.kwargs['failure_stage'],'PARSE')
        self.assertEqual(limit.kwargs['limit_kind'],'programmes')
        self.assertNotIn('limit_bytes',limit.kwargs)
        self.assertEqual(diagnostic.record.call_args.args,('epg','NO_NEW_GUIDE'))
        self.assertEqual(self.epg.load_cache('p'),old)

    def test_http_and_xmltv_input_and_decoded_byte_limits_are_distinct(self):
        from epg_errors import failure_details
        cases = [('DOWNLOAD', lambda:read_http_chunks([b'x'*65],{},64,time.monotonic()+5),'input_bytes'),
                 ('DOWNLOAD', lambda:read_http_chunks([gzip.compress(b'x'*1024)],
                    {'content-encoding':'gzip'},64,time.monotonic()+5),'decoded_bytes'),
                 ('PARSE', lambda:XMLTVReader(b'x'*65,max_bytes=64),'input_bytes'),
                 ('PARSE', lambda:XMLTVReader(gzip.compress(b'x'*1024),max_bytes=64).read(),
                    'decoded_bytes')]
        for stage, action, kind in cases:
            with self.subTest(stage=stage,kind=kind):
                try: action()
                except ValueError as exc:
                    code,fields=failure_details(exc,stage)
                    self.assertEqual(fields['limit_kind'],kind)
                    self.assertIn(kind.upper(),code)
                else: self.fail('Expected a bounded size failure')

    def test_truncated_http_gzip_has_a_transport_compression_error(self):
        from epg_errors import failure_details
        from network_io import HTTPCompressionError
        try:
            read_http_chunks([gzip.compress(b'guide')[:-5]],{'content-encoding':'gzip'},
                             1024,time.monotonic()+5)
        except HTTPCompressionError as exc:
            code,fields=failure_details(exc,'DOWNLOAD')
            self.assertEqual(code,'HTTP_COMPRESSION_FAILED')
            self.assertEqual(fields['exception_class'],'HTTPCompressionError')
        else: self.fail('Truncated HTTP gzip accepted')

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
        module.request_refresh=lambda *a,**kw:events.append('scheduled')
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
