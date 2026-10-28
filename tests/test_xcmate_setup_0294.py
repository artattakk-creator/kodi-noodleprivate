"""Real executor threads + native XML events; no Android rendering claim."""
import importlib
import importlib.util
import io
import json
from pathlib import Path
import sys
import threading
import time
import types
import unittest
from concurrent.futures import wait
from contextlib import contextmanager
from unittest import mock
import xml.etree.ElementTree as ET
from xcmate027_fixture import Fixture,WindowXML,Control,ADDON,LIB


class SetupThreadTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        sys.modules.pop('setup_window',None);self.ui=importlib.import_module('setup_window')
        self.owner=threading.get_ident();self.calls=[];self.violations=[]
        def guard(method):
            def checked(*args,**kwargs):
                self.calls.append(threading.get_ident())
                if threading.get_ident()!=self.owner:
                    self.violations.append(method.__name__);raise AssertionError('GUI accessed from worker')
                return method(*args,**kwargs)
            return checked
        for cls,names in ((WindowXML,('getControl','setFocusId','setProperty','close')),
                          (Control,('setLabel','setText','setVisible','reset','addItems','selectItem'))):
            for name in names:
                patch=mock.patch.object(cls,name,guard(getattr(cls,name)));patch.start();self.addCleanup(patch.stop)
        patch=mock.patch.object(Control,'setPercent',guard(lambda c,p:setattr(c,'percent',p)),create=True);patch.start();self.addCleanup(patch.stop)
        self.data=types.SimpleNamespace(data=dict(id='new',name='Setup',type='xtream'),
            categories={k:[dict(category_id=str(i),category_name=k+' '+str(i)) for i in range(n)] for k,n in (('live',220),('vod',4),('series',0))},
            selected={k:set() for k in ('live','vod','series')},provider_epg=False,epg_sources=[],scanned=False,
            report=dict(live=2400,vod=4,series=0,epg=0,sources=[],warnings=[]),dispose=mock.Mock())
        self.worker_threads=[]
        def discover(cancel,status):
            self.worker_threads.append(threading.get_ident());status(None,'Discovery');return self.data.categories
        self.data.discover=discover
        self.data.scan=lambda cancel,status:self.data.report
        self.data.save=lambda cancel,status:dict(id='new',type='xtream')
        self.window=self.ui.SetupWindow('XCMateSetup.xml',str(ADDON),'Default','720p');self.window.configure(self.data)
        self.addCleanup(self.window._pool.shutdown,wait=True,cancel_futures=True)
        self.addCleanup(self.window.close)
    def finish(self):
        future=self.window._future
        self.assertTrue(wait([future],timeout=3).done)
        self.assertFalse(self.violations)
        self.window.pump()
    def show(self):
        self.window.show();self.finish()
        # .51 intentionally renders bounded batches in the owner pump.
        for _ in range(100):
            if self.window._rendered[self.window.kind]==len(self.window._entries):break
            self.window.pump()
    def test_worker_progress_completion_scan_save_and_close_only_touch_gui_on_owner(self):
        self.show();self.assertEqual(self.window.stage,'groups')
        self.window.setFocusId(17);self.window.native(7);self.finish()
        self.assertEqual(self.window.stage,'summary');self.window.native(7);self.finish()
        self.assertTrue(self.window._closed);self.assertEqual(self.window.result['id'],'new')
        self.assertNotIn(self.owner,self.worker_threads);self.assertFalse(self.violations)
        self.assertTrue(all(t==self.owner for t in self.calls))
    def test_graphical_checkbox_has_no_list_reset_or_scroll_movement(self):
        self.show();control=self.window.getControl(100);control.selectItem(155)
        with mock.patch.object(control,'reset',wraps=control.reset) as reset,mock.patch.object(control,'selectItem',wraps=control.selectItem) as select:
            self.window.native(7)
            self.assertEqual(control.getSelectedPosition(),155);reset.assert_not_called();select.assert_not_called()
            item=control.getListItem(155);self.assertEqual(item.getProperty('setup_selected'),'true')
            self.assertTrue(item.art['icon'].endswith('setup_checked.png'));self.assertNotIn('☑',item.label)
            self.window.native(7);self.assertEqual(item.getProperty('setup_selected'),'false')
            self.assertTrue(item.art['icon'].endswith('setup_unchecked.png'))
        self.assertEqual(self.data.selected['live'],set())
    def test_native_tab_roundtrip_preserves_separate_list_cursors_and_selections(self):
        self.show();w=self.window;w.getControl(100).selectItem(155);w.native(7)
        w.native(1);self.assertEqual(w.getFocusId(),10)
        w.native(2);self.assertEqual(w.getFocusId(),11)
        w.native(7);self.assertEqual((w.kind,w.getFocusId()),('vod',101))
        w.getControl(101).selectItem(2);w.native(7)
        w.native(1);w.native(1);w.native(7)
        self.assertEqual((w.kind,w.getControl(100).getSelectedPosition()),('live',155))
        self.assertEqual(self.data.selected['live'],{'155'});self.assertEqual(self.data.selected['vod'],{'2'})
        self.assertEqual(w.getProperty('XCMate.SetupKind'),'live')
    def test_empty_tab_count_and_bottom_controls_remain_navigable(self):
        self.show();w=self.window;w.setFocusId(12);w.native(7)
        self.assertEqual(w.kind,'series');self.assertTrue(w.getControl(6).visible)
        self.assertFalse(w.getControl(102).visible);self.assertEqual(w.getFocusId(),17)
        self.assertIn('0',w.getControl(5).label)
        for key in (1,1,2,2):w.native(key);self.assertIn(w.getFocusId(),(16,17,18))
    def test_select_all_none_keeps_list_and_other_kind_selection(self):
        self.show();w=self.window;self.data.selected['vod']={'2'}
        control=w.getControl(100);control.selectItem(170)
        with mock.patch.object(control,'reset',wraps=control.reset) as reset:
            w.onClick(13);self.assertEqual(len(self.data.selected['live']),220)
            w.onClick(14);self.assertEqual(self.data.selected['live'],set());reset.assert_not_called()
        self.assertEqual(control.getSelectedPosition(),170);self.assertEqual(self.data.selected['vod'],{'2'})
    def test_close_during_real_worker_defers_cleanup_and_never_applies_late_result(self):
        started=threading.Event();release=threading.Event()
        def delayed(cancel,status):started.set();release.wait(2);status(None,'late');return self.data.categories
        self.data.discover=delayed;self.window.show();self.assertTrue(started.wait(2))
        self.window.native(92);self.assertTrue(self.window._closed);calls=len(self.calls)
        self.assertFalse(self.data.dispose.called);release.set();self.window._pool.shutdown(wait=True)
        self.assertIsNone(self.window.result);self.assertEqual(len(self.calls),calls)
        self.data.dispose.assert_called_once();self.assertFalse(self.violations)
    def test_owner_loop_processes_completion_without_any_keypress(self):
        xbmc=sys.modules['xbmc'];iterations=[]
        def tick(_):
            iterations.append(1)
            future=self.window._future
            if future is not None:wait([future],timeout=2)
            return self.window.stage=='groups'
        with mock.patch.object(xbmc,'Monitor',return_value=types.SimpleNamespace(waitForAbort=tick),create=True):
            self.window.run()
        self.assertEqual(self.window.stage,'groups');self.assertTrue(iterations)
        self.assertFalse(self.violations)
    def test_xml_uses_owned_focus_bitmaps_active_tab_markers_and_real_translations(self):
        tree=ET.parse(ADDON/'resources/skins/Default/720p/XCMateSetup.xml')
        for ident in (100,101,102):
            node=tree.find("./controls/control[@id='"+str(ident)+"']")
            self.assertEqual(node.find('focusedlayout/control/texture').text.rsplit('/',1)[-1],'wizard_plain51.png')
            self.assertEqual(node.find('focusedlayout/control/texture').get('colordiffuse'),'FF72D7F4')
            self.assertIn('ListItem.Art(icon)',ET.tostring(node).decode())
            self.assertNotIn('☐',ET.tostring(node).decode())
        for ident in (110,111,112):self.assertIn('Window.Property(XCMate.SetupKind)',tree.find("./controls/control[@id='"+str(ident)+"']/visible").text)
        from localization import read_catalog
        for locale in ('de_de','en_gb'):
            catalog=read_catalog(ADDON/('resources/language/resource.language.'+locale+'/strings.po'))
            self.assertIn('2',catalog[32780].format(2,43));self.assertNotIn('#32781',catalog[32781])


class StorageTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('setup_draft','source_adapters'):sys.modules.pop(name,None)
        sys.modules['utils'].cache_key=lambda text:__import__('hashlib').sha256(text.encode()).hexdigest()
        sys.modules['utils'].cache_get=lambda *a,**k:None
        for name in ('portals','epg_sources'):
            spec=importlib.util.spec_from_file_location(name,LIB/(name+'.py'));module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);sys.modules[name]=module
        self.portals=sys.modules['portals'];self.portals.save_all([self.portal])
        self.sources=sys.modules['epg_sources'];sys.modules['epg_status'].changed=lambda *a:None
        def open_vfs(uri):
            stream=open(uri,'rb')
            return types.SimpleNamespace(readBytes=stream.read,close=stream.close)
        sys.modules['xbmcvfs'].File=open_vfs
        sys.modules['utils'].cache_key=lambda text:__import__('hashlib').sha256(text.encode()).hexdigest()
        self.draft=importlib.import_module('setup_draft').Draft(dict(type='xtream',name='New',xc_host='https://provider.invalid',xc_user='user',xc_pass='SECRET'))
        self.addCleanup(self.draft.dispose);self.old=Path(self.portals._db_path()).read_bytes()
        self.draft.adapter=types.SimpleNamespace(authenticate=lambda *a:True,
            categories=lambda kind,remote:[dict(category_id=kind+'-'+str(i),category_name=kind+' '+str(i)) for i in (1,2)],
            entries=self.entries,get_xmltv_epg_url=lambda:None)
        self.draft.discover()
        self.draft.selected={kind:{kind+'-1'} for kind in ('live','vod','series')}
    def entries(self,kind,cid,cancel,allowed):
        for i in range(2400 if kind=='live' else 7 if kind=='vod' else 9):
            if cancel():raise InterruptedError()
            yield dict(name=kind+' '+str(i),category_id=cid,**{'series_id' if kind=='series' else 'stream_id':str(i)})
    def test_2400_channels_separate_movies_series_persistent_readback_and_restart(self):
        messages=[];report=self.draft.scan(status=lambda *p:messages.append(p))
        self.assertEqual((report['live'],report['vod'],report['series']),(2400,7,9))
        self.assertTrue(any(p[0] is None and 'live 1' in p[1] and '256' in p[1] for p in messages))
        portal=self.draft.save();self.assertTrue(self.draft.verification['portal'])
        # Reload actual modules and fresh SQLite connections like a new Kodi interpreter.
        self.portals=importlib.reload(self.portals);index=importlib.reload(self.index)
        self.assertEqual(self.portals.get_by_id(portal['id'])['xc_pass'],'SECRET')
        for kind,n in (('live',2400),('vod',7),('series',9)):
            self.assertEqual(index.Reader(portal['id']).page(kind,limit=1)[1],n)
            groups=importlib.reload(importlib.import_module('group_selection'))
            self.assertEqual(groups.load(portal['id'],kind),{kind+'-1'})
            self.assertFalse(groups._state(groups._read(),portal['id'],kind)['auto_new'])
        self.assertEqual(self.portals.get_by_id('p'),self.portal)
        with self.assertRaisesRegex(ValueError,'SAVE-BUSY'):self.draft.save()
    def test_rescan_removes_deselected_staging_content_and_requires_current_selection(self):
        self.draft.scan();self.draft.selected['live']={'live-2'}
        with self.assertRaisesRegex(ValueError,'RESCAN'):self.draft.save()
        self.draft.selected['vod']=set();self.draft.scan();portal=self.draft.save()
        rows,n=self.index.Reader(portal['id']).page('live',limit=100)
        self.assertEqual(n,2400);self.assertTrue(all(r['category_id']=='live-2' for r in rows))
        self.assertEqual(self.index.Reader(portal['id']).page('vod')[1],0)
    def test_failed_copy_rolls_back_only_new_account_and_allows_retry(self):
        self.draft.scan();original=self.draft._copy
        def fail(source,destination,tables,cancel):
            original(source,destination,tables,cancel);raise OSError('SECRET provider URL')
        with mock.patch.object(self.draft,'_copy',side_effect=fail):
            with self.assertRaises(OSError):self.draft.save()
        self.assertEqual(Path(self.portals._db_path()).read_bytes(),self.old)
        self.assertEqual(self.index.Reader('p').page('vod')[1],100)
        self.assertEqual(self.index.Reader(self.draft.pid).page('live')[1],0)
        portal=self.draft.save();self.assertEqual(self.index.Reader(portal['id']).page('live')[1],2400)
    def test_readback_mismatch_after_publication_removes_only_new_portal(self):
        self.draft.scan();verify=self.draft._verify
        def fail(portal=None):
            if portal:raise self.draft_module_error()
            return verify()
        with mock.patch.object(self.draft,'_verify',side_effect=fail):
            with self.assertRaisesRegex(ValueError,'VERIFY'):self.draft.save()
        self.assertEqual(self.portals.load_all(),[self.portal])
        self.assertEqual(self.index.Reader(self.draft.pid).page('live')[1],0)
        self.assertEqual(self.index.Reader('p').page('vod')[1],100)
    def draft_module_error(self):return importlib.import_module('setup_draft').SaveError('XM-SETUP-VERIFY')
    def test_duplicate_save_in_progress_and_prepublication_cancel_are_safe(self):
        self.draft.scan();self.draft._save_guard.acquire()
        try:
            with self.assertRaisesRegex(ValueError,'SAVE-BUSY'):self.draft.save()
        finally:self.draft._save_guard.release()
        with self.assertRaises(InterruptedError):self.draft.save(cancel=lambda:True)
        self.assertIsNone(self.portals.get_by_id(self.draft.pid))
        self.assertEqual(self.portals.load_all(),[self.portal])
    def test_database_corruption_or_wrong_counts_cannot_report_success(self):
        self.draft.scan();self.draft.report['live']+=1
        with self.assertRaisesRegex(ValueError,'VERIFY'):self.draft.save()
        self.assertFalse(self.draft.saved);self.assertIsNone(self.portals.get_by_id(self.draft.pid))
    def test_optional_epg_failure_after_publication_rolls_back_new_cache_and_guide_only(self):
        import time
        now=int(time.time());stamp=lambda n:time.strftime('%Y%m%d%H%M%S +0000',time.gmtime(n))
        source=self.folder/'optional-guide.xml'
        source.write_text('<tv><channel id="xml"><display-name>live 0</display-name></channel><programme channel="xml" start="'+stamp(now-60)+'" stop="'+stamp(now+3600)+'"><title>Programme</title></programme></tv>')
        self.draft.epg_sources=[dict(id='manual',name='Guide',uri=str(source),local=True,enabled=True)]
        # Attach real XMLTV identity to the synthetic provider's first channel.
        entries=self.draft.adapter.entries
        def with_epg(*args,**kwargs):
            for row in entries(*args,**kwargs):
                if args[0]=='live' and row.get('stream_id')=='0':row['epg_channel_id']='xml'
                yield row
        self.draft.adapter.entries=with_epg
        self.draft.scan();self.assertGreater(self.draft.report['epg'],0)
        epg=sys.modules['epg'];key=epg._disk_ck(self.draft.pid);cache=self.folder/(key+'.json')
        def save_disk(pid,data,notify=True):
            self.assertFalse(notify);cache.write_text(json.dumps(data))
        epg._save_disk=save_disk;epg._mem_set=lambda *args:None
        verify=self.draft._verify
        def fail(portal=None):
            if portal:raise self.draft_module_error()
            return verify()
        with mock.patch.object(self.draft,'_verify',side_effect=fail):
            with self.assertRaisesRegex(ValueError,'VERIFY'):self.draft.save()
        self.assertFalse(cache.exists());self.assertEqual(self.portals.load_all(),[self.portal])
        from guide_store import connect
        db=connect()
        try:self.assertEqual(db.execute('SELECT count(*) FROM programmes WHERE pid=?',(self.draft.pid,)).fetchone()[0],0)
        finally:db.close()
        self.assertEqual(self.sources.configuration(self.draft.pid),dict(sources=[],mappings={}))
    def test_stalker_pages_continue_beyond_300_seconds_and_cycles_fail(self):
        adapter=importlib.import_module('source_adapters').for_portal(dict(id='s',type='stb'))
        adapter._provider=types.SimpleNamespace(authenticate=lambda:True,_portal='https://provider.invalid',_headers=lambda:{})
        clock=[0];calls=[]
        @contextmanager
        def transport(uri,params,**kw):
            n=params['p'];clock[0]+=120;calls.append(n)
            yield io.BytesIO(json.dumps(dict(js=dict(data=[dict(id=str(n))] if n<7 else [],total_items=0))).encode())
        sys.modules['utils'].http_stream=transport
        with mock.patch('time.monotonic',side_effect=lambda:clock[0]):
            self.assertEqual(len(list(adapter._stalker_rows('live','a',lambda:False))),7)
        self.assertGreater(clock[0],300)
        @contextmanager
        def cycle(uri,params,**kw):yield io.BytesIO(json.dumps(dict(js=dict(data=[dict(id=str(params['p']%2))]))).encode())
        sys.modules['utils'].http_stream=cycle
        with self.assertRaisesRegex(ValueError,'cycle'):list(adapter._stalker_rows('live','a',lambda:False))
        self.assertFalse(list(self.folder.glob('xcmate-pages-*')))


class StreamingTimeoutTests(unittest.TestCase):
    def setUp(self):
        # Import the fixture module, not its TestCase into discovery namespace.
        import test_xcmate_epg_limits as limits
        limits.CacheAndEPGTests.setUp(self)
    def test_real_http_stream_default_allows_20_minute_progress_and_2400_parsed_rows(self):
        from streaming_json import iter_array
        raw=json.dumps([dict(stream_id=str(i),category_id='a',name='Channel '+str(i)) for i in range(2400)]).encode()
        clock=[0];chunks=iter(raw[i:i+1024] for i in range(0,len(raw),1024))
        def read(size):
            clock[0]+=12
            return next(chunks,b'')
        response=types.SimpleNamespace(headers={},read1=read)
        @contextmanager
        def open_url(*args,**kwargs):
            self.assertEqual(kwargs['timeout'],15);yield response
        with mock.patch.object(self.utils,'HAVE_HTTPX',False),mock.patch('urllib.request.urlopen',side_effect=open_url),mock.patch('time.monotonic',side_effect=lambda:clock[0]):
            with self.utils.http_stream('https://provider.invalid/catalog') as stream:
                rows=list(iter_array(stream))
        self.assertEqual(len(rows),2400);self.assertGreater(clock[0],1200)
    def test_stalled_stream_and_explicit_small_request_deadline_remain_bounded(self):
        from network_io import decoded_chunks
        clock=[0]
        def stalled():
            clock[0]=31;yield b'data'
        with mock.patch('time.monotonic',side_effect=lambda:clock[0]):
            with self.assertRaisesRegex(TimeoutError,'idle'):list(decoded_chunks(stalled(),{},None))
        with self.assertRaisesRegex(TimeoutError,'deadline'):list(decoded_chunks([b'data'],{},time.monotonic()-1))
        with self.assertRaises(TimeoutError),mock.patch.object(self.utils,'HAVE_HTTPX',False),mock.patch('urllib.request.urlopen',side_effect=TimeoutError('not responding')):
            with self.utils.http_stream('https://provider.invalid'):pass
    def test_cancel_and_compression_security_still_fail_without_global_deadline(self):
        from network_io import decoded_chunks,HTTPCompressionError
        self.assertRaises(InterruptedError,lambda:list(decoded_chunks([b'data'],{},None,cancel=lambda:True)))
        self.assertRaises(HTTPCompressionError,lambda:list(decoded_chunks([__import__('gzip').compress(b'data')[:-4]],{'Content-Encoding':'gzip'},None)))
    def test_xmltv_import_continues_beyond_300_seconds_but_explicit_budget_still_works(self):
        from xmltv_stream import parse
        clock=[0]
        raw=('<tv>'+''.join('<programme channel="x" start="20261021000000 +0000" stop="20261021010000 +0000"><title>Programme</title></programme>' for _ in range(500))+'</tv>').encode()
        class Slow(io.BytesIO):
            def read(self,n=65536):clock[0]+=12;return super().read(min(n,128))
        with mock.patch('time.monotonic',side_effect=lambda:clock[0]):
            counts=parse(Slow(raw),lambda *a:None,lambda e:None)
            self.assertEqual(counts['programmes'],500);self.assertGreater(clock[0],300)
            with self.assertRaises(TimeoutError):parse(Slow(raw),lambda *a:None,lambda e:None,max_seconds=1)
