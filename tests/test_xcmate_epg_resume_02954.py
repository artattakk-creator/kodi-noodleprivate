"""Two verified sources, per-portal exclusion, cancel/restart and LastGood."""
import importlib,io,sqlite3,sys,time,unittest
from contextlib import contextmanager
from pathlib import Path
from unittest import mock
import test_xcmate_setup_0294 as old

class EPG54(unittest.TestCase):
    def setUp(self):
        self.m=old.StorageTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.d=self.m.draft;self.d.phased54=True;entries=self.d.adapter.entries
        def rows(kind,cid,cancel,allowed):
            for row in entries(kind,cid,cancel,allowed):
                if kind=='live':row=dict(row,epg_channel_id='xml')
                yield row
                if kind=='live':break
        self.d.adapter.entries=rows;self.files=[]
        stamp=lambda n:time.strftime('%Y%m%d%H%M%S +0000',time.gmtime(n))
        for i in (1,2):
            f=self.m.folder/('feed'+str(i)+'.xml');f.write_text('<tv><channel id="xml"><display-name>Station</display-name></channel><programme channel="xml" start="'+stamp(self.m.now-60)+'" stop="'+stamp(self.m.now+3600)+'"><title>Source '+str(i)+'</title><desc>Actual source description</desc></programme></tv>');self.files.append(f)
        self.d.epg_sources=[dict(id='feed'+str(i),name='Source '+str(i),uri=str(f),local=True,enabled=True) for i,f in enumerate(self.files,1)]
        self.d.scan();self.portal=self.d.save();self.mod=importlib.import_module('wizard_epg54');self.stream=importlib.import_module('stream_epg')
        status=sys.modules['epg_status'];status.source_key=lambda s:s.get('id','provider');status.update=mock.Mock();status.read=lambda pid:{}
    def backup(self):
        from guide_backup44 import authorize
        from guide_store import path
        self.assertEqual(authorize(path())['code'],'BACKUP_VERIFIED')
    def test_portal_already_usable_before_two_sources_then_each_receipt_verified(self):
        self.assertEqual(self.m.index.Reader(self.portal['id']).page('series',limit=1)[1],9)
        state=self.mod.run(self.portal);self.assertEqual(state['phase'],'READY');self.assertEqual(len(state['sources']),2)
        self.assertTrue(all(s['verified']['rows']==1 for s in state['sources'].values()));self.assertFalse(self.mod.pending(self.portal))
    def test_first_source_survives_second_cancel_and_restart_skips_it_after_backup(self):
        original=self.stream.import_source;calls=[]
        def interrupted(pid,source,rank,*a,**k):
            calls.append(rank)
            if rank==2:raise InterruptedError('synthetic user cancel')
            return original(pid,source,rank,*a,**k)
        with mock.patch.object(self.stream,'import_source',side_effect=interrupted):
            with self.assertRaises(InterruptedError):self.mod.run(self.portal)
        self.assertEqual(calls,[1,2]);self.assertIsNotNone(self.m.portals.get_by_id(self.portal['id']))
        state=self.mod.read(self.portal);self.assertEqual(state['phase'],'PARTIAL')
        self.backup();calls.clear()
        def observed(pid,source,rank,*a,**k):calls.append(rank);return original(pid,source,rank,*a,**k)
        with mock.patch.object(self.stream,'import_source',side_effect=observed):self.assertEqual(self.mod.run(dict(self.portal))['phase'],'READY')
        self.assertEqual(calls,[2])
    def test_failed_second_feed_preserves_first_and_no_catalog_reimport_on_retry(self):
        self.files[1].write_text('<tv><programme>broken')
        state=self.mod.run(self.portal);self.assertEqual(state['phase'],'PARTIAL');self.assertEqual(sum(s['code']=='READY' for s in state['sources'].values()),1)
        self.assertEqual(self.m.index.Reader(self.portal['id']).page('live',limit=1)[1],1)
        self.d.adapter.entries=mock.Mock(side_effect=AssertionError('EPG must not restart catalogue'))
        self.backup();before=self.m.portals.get_by_id(self.portal['id']);self.mod.run(self.portal)
        self.assertEqual(self.m.portals.get_by_id(self.portal['id']),before);self.d.adapter.entries.assert_not_called()
    def test_source_fingerprint_change_or_modified_archive_prevents_false_skip(self):
        self.mod.run(self.portal);self.backup();original=self.stream.import_source;calls=[]
        db=sqlite3.connect(importlib.import_module('guide_store').path())
        source=list(self.mod.read(self.portal)['sources'])[0]
        with db:db.execute('UPDATE guide44_inputs SET description=? WHERE pid=? AND source_id=?',('synthetic changed',self.portal['id'],source))
        db.close()
        def observed(pid,s,rank,*a,**k):calls.append(rank);return original(pid,s,rank,*a,**k)
        with mock.patch.object(self.stream,'import_source',side_effect=observed):self.mod.run(self.portal)
        self.assertEqual(calls,[1])
    def test_same_portal_native_refresh_lease_rejects_duplicate_import(self):
        with self.stream.portal_lease44(self.portal['id']) as held:
            self.assertTrue(held)
            with self.assertRaises(OSError),mock.patch.object(self.stream,'import_source',side_effect=AssertionError('duplicate')):self.mod.run(self.portal)
        self.assertTrue(self.mod.pending(self.portal))
    def test_existing_guide_backup_gate_is_never_bypassed_on_resume(self):
        self.mod.run(self.portal);state=self.mod.read(self.portal);state['phase']='PARTIAL';state['sources'].clear();self.mod.write(self.portal,state)
        with mock.patch.object(self.stream,'import_source',side_effect=AssertionError('backup gate')):
            result=self.mod.run(self.portal)
        self.assertEqual(result['code'],'BACKUP_REQUIRED');self.assertIsNotNone(self.m.portals.get_by_id(self.portal['id']))
    def test_checkpoints_are_private_and_have_no_raw_urls_passwords_or_programme_text(self):
        self.mod.run(self.portal);file=Path(self.mod.path(self.portal));raw=file.read_text()
        for value in ('SECRET','https://',str(self.files[0]),'Actual source description','Source 1'):self.assertNotIn(value,raw)
        import stat
        self.assertEqual(stat.S_IMODE(file.stat().st_mode),0o600)
    def test_automatic_refresh_does_not_compete_with_pending_setup(self):
        schedule=importlib.import_module('epg_schedule53')
        with mock.patch.object(schedule,'interval',return_value=86400):self.assertEqual(schedule.plan(self.portal,time.time()+999999),[])
    def test_corrupt_or_incomplete_receipt_never_claims_ready(self):
        file=Path(self.mod.path(self.portal));file.write_text('{broken')
        self.assertIsNone(self.mod.read(self.portal));self.mod.prepare(self.portal)
        self.assertTrue(self.mod.pending(self.portal));self.assertEqual(self.mod.read(self.portal)['sources'],{})
    def test_real_bytes_parser_and_stored_callbacks_have_no_fixed_total_deadline(self):
        progress=[];source=self.d.epg_sources[0];clock=[0]
        raw=self.files[0].read_bytes()
        class Slow:
            def __init__(self):self.s=io.BytesIO(raw)
            def read(self,n):clock[0]+=250;return self.s.read(min(n,64))
        @contextmanager
        def source_stream(*a,**k):yield Slow()
        with mock.patch.object(self.stream,'source_stream',source_stream),mock.patch('time.monotonic',side_effect=lambda:clock[0]):
            result=self.stream.import_source(self.portal['id'],source,1,[dict(sid='0',name='Station',epg_channel_id='xml')],{},filename=str(self.m.folder/'long.sqlite'),progress=progress.append)
        self.assertGreater(clock[0],1200);self.assertEqual(result['stored'],1)
        self.assertTrue(any(v['phase']=='PARSE' and v['programmes']==1 for v in progress));self.assertTrue(any(v['bytes']>0 for v in progress));self.assertEqual(progress[-1]['stored'],1)
    def test_cancel_during_read_has_no_success_receipt_or_partial_publication(self):
        cancelled=[False];original=self.stream.source_stream
        @contextmanager
        def source_stream(*a,**k):
            with original(*a,**k) as source:
                cancelled[0]=True;yield source
        with mock.patch.object(self.stream,'source_stream',source_stream):
            with self.assertRaises(InterruptedError):self.mod.run(self.portal,cancel=lambda:cancelled[0])
        self.assertTrue(self.mod.pending(self.portal));self.assertFalse(any(v['code']=='READY' for v in self.mod.read(self.portal)['sources'].values()))
    def test_unpublished_portal_cannot_start_any_epg_import(self):
        with self.assertRaises(ValueError):self.mod.run(dict(self.portal,id='not-published'))
    def test_unavailable_provider_does_not_block_independent_external_sources(self):
        portal=dict(self.portal,provider_epg_enabled=True)
        with mock.patch('source_adapters.for_portal',side_effect=OSError('synthetic provider unavailable')):
            state=self.mod.run(portal)
        self.assertEqual(state['phase'],'PARTIAL');self.assertEqual(state['sources']['provider']['code'],'SOURCE_UNAVAILABLE')
        self.assertEqual(sum(s['code']=='READY' for s in state['sources'].values()),2)
    def test_ci_style_checkpoint_write_failure_after_publish_cannot_remove_portal_or_duplicate_events(self):
        real=self.mod.write;failed=[]
        def write(portal,state):
            if not failed and any(s.get('code')=='READY' for s in state['sources'].values()):failed.append(True);raise OSError('synthetic interrupted checkpoint')
            return real(portal,state)
        with mock.patch.object(self.mod,'write',side_effect=write):state=self.mod.run(self.portal)
        self.assertIsNotNone(self.m.portals.get_by_id(self.portal['id']));self.assertTrue(failed)
        self.backup();self.mod.run(self.portal)
        from guide_store import path
        db=sqlite3.connect(path())
        try:
            counts=db.execute('SELECT source_id,count(*) FROM guide44_inputs WHERE pid=? AND source_id LIKE ? GROUP BY source_id',(self.portal['id'],'external:%')).fetchall()
            self.assertEqual(sorted(c for s,c in counts),[1,1])
        finally:db.close()
    def test_manager_offers_actual_resume_and_closes_owner_before_opening_followup(self):
        from xcmate027_fixture import ADDON,QueuedPool
        manager=importlib.import_module('epg_manager53')
        with mock.patch.object(manager,'ThreadPoolExecutor',QueuedPool):
            w=manager.Manager53('XCMateEPGManager53.xml',str(ADDON),'Default','720p');w.configure(self.portal)
        self.addCleanup(w.close);w.show();w._pool.drain();w.pump()
        self.assertEqual(w.getControl(402).label,'Jetzt aktualisieren');self.assertTrue(w.getControl(411).enabled);w.onClick(411)
        self.assertTrue(w._closed);self.assertEqual(w.next_action,'resume_epg54')
    def test_gzip_prefix_reader_never_asks_kodi_vfs_for_zero_bytes_or_entire_file(self):
        import gzip
        from xmltv_stream import parse
        raw=gzip.compress(self.files[0].read_bytes());stream=io.BytesIO(raw);requested=[];events=[]
        class VFS:
            def read(self,n):
                requested.append(n)
                if n==0:raise AssertionError('Kodi zero-byte read may allocate the entire feed')
                return stream.read(n)
        result=parse(VFS(),lambda *a:None,events.append)
        self.assertEqual(result['programmes'],1);self.assertEqual(len(events),1);self.assertNotIn(0,requested)
    def test_crash_recovery_cleans_only_recorded_invisible_generation_not_other_work(self):
        self.mod.run(self.portal);self.backup();state=self.mod.read(self.portal);identity=list(state['sources'])[0]
        abandoned='a'*32;other='b'*32;state['phase']='PARTIAL';state['sources'][identity]=dict(code='RUNNING',generation=abandoned);self.mod.write(self.portal,state)
        from guide_store import path
        db=sqlite3.connect(path())
        with db:
            for gen in (abandoned,other):db.execute('INSERT INTO xml_stage VALUES(?,?,?,?,?,?)',(gen,'invisible',self.m.now,self.m.now+100,'Incomplete','Never publish'))
        db.close();self.assertEqual(self.mod.run(self.portal)['phase'],'READY')
        db=sqlite3.connect(path())
        try:self.assertEqual(db.execute('SELECT generation FROM xml_stage').fetchall(),[(other,)])
        finally:db.close()
    def test_crash_after_running_marker_before_first_sqlite_table_can_resume(self):
        state=self.mod.read(self.portal);state['phase']='RUNNING';state['sources']['external:any']=dict(code='RUNNING',generation='a'*32);self.mod.write(self.portal,state)
        # Use the real configured source identity with a pre-import marker.
        from guide_publish44 import source_id
        state['sources']={source_id(self.d.epg_sources[0],1):dict(code='RUNNING',generation='a'*32)};self.mod.write(self.portal,state)
        self.assertEqual(self.mod.run(self.portal)['phase'],'READY')
    def test_two_large_active_sources_exceed_five_minutes_each_without_total_timeout(self):
        stamp=lambda n:time.strftime('%Y%m%d%H%M%S +0000',time.gmtime(n))
        for file in self.files:
            with file.open('w') as f:
                f.write('<tv><channel id="xml"><display-name>Station</display-name></channel>')
                for i in range(6000):
                    start=self.m.now-60+i*300
                    f.write('<programme channel="xml" start="'+stamp(start)+'" stop="'+stamp(start+300)+'"><title>Programme '+str(i)+'</title><desc>Real parsed source row</desc></programme>')
                f.write('</tv>')
        original=self.stream.source_stream;clock=[0];elapsed=[]
        @contextmanager
        def delayed(source,cancel=lambda:False):
            begin=clock[0]
            with original(source,cancel) as stream:
                class Slow:
                    def read(self,n):clock[0]+=75;return stream.read(min(n,4096))
                yield Slow()
            elapsed.append(clock[0]-begin)
        messages=[]
        with mock.patch.object(self.stream,'source_stream',delayed),mock.patch('time.monotonic',side_effect=lambda:clock[0]):
            state=self.mod.run(self.portal,status=lambda *args:messages.append(args))
        self.assertEqual(state['phase'],'READY');self.assertEqual(len(elapsed),2);self.assertTrue(all(t>300 for t in elapsed))
        self.assertTrue(all(s['verified']['rows']>5000 for s in state['sources'].values()))
        self.assertTrue(any('Sendungen gelesen' in text for p,text in messages));self.assertTrue(any('EPG-Quelle 2 von 2' in text for p,text in messages))
