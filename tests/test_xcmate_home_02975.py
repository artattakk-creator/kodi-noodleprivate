"""Cold local EPG, receiver gates, event origins and .75 native skin contracts."""
import hashlib,importlib,json,time,types,unittest
from pathlib import Path
from unittest import mock
import xml.etree.ElementTree as E
from xcmate027_fixture import Fixture,ADDON
from xcmate050_fixture import Fixture50

class Cold75(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.local=importlib.import_module('local_epg');self.bridge=importlib.import_module('epg_handoff63');self.snapshot=importlib.import_module('epg_snapshot75')
        self.row=dict(sid='1',name='Station',epg_channel_id='xml')
        importlib.import_module('guide_store').import_cache('p',{'xml':[dict(name='Current programme',descr='Local text',start_timestamp=self.now-60,stop_timestamp=self.now+600),dict(name='Next programme',start_timestamp=self.now+600,stop_timestamp=self.now+3600)]},'synthetic75',now=self.now,trusted_feed=True)
    def seed(self):
        self.local.now_next('p',[self.row],{},now=self.now);self.assertTrue(self.snapshot.checkpoint('p',[self.row]))
    def test_cold_restart_restores_local_now_next_without_tune_sql_or_http(self):
        self.seed();self.properties.clear()
        with mock.patch('sqlite3.connect',side_effect=AssertionError('COLD_SQL')),mock.patch('utils.http_get',side_effect=AssertionError('COLD_HTTP')):
            self.assertEqual(self.snapshot.restore('p'),1);value=self.bridge.get('p','1',now=self.now)
        self.assertEqual((value['now'],value['next']),('Current programme','Next programme'))
    def test_changed_provider_does_not_restore_old_checkpoint(self):
        self.seed();self.properties.clear();self.portal['xc_user']='different'
        self.assertEqual(self.snapshot.restore('p'),0)
    def test_changed_profile_does_not_restore_old_checkpoint(self):
        self.seed();self.properties.clear()
        with mock.patch('epg_handoff63.profile_scope',return_value='different'):self.assertEqual(self.snapshot.restore('p'),0)
    def test_real_new_guide_generation_wins_over_checkpoint(self):
        self.seed();self.properties[self.bridge.meta_key('p')]='["new",9999999999]'
        self.assertEqual(self.snapshot.restore('p'),0)
    def test_checkpoint_io_failure_does_not_break_authoritative_epg(self):
        self.local.now_next('p',[self.row],{},now=self.now)
        with mock.patch('epg_snapshot75.tempfile.mkstemp',side_effect=OSError(28,'synthetic')):self.assertFalse(self.snapshot.checkpoint('p',[self.row]))
        self.assertEqual(self.bridge.get('p','1',now=self.now)['now'],'Current programme')
    def test_corrupt_checkpoint_is_bounded_and_ignored(self):
        Path(self.snapshot._path('p')).write_text('{broken')
        self.assertEqual(self.snapshot.restore('p'),0)
    def test_ended_event_not_restored_as_current(self):
        self.seed();self.properties.clear()
        with mock.patch('time.time',return_value=self.now+3601):self.assertEqual(self.snapshot.restore('p'),0)
    def test_missing_optional_progress_controls_still_commit_complete_bank(self):
        self.local.now_next('p',[self.row],{},now=self.now)
        hero=importlib.import_module('hero_epg63');selected={'XCMate.Home50':'true','XCMate.PortalId':'p','XCMate.MediaId':'1','XCMate.WidgetToken41':'1'*32,'XCMate.NoEpg63':'Unavailable','XCMate.RemainingFormat63':'{0} min'}
        values=lambda expr:selected.get(expr.removeprefix('ListItem.Property(').removesuffix(')'),'')
        window=types.SimpleNamespace(getControl=mock.Mock(side_effect=RuntimeError('Missing control')),getProperty=lambda k:self.properties.get(k,''),setProperty=self.properties.__setitem__)
        with mock.patch('xbmc.getSkinDir',return_value='skin.titan.bingie.mod',create=True),mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('xbmc.getInfoLabel',side_effect=values),mock.patch('xbmcgui.Window',return_value=window),mock.patch('sqlite3.connect',side_effect=AssertionError('GUI_SQL')):
            hero.poll()
        bank=self.properties['XCMate.Hero63.Active'];self.assertEqual(self.properties['XCMate.Hero63.'+bank+'.Title'],'Current programme');self.assertEqual(self.properties['XCMate.Hero63.'+bank+'.ProgressControl'],'UNAVAILABLE')

class Schedule75(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.s=importlib.import_module('home_schedule75');self.s.configure(self.portals)
    def test_live_not_visible_blocks_new_automatic_movie_and_series_jobs(self):
        with mock.patch.object(self.s,'applicable',return_value=True):
            self.assertFalse(self.s.allowed('vod'));self.assertFalse(self.s.allowed('series'));self.assertTrue(self.s.allowed('live'))
    def test_bingie_splash_also_blocks_automatic_covers_until_live_receiver_ready(self):
        with mock.patch('xbmc.getSkinDir',return_value='skin.titan.bingie.mod',create=True),mock.patch('xbmcgui.getCurrentWindowId',return_value=10099):
            self.assertFalse(self.s.allowed('vod'));self.assertFalse(self.s.allowed('series'))
    def test_queue_or_prepared_reference_cannot_fake_render_readiness(self):
        self.s.prepared('vod',24)
        self.assertEqual(self.s._read(self.s.KEY)['phase'],0)
    def test_live_then_movies_then_series_admission_order(self):
        state=self.s._read(self.s.KEY)
        with mock.patch.object(self.s,'applicable',return_value=True):
            for phase,expected in [(0,(False,False)),(1,(True,False)),(2,(True,True))]:
                state['phase']=phase;self.properties[self.s.KEY]=json.dumps(state)
                self.assertEqual((self.s.allowed('vod'),self.s.allowed('series')),expected)
    def test_focused_series_can_bypass_gate_only_for_selected_item(self):
        from epg_handoff63 import profile_scope
        self.properties[self.s.FOCUS]=json.dumps(dict(profile=profile_scope(),pid='p',sid='7',kind='series',at=time.monotonic()))
        self.assertEqual(self.s.focused_rows(self.portal,'series',[dict(sid=str(i)) for i in range(20)]),[dict(sid='7')])
        self.assertEqual(self.s._read(self.s.KEY)['phase'],0)
    def test_stale_focus_and_foreign_profile_cannot_bypass(self):
        self.properties[self.s.FOCUS]=json.dumps(dict(profile='foreign',pid='p',sid='7',kind='series',at=time.monotonic()))
        self.assertEqual(self.s.focused_rows(self.portal,'series',[dict(sid='7')]),[])
    def test_profile_or_start_group_change_invalidates_only_phase_receipts(self):
        old=self.s._read(self.s.KEY);old['phase']=3;self.properties[self.s.KEY]=json.dumps(old)
        self.portal['start_group_id']='changed';new=self.s.configure(self.portals)
        self.assertEqual(new['phase'],0);self.assertNotEqual(new['context'],old['context']);self.assertEqual(self.portal['xc_pass'],'SECRET')
    def test_same_context_keeps_ready_receipts(self):
        old=self.s._read(self.s.KEY);old['phase']=3;self.properties[self.s.KEY]=json.dumps(old)
        self.assertEqual(self.s.configure(self.portals)['phase'],3)
    def test_visible_five_follow_actual_viewport_and_focus_first(self):
        module=importlib.import_module('programme_prefetch48');rows=[dict(sid=str(i)) for i in range(88)]
        with mock.patch('hero_epg63.focused64',return_value='40'),mock.patch.object(self.s,'visible_position',return_value=38):
            batch=module.visible75(self.portal,rows)
        self.assertEqual(batch[0]['sid'],'40');self.assertEqual({r['sid'] for r in batch},{'38','39','40','41','42'})

class QueueFocus75(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.options['programme_art_local69']=True
        import sys
        sys.modules.pop('programme_urls55',None)
        self.q=importlib.import_module('programme_urls55')
        self.q._thread=mock.Mock();self.q._thread.is_alive.return_value=True
    def event75(self,key):return dict(key=key,title='Synthetic focus',pid='p',sid=key,placeholder='/synthetic/none.png')
    def test_focus_enters_a_full_all_urgent_queue_without_exceeding_24(self):
        for i in range(24):self.assertTrue(self.q.enqueue(self.event75(str(i)),priority68=True))
        self.assertTrue(self.q.enqueue(self.event75('focus'),priority68=2))
        self.assertEqual((len(self.q._pending),len(self.q._queue),len(self.q._urgent68)),(24,24,24))
        self.assertEqual(next(iter(self.q._queue)),'focus');self.assertNotIn('23',self.q._urgent68)
    def test_existing_focus_is_promoted_without_a_second_job_or_worker(self):
        self.q.enqueue(self.event75('old'),priority68=True);self.q.enqueue(self.event75('focus'))
        self.assertFalse(self.q.enqueue(self.event75('focus'),allow_lookup=True,priority68=2))
        self.assertEqual(list(self.q._queue),['focus','old']);self.assertEqual(len(self.q._pending),2)
        self.assertTrue(self.q._queue['focus'][1])
    def test_queued_intent_promotes_exact_profile_and_never_reads_files_or_http(self):
        from programme_requests68 import identity
        event=self.event75('focus');self.q.enqueue(self.event75('old'),priority68=True);self.q.enqueue(event)
        tag=identity(event)
        with mock.patch('builtins.open',side_effect=AssertionError('FOCUS_FILE')),mock.patch('media_sources43.get',side_effect=AssertionError('FOCUS_HTTP')):
            self.assertTrue(self.q.promote_focus75(tag))
        self.assertEqual(next(iter(self.q._queue)),'focus')
        with mock.patch('epg_handoff63.profile_scope',return_value='foreign'):
            self.assertFalse(self.q.promote_focus75(tag))
    def test_latest_focus_wins_even_after_the_visible_job_fairness_burst(self):
        for name in ('visible','old-focus','new-focus'):
            self.q.enqueue(self.event75(name),priority68=2 if 'focus' in name else True)
        self.q.enqueue(self.event75('background'));self.q._burst68=3;order=[]
        def resolved(event,**kw):
            order.append(event['key']);self.q._stop.set()
            return dict(code='NO_MATCH',source='placeholder')
        with mock.patch.object(self.q,'resolve',side_effect=resolved):self.q._run()
        self.assertEqual(order,['new-focus']);self.assertEqual(len(self.q._pending),3)

class Origin75(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.origin=importlib.import_module('programme_origin75');self.urls=importlib.import_module('programme_urls55');self.url='https://public.example.org/image.jpg';self.event=dict(key='a'*64,pid='p',sid='1',canonical='xml',xmltv_image=self.url)
    def test_exact_configured_event_url_is_eligible_but_not_preapproved(self):
        self.assertTrue(self.origin.candidate(self.event,self.url,'xmltv_event'));self.assertFalse(self.urls.safe(self.url))
    def test_grant_is_exact_url_short_lived_and_profile_bound(self):
        self.origin.grant(self.url);self.assertTrue(self.urls.safe(self.url));self.assertFalse(self.urls.safe(self.url+'other'))
        with mock.patch('time.time',return_value=time.time()+301):self.assertFalse(self.urls.safe(self.url))
        with mock.patch('epg_handoff63.profile_scope',return_value='foreign'):self.assertFalse(self.urls.safe(self.url))
    def test_foreign_or_invented_image_is_never_provider_authorized(self):
        self.assertFalse(self.origin.candidate(self.event,'https://foreign.example.org/image.jpg','xmltv_event'));self.assertFalse(self.origin.candidate(self.event,self.url,'tmdb_helper'))
    def test_local_ip_http_query_credentials_and_traversal_rejected(self):
        for value in ['https://127.0.0.1/x.png','https://10.0.0.1/x.png','http://public.example.org/x.jpg','https://public.example.org/x?token=a','https://user:pass@public.example.org/x.jpg','https://public.example.org/user/SECRET/x.jpg','https://public.example.org/a/%2e%2e/x.jpg','https://host.internal/x.jpg']:
            self.assertFalse(self.origin.candidate(dict(self.event,xmltv_image=value),value,'xmltv_event'),value)
    def test_legacy_blocked_negative_retries_one_event_only_once_after_upgrade(self):
        from programme_status70 import legacy_negative
        value=dict(source='placeholder',code='BLOCKED_IMAGE_HOST_OR_URL');self.assertTrue(legacy_negative(value));self.assertFalse(legacy_negative(dict(value,origin_policy75=1)))
    def test_verified_xmltv_candidate_requires_worker_preflight_before_url_display(self):
        event=dict(self.event,title='Exact film',genre='Film',year=2026,start=self.now-60,stop=self.now+900,placeholder=str(ADDON/'resources/media/programme46/neutral.png'))
        with mock.patch('programme_urls55.probe') as probe:
            art=self.urls.resolve(event,allow_lookup=False,url_mode69=True)
        probe.assert_called_once_with(self.url,cancel=mock.ANY)
        self.assertEqual(art['source'],'xmltv_event');self.assertEqual(art['code'],'READY');self.assertTrue(self.urls.safe(self.url))
    def test_failed_image_preflight_never_grants_public_url(self):
        from media_sources43 import SourceError
        event=dict(self.event,title='Exact film',start=self.now-60,stop=self.now+900,placeholder=str(ADDON/'resources/media/programme46/neutral.png'))
        with mock.patch('programme_urls55.probe',side_effect=SourceError('INVALID_IMAGE')):
            art=self.urls.resolve(event,allow_lookup=False,url_mode69=True)
        self.assertEqual(art['source'],'placeholder');self.assertFalse(self.urls.safe(self.url))

class Schema75(Fixture,unittest.TestCase):
    def test_missing_kodi_views_are_reported_without_database_changes(self):
        import sqlite3,hashlib
        filename=self.folder/'MyVideos131.db';db=sqlite3.connect(filename);db.execute('CREATE TABLE keep(value TEXT)');db.execute("INSERT INTO keep VALUES('unchanged')");db.commit();db.close()
        before=hashlib.sha256(filename.read_bytes()).hexdigest()
        with mock.patch('xbmcvfs.translatePath',return_value=str(self.folder)):
            result=importlib.import_module('kodi_schema75').inspect()
        self.assertEqual(result['code'],'KODI_LIBRARY_MISSING_VIEWS');self.assertTrue(result['read_only'])
        self.assertEqual(hashlib.sha256(filename.read_bytes()).hexdigest(),before)
    def test_no_kodi_database_is_not_created_by_diagnosis(self):
        with mock.patch('xbmcvfs.translatePath',return_value=str(self.folder)):
            result=importlib.import_module('kodi_schema75').inspect()
        self.assertEqual(result['code'],'KODI_LIBRARY_NOT_FOUND');self.assertFalse(list(self.folder.glob('MyVideos*')))

class Skin75(Fixture50,unittest.TestCase):
    def navigation75(self):
        target=self.skin/'xml/IncludesBingie.xml'
        raw=(ADDON.parents[1]/'tests/fixtures/bingie223_navigation75.xml').read_bytes()
        self.assertEqual(hashlib.sha256(raw).hexdigest(),'ab30a92b13a80123cf7ac2a6a24f4b3f2e9669c3a2da769666868cc60649077b')
        target.write_bytes(raw)
        return target,raw
    def test_five_file_navigation_transaction_restores_exact_upstream_bytes(self):
        target,raw=self.navigation75();before=self.skin_bytes();saved=(self.menu.read_bytes(),self.prop.read_bytes())
        plan=self.skinmod.prepare(self.skin);self.assertEqual(len(plan['entries']),5)
        self.assertEqual(target.read_bytes(),raw)
        self.skinmod.apply(plan['id'],self.skin,confirmed=True)
        tree=E.parse(target)
        icon=tree.find("variable[@name='XCMate75.MenuIcon']")
        self.assertEqual(len({n.text for n in icon.findall('value')[:-1]}),7)
        self.assertEqual(icon.findall('value')[-1].text,'$INFO[ListItem.Icon]')
        self.assertTrue(self.skinmod.applied(self.skin))
        self.skinmod.apply(plan['id'],self.skin,confirmed=True,restore=True)
        self.assertEqual(target.read_bytes(),raw);self.assertEqual(self.skin_bytes(),before)
        self.assertEqual((self.menu.read_bytes(),self.prop.read_bytes()),saved)
    def test_navigation_replace_failure_before_and_after_rolls_back_all_five(self):
        target,raw=self.navigation75();before=self.skin_bytes()
        for after in (False,True):
            with self.subTest(after=after):
                plan=self.skinmod.prepare(self.skin);original=self.tx.replace;failed=[False]
                def replace(path,data,expected,mode=0o600):
                    if Path(path)==target and not failed[0]:
                        failed[0]=True
                        if after:original(path,data,expected,mode)
                        raise OSError('synthetic navigation write fault')
                    return original(path,data,expected,mode)
                with mock.patch.object(self.tx,'replace',side_effect=replace),self.assertRaises(OSError):
                    self.skinmod.apply(plan['id'],self.skin,confirmed=True)
                self.assertEqual(target.read_bytes(),raw);self.assertEqual(self.skin_bytes(),before)
    def test_unknown_navigation_xml_blocks_all_five_files_before_write(self):
        target,raw=self.navigation75();target.write_bytes(raw+b'<!-- custom -->');before=self.skin_bytes()
        with self.assertRaisesRegex(ValueError,'UNVERIFIED_NAVIGATION_SKIN'):self.skinmod.prepare(self.skin)
        self.assertEqual(target.read_bytes(),raw+b'<!-- custom -->');self.assertEqual(self.skin_bytes(),before)
    def test_right_panel_and_one_fixed_viewport_do_not_change_saved_bindings(self):
        before=self.skin_bytes();menu=self.menu.read_bytes();props=self.prop.read_bytes();plan=self.skinmod.prepare(self.skin)
        self.skinmod.apply(plan['id'],self.skin,confirmed=True)
        tree=E.parse(self.skin/'xml/IncludesHomeWidgets.xml');hero=tree.find("include[@name='XCMate50.Hero']")
        image=hero.find(".//control[@id='296751']");panel=hero.find(".//control[@id='296750']")
        self.assertEqual((image.findtext('left'),image.findtext('width'),panel.findtext('left'),panel.findtext('width')),('270','1080','1350','540'))
        self.assertEqual(self.menu.read_bytes(),menu);self.assertEqual(self.prop.read_bytes(),props)
        self.skinmod.apply(plan['id'],self.skin,confirmed=True,restore=True);self.assertEqual(self.skin_bytes(),before)
    def test_all_long_text_and_attribution_are_children_of_right_panel(self):
        tree=E.parse(ADDON/'resources/bingie75/IncludesXCMate75.xml');hero=tree.find("include[@name='XCMate50.Hero']/control");panel=hero.find("control[@id='296750']")
        self.assertFalse(hero.findall("control[@type='textbox']"));self.assertTrue(panel.findall("control[@type='textbox']"))
        self.assertFalse(any('tmdb' in (n.findtext('texture') or '') for n in hero.findall("control[@type='image']")))
    def test_unknown_skin_changes_are_blocked_before_any_write(self):
        p=self.skin/'xml/IncludesHomeBingie.xml';p.write_bytes(p.read_bytes()+b'<!-- private -->');before=self.skin_bytes()
        with self.assertRaises(ValueError):self.skinmod.prepare(self.skin)
        self.assertEqual(self.skin_bytes(),before)

class Stop75(Fixture,unittest.TestCase):
    def test_five_and_ten_second_observations_never_query_player_or_repost_stop(self):
        module=importlib.import_module('live_stop75');value=dict(token=['live',dict(nonce='a'*32)],native_posted=True,native_ack='b'*32,posted_at75=time.monotonic()-11,strategy42='direct41')
        with mock.patch('xbmc.Player',side_effect=AssertionError('NATIVE_MUTEX')),mock.patch('xbmc.executebuiltin',side_effect=AssertionError('REPOST_STOP')):
            module.observe(value);module.observe(value)
        self.assertFalse(self.native_builtins)

class LateFullscreen75(unittest.TestCase):
    def test_twenty_late_ack_cycles_can_leave_empty_owned_fullscreen_once(self):
        from test_xcmate_live_recovery_02946 import LateReturn46
        for _ in range(20):
            model=LateReturn46(methodName='runTest');model.setUp()
            try:
                model.timeout(True);before=list(model.m.native_builtins)
                with mock.patch('xbmcgui.getCurrentWindowId',return_value=12005):model.tick(20)
                self.assertEqual(model.m.exit.state()['phase'],'complete')
                self.assertEqual(model.m.native_builtins,before);self.assertEqual(len(model.m.builtins),1)
            finally:model.doCleanups()
