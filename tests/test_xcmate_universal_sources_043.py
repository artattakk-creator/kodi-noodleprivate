"""Actual streaming sources/staging/overrides; no real IPTV credentials."""
import importlib
import importlib.util
import io
import json
import os
from pathlib import Path
import sys
import types
import unittest
from contextlib import contextmanager
from unittest import mock
from xcmate027_fixture import Fixture,LIB


class SourceTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('source_adapters','m3u_store','setup_draft'): sys.modules.pop(name,None)
        self.store=importlib.import_module('m3u_store');self.adapters=importlib.import_module('source_adapters')
        spec=importlib.util.spec_from_file_location('portals',LIB/'portals.py');portal=importlib.util.module_from_spec(spec);spec.loader.exec_module(portal)
        sys.modules['portals']=portal;portal.save_all([self.portal]);self.real_portals=portal
        sys.modules['utils'].cache_key=lambda value:__import__('hashlib').sha256(value.encode()).hexdigest()
        sys.modules['utils'].safe_int=lambda v,d=0:int(v) if str(v).isdigit() else d
        sys.modules['utils'].safe_float=lambda v,d=0:float(v) if str(v).replace('.','',1).isdigit() else d
        sys.modules['epg_status'].changed=lambda pid:None
        sys.modules['utils'].cache_get=lambda *a,**kw:None
        spec=importlib.util.spec_from_file_location('epg_sources',LIB/'epg_sources.py');sources=importlib.util.module_from_spec(spec);spec.loader.exec_module(sources)
        sys.modules['epg_sources']=sources
        vfs=sys.modules['xbmcvfs'];vfs.exists=os.path.exists;vfs.delete=lambda p:os.unlink(p)
        def rename(a,b): os.replace(a,b);return True
        vfs.rename=rename
        def file(uri,mode='r'):
            stream=open(uri,'rb' if mode=='r' else 'wb')
            return types.SimpleNamespace(readBytes=lambda n:stream.read(n),write=lambda s:bool(stream.write(s.encode() if isinstance(s,str) else s)),close=stream.close)
        vfs.File=file
        self.original=self.folder/'original.m3u'
        self.original.write_text('#EXTM3U\n#EXTINF:-1 tvg-id="news" group-title="DE",News, Regional\nhttps://stream.invalid/live.ts?token=old\n#EXTINF:-1 tvg-id="foreign" group-title="FR",Other\nhttps://stream.invalid/other.ts\n#EXTINF:-1 tvg-id="movie" group-title="Filme",Film\nhttps://stream.invalid/movie.mkv\n')

    def draft(self):
        cls=importlib.import_module('setup_draft').Draft
        d=cls(dict(type='m3u',name='Private file',m3u_url=str(self.original)))
        self.addCleanup(d.dispose);return d

    def test_staged_selective_file_scan_and_save_preserve_existing_account(self):
        original=self.original.read_bytes();before=Path(self.real_portals._db_path()).read_bytes()
        d=self.draft();categories=d.discover()
        self.assertEqual(Path(self.real_portals._db_path()).read_bytes(),before)
        selected=next(g['category_id'] for g in categories['live'] if g['category_name']=='DE')
        d.selected['live']={selected};report=d.scan()
        self.assertEqual((report['live'],report['vod'],report['series']),(1,0,0))
        self.assertEqual(Path(self.real_portals._db_path()).read_bytes(),before)
        portal=d.save();self.assertEqual(len(self.real_portals.load_all()),2)
        self.assertEqual(self.real_portals.get_by_id('p'),self.portal)
        rows,total=self.index.Reader(portal['id']).page('live')
        self.assertEqual(total,1);self.assertEqual(rows[0]['name'],'News, Regional')
        self.assertEqual(self.original.read_bytes(),original)
        self.original.unlink()  # Playlist itself no longer needs the USB source.
        adapter=self.adapters.for_portal(portal)
        uri,headers=adapter.play_uri('live',rows[0]['sid']);self.assertIn('live.ts',uri)
        self.assertTrue(Path(portal['m3u_url']).is_file())

    def test_cancelled_or_failed_scan_never_registers_portal_or_selection(self):
        d=self.draft();d.discover();before=Path(self.real_portals._db_path()).read_bytes()
        d.selected['live']={d.categories['live'][0]['category_id']}
        with self.assertRaises(InterruptedError): d.scan(cancel=lambda:True)
        self.assertEqual(Path(self.real_portals._db_path()).read_bytes(),before)
        self.assertIsNone(self.real_portals.get_by_id(d.pid))
        with self.assertRaises(ValueError): d.save()

    def test_save_failure_rolls_back_only_new_id_without_profile_loss(self):
        d=self.draft();d.discover();d.selected['live']={d.categories['live'][0]['category_id']};d.scan()
        before=Path(self.real_portals._db_path()).read_bytes()
        with mock.patch.object(self.real_portals,'add',side_effect=OSError('write failed')):
            with self.assertRaises(OSError): d.save()
        self.assertEqual(Path(self.real_portals._db_path()).read_bytes(),before)
        self.assertEqual(self.index.Reader('p').page('vod')[1],100)
        self.assertIsNone(self.real_portals.get_by_id(d.pid));self.assertFalse(Path(self.store.path(d.pid)).exists())

    def test_private_edits_survive_source_refresh_and_roundtrip_export(self):
        filename=str(self.folder/'working.sqlite');self.store.import_playlist(str(self.original),filename)
        row=next(self.store.entries(filename,query='Regional'));sid=row['sid']
        self.store.edit(filename,sid,name='My news',epg='manual.epg',logo='https://image.invalid/logo')
        gid=self.store.group(filename,'Custom group','live');self.store.edit(filename,sid,gid=gid)
        self.store.edit(filename,sid,ordinal=-10)
        self.original.write_text(self.original.read_text().replace('token=old','token=new'))
        self.store.import_playlist(str(self.original),filename)
        row=self.store.get(filename,sid);self.assertEqual((row['name'],row['epg'],row['gid']),('My news','manual.epg',gid))
        self.assertIn('token=new',row['url'])
        exported=self.folder/'exported.m3u';self.store.export(filename,str(exported))
        with self.assertRaises(FileExistsError): self.store.export(filename,str(exported))
        other=str(self.folder/'roundtrip.sqlite');self.store.import_playlist(str(exported),other)
        self.assertEqual(next(self.store.entries(other,query='My news'))['epg'],'manual.epg')
        self.assertIn('News, Regional',self.original.read_text())

    def test_cp1252_utf16_line_budget_invalid_rows_and_duplicate_detection(self):
        for encoding in ('cp1252','utf-16'):
            p=self.folder/(encoding+'.m3u');p.write_bytes(('#EXTM3U\n#EXTINF:-1 group-title="DE",Österreich\nhttps://stream.invalid/one\n#EXTINF:-1,Same\nhttps://stream.invalid/one\n').encode(encoding))
            filename=str(self.folder/(encoding+'.sqlite'));self.store.import_playlist(str(p),filename)
            rows=list(self.store.entries(filename));self.assertEqual(rows[0]['name'],'Österreich')
            self.assertEqual(len(self.store.duplicates(filename)),1)
        with self.assertRaises(ValueError): list(self.store.lines(io.BytesIO(b'x'*262145)))

    def test_editor_enable_disable_add_remove_preserves_original(self):
        filename=str(self.folder/'work.sqlite');before=self.original.read_bytes();self.store.import_playlist(str(self.original),filename)
        row=next(self.store.entries(filename));self.store.edit(filename,row['sid'],enabled=0)
        self.assertNotIn(row['sid'],[r['sid'] for r in self.store.entries(filename)])
        self.assertIsNotNone(self.store.get(filename,row['sid']))
        sid=self.store.add(filename,'Own channel',row['gid'],'https://stream.invalid/custom')
        self.assertIsNotNone(self.store.get(filename,sid));self.store.edit(filename,sid,deleted=1)
        self.assertIsNone(self.store.get(filename,sid));self.assertEqual(self.original.read_bytes(),before)
        with self.assertRaises(ValueError): self.store.edit(filename,row['sid'],name='bad\n#EXTINF')
        with self.assertRaises(ValueError): self.store.path('../escape')

    def test_xtream_discovery_only_calls_categories_before_selective_scan(self):
        adapter=self.adapters.for_portal(self.portal)
        provider=types.SimpleNamespace(authenticate=lambda:{'user_info':{'auth':1}},get_live_categories=mock.Mock(return_value=[dict(category_id='de',category_name='DE')]),
            get_vod_categories=mock.Mock(return_value=[]),get_series_categories=mock.Mock(return_value=[]),iter_catalog=mock.Mock(return_value=iter([dict(stream_id='1',category_id='de',name='News')])))
        adapter._provider=provider;self.assertTrue(adapter.authenticate());adapter.categories('live',remote=True)
        provider.iter_catalog.assert_not_called();self.assertEqual(list(adapter.entries('live','de'))[0]['stream_id'],'1')
        provider.iter_catalog.assert_called_once_with('get_live_streams','de',cancel=mock.ANY)

    def test_stalker_streams_over_fifty_pages_and_rejects_invalid_trailer(self):
        adapter=self.adapters.for_portal(dict(id='stb',type='stb',stb_url='https://provider.invalid',stb_mac='00:11:22:33:44:55'))
        adapter._provider=types.SimpleNamespace(authenticate=lambda:True,_portal='https://provider.invalid/portal.php',_headers=lambda:{})
        calls=[]
        @contextmanager
        def transport(uri,params,**kw):
            calls.append(params);number=params['p'];rows=[dict(id=str(i),name='TV',cmd='https://stream.invalid/'+str(i),tv_genre_id='de') for i in range(number*2,min(number*2+2,123))]
            yield io.BytesIO(json.dumps({'js':{'data':rows,'total_items':123}}).encode())
        utils=sys.modules['utils'];utils.http_stream=transport
        rows=list(adapter._stalker_rows('live','de',lambda:False));self.assertEqual(len(rows),123)
        self.assertEqual(len(calls),62);self.assertTrue(all(c['genre']=='de' for c in calls))
        from stalker_stream import page
        self.assertEqual(list(page(io.BytesIO(b'{"js":{"data":[{"id":1}],"total_items":1}}'))),[{'id':1}])
        with self.assertRaises(ValueError): list(page(io.BytesIO(b'{"js":{"data":[{"id":1}]}}trailer')))
    def test_native_setup_checks_selection_before_scan_and_only_publishes_on_save(self):
        from xcmate027_fixture import QueuedPool,ADDON,Control
        sys.modules.pop('setup_window',None)
        ui=importlib.import_module('setup_window')
        with mock.patch.object(ui,'ThreadPoolExecutor',QueuedPool),mock.patch.object(Control,'setPercent',lambda c,p:setattr(c,'percent',p),create=True):
            d=self.draft();window=ui.SetupWindow('XCMateSetup.xml',str(ADDON),'Default','720p');window.configure(d)
            window.doModal();self.assertTrue(window.busy);self.assertEqual(len(self.real_portals.load_all()),1)
            window._pool.drain();self.assertEqual(window.stage,'groups');self.assertFalse(any(d.selected.values()))
            self.assertFalse(d.provider_epg);self.assertEqual(d.epg_sources,[])
            pos=next(i for i,g in enumerate(window._entries) if g['category_name']=='DE')
            window.getControl(100).selectItem(pos);window.native(7)
            self.assertEqual(len(d.selected['live']),1)
            window.setFocusId(17);window.native(7);self.assertTrue(window.busy)
            window._pool.drain();self.assertEqual(window.stage,'summary');self.assertEqual(d.report['live'],1)
            self.assertEqual(len(self.real_portals.load_all()),1)
            window.native(7);window._pool.drain()
            self.assertTrue(d.saved);self.assertEqual(window.result['id'],d.pid)
            self.assertEqual(len(self.real_portals.load_all()),2)
            self.assertFalse(Path(d.folder).exists())

    def test_editor_paged_search_reorder_reclassification_and_private_projection(self):
        d=self.draft();d.discover();d.selected['live']={g['category_id'] for g in d.categories['live']};d.scan();p=d.save()
        filename=self.store.path(p['id']);rows=list(self.store.entries(filename));first,second=rows[:2]
        self.store.edit(filename,second['sid'],gid=first['gid']);self.store.reorder(filename,second['sid'],-1)
        order=list(self.store.entries(filename,gid=first['gid']));self.assertEqual(order[0]['sid'],second['sid'])
        self.assertEqual(len(list(self.store.entries(filename,offset=1,limit=1))),1)
        self.store.group(filename,'Manual films','vod',first['gid'])
        from group_selection import save
        save(p['id'],[first['gid']],'vod',known=[first['gid']])
        p['include_vod']=True  # Explicitly enable the manually assigned media section.
        from source_sync import sync_kind
        sys.modules['utils'].http_get.side_effect=AssertionError('editor must not connect')
        sync_kind(p,'vod',force=True,local_only=True)
        self.assertEqual(self.index.Reader(p['id']).page('vod')[1],2)
        self.assertEqual(self.index.Reader(p['id']).get('vod',first['sid'])['name'],first['name'])

    def test_cancel_during_native_discovery_cannot_apply_late_result(self):
        from xcmate027_fixture import QueuedPool,ADDON,Control
        sys.modules.pop('setup_window',None);ui=importlib.import_module('setup_window')
        with mock.patch.object(ui,'ThreadPoolExecutor',QueuedPool),mock.patch.object(Control,'setPercent',lambda c,p:None,create=True):
            d=self.draft();window=ui.SetupWindow('XCMateSetup.xml',str(ADDON),'Default','720p');window.configure(d)
            window.doModal();window.native(92);window._pool.drain()
            self.assertIsNone(window.result);self.assertFalse(Path(d.folder).exists());self.assertEqual(len(self.real_portals.load_all()),1)

    def test_large_file_and_real_http_playlist_stream_to_selected_index(self):
        import threading
        import urllib.request
        from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
        source=self.folder/'large.m3u8';count=20005
        with source.open('w') as file:
            file.write('#EXTM3U\n')
            for n in range(count):
                file.write('#EXTINF:-1 tvg-id="id'+str(n)+'" group-title="'+('DE' if n%4==0 else 'FR')+'",Channel '+str(n)+'\nhttps://stream.invalid/'+str(n)+'\n')
        local=str(self.folder/'large.sqlite');result=self.store.import_playlist(str(source),local)
        self.assertEqual(result['entries'],count)
        class Handler(BaseHTTPRequestHandler):
            def log_message(self,*args): pass
            def do_GET(self):
                self.send_response(200);self.send_header('Content-Length',str(source.stat().st_size));self.end_headers()
                with source.open('rb') as f:
                    while True:
                        chunk=f.read(32768)
                        if not chunk: break
                        self.wfile.write(chunk)
        server=ThreadingHTTPServer(('127.0.0.1',0),Handler);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
        self.addCleanup(server.server_close);self.addCleanup(server.shutdown)
        @contextmanager
        def transport(uri,cancel=lambda:False,**kw):
            with urllib.request.urlopen(uri,timeout=5) as response: yield response
        sys.modules['utils'].http_stream=transport
        d=importlib.import_module('setup_draft').Draft(dict(type='m3u',name='HTTP',m3u_url='http://127.0.0.1:'+str(server.server_port)+'/large.m3u8'))
        self.addCleanup(d.dispose);d.discover();d.selected['live']={g['category_id'] for g in d.categories['live'] if g['category_name']=='DE'}
        report=d.scan();self.assertEqual(report['live'],5002)
        p=d.save();rows,total=self.index.Reader(p['id']).page('live');self.assertEqual(total,5002)
        self.assertTrue(all(int(r['name'].split()[-1])%4==0 for r in rows))
        # Once committed, the configured background queue accepts this source.
        self.index.request_sync(p,'live')
        db=self.index.connect()
        try: self.assertIsNotNone(db.execute('SELECT 1 FROM sync_requests WHERE pid=?',(p['id'],)).fetchone())
        finally: db.close()
        print('\nLARGE_M3U '+json.dumps(dict(parsed=count,active=report['live'],bytes=source.stat().st_size)))

    def test_failed_playlist_refresh_retains_generation_and_manual_overrides(self):
        filename=str(self.folder/'stable.sqlite');self.store.import_playlist(str(self.original),filename)
        row=next(self.store.entries(filename));self.store.edit(filename,row['sid'],name='Persistent override')
        before=[(r['sid'],r['name']) for r in self.store.entries(filename)]
        self.original.write_text('#EXTM3U\n#EXTINF:-1,Broken\nhttps://stream.invalid/\x00bad\n')
        with self.assertRaises(ValueError): self.store.import_playlist(str(self.original),filename)
        self.assertEqual([(r['sid'],r['name']) for r in self.store.entries(filename)],before)
        with mock.patch('import_budget.check_space',side_effect=OSError(28,'full')):
            self.original.write_text('#EXTM3U\n#EXTINF:-1,New\nhttps://stream.invalid/new\n')
            with self.assertRaises(OSError): self.store.import_playlist(str(self.original),filename)
        self.assertEqual([(r['sid'],r['name']) for r in self.store.entries(filename)],before)

    def test_stalker_selected_raw_index_details_and_link_only_after_scan(self):
        d=importlib.import_module('setup_draft').Draft(dict(type='stb',name='MAG',stb_url='https://provider.invalid',stb_mac='00:11:22:33:44:55'))
        self.addCleanup(d.dispose)
        provider=types.SimpleNamespace(authenticate=lambda:True,get_live_categories=lambda:[dict(id='de',title='DE'),dict(id='fr',title='FR')],get_vod_categories=lambda:[],get_series_categories=lambda:[],
            get_channel_stream_url=mock.Mock(return_value='https://stream.invalid/resolved'),stream_headers=lambda:{'User-Agent':'MAG'})
        d.adapter._provider=provider;d.discover();provider.get_channel_stream_url.assert_not_called();d.selected['live']={'de'}
        called=[]
        def rows(kind,cid,cancel):
            called.append((kind,cid));yield dict(id='opaque-id',name='News',tv_genre_id='de',cmd='ffmpeg http://localhost/ch/1')
            yield dict(id='other-id',name='Foreign',tv_genre_id='fr',cmd='secret')
        d.adapter._stalker_rows=rows;report=d.scan();self.assertEqual(report['live'],1);self.assertEqual(called,[('live','de')])
        p=d.save();adapter=self.adapters.for_portal(p);adapter._provider=provider
        uri,headers=adapter.play_uri('live','opaque-id');self.assertEqual(uri,'https://stream.invalid/resolved')
        provider.get_channel_stream_url.assert_called_once_with('ffmpeg http://localhost/ch/1')
        with self.assertRaises(ValueError): adapter.play_uri('live','other-id')

    def test_m3u_flat_series_has_no_fabricated_seasons_and_uses_verified_playback_state(self):
        from xcmate027_fixture import ADDON
        self.original.write_text('#EXTM3U\n#EXTINF:-1 tvg-id="flat" group-title="Series",Single entry\nhttps://stream.invalid/series.mkv\n')
        d=self.draft();d.discover();self.assertTrue(d.categories['series'])
        d.selected['series']={g['category_id'] for g in d.categories['series']};d.scan();p=d.save()
        row=self.index.Reader(p['id']).page('series')[0][0];self.assertTrue(row['series_flat'])
        self.router._xc=lambda portal:self.adapters.for_portal(portal)
        self.router._params.update(pid=p['id'],kind='series_item',sid=row['sid'])
        progress=importlib.import_module('media_progress');tag=types.SimpleNamespace(setUniqueIDs=mock.Mock())
        item=types.SimpleNamespace(getVideoInfoTag=lambda:tag)
        builder=mock.Mock(return_value=item)
        with mock.patch.dict(sys.modules,player=types.SimpleNamespace(build_playable_item=builder)):
            progress.play(self.router,p)
        session=json.loads(self.properties[progress.PROPERTY]);self.assertEqual(session['kind'],'series_item')
        self.assertNotIn('season',session);self.assertEqual(builder.call_args.args[0],'https://stream.invalid/series.mkv')
        self.state.save_progress(session,100,1000)
        self.assertEqual(self.state.rail_items(p['id'],'series',self.index.Reader(p['id']),'continue')[0]['sid'],row['sid'])
        details=self.adapters.for_portal(p).details('series',row['sid']);self.assertEqual(details['episodes'],{})
        window=self.media.MediaWindow('XCMateMedia.xml',str(ADDON),'Default','720p')
        window.configure(self.router,p,'series',row['sid']);window.doModal();window._pool.drain()
        self.assertIn('resume',[action for label,action in window.actions]);self.assertNotIn('seasons',[action for label,action in window.actions])
        window.close()

    def test_explicit_epg_stream_filters_foreign_data_and_restores_now_from_saved_sqlite(self):
        import time
        now=int(time.time());stamp=lambda n:time.strftime('%Y%m%d%H%M%S +0000',time.gmtime(n))
        source=self.folder/'guide.xml'
        source.write_text('<tv><channel id="news"><display-name>News</display-name></channel><channel id="foreign"><display-name>Other</display-name></channel>'+''.join('<programme channel="'+cid+'" start="'+stamp(now-60)+'" stop="'+stamp(now+3600)+'"><title>'+name+'</title></programme>' for cid,name in (('news','Current saved programme'),('foreign','Foreign programme')) )+'</tv>')
        d=self.draft();d.discover();d.selected['live']={g['category_id'] for g in d.categories['live'] if g['category_name']=='DE'}
        d.epg_sources=[dict(id='manual',uri=str(source),name='Test',local=True,enabled=True)]
        report=d.scan();self.assertEqual(report['epg'],1);self.assertEqual(report['sources'][0]['stored'],1)
        self.assertEqual(report['sources'][0]['bytes'],source.stat().st_size)
        epg=sys.modules['epg'];snapshots={};epg._save_disk=lambda pid,cache:snapshots.update({pid:cache});epg._mem_set=lambda *a:None
        p=d.save();sid=self.index.Reader(p['id']).page('live')[0][0]['sid']
        self.assertEqual(snapshots[p['id']][sid][0]['name'],'Current saved programme')
        from guide_store import events
        self.assertEqual(events(p['id'],'foreign',now,now+3600)[1],0)
        # Compatibility snapshot may expire; the persistent DB remains valid.
        epg._mem_clear=lambda *a:None
        spec=importlib.util.spec_from_file_location('saved_tv_data',LIB/'tv_data.py');data=importlib.util.module_from_spec(spec);spec.loader.exec_module(data)
        with mock.patch.dict(sys.modules,logo_cache=types.SimpleNamespace(request=lambda *a:None),live_diagnostics=types.SimpleNamespace(record=lambda *a,**kw:None)):
            guide=data.GuideSnapshot(p,self.adapters.for_portal(p));guide.request([types.SimpleNamespace(tvg_id='news',name='News',logo='',extra={'stream_id':sid})]);guide.refresh()
        self.assertEqual(guide.get(sid)['now'],'Current saved programme')
        print('\nSELECTIVE_XMLTV '+json.dumps(dict(bytes=source.stat().st_size,parsed=2,stored=report['epg'])))

    def test_legacy_source_discovers_categories_without_automatic_country_import(self):
        portal=self.real_portals.add(dict(type='m3u',name='Legacy',m3u_url=str(self.original)))
        from source_sync import sync_kind
        sync_kind(portal,'live')
        self.assertEqual(self.index.Reader(portal['id']).page('live')[1],0)
        adapter=self.adapters.for_portal(portal);self.assertTrue(adapter.categories('live'))
        self.assertFalse(self.real_portals.get_by_id(portal['id']).get('source_schema'))
