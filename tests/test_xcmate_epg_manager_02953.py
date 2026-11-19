"""Committed local history, source-aware scheduling and bounded native controls."""
import contextlib,importlib,io,json,sys,time,types,unittest
from pathlib import Path
from unittest import mock
import test_xcmate_epg_02952 as data52
from xcmate027_fixture import ADDON,QueuedPool


class Manager53Tests(unittest.TestCase):
    def setUp(self):
        self.m=data52.EPG52(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.report=importlib.import_module('epg_report53');self.schedule=importlib.import_module('epg_schedule53')
        sys.modules['epg_status'].source_key=lambda source:source['id']
        self.portal=dict(self.m.portal,provider_epg_enabled=False)
        self.m.config['sources']=self.m.config['sources'][:1]
        self.identity=importlib.import_module('guide_publish44').source_id(self.m.config['sources'][0],1)
    def run_record(self,code='READY',start=None,source_code=None):
        now=time.time() if start is None else start
        return dict(started=now,finished=now+1,seconds=1,automatic=True,code=code,
                    before=dict(programmes=0),after=self.report.statistics('p'),
                    sources=[dict(id=self.identity,key='safe',rank=1,started=now,finished=now+1,code=source_code or code,channels=1,stored=1)])
    def test_twenty_four_hour_default_and_existing_explicit_interval_preserved(self):
        import xml.etree.ElementTree as ET
        self.assertEqual(ET.parse(ADDON/'resources/settings.xml').find(".//setting[@id='epg_refresh_hours']").get('default'),'24')
        self.assertEqual(self.schedule.interval(),86400)
        for hours in (6,12,36,48):
            self.m.options['epg_refresh_hours']=str(hours);self.assertEqual(self.schedule.interval(),hours*3600)
    def test_existing_lastgood_prevents_restart_download_but_not_next_day_refresh(self):
        self.m.put('a',[self.m.event()],1);now=time.time()
        self.assertEqual(self.schedule.plan(self.portal,now),[])
        self.assertEqual(self.schedule.plan(self.portal,now+86410),[self.identity])
    def test_successful_source_not_retried_with_failed_source(self):
        now=time.time();r=self.run_record('PARTIAL_SUCCESS',now-1000,'HTTP_ERROR')
        r['sources'].append(dict(id='provider',started=now-1000,finished=now-999,code='READY'))
        self.report.store('p',r)
        portal=dict(self.portal,provider_epg_enabled=True)
        self.assertEqual(self.schedule.plan(portal,now),[self.identity])
    def test_backoff_is_bounded_and_retries_stop_after_three_attempts(self):
        now=time.time()
        for ago in (5000,4000,1000):self.report.store('p',self.run_record('PARTIAL_SUCCESS',now-ago,'HTTP_ERROR'))
        self.assertEqual(self.schedule.plan(self.portal,now),[])
        self.assertEqual(self.schedule.plan(self.portal,now+86400),[self.identity])
    def test_first_failure_waits_fifteen_minutes(self):
        now=time.time();self.report.store('p',self.run_record('PARTIAL_SUCCESS',now-100,'HTTP_ERROR'))
        self.assertFalse(self.schedule.plan(self.portal,now));self.assertEqual(self.schedule.plan(self.portal,now+1000),[self.identity])
    def test_backup_block_is_reported_and_does_not_retry_every_service_tick(self):
        now=time.time();self.report.store('p',self.run_record('BACKUP_REQUIRED',now))
        self.assertFalse(self.schedule.plan(self.portal,now+61))
        self.assertIn('Sicherung',self.report.describe(self.report.history('p')[-1],self.portal))
    def test_history_has_bounded_rotation_and_real_readonly_stored_horizon(self):
        self.m.put('a',[self.m.event(-7),self.m.event(20)],1)
        before=Path(self.m.g.path()).read_bytes();stats=self.report.statistics('p')
        self.assertEqual(stats['programmes'],2);self.assertLess(stats['first'],self.m.now);self.assertGreater(stats['last'],self.m.now+19*86400)
        for n in range(25):self.assertTrue(self.report.store('p',dict(self.run_record(),number=n)))
        self.assertEqual(len(self.report.history('p')),16);self.assertEqual(self.report.history('p')[0]['number'],9)
        self.assertEqual(Path(self.m.g.path()).read_bytes(),before)
    def test_readable_report_contains_counts_dates_and_no_structured_dump(self):
        r=self.run_record();r['after']=dict(code='READY',programmes=10,first=self.m.now,last=self.m.now+3600)
        r['sources'][0].update(saved=dict(channels=1,programmes=10,first=self.m.now,last=self.m.now+3600),added=2,corrected=1,conflicts=3)
        text=self.report.describe(r,self.portal)
        for word in ('Gespeicherte Programme: 10','Geladen: 1 Sender','Neu: 2','aktualisiert: 1','Konflikte bewahrt: 3'):self.assertIn(word,text)
        for secret in ('https://','password=','Traceback','{"','SELECT '):self.assertNotIn(secret,text)
    def test_source_labels_redact_addresses_and_token_fields(self):
        for name in ('https://private.invalid/token','token=secret','password=secret','person@example.invalid'):
            self.assertEqual(self.report.label(name),'XMLTV-Quelle')
    def test_corrupt_history_is_unknown_not_import_success(self):
        Path(self.report.path('p')).write_text('{broken');self.assertEqual(self.report.history('p'),[])
    def test_observer_records_committed_import_and_retrievable_source_summary(self):
        with self.report.observing('p') as run:
            self.report.started('p','safe',self.identity,1)
            counts=self.m.put('a',[self.m.event()],1)
            self.report.source_done('p',self.identity,'READY',counts,dict(added=counts['added'],conflicts=counts['conflicts']))
            run['result']=True
        r=self.report.history('p')[-1]
        self.assertEqual(r['code'],'READY');self.assertEqual(r['after']['programmes'],1)
        self.assertEqual(r['sources'][0]['saved']['programmes'],1)
        self.assertGreater(self.report.overview(self.portal)[1]['last_success'],0)
    def test_observer_exception_never_reports_a_queued_or_failed_request_as_success(self):
        with self.assertRaises(OSError),self.report.observing('p'):
            self.report.started('p','safe',self.identity,1);raise OSError('synthetic')
        r=self.report.history('p')[-1];self.assertNotIn(r['code'],self.report.SUCCESS)
        self.assertEqual(r['sources'][0]['code'],'CANCELLED')
    def test_automatic_retry_filters_existing_streaming_import_to_one_source(self):
        fake=sys.modules['epg'];fake._save_disk=mock.Mock();fake._mem_set=mock.Mock()
        sys.modules['epg_status'].update=mock.Mock();sys.modules['epg_status'].source_key=lambda s:s['id']
        sys.modules['epg_sources']._channels_cache_key=lambda pid:'safe'
        raw=self.m.xml('a',[self.m.event()]);seen=[]
        @contextlib.contextmanager
        def stream(source,**kwargs):seen.append(source.get('id'));yield io.BytesIO(raw)
        with mock.patch('epg_gate46.access',return_value='READY'),mock.patch.object(self.m.stream,'active_streams',return_value=iter([self.m.channel])),mock.patch.object(self.m.stream,'source_stream',stream),mock.patch('source_adapters.for_portal',side_effect=AssertionError('successful provider must not be resolved again')):
            self.assertTrue(self.m.stream.refresh(dict(self.m.portal,_epg_sources53=[self.identity]),force=True))
        self.assertEqual(seen,['one'])
    def test_manager_loading_uses_worker_and_report_stays_plain_readable(self):
        module=importlib.import_module('epg_manager53')
        with mock.patch.object(module,'ThreadPoolExecutor',QueuedPool):
            w=module.Manager53('XCMateEPGManager53.xml',str(ADDON),'Default','720p');w.configure(self.portal)
        self.addCleanup(w.close);w.show();self.assertEqual([row['key'] for row in w.rows][:2],['provider','one']);w._pool.drain();w.pump()
        self.assertIn('24 Stunden',w.getControl(102).label)
        self.report.store('p',self.run_record());self.m.dialog.select.return_value=0
        w.onClick(403);w._pool.drain();w.pump()
        self.assertEqual(w.mode,'report');self.assertTrue(w.getControl(300).visible)
        self.assertIn('Dauer:',w.getControl(300).text);w.onClick(409);self.assertEqual(w.getControl(300).scroll_position,12)
        w.onAction(types.SimpleNamespace(getId=lambda:92));w._pool.drain();w.pump();self.assertEqual(w.mode,'sources')
    def test_pending_inventory_does_not_block_job_or_replace_source_selection(self):
        module=importlib.import_module('epg_manager53')
        with mock.patch.object(module,'ThreadPoolExecutor',QueuedPool):
            w=module.Manager53('XCMateEPGManager53.xml',str(ADDON),'Default','720p');w.configure(self.portal)
        self.addCleanup(w.close)
        with mock.patch.object(self.report,'statistics',return_value=dict(code='DB_BUSY',sources=[])):
            w.show()
            control=w.getControl(200)
            self.assertGreaterEqual(control.size(),2)
            control.selectItem(1);item=control.getListItem(1)
            job=dict(id='12345678',state='RUNNING',source='one',sources={'one':dict(phase='STAGING',source_index=2,sources=2,programmes=21,staged=13)})
            w._job_loaded94(job)
            w._pool.drain();w.pump()
            self.assertFalse(w._inventory_future.done())
            self.assertIn('2 von 2',w.getControl(102).label)
            w._inventory_pool.drain();w.pump()
            self.assertEqual(w.rows[1]['inventory95'],'DB_BUSY')
            self.assertEqual(control.getSelectedPosition(),1)
            self.assertIs(control.getListItem(1),item)
            self.assertIn('2 von 2',w.getControl(102).label)

    def test_configured_agent_row_is_available_before_saved_counts(self):
        module=importlib.import_module('epg_manager53')
        agent=types.SimpleNamespace(SOURCE_RANK=1000,enabled=lambda:False)
        with mock.patch.object(module,'ThreadPoolExecutor',QueuedPool),mock.patch.dict(sys.modules,epg_agent100=agent):
            w=module.Manager53('XCMateEPGManager53.xml',str(ADDON),'Default','720p');w.configure(self.portal)
            w.show()
            self.addCleanup(w.close)
            self.assertEqual([source['key'] for source in w.rows],['provider','one','agent'])
            self.assertFalse(w.rows[-1]['enabled'])
            self.assertEqual(w.rows[-1]['inventory95'],'PENDING')
            w._pool.drain();w.pump()
            w.getControl(200).selectItem(2)
            w.onClick(200)
            self.assertEqual(w.next_action,'epg_agent100')

    def test_agent_manifest_check_shows_status_before_a_durable_import_job(self):
        module=importlib.import_module('epg_manager53')
        agent=types.SimpleNamespace(SOURCE_RANK=1000,enabled=lambda:True,state=lambda:{'code':'CHECKING'})
        with mock.patch.object(module,'ThreadPoolExecutor',QueuedPool),mock.patch.dict(sys.modules,epg_agent100=agent):
            w=module.Manager53('XCMateEPGManager53.xml',str(ADDON),'Default','720p');w.configure(self.portal)
            self.addCleanup(w.close);w.show();w._pool.drain();w.pump()
            w._pool.drain();w.pump()
            item=w.getControl(200).getListItem(2)
            self.assertIn('Manifest wird geprüft',item.label2)
            self.assertEqual(item.getProperty('Busy94'),'')
            self.assertFalse(w._job94)

    def test_inventory_result_after_four_seconds_is_still_accepted(self):
        module=importlib.import_module('epg_manager53')
        with mock.patch.object(module,'ThreadPoolExecutor',QueuedPool):
            w=module.Manager53('XCMateEPGManager53.xml',str(ADDON),'Default','720p');w.configure(self.portal)
        self.addCleanup(w.close);w.show();w._pool.drain();w.pump()
        test_clock=[100]
        def slow_statistics(pid,*,cancel):
            test_clock[0]+=7
            self.assertFalse(cancel())
            return dict(code='READY',sources=[dict(id=self.identity,channels=2,programmes=21)])
        with mock.patch.object(self.report,'statistics',side_effect=slow_statistics),mock.patch('time.monotonic',side_effect=lambda:test_clock[0]):
            w._inventory_pool.drain();w.pump()
        self.assertEqual(w.rows[1]['saved']['programmes'],21)

    def test_report_with_empty_history_shows_active_job_and_preserves_scroll(self):
        module=importlib.import_module('epg_manager53')
        with mock.patch.object(module,'ThreadPoolExecutor',QueuedPool):
            w=module.Manager53('XCMateEPGManager53.xml',str(ADDON),'Default','720p');w.configure(self.portal)
        self.addCleanup(w.close);w.show();w._pool.drain();w.pump()
        job=dict(id='12345678',state='RUNNING',source='one',sources={'one':dict(phase='STAGING',source_index=2,sources=2,programmes=21,staged=13)})
        with mock.patch('epg_jobs94.snapshot',return_value=job):
            w.onClick(403);w._pool.drain();w.pump()
        self.assertEqual(w.mode,'report')
        self.assertIn('RUNNING',w.getControl(300).text)
        self.assertIn('21',w.getControl(300).text)
        self.assertEqual(w.getFocusId(),409)
        for control in (401,402,403,405,407,410,411,412):
            self.assertFalse(w.getControl(control).isVisible())
        w.onClick(409)
        progress=dict(job['sources']['one'],staged=15)
        w._job_loaded94(dict(job,sources={'one':progress}))
        self.assertIn('15',w.getControl(300).text)
        self.assertEqual(w.getControl(300).scroll_position,12)
        w.onAction(types.SimpleNamespace(getId=lambda:92))
        self.assertEqual(w.mode,'sources')
        self.assertTrue(w.getControl(200).isVisible())
        self.assertEqual(w.getFocusId(),403)

    def test_report_avoids_both_button_rows(self):
        import xml.etree.ElementTree as ET
        root=ET.parse(ADDON/'resources/skins/Default/720p/XCMateEPGManager53.xml').getroot()
        control=lambda key:root.find(f".//control[@id='{key}']")
        top=lambda key:int(control(key).findtext('top'))
        bottom=lambda key:top(key)+int(control(key).findtext('height'))
        self.assertGreaterEqual(top(300),max(bottom(key) for key in (410,411,412,413)))
        self.assertLessEqual(bottom(300),min(top(key) for key in (404,406,408,409)))

    def test_explicit_intervals_only_written_after_user_selection(self):
        module=importlib.import_module('epg_manager53')
        with mock.patch.object(module,'ThreadPoolExecutor',QueuedPool):
            w=module.Manager53('XCMateEPGManager53.xml',str(ADDON),'Default','720p');w.configure(self.portal)
        self.addCleanup(w.close);w.show();w._pool.drain();w.pump()
        self.assertNotIn('epg_refresh_hours',self.m.options)
        self.m.dialog.select.return_value=2;w.onClick(407)
        self.assertEqual(self.m.options['epg_refresh_hours'],'12')


class Variant53Tests(unittest.TestCase):
    def setUp(self):
        p=mock.patch.object(sys,'path',[str(ADDON/'resources/lib')]+sys.path);p.start();self.addCleanup(p.stop)
    def test_welt_sd_hd_and_comedy_regular_plus_one_country_are_not_confused(self):
        from epg_variant53 import compatible
        self.assertFalse(compatible('WELT HD','WELT.de@HD','WELT','WELT.de@SD'))
        self.assertTrue(compatible('WELT HD','WELT.de@HD','WELT HD','WELT.de@HD'))
        self.assertFalse(compatible('Comedy Central','ComedyCentral.de','Comedy Central +1','ComedyCentral.de@Plus1'))
        self.assertFalse(compatible('Comedy Central','ComedyCentral.de','Comedy Central','ComedyCentral.at'))
        self.assertTrue(compatible('Comedy Central Deutschland','ComedyCentral.de','Comedy Central','ComedyCentral.de@SD'))
