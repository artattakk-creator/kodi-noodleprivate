"""Real bounded parser, HTTP, disk and native-callback regressions for 0.1.28."""
import gzip
import importlib
import io
import json
import os
from pathlib import Path
import sqlite3
import sys
import tempfile
import time
import types
import unittest
from unittest import mock

LIB=Path(__file__).resolve().parents[1]/'src/plugin.video.xtreammate/resources/lib'
sys.path.insert(0,str(LIB))
from streaming_json import iter_array,cached_array
from network_io import decoded_chunks,ChunkReader
from xmltv_stream import parse,timestamp,UnsafeXMLTV,XMLTVSyntaxError


class TinyReads(io.BytesIO):
    def read(self,n=-1):
        if n<0 or n>65536: raise AssertionError('unbounded read')
        return super().read(min(n,7))


class ParserTests(unittest.TestCase):
    def test_json_split_utf8_strings_escapes_and_nested_objects(self):
        value=[dict(name='Über \\" { test }',nested=[dict(a=[1,2])]),dict(name='Last')]
        self.assertEqual(list(iter_array(TinyReads(json.dumps(value,ensure_ascii=False).encode()))),value)

    def test_cache_envelope_and_trailing_data_validated(self):
        for raw in (b'[]',b'{"ts":1.2,"data":[]}'):
            self.assertEqual(list(cached_array(io.BytesIO(raw))),[])
        for raw in (b'[{}',b'[{},]',b'[1]',b'[{}]evil',b'{}',b'[{"a":NaN}]'):
            with self.subTest(raw=raw),self.assertRaises(ValueError): list(iter_array(TinyReads(raw)))

    def test_item_and_nesting_budgets_without_collection_cap(self):
        with self.assertRaises(ValueError): list(iter_array(io.BytesIO(b'[{"name":"'+b'a'*524289+b'"}]')))
        with self.assertRaises(ValueError): list(iter_array(io.BytesIO(b'[{"a":'+b'['*65+b'0'+b']'*65+b'}]')))
        with self.assertRaises(InterruptedError): list(iter_array(io.BytesIO(b'[{}]'),lambda:True))

    def test_chunked_http_gzip_and_truncated_compression(self):
        raw=json.dumps([dict(name='Ä'*1000)]).encode();compressed=gzip.compress(raw)
        stream=ChunkReader(decoded_chunks((compressed[i:i+3] for i in range(0,len(compressed),3)),{'Content-Encoding':'gzip'},time.monotonic()+5))
        self.assertEqual(list(iter_array(stream))[0]['name'],'Ä'*1000)
        with self.assertRaises(ValueError):
            list(decoded_chunks([compressed[:-4]],{'Content-Encoding':'gzip'},time.monotonic()+5))

    def test_numeric_timestamp_avoids_kodi_lazy_strptime_worker_import(self):
        # Embedded Kodi can fail lazy _strptime imports. The shared parser no
        # longer needs it; this does not assert it was the user's exact stack.
        with mock.patch.dict(sys.modules,_strptime=None):
            self.assertEqual(timestamp('20261019203000 +0200'),1792434600)
        for value in ('20260230000000 +0000','20261019000000 +2460',None,'broken'):
            with self.assertRaises(ValueError): timestamp(value)

    def test_xml_gzip_bad_programme_isolated_and_no_element_tree(self):
        raw=b'<tv><channel id="a"><display-name>ARD HD</display-name></channel><programme channel="a" start="bad" stop="bad"/><programme channel="a" start="20261019000000 +0000" stop="20261019010000 +0000"><title>Real</title><desc>Details</desc></programme></tv>'
        channels=[];events=[]
        for data in (raw,gzip.compress(raw)):
            channels.clear();events.clear()
            result=parse(TinyReads(data),lambda *a:channels.append(a),events.append)
            self.assertEqual((result['skipped'],len(events)),(1,1));self.assertEqual(events[0]['name'],'Real')
            self.assertEqual(channels,[('a','ARD HD')])

    def test_standard_xmltv_doctype_is_inert_but_undeclared_entities_rejected(self):
        counts=parse(io.BytesIO(b'<!DOCTYPE tv SYSTEM "xmltv.dtd"><tv/>'),lambda *a:None,lambda e:None)
        self.assertEqual(counts['programmes'],0)
        with self.assertRaises(UnsafeXMLTV):
            parse(io.BytesIO(b'<!DOCTYPE tv SYSTEM "xmltv.dtd"><tv><programme><title>&secret;</title></programme></tv>'),lambda *a:None,lambda e:None)

    def test_xml_syntax_entities_depth_field_and_gzip_classified(self):
        for raw in (b'<!DOCTYPE tv SYSTEM "https://evil.invalid/secret"><tv/>',b'<!DOCTYPE tv [<!ENTITY x "bad">]><tv/>'):
            with self.assertRaises(UnsafeXMLTV): parse(io.BytesIO(raw),lambda *a:None,lambda e:None)
        with self.assertRaises(XMLTVSyntaxError): parse(io.BytesIO(b'<html/>'),lambda *a:None,lambda e:None)
        with self.assertRaises(XMLTVSyntaxError): parse(io.BytesIO(b'<tv><channel>'),lambda *a:None,lambda e:None)
        from epg_io import XMLTVLimitError
        with self.assertRaises(XMLTVLimitError): parse(io.BytesIO(b'<tv><programme><desc>'+b'x'*300000+b'</desc></programme></tv>'),lambda *a:None,lambda e:None)
        with self.assertRaises((EOFError,OSError)): parse(io.BytesIO(gzip.compress(b'<tv/>')[:-5]),lambda *a:None,lambda e:None)


class IndexTests(unittest.TestCase):
    def setUp(self):
        temp=tempfile.TemporaryDirectory();self.addCleanup(temp.cleanup);self.folder=Path(temp.name)
        self.options={};self.portal=dict(id='p',type='xtream')
        utils=types.ModuleType('utils');utils.addon_data_dir=lambda:str(self.folder)
        utils.setting_int=lambda k,d=0:d;utils.setting=lambda k,d='':self.options.get(k,d)
        utils.cache_dir=utils._private_cache_dir=lambda:str(self.folder);utils.warn=utils.error=lambda *a:None
        import hashlib
        utils.cache_key=lambda s:hashlib.md5(s.encode()).hexdigest()
        utils.cache_get=lambda *a,**kw:None;utils.cache_set=lambda *a,**kw:True;utils.http_get=mock.Mock()
        patch=mock.patch.dict(sys.modules,utils=utils);patch.start();self.addCleanup(patch.stop)
        self.index=importlib.import_module('library_index');self.groups=importlib.import_module('group_selection')
        self.categories=[dict(category_id='a',category_name='A'),dict(category_id='b',category_name='B')]
        self.client=types.SimpleNamespace(get_cached_catalog=lambda a:self.categories,_get_json=mock.Mock())

    def seed(self,kind='vod'):
        self.index.replace_catalog('p',kind,[dict(stream_id='old',series_id='old',category_id='a',name='Previous')],self.categories)

    def test_streaming_group_publishes_only_after_complete_json(self):
        self.seed();reader=self.index.Reader('p');seen=[]
        def source():
            for n in range(600):
                yield dict(stream_id=str(n),category_id='a',name='Über den Wolken')
                if n in (256,512): seen.append(reader.page('vod')[1])
        self.index.import_group('p','vod','a',source())
        self.assertEqual(seen,[1,1]);self.assertEqual(reader.page('vod','uber')[1],600)

    def test_interrupted_disk_full_malformed_and_cancelled_keep_previous_generation(self):
        self.seed()
        def source():
            yield from (dict(stream_id=str(n),category_id='a',name='Partial') for n in range(300))
            raise ValueError('secret URL not diagnostic output')
        with self.assertRaises(ValueError): self.index.import_group('p','vod','a',source())
        with mock.patch('import_budget.check_space',side_effect=OSError(28,'full')):
            with self.assertRaises(OSError): self.index.import_group('p','vod','a',iter([]))
        with self.assertRaises(InterruptedError):
            self.index.import_group('p','vod','a',[dict(stream_id='new',category_id='a')],cancel=lambda:True)
        self.assertEqual(self.index.Reader('p').page('vod')[0][0]['sid'],'old')

    def test_only_enabled_categories_preferred_first_and_provider_ignores_filter(self):
        self.groups.save('p',['a'],kind='vod',known=['a','b'])
        calls=[]
        def stream(action,cid,**kwargs):
            calls.append((action,cid));yield dict(stream_id='1',category_id='a',name='Allowed');yield dict(stream_id='2',category_id='b',name='Disabled')
        self.client.iter_catalog=stream
        self.index.sync_kind(self.portal,self.client,'vod',preferred='a',force=True)
        self.assertEqual(calls,[('get_vod_streams','a')]);self.assertEqual(self.index.Reader('p').page('vod')[1],1)
        self.assertEqual(self.index.sync_state('p','vod')[0]['discarded'],1)
        self.assertIsNone(self.index.Reader('p').state('series'))
        self.groups.save('p',['a','b'],kind='vod',known=['a','b']);calls.clear()
        self.index.sync_kind(self.portal,self.client,'vod',preferred='b',force=True)
        self.assertEqual([cid for _,cid in calls],['b'])  # ignored filter: all active groups imported once

    def test_restart_offline_previous_index_and_immediate_disabled_filter(self):
        self.seed();self.client.iter_catalog=mock.Mock(side_effect=OSError('offline'))
        self.index.sync_kind(self.portal,self.client,'vod',force=True)
        other=self.index.Reader('p');self.assertEqual(other.page('vod')[1],1)
        self.assertEqual(self.index.sync_state('p','vod')[0]['code'],'FAILED')
        self.groups.save('p',[],kind='vod',known=['a','b']);self.assertEqual(other.page('vod')[1],0)

    def test_corrupt_index_reports_read_error_instead_of_zero_results(self):
        (self.folder/'library_v1.sqlite').write_bytes(b'corrupt database')
        with self.assertRaises(self.index.IndexReadError): self.index.Reader('p').page('vod','known')

    def test_first_streaming_baseline_is_not_all_new_and_later_discovery_is_real(self):
        self.index.import_group('p','vod','a',[dict(stream_id='1',category_id='a',name='Undated')])
        self.assertIsNone(self.index.Reader('p').get('vod','1')['added_at'])
        self.index.import_group('p','vod','a',[dict(stream_id='1',category_id='a',name='Undated'),dict(stream_id='2',category_id='a',name='Discovered')])
        reader=self.index.Reader('p')
        self.assertIsNone(reader.get('vod','1')['added_at'])
        self.assertGreater(reader.get('vod','2')['added_at'],time.time()-10)

    def test_completed_categories_resume_and_disabled_category_is_never_fetched(self):
        calls=[]
        def stream(action,cid,**kwargs):
            calls.append(cid);yield dict(series_id=cid,category_id=cid,name=cid)
        self.client.iter_catalog=stream
        requested=time.time()
        more=self.index.sync_kind(self.portal,self.client,'series',preferred='b',force=True,max_groups=1,requested_at=requested)
        # Use the correct series ID to exercise the same source with identity.
        self.assertTrue(more);self.assertEqual(calls,['b'])
        self.index.sync_kind(self.portal,self.client,'series',preferred='b',force=True,max_groups=1,requested_at=requested)
        self.assertEqual(calls,['b','a']);self.assertEqual(self.index.Reader('p').page('series')[1],2)

    def test_same_stream_in_two_groups_counted_once_globally_but_available_in_each(self):
        rows=[dict(stream_id='1',category_id=cid,name='Shared title') for cid in ('a','b')]
        self.index.import_group('p','vod','a',rows,allowed={'a','b'})
        reader=self.index.Reader('p')
        self.assertEqual(reader.page('vod','shared')[1],1)
        self.assertEqual(reader.page('vod',category='a')[1],1)
        self.assertEqual(reader.page('vod',category='b')[1],1)
        self.groups.save('p',['b'],kind='vod',known=['a','b'])
        self.assertEqual(reader.page('vod','shared')[0][0]['category_id'],'b')
        self.assertFalse(self.index.replace_catalog('p','vod',{},self.categories))
        self.assertEqual(reader.page('vod','shared')[1],1)

    def test_requests_deduplicate_and_promote_visible_group(self):
        self.index.request_sync(self.portal,'vod','a',20)
        self.index.request_sync(self.portal,'vod','b',1,True)
        db=self.index.connect()
        try:
            jobs=db.execute('SELECT * FROM sync_requests').fetchall()
            self.assertEqual(len(jobs),1);self.assertEqual((jobs[0]['preferred'],jobs[0]['priority'],jobs[0]['force']),('b',1,1))
        finally: db.close()

    def test_catalogue_failure_diagnostic_has_frames_without_secret_message(self):
        from import_budget import safe_failure
        try: raise ValueError('https://user:SECRET@provider.invalid/')
        except ValueError as exc: fields=safe_failure(exc)
        self.assertNotIn('SECRET',json.dumps(fields));self.assertTrue(fields['frames'])


class LargeHTTPTests(unittest.TestCase):
    def test_real_http_over_80mib_and_200000_titles_into_sqlite_over_64mib(self):
        # A generated HTTP stream, not a preallocated response or mocked parser.
        # The same path handles VOD and series IDs; both kinds remain isolated.
        from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
        import threading
        from test_xcmate_epg_limits import CacheAndEPGTests
        CacheAndEPGTests.setUp(self)
        index=importlib.import_module('library_index')
        total=200005
        template=b'{"stream_id":"%d","name":"Film %d Uber den Wolken","category_id":"a","plot":"'+b'x'*460+b'"}'
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args): pass
            def do_GET(self):
                self.send_response(200);self.send_header('Content-Type','application/json');self.end_headers()
                self.wfile.write(b'[')
                for base in range(0,total,256):
                    selected=template.replace(b'stream_id',b'series_id') if self.path=='/series' else template
                    chunk=b','.join(selected%(n,n) for n in range(base,min(total,base+256)))
                    if base: self.wfile.write(b',')
                    self.wfile.write(chunk)
                self.wfile.write(b']')
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler)
        thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        results=[]
        try:
            for kind,suffix in (('vod','/vod'),('series','/series')):
                started=time.monotonic()
                with mock.patch.object(self.utils,'HAVE_HTTPX',False):
                    with self.utils.http_stream('http://127.0.0.1:'+str(server.server_port)+suffix,max_seconds=300) as stream:
                        counts=index.import_group('large',kind,'a',iter_array(stream))
                        downloaded=stream.total
                reader=index.Reader('large')
                rows,count=reader.page(kind,'uber',offset=total-5,limit=100)
                self.assertEqual((counts['stored'],count,len(rows)),(total,total,5))
                self.assertEqual(rows[-1]['sid'],str(total-1))
                self.assertGreater(downloaded,80*1024*1024)
                size=os.path.getsize(index.path());self.assertGreater(size,64*1024*1024)
                results.append(dict(kind=kind,rows=total,http_bytes=downloaded,sqlite_bytes=size,
                    seconds=round(time.monotonic()-started,3),peak_rss_kib=__import__('resource').getrusage(__import__('resource').RUSAGE_SELF).ru_maxrss))
                if kind=='vod': self.assertIsNone(reader.state('series'))
            self.assertEqual(index.Reader('large').page('vod','uber')[1],total)
            self.assertEqual(index.Reader('large').page('series','uber')[1],total)
        finally: server.shutdown();server.server_close();thread.join(2)
        print('\nLARGE_CATALOGUE '+json.dumps(results),flush=True)


class StreamingEPGTests(unittest.TestCase):
    def setUp(self):
        IndexTests.setUp(self)
        self.epg=importlib.import_module('stream_epg')
        self.guide=importlib.import_module('guide_store')
        sources=importlib.import_module('epg_sources')
        self.streams=[dict(sid='1',category_id='a',name='DE | ARD HD',epg_channel_id='provider.wrong'),
                      dict(sid='2',category_id='a',name='ZDF',epg_channel_id='zdf')]
        self.now=int(time.time())
        import datetime
        self.start=datetime.datetime.fromtimestamp(self.now-60,datetime.timezone.utc).strftime('%Y%m%d%H%M%S +0000')
        self.stop=datetime.datetime.fromtimestamp(self.now+3600,datetime.timezone.utc).strftime('%Y%m%d%H%M%S +0000')
    def source(self,title='News',trailer=''):
        return ('<tv><channel id="ard"><display-name>ARD</display-name></channel><channel id="hidden"><display-name>Disabled</display-name></channel>'
            '<programme channel="ard" start="'+self.start+'" stop="'+self.stop+'"><title>'+title+'</title></programme>'
            '<programme channel="hidden" start="'+self.start+'" stop="'+self.stop+'"><title>Must not persist</title></programme></tv>'+trailer).encode()
    def import_(self,raw,index=0,mappings=None):
        from contextlib import contextmanager
        @contextmanager
        def stream(_): yield io.BytesIO(gzip.compress(raw))
        with mock.patch.object(self.epg,'source_stream',stream):
            return self.epg.import_source('p',dict(uri='redacted'),index,self.streams,mappings or {})
    def test_real_gzip_import_name_match_active_filter_shared_fast_snapshot(self):
        counts=self.import_(self.source());self.assertEqual(counts['stored'],1)
        rows,count=self.guide.events('p','1',self.now,self.now+7200)
        self.assertEqual((count,rows[0]['title']),(1,'News'))
        self.assertEqual(self.guide.events('p','hidden',self.now,self.now+7200)[1],0)
        cache=self.epg.fast_snapshot('p',self.streams,{})
        self.assertEqual(cache['1'][0]['name'],'News');self.assertEqual(cache['ard'][0]['name'],'News')
    def test_bad_xml_and_disk_full_leave_old_guide_and_mapping(self):
        self.import_(self.source())
        with self.assertRaises(XMLTVSyntaxError): self.import_(self.source('Wrong','<broken'))
        with mock.patch('import_budget.check_space',side_effect=OSError(28,'full')):
            with self.assertRaises(OSError): self.import_(self.source('Full'))
        rows,count=self.guide.events('p','1',self.now,self.now+7200)
        self.assertEqual((count,rows[0]['title']),(1,'News'))
    def test_existing_guide_readable_when_no_space_remains_for_import(self):
        self.import_(self.source())
        with mock.patch('import_budget.check_space',side_effect=OSError(28,'full')):
            rows,total=self.guide.events('p','1',self.now,self.now+7200)
        self.assertEqual((total,rows[0]['title']),(1,'News'))

    def test_saved_ten_day_guide_reused_even_with_only_small_fast_snapshot(self):
        self.seed=IndexTests.seed.__get__(self)
        self.index.replace_catalog('p','live',[dict(stream_id='1',category_id='a',name='TV',epg_channel_id='x')],self.categories)
        event=dict(channel='x',name='Real long coverage',start_timestamp=self.now-10,stop_timestamp=self.now+10*86400)
        self.guide.import_cache('p',{'1':[event],'x':[event]})
        sources=types.SimpleNamespace(configuration=lambda pid:dict(mappings={}))
        with mock.patch.dict(sys.modules,epg_sources=sources): self.assertTrue(self.guide.covers_active(self.portal))

    def test_source_priority_partial_failure_and_manual_mapping(self):
        self.import_(self.source('Provider'),0)
        self.import_(self.source('External'),1,{'1':'ard'})
        rows,count=self.guide.events('p','1',self.now,self.now+7200)
        self.assertEqual((count,rows[0]['title']),(1,'Provider'))
        self.assertEqual(self.epg.fast_snapshot('p',self.streams,{'1':'ard'})['1'][0]['name'],'Provider')


class LargeGuideTests(unittest.TestCase):
    def setUp(self): IndexTests.setUp(self)
    def test_streamed_xml_over_80mib_more_than_150000_programmes_and_later_short_update(self):
        from contextlib import contextmanager
        epg=importlib.import_module('stream_epg');guide=importlib.import_module('guide_store')
        import datetime
        start=int(time.time())-10;total=160005
        def chunks():
            yield b'<tv><channel id="xml"><display-name>TV</display-name></channel>'
            for n in range(total):
                begin=datetime.datetime.fromtimestamp(start+n*4,datetime.timezone.utc).strftime('%Y%m%d%H%M%S +0000')
                end=datetime.datetime.fromtimestamp(start+(n+1)*4,datetime.timezone.utc).strftime('%Y%m%d%H%M%S +0000')
                yield ('<programme channel="xml" start="'+begin+'" stop="'+end+'"><title>Programme '+str(n)+'</title><desc>'+'d'*460+'</desc></programme>').encode()
            yield b'</tv>'
        streams=[dict(sid='1',name='TV',epg_channel_id='xml')]
        @contextmanager
        def source(_): yield ChunkReader(chunks())
        started=time.monotonic()
        with mock.patch.object(epg,'source_stream',source):
            counts=epg.import_source('p',{},0,streams,{})
        self.assertGreater(counts['bytes'],80*1024*1024)
        self.assertGreater(guide.horizon('p','xml')['programmes'],150000)
        size=os.path.getsize(guide.path());self.assertGreater(size,80*1024*1024)
        future=guide.horizon('p','xml')['last_event']
        guide.import_cache('p',{'xml':[dict(channel='xml',name='Short update',start_timestamp=start+20,stop_timestamp=start+30)]})
        self.assertEqual(guide.horizon('p','xml')['last_event'],future)
        print('\nLARGE_XMLTV '+json.dumps(dict(parsed=counts['programmes'],stored=counts['stored'],xml_bytes=counts['bytes'],sqlite_bytes=size,seconds=round(time.monotonic()-started,3))),flush=True)
