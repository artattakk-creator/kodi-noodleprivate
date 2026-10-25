"""Cross-PR integration failures; actual XML callbacks, SQLite and delayed resolver."""
import importlib
import json
from pathlib import Path
import sys
import types
import unittest
from unittest import mock
from urllib.parse import parse_qsl,urlsplit
from xcmate027_fixture import Fixture


class IntegrationTests(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        for name in ('playback_exit','media_progress','media_intent','m3u_store'):
            sys.modules.pop(name,None)
        utils=sys.modules['utils'];utils.cache_key=lambda value:__import__('hashlib').sha256(value.encode()).hexdigest();utils.cache_get=lambda *a,**kw:None
        self.progress=importlib.import_module('media_progress')
        self.exit=importlib.import_module('playback_exit')
        self.playing=False;self.nonce='';self.stops=[];self.position=75
        self.player=types.SimpleNamespace(isPlayingVideo=lambda:self.playing,
            getVideoInfoTag=lambda:types.SimpleNamespace(getUniqueID=lambda key:self.nonce if key=='xcmate_media' else ''),
            getTime=lambda:self.position,getTotalTime=lambda:1000,stop=lambda:self.stops.append(self.nonce))
        sys.modules['xbmc'].Player=lambda:self.player
        tag=types.SimpleNamespace(setUniqueIDs=lambda ids:setattr(self,'nonce',ids['xcmate_media']))
        self.builder=mock.Mock(return_value=types.SimpleNamespace(getVideoInfoTag=lambda:tag))
        patch=mock.patch.dict(sys.modules,player=types.SimpleNamespace(build_playable_item=self.builder))
        patch.start();self.addCleanup(patch.stop)

    def requested(self,window):
        window._play(dict(sid='1'),'vod')
        call=self.builtins[-1];self.assertTrue(call.startswith('PlayMedia('))
        self.router._params=dict(parse_qsl(urlsplit(call[len('PlayMedia('):-1]).query))

    def test_back_before_plugin_resolver_cannot_start_late_hidden_movie(self):
        window=self.media_window();self.requested(window)
        window.native(92)  # Real WindowXML Back, before the plugin interpreter runs.
        self.progress.play(self.router,self.portal)
        resolved=sys.modules['xbmcplugin'].setResolvedUrl.call_args.args[1]
        self.assertFalse(resolved,'cancelled request resolved successfully after Back')
        self.assertEqual(self.stops,[])  # No unverified generic player.stop().

    def test_back_during_buffering_stops_verified_late_video_without_arming_fullscreen(self):
        window=self.media_window();self.requested(window)
        self.progress.play(self.router,self.portal)
        self.assertTrue(sys.modules['xbmcplugin'].setResolvedUrl.call_args.args[1])
        window.native(92)  # Resolver returned, but Kodi has not started video yet.
        self.assertEqual(self.stops,[])
        self.playing=True
        self.assertTrue(self.exit.poll(self.player,fullscreen=False))
        from exit37_fixture import drain_stop
        drain_stop()
        self.assertEqual(self.stops,[self.nonce])
        self.assertEqual(self.state.progress('p','vod','1')['position'],75)

    def test_partial_refresh_with_dangling_extinf_keeps_previous_private_generation(self):
        from contextlib import contextmanager
        import io
        store=importlib.import_module('m3u_store')
        # Parser helpers are the actual released iptv module; transport only is modeled.
        utils=sys.modules['utils'];utils.cache_key=lambda value:value;utils.cache_get=lambda *a,**kw:None
        utils.safe_int=lambda v,d=0:int(v) if str(v).isdigit() else d;utils.safe_float=lambda v,d=0:d
        data=[b'#EXTM3U\n#EXTINF:-1 tvg-id="one" group-title="DE",Old\nhttps://stream.invalid/old\n']
        @contextmanager
        def source(uri,cancel=lambda:False): yield io.BytesIO(data[0])
        filename=str(self.folder/'partial.sqlite')
        with mock.patch.object(store,'source',source):
            store.import_playlist('https://source.invalid/list',filename)
            before=list(store.entries(filename))
            data[0]=b'#EXTM3U\n#EXTINF:-1 tvg-id="new",Partial\nhttps://stream.invalid/new\n#EXTINF:-1 tvg-id="missing",Truncated\n'
            with self.assertRaises(ValueError): store.import_playlist('https://source.invalid/list',filename)
        self.assertEqual(list(store.entries(filename)),before)

    def test_cancelled_request_never_stops_foreign_playback_or_another_portal(self):
        window=self.media_window();self.requested(window);window.native(92)
        self.playing=True;self.nonce='foreign'
        self.assertFalse(self.exit.poll(self.player,fullscreen=False));self.assertEqual(self.stops,[])
        intent=importlib.import_module('media_intent')
        token=intent.begin('other','vod','1')
        self.assertFalse(intent.cancel('p',token));self.assertTrue(intent.allowed(token,'other','vod','1'))

    def test_uncancelled_pending_start_is_not_stopped_and_superseded_request_is_rejected(self):
        window=self.media_window();self.requested(window)
        first=dict(self.router._params)
        self.requested(window)
        self.router._params=first;self.progress.play(self.router,self.portal)
        self.assertFalse(sys.modules['xbmcplugin'].setResolvedUrl.call_args.args[1])
        from media_intent import _read,REQUEST
        latest=_read(REQUEST);self.router._params.update(intent=latest['nonce'])
        self.progress.play(self.router,self.portal);self.playing=True
        self.assertTrue(sys.modules['xbmcplugin'].setResolvedUrl.call_args.args[1])
        self.assertFalse(self.exit.poll(self.player,fullscreen=False));self.assertEqual(self.stops,[])

    def test_cancel_during_provider_resolution_rechecks_intent_before_resolving(self):
        window=self.media_window();self.requested(window)
        self.portal['type']='stb'
        # Source work is on the plugin interpreter. Back may arrive while
        # create_link runs; it must be checked again before setResolvedUrl.
        def resolve(kind,sid): window.native(92);return 'https://stream.invalid/late',{}
        self.router._xc=lambda portal:types.SimpleNamespace(play_uri=resolve)
        self.progress.play(self.router,self.portal)
        self.assertFalse(sys.modules['xbmcplugin'].setResolvedUrl.call_args.args[1]);self.assertEqual(self.stops,[])

    def _released(self,name):
        import zipfile
        from xcmate027_fixture import ROOT
        archive=ROOT/'plugin.video.xtreammate/plugin.video.xtreammate-0.1.28.zip'
        module=types.ModuleType('released_'+name);module.__file__=str(archive)+'/'+name+'.py'
        with zipfile.ZipFile(archive) as file: source=file.read('plugin.video.xtreammate/resources/lib/'+name+'.py')
        exec(compile(source,module.__file__,'exec'),module.__dict__)
        return module

    def test_direct_upgrade_from_actual_028_profile_preserves_all_account_and_state_data(self):
        import hashlib
        import time
        from xcmate027_fixture import LIB
        utils=sys.modules['utils'];utils.cache_key=lambda value:hashlib.sha256(value.encode()).hexdigest();utils.cache_get=lambda *a,**kw:None
        sys.modules['epg_status'].changed=lambda pid:None
        # Seed with modules extracted from the actual published 0.1.28 ZIP,
        # not current code pretending to be an older schema.
        import os
        sys.modules['xbmcvfs'].exists=os.path.exists
        old_portals=self._released('portals');portals=[self.portal,
            dict(id='m3u-old',name='M3U',type='m3u',m3u_url='smb://private/list.m3u',enabled=True),
            dict(id='stb-old',name='STB',type='stb',stb_url='https://provider.invalid',stb_mac='00:11:22:33:44:55',enabled=True)]
        old_portals.save_all(portals)
        old_groups=self._released('group_selection')
        for kind in ('live','vod','series'): old_groups.save('p',['a'],kind,known=['a','b'],auto_new=False)
        old_sources=self._released('epg_sources');old_sources._save('p',dict(sources=[dict(id='old',uri='https://guide.invalid/feed',enabled=False)],mappings={'1':'manual.id'}))
        # Rebuild the index using the published implementation as well.
        from library_index import path as index_path
        for suffix in ('','-wal','-shm'):
            target=Path(index_path()+suffix)
            if target.exists(): target.unlink()
        self._released('library_index').refresh(self.portal,self.client)
        old_state=self._released('media_state');session=dict(pid='p',kind='episode',sid='12',series_id='1',season='1',episode='2')
        old_state.save_progress(session,300,1000);old_state.toggle('p','series','1')
        old_remote=self._released('remote_profiles');old_remote.save(dict(old_remote.DEFAULT,left=42))
        # Keep real prior index and EPG rows too; exact configuration bytes
        # should not change during normal current-version read/bootstrap.
        from guide_store import events
        now=int(time.time());self._released('guide_store').import_cache('p',{'manual.id':[dict(name='Old guide',start_timestamp=now-50,stop_timestamp=now+3600)]},'old')
        configs=['portals.json','xtreammate_groups.json','xtreammate_epg_sources.json',Path(old_remote.path()).name]
        configs=[p for p in (self.folder/name for name in configs) if p.exists()]
        self.assertEqual(len(configs),4)
        before={p:p.read_bytes() for p in configs};state=old_state.read()
        old_art=self._released('media_art');png=self.png()
        utils.http_get.side_effect=None;utils.http_get.return_value=(png,{})
        art_files=[Path(old_art.fetch('https://image.invalid/old-'+str(i))) for i in range(8)]
        image_bytes={p:p.read_bytes() for p in art_files}
        calls=utils.http_get.call_count
        new_portals=importlib.util.module_from_spec(importlib.util.spec_from_file_location('integration_portals',LIB/'portals.py'))
        importlib.util.spec_from_file_location('integration_portals',LIB/'portals.py').loader.exec_module(new_portals)
        self.assertEqual(new_portals.load_all(),portals)
        self.index.connect(write=True).close()  # Idempotent additive schema check.
        self.index.connect(write=True).close()
        self.assertEqual(self.state.read(),state)
        self.assertEqual(self.index.Reader('p').get('vod','1')['name'],'House of Dragon 1')
        self.assertEqual(events('p','manual.id',now,now+3600)[0][0]['title'],'Old guide')
        self.assertEqual(old_remote.load()['left'],42)
        self.assertEqual({p:p.read_bytes() for p in configs},before)
        art=importlib.import_module('media_art');store=importlib.import_module('art_store')
        self.assertEqual(store.used(),8*len(png))
        for i in range(8): self.assertTrue(art.fetch('https://image.invalid/old-'+str(i)))
        self.assertEqual(utils.http_get.call_count,calls)
        self.assertEqual({p:p.read_bytes() for p in art_files},image_bytes)

    def png(self):
        import struct,zlib
        def chunk(kind,data): return struct.pack('>I',len(data))+kind+data+struct.pack('>I',zlib.crc32(kind+data)&0xffffffff)
        return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',8,8,8,2,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+b'\x10\x20\x30'*8)*8))+chunk(b'IEND',b'')

    def test_simultaneous_epg_and_art_workers_leave_native_navigation_responsive(self):
        import io,threading,time
        from contextlib import contextmanager
        from concurrent.futures import ThreadPoolExecutor
        from stream_epg import import_source
        from guide_store import events
        from media_art import fetch,cached
        window=self.media_window();barrier=threading.Barrier(3);release=threading.Event()
        self.addCleanup(release.set);now=int(time.time());stamp=lambda n:time.strftime('%Y%m%d%H%M%S +0000',time.gmtime(n))
        raw=('<tv><channel id="news"><display-name>One</display-name></channel><programme channel="news" start="'+stamp(now-50)+'" stop="'+stamp(now+3600)+'"><title>Concurrent guide</title></programme></tv>').encode()
        main=threading.get_ident()
        @contextmanager
        def transport(source,cancel=lambda:False):
            self.assertNotEqual(threading.get_ident(),main);barrier.wait(timeout=5)
            self.assertTrue(release.wait(5));yield io.BytesIO(raw)
        def image(uri,**kwargs):
            self.assertNotEqual(threading.get_ident(),main);barrier.wait(timeout=5)
            self.assertTrue(release.wait(5));return self.png(),{}
        sys.modules['utils'].http_get.side_effect=image
        with mock.patch.dict(sys.modules,epg_sources=self._released('epg_sources')),mock.patch('stream_epg.source_stream',transport),ThreadPoolExecutor(max_workers=2) as pool:
            guide=pool.submit(import_source,'p',dict(uri='https://guide.invalid'),0,[dict(sid='1',name='One',epg_channel_id='news')],{})
            art=pool.submit(fetch,'https://image.invalid/concurrent')
            barrier.wait(timeout=5)
            try:
                self.assertFalse(guide.done());self.assertFalse(art.done())
                for _ in range(10): window.native(2);window.native(1)
                self.assertFalse(guide.done());self.assertFalse(art.done())
            finally: release.set()
            self.assertEqual(guide.result(timeout=5)['stored'],1);self.assertTrue(art.result(timeout=5))
        self.assertTrue(cached('https://image.invalid/concurrent'))
        self.assertEqual(events('p','1',now,now+3600)[0][0]['title'],'Concurrent guide')

    def test_real_stalker_handshake_failure_keeps_existing_profile_and_no_partial_portal(self):
        from xcmate027_fixture import LIB
        utils=sys.modules['utils'];utils.cache_key=lambda value:value;utils.cache_get=lambda *a,**kw:None
        utils.http_get.side_effect=None;utils.http_get.return_value=(b'{"js":{}}',{})
        spec=importlib.util.spec_from_file_location('integration_stalker',LIB/'stalker.py');stalker=importlib.util.module_from_spec(spec);spec.loader.exec_module(stalker)
        client=stalker.StalkerClient('https://provider.invalid','00:11:22:33:44:55')
        self.assertFalse(client.authenticate());self.assertFalse(client._authed)
        from source_adapters import for_portal
        adapter=for_portal(dict(id='new',type='stb',stb_url='https://provider.invalid',stb_mac='00:11:22:33:44:55'))
        adapter._provider=client
        with self.assertRaises(ValueError): adapter.authenticate()
        self.assertEqual(self.portals,[self.portal]);self.assertEqual(self.index.Reader('p').page('vod')[1],100)

    def test_failed_additive_art_migration_retains_rows_and_retries_idempotently(self):
        import sqlite3
        filename=self.folder/'media_art_jobs_v1.sqlite'
        db=sqlite3.connect(filename)
        db.executescript('CREATE TABLE jobs(ident TEXT PRIMARY KEY,url TEXT,status TEXT,priority INTEGER,attempts INTEGER,next_at REAL,updated REAL,bytes INTEGER);CREATE TABLE worker(id INTEGER PRIMARY KEY,until REAL);INSERT INTO worker VALUES(1,0);')
        db.execute('INSERT INTO jobs VALUES(?,?,?,?,?,?,?,?)',('old','private','READY',0,0,0,0,123));db.commit();db.close()
        connect=sqlite3.connect
        health=importlib.import_module('artwork_db');execute=health._Connection.execute
        def fail(db,sql,parameters=()):
            if sql.startswith('ALTER TABLE'):raise sqlite3.OperationalError('secret provider details')
            return execute(db,sql,parameters)
        store=importlib.import_module('art_store')
        with mock.patch.object(health._Connection,'execute',fail),mock.patch.object(sys.modules['utils'],'warn') as warn:
            with self.assertRaises(sqlite3.OperationalError): store.connect()
            warn.assert_called_once()
            self.assertIn('code=SQL_ERROR',warn.call_args.args[0])
            self.assertNotIn('secret provider details',warn.call_args.args[0])
        db=connect(filename)
        self.assertEqual(db.execute('SELECT * FROM jobs').fetchone(),('old','private','READY',0,0,0,0,123));db.close()
        health.reset_retry()
        for _ in range(2):
            db=store.connect()
            self.assertIn('owner',{row[1] for row in db.execute('PRAGMA table_info(worker)')})
            self.assertEqual(db.execute('SELECT bytes FROM jobs WHERE ident="old"').fetchone()[0],123);db.close()

    def test_manifest_assets_exist_in_complete_addon(self):
        import xml.etree.ElementTree as ET
        from xcmate027_fixture import ADDON
        manifest=ET.parse(ADDON/'addon.xml').getroot()
        for node in manifest.findall('.//assets/*'):
            if node.tag in ('icon','fanart','screenshot'): self.assertTrue((ADDON/node.text).is_file(),node.text)

    def test_builder_keeps_real_jpeg_reference_and_legacy_png_fallback(self):
        from xcmate027_fixture import ROOT
        spec=importlib.util.spec_from_file_location('integration_builder',ROOT/'tools/build_repository.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
        source=self.folder/'source';xtream=source/'plugin.video.xtreammate';noodle=source/'plugin.video.noodleprivate'
        xtream.mkdir(parents=True);noodle.mkdir()
        original='<addon><assets><fanart>fanart.jpg</fanart></assets></addon>'
        (xtream/'addon.xml').write_text(original);(xtream/'fanart.jpg').write_bytes(b'existing jpeg asset')
        (noodle/'addon.xml').write_text(original);(noodle/'default.py').write_text('# no runtime changes')
        with mock.patch.object(builder,'SRC',source),mock.patch.object(builder,'IDS',('plugin.video.xtreammate','plugin.video.noodleprivate')): builder.seed()
        self.assertEqual((xtream/'addon.xml').read_text(),original)
        self.assertIn('fanart.png',(noodle/'addon.xml').read_text())

    def test_xcmate_zip_is_reproducible_across_source_timestamps(self):
        import os,zipfile,hashlib
        from xcmate027_fixture import ROOT
        spec=importlib.util.spec_from_file_location('integration_repro_builder',ROOT/'tools/build_repository.py');builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
        source=self.folder/'example.py';source.write_text('# unchanged source\n')
        digests=[]
        for i,stamp in enumerate((1600000000,1800000000)):
            os.utime(source,(stamp,stamp));target=self.folder/('repro-'+str(i)+'.zip')
            with zipfile.ZipFile(target,'w') as file: builder.package_file(file,'plugin.video.xtreammate',source,'plugin.video.xtreammate/example.py')
            with zipfile.ZipFile(target) as file:
                self.assertEqual(file.infolist()[0].date_time,(1980,1,1,0,0,0));self.assertEqual(file.read(file.infolist()[0]),source.read_bytes())
            digests.append(hashlib.sha256(target.read_bytes()).hexdigest())
        self.assertEqual(digests[0],digests[1])
