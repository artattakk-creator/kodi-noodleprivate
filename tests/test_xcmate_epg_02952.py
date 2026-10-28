"""Real isolated master/fact stores; no device or private feeds."""
import contextlib,hashlib,importlib,io,json,os,sqlite3,sys,time,unittest
from pathlib import Path
from unittest import mock
from xml.sax.saxutils import escape
from xcmate027_fixture import Fixture


class EPG52(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.g=importlib.import_module('guide_store');self.stream=importlib.import_module('stream_epg')
        self.facts=importlib.import_module('programme_index46');self.merge=importlib.import_module('epg_merge52')
        self.config=dict(mappings={},sources=[dict(id='one',uri='https://fixture.invalid/one',enabled=True),dict(id='two',uri='https://fixture.invalid/two',enabled=True)])
        sys.modules['epg_sources'].configuration=lambda pid:self.config
        sys.modules['epg_sources']._channel_name_key=lambda name:str(name).casefold()
        self.channel=dict(sid='1',name='Station',epg_channel_id='a',kind='live')
        self.g.connect().close()
    def event(self,day=0,title='Programme',**extra):
        start=self.now-60 if day==0 else self.g.day_window(day,self.now)[0]+3600
        return dict(start=start,stop=start+1800,title=title,description='',**extra)
    def xml(self,cid,events):
        stamp=lambda v:time.strftime('%Y%m%d%H%M%S +0000',time.gmtime(v))
        return ('<tv><channel id="'+cid+'"><display-name>Station</display-name></channel>'+''.join('<programme channel="'+cid+'" start="'+stamp(e['start'])+'" stop="'+stamp(e['stop'])+'"><title>'+escape(e['title'])+'</title><desc>'+escape(e.get('description',''))+'</desc>'+e.get('extra','')+'</programme>' for e in events)+'</tv>').encode()
    def put(self,cid,events,index=0):
        raw=self.xml(cid,events)
        @contextlib.contextmanager
        def source(*a,**kw):yield io.BytesIO(raw)
        record={} if index==0 else self.config['sources'][index-1]
        with mock.patch.object(self.stream,'source_stream',source):
            return self.stream.import_source('p',dict(record,uri='https://fixture.invalid/feed'),index,[self.channel],self.config['mappings'])
    def master(self):
        db=sqlite3.connect(self.g.path())
        try:return db.execute('SELECT cid,start,stop,title,description,source FROM programmes ORDER BY cid,start,stop').fetchall()
        finally:db.close()
    def view(self,start=None,stop=None,mappings=None):
        from local_epg import window
        return window('p',[self.channel],self.config['mappings'] if mappings is None else mappings,start or self.now,stop or self.now+7200)

    def test_master_and_facts_share_seven_full_days_and_twenty_future_days(self):
        events=[self.event(day,str(day)) for day in (-8,-7,0,20,21)]
        self.put('a',events)
        self.assertEqual({r[3] for r in self.master()},{'-7','0','20'})
        db=self.facts.connect(False)
        try:self.assertEqual(db.execute('SELECT count(*) FROM facts').fetchone()[0],3)
        finally:db.close()

    def test_day_twenty_only_feed_is_successfully_published_to_master(self):
        counts=self.put('a',[self.event(20,'Last supplied day')]);self.assertEqual(counts['stored'],1)
        self.assertEqual(self.master()[0][3],'Last supplied day')

    def test_shorter_feed_keeps_history_and_future_programmes(self):
        self.put('a',[self.event(-7,'History'),self.event(),self.event(20,'Future')]);before=self.master()
        self.put('a',[self.event()]);self.assertEqual(self.master(),before)

    def test_partial_same_source_does_not_erase_description_or_image_facts(self):
        event=self.event();event['description']='Verified description';event['extra']='<icon src="https://images.invalid/real.png"/><category>Drama</category>'
        self.put('a',[event]);self.put('a',[self.event()])
        self.assertEqual(self.master()[0][4],'Verified description')
        row=self.view()['a'][0]
        self.assertEqual(row['descr'],'Verified description');self.assertEqual(row['xmltv_image'],'https://images.invalid/real.png')

    def test_same_slot_different_title_never_inherits_old_episode_image(self):
        event=self.event();event['extra']='<icon src="https://images.invalid/old.png"/>'
        self.put('a',[event]);self.put('a',[self.event(title='Different programme')])
        self.assertEqual(self.master()[0][3],'Different programme')
        self.assertFalse(self.view()['a'][0].get('xmltv_image'))

    def test_three_sources_with_distinct_channel_ids_fill_actual_time_gaps(self):
        one=self.event();two=dict(one,start=one['stop'],stop=one['stop']+1800,title='Second')
        three=self.event(20,'Third source future')
        self.put('a',[one]);self.put('b',[two],1);self.put('c',[three],2)
        self.assertEqual([r['name'] for r in self.view()['a']],['Programme','Second'])
        self.assertEqual(self.view(three['start'],three['stop'])['a'][0]['name'],'Third source future')

    def test_same_event_fills_missing_description_genre_episode_cast_and_image(self):
        primary=self.event();donor=dict(primary,description='Source two details',extra='<category>Drama</category><episode-num system="xmltv_ns">1.2.</episode-num><credits><actor>Actor</actor><director>Director</director></credits><icon src="https://images.invalid/event.png"/>')
        self.put('a',[primary]);self.put('b',[donor],1)
        row=self.view()['a'][0]
        self.assertEqual(row['descr'],'Source two details');self.assertEqual(row['genre'],'Drama')
        self.assertEqual(row['xmltv_image'],'https://images.invalid/event.png');self.assertIn('Actor',row['cast'])
        self.assertEqual((row['season'],row['episode']),(2,3));self.assertEqual(row['director'],'Director')
        self.assertEqual(row['field_sources52']['descr']['channel'],'b')
        self.assertTrue(row['field_sources52']['xmltv_image']['source'].startswith('external:'))

    def test_conflicting_events_keep_lastgood_slot_and_do_not_make_duplicates(self):
        one=self.event();two=dict(one,title='Conflicting other source')
        self.put('a',[one]);self.put('a',[two],1)
        self.assertEqual([e['name'] for e in self.view()['a']],['Programme'])
        db=sqlite3.connect(self.g.path())
        try:self.assertEqual(db.execute('SELECT count(*) FROM guide44_inputs').fetchone()[0],2)
        finally:db.close()

    def test_near_duplicate_fills_facts_but_real_repeat_is_retained(self):
        a=self.event();b=dict(a,start=a['start']+60,description='Extra detail')
        repeat=dict(a,start=a['stop']+3600,stop=a['stop']+5400)
        self.put('a',[a]);self.put('b',[b,repeat],1)
        result=self.view(stop=self.now+10000)['a']
        self.assertEqual(len(result),2);self.assertEqual(result[0]['descr'],'Extra detail')

    def test_manual_source_mapping_remains_strict_with_same_channel_ids(self):
        self.put('a',[self.event(title='First')],1);self.put('a',[self.event(title='Second')],2)
        from epg_binding48 import Mappings
        source=importlib.import_module('guide_publish44').source_id(self.config['sources'][1],2)
        mappings=Mappings({'1':'a'},{'1':dict(channel='a',source=source)})
        before=json.dumps(mappings.sources48,sort_keys=True)
        self.assertEqual(self.view(mappings=mappings)['a'][0]['name'],'Second')
        self.assertEqual(json.dumps(mappings.sources48,sort_keys=True),before)

    def test_missing_manual_mapping_never_uses_automatic_station_alias(self):
        self.put('b',[self.event()],1)
        self.assertEqual(self.view(mappings={'1':'missing'})['missing'],[])

    def test_different_episode_is_not_an_artwork_donor(self):
        base=dict(channel='a',name='Series',start_timestamp=100,stop_timestamp=1000,season=1,episode=1)
        donor=dict(base,episode=2,xmltv_image='https://images.invalid/wrong.png',source_key46='provider')
        result=self.merge.merge([base],[donor],'a')
        self.assertEqual(len(result),1);self.assertFalse(result[0].get('xmltv_image'))

    def test_conflicting_nonempty_episode_description_cannot_donate_an_image(self):
        one=dict(self.event(),description='Episode A')
        two=dict(self.event(),description='Episode B',extra='<episode-num system="xmltv_ns">0.7.</episode-num><icon src="https://images.invalid/wrong.png"/>')
        self.put('a',[one]);self.put('b',[two],1)
        row=self.view()['a'][0]
        self.assertEqual(row['descr'],'Episode A');self.assertFalse(row.get('xmltv_image'))

    def test_source_reordering_keeps_stable_alias_identity(self):
        self.put('a',[self.event()]);later=self.event(1,'Later');self.put('b',[later],1)
        self.config['sources'].reverse()
        self.assertEqual(self.view(later['start'],later['stop'])['a'][0]['name'],'Later')

    def test_disabled_source_is_not_used_for_new_gap_filling(self):
        self.put('a',[self.event()]);later=self.event(1,'Later');self.put('b',[later],1)
        self.config['sources'][0]['enabled']=False
        self.assertEqual(self.view(later['start'],later['stop'])['a'],[])

    def test_restart_and_offline_reads_do_not_write_or_fetch(self):
        self.put('a',[self.event()]);filename=Path(self.g.path());before=filename.read_bytes()
        importlib.reload(self.merge)
        with mock.patch.object(sys.modules['utils'],'http_get',side_effect=AssertionError('offline')):
            self.assertEqual(self.view()['a'][0]['name'],'Programme')
        self.assertEqual(filename.read_bytes(),before)

    def test_grid_mini_infobar_and_widget_use_same_now_identity_and_metadata(self):
        self.put('a',[self.event()]);self.put('b',[dict(self.event(),description='Shared details',extra='<icon src="https://images.invalid/event.png"/>')],1)
        from local_epg import now_next
        from programme_events46 import from_info
        info=now_next('p',[self.channel],{},self.now)['1'];description=from_info(self.portal,self.channel,info)
        grid=importlib.import_module('guide_grid_data').page(self.portal,0,self.now,category='a')
        event=grid['rows'][0]['events'][0]
        self.assertEqual(event['title'],info['now']);self.assertEqual(event['description'],info['description'])
        self.assertEqual(event['programme_key47'],description['key']);self.assertEqual(description['xmltv_image'],'https://images.invalid/event.png')

    def test_source_day_coverage_reports_real_union_not_duplicate_seconds(self):
        self.put('a',[self.event()]);coverage=importlib.import_module('guide_coverage52')
        report=coverage.inspect('p','1','a',now=self.now)
        self.assertEqual(report['code'],'READY');self.assertEqual(len(report['matrix']),28)
        today=next(r for r in report['matrix'] if r['day']==0)
        self.assertEqual(today['covered_seconds'],coverage.union_seconds([(self.now-60,self.now+1740)],*self.g.day_window(0,self.now)));self.assertGreater(report['last_good'],0)
        self.assertEqual(coverage.union_seconds([(1,5),(2,7)],0,10),6)

    def test_failed_parse_keeps_published_programmes_and_revision(self):
        self.put('a',[self.event()]);before=self.master()
        @contextlib.contextmanager
        def broken(*a,**kw):yield io.BytesIO(b'<tv><programme')
        with mock.patch.object(self.stream,'source_stream',broken),self.assertRaises(Exception):
            self.stream.import_source('p',{'uri':'https://fixture.invalid'},0,[self.channel],{})
        self.assertEqual(self.master(),before)

    def test_manual_and_automatic_refresh_allow_external_source_without_provider_url(self):
        self.config['sources']=self.config['sources'][:1]
        fake_epg=sys.modules['epg'];fake_epg._save_disk=mock.Mock();fake_epg._mem_set=mock.Mock()
        status=sys.modules['epg_status'];status.update=mock.Mock();status.source_key=lambda s:s['id']
        sys.modules['utils'].cache_set=mock.Mock()
        sys.modules['epg_sources']._channels_cache_key=lambda pid:'synthetic-channels'
        adapter=types.SimpleNamespace(get_xmltv_epg_url=lambda:None)
        raw=self.xml('a',[self.event()])
        @contextlib.contextmanager
        def source(*a,**kw):yield io.BytesIO(raw)
        with mock.patch('source_adapters.for_portal',return_value=adapter),mock.patch('epg_gate46.access',return_value='READY'),mock.patch.object(self.stream,'active_streams',return_value=iter([self.channel])),mock.patch.object(self.stream,'source_stream',source):
            self.assertTrue(self.stream.refresh(self.portal,force=True))
        with mock.patch('source_adapters.for_portal',return_value=adapter),mock.patch('epg_gate46.access',return_value='READY'),mock.patch.object(self.stream,'active_streams',return_value=iter([self.channel])),mock.patch.object(self.stream,'source_stream',source):
            self.assertTrue(self.stream.refresh(self.portal,force=False))
        self.assertEqual(self.master()[0][3],'Programme')

    def test_provider_url_failure_does_not_starve_enabled_external_sources(self):
        adapter=types.SimpleNamespace(get_xmltv_epg_url=mock.Mock(side_effect=OSError('synthetic provider error')))
        sys.modules['epg']._save_disk=mock.Mock();sys.modules['epg']._mem_set=mock.Mock()
        sys.modules['epg_status'].update=mock.Mock();sys.modules['epg_status'].source_key=lambda s:s['id']
        sys.modules['epg_sources']._channels_cache_key=lambda pid:'synthetic'
        raw=self.xml('a',[self.event()])
        @contextlib.contextmanager
        def source(*a,**kw):yield io.BytesIO(raw)
        with mock.patch('source_adapters.for_portal',return_value=adapter),mock.patch('epg_gate46.access',return_value='READY'),mock.patch.object(self.stream,'active_streams',return_value=iter([self.channel])),mock.patch.object(self.stream,'source_stream',source):
            self.stream.refresh(self.portal,force=True)
        self.assertEqual(self.master()[0][3],'Programme')
        self.assertTrue(any(c.args[2]=='PARTIAL_SUCCESS' for c in sys.modules['epg_status'].update.call_args_list))

    def test_populated_guide_backup_gate_is_not_bypassed_by_either_refresh(self):
        self.put('a',[self.event()]);before=self.master()
        sys.modules['epg_status'].update=mock.Mock()
        with mock.patch.object(self.stream,'source_stream',side_effect=AssertionError('must not download')):
            for force in (False,True):self.assertEqual(self.stream.refresh(self.portal,force=force),{})
        self.assertEqual(self.master(),before)
        self.assertTrue(all(c.args[2]=='BACKUP_REQUIRED' for c in sys.modules['epg_status'].update.call_args_list))

    def test_coverage_includes_preexisting_twenty_day_facts_without_reimport(self):
        self.put('a',[self.event(),self.event(20,'Future')])
        db=sqlite3.connect(self.g.path())
        with db:
            db.execute("DELETE FROM programmes WHERE title='Future'")
            db.execute("DELETE FROM guide44_inputs WHERE title='Future'")
        db.close()
        coverage=importlib.import_module('guide_coverage52').inspect('p','1','a',now=self.now)
        self.assertEqual(coverage['code'],'READY')
        self.assertEqual(next(r['covered_seconds'] for r in coverage['matrix'] if r['day']==20),1800)

    @unittest.skipUnless(hasattr(time,'tzset'),'local timezone switching unavailable')
    def test_local_calendar_horizon_and_coverage_respect_dst_short_and_long_days(self):
        import datetime
        previous=os.environ.get('TZ')
        try:
            os.environ['TZ']='Europe/Berlin';time.tzset()
            for year,month,day,seconds in [(2026,3,29,23*3600),(2026,10,25,25*3600)]:
                now=int(datetime.datetime(year,month,day,12).timestamp());a,b=self.g.day_window(0,now)
                self.assertEqual(b-a,seconds)
                coverage=importlib.import_module('guide_coverage52')
                self.assertEqual(coverage.union_seconds([(a,b)],a,b),seconds)
                left,right=self.facts.bounds(now)
                self.assertEqual(datetime.datetime.fromtimestamp(left).hour,0)
                self.assertEqual((datetime.datetime.fromtimestamp(right).date()-datetime.datetime(year,month,day).date()).days,21)
        finally:
            if previous is None:os.environ.pop('TZ',None)
            else:os.environ['TZ']=previous
            time.tzset()

    def test_indexed_legacy_m3u_and_stb_use_existing_streaming_source_path(self):
        import importlib.util
        filename=Path(self.stream.__file__).with_name('epg.py')
        spec=importlib.util.spec_from_file_location('actual_epg52',filename);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
        for kind in ('m3u','stb'):
            with mock.patch.object(sys.modules['xbmc'],'Monitor',return_value=types.SimpleNamespace(abortRequested=lambda:False)),mock.patch.object(self.stream,'refresh',return_value={'synthetic':[]}) as refresh:
                result=module._refresh_portal_epg_inner('p',dict(self.portal,type=kind),force=True)
            self.assertEqual(result,{'synthetic':[]});refresh.assert_called_once()


import types
