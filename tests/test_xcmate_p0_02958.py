"""Distinct P0 evidence. Synthetic tests never assert Android/Home pixels."""
import ast,copy,hashlib,importlib,json,sys,time,unittest
from pathlib import Path
from unittest import mock
import xml.etree.ElementTree as ET
from xcmate027_fixture import Fixture,ADDON,LIB,QueuedPool


class Provider58(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.provider=importlib.import_module('provider_epg58')
        self.portal.update(provider_epg_enabled=False)
        def update(pid,data):
            item=next((p for p in self.portals if p['id']==pid),None)
            if item is None:return False
            item.update(data);return True
        sys.modules['portals'].update=mock.Mock(side_effect=update)
    def test_toggle_rereads_saved_state_not_stale_dialog_row(self):
        stale=dict(self.portal);self.portal['provider_epg_enabled']=True
        self.assertFalse(self.provider.toggle(stale)['provider_epg_enabled'])
    def test_only_selected_portal_changed_and_other_fields_preserved(self):
        second=dict(self.portal,id='other',provider_epg_enabled=True);self.portals.append(second)
        before=copy.deepcopy(self.portals)
        self.provider.toggle(self.portal)
        before[0]['provider_epg_enabled']=True
        self.assertEqual(self.portals,before)
    def test_missing_portal_cannot_be_created_or_enabled(self):
        with self.assertRaises(ValueError):self.provider.toggle(dict(self.portal,id='missing'))
        sys.modules['portals'].update.assert_not_called()
    def test_update_failure_is_not_reported_as_activation(self):
        sys.modules['portals'].update.return_value=False;sys.modules['portals'].update.side_effect=None
        with self.assertRaises(OSError):self.provider.toggle(self.portal)
    def test_success_without_persistence_is_rejected(self):
        sys.modules['portals'].update.side_effect=None;sys.modules['portals'].update.return_value=True
        with self.assertRaises(OSError):self.provider.toggle(self.portal)
    def test_non_xtream_portal_switch_is_rejected(self):
        self.portal['type']='m3u'
        with self.assertRaises(ValueError):self.provider.toggle(self.portal)
    def test_activation_never_requests_import_or_marks_ready(self):
        with mock.patch('epg.request_refresh',create=True,side_effect=AssertionError('implicit download')):
            value=self.provider.toggle(self.portal)
        self.assertTrue(value['provider_epg_enabled']);self.assertNotIn('READY',value)
    def test_same_feed_is_exact_without_merging_different_credentials(self):
        self.assertTrue(self.provider.same_feed('https://FEED.invalid:443/x?a=1','https://feed.invalid/x?a=1#fragment'))
        for uri in ('http://feed.invalid/x?a=1','https://feed.invalid/X?a=1','https://feed.invalid/x?a=2','https://other.invalid/x?a=1'):
            self.assertFalse(self.provider.same_feed('https://feed.invalid/x?a=1',uri))
    def test_duplicate_actual_provider_feed_cannot_be_added_as_external(self):
        self.portal['epg_url']='https://feed.invalid/authorized.xml'
        add=mock.Mock()
        with mock.patch.object(sys.modules['epg_sources'],'add_source',add,create=True):
            with self.assertRaises(ValueError):self.provider.add_source(self.portal,'extra',self.portal['epg_url'])
        add.assert_not_called()
    def test_distinct_authorized_external_address_is_retained(self):
        self.portal['epg_url']='https://feed.invalid/authorized.xml';add=mock.Mock()
        with mock.patch.object(sys.modules['epg_sources'],'add_source',add,create=True):self.provider.add_source(self.portal,'extra','https://extra.invalid/given.xml')
        add.assert_called_once_with('p','extra','https://extra.invalid/given.xml',False)
    def test_unavailable_provider_url_does_not_prevent_a_distinct_external_source(self):
        self.portal['epg_url']='';add=mock.Mock()
        with mock.patch('source_adapters.for_portal',side_effect=OSError('synthetic provider failure')),mock.patch.object(sys.modules['epg_sources'],'add_source',add,create=True):
            self.provider.add_source(self.portal,'extra','https://extra.invalid/given.xml')
        add.assert_called_once()
    def test_non_xtream_portals_keep_existing_external_xmltv_addition(self):
        self.portal['type']='m3u';add=mock.Mock()
        with mock.patch('source_adapters.for_portal',side_effect=AssertionError('Xtream URL for M3U')),mock.patch.object(sys.modules['epg_sources'],'add_source',add,create=True):
            self.provider.add_source(self.portal,'extra','https://extra.invalid/given.xml')
        add.assert_called_once_with('p','extra','https://extra.invalid/given.xml',False)
    def manager(self):
        module=importlib.import_module('epg_manager53')
        with mock.patch.object(module,'ThreadPoolExecutor',QueuedPool):
            w=module.Manager53('XCMateEPGManager53.xml',str(ADDON),'Default','720p');w.configure(dict(self.portal))
        self.addCleanup(w.close);w.show();w._pool.drain();w.pump();return w
    def test_actual_portal_json_survives_fresh_module_reader(self):
        import importlib.util
        def module():
            spec=importlib.util.spec_from_file_location('real_portals58',LIB/'portals.py')
            value=importlib.util.module_from_spec(spec);spec.loader.exec_module(value);return value
        real=module();real.save_all([dict(self.portal),dict(self.portal,id='other')])
        with mock.patch.dict(sys.modules,portals=real):self.provider.toggle(self.portal)
        fresh=module();self.assertTrue(fresh.get_by_id('p')['provider_epg_enabled'])
        self.assertFalse(fresh.get_by_id('other')['provider_epg_enabled'])
        self.assertEqual(fresh.get_by_id('p')['xc_pass'],self.portal['xc_pass'])
    def test_visible_toggle_is_initial_remote_focus_and_roundtrips(self):
        w=self.manager();self.assertEqual(w.getFocusId(),410)
        self.assertIn('aktivieren',w.getControl(410).label)
        w.onClick(410);w._pool.drain();w.pump();w._pool.drain();w.pump()
        self.assertTrue(self.portal['provider_epg_enabled']);self.assertIn('deaktivieren',w.getControl(410).label)
        w.close();again=self.manager();self.assertIn('deaktivieren',again.getControl(410).label)
    def test_back_remains_responsive_during_pending_switch(self):
        w=self.manager();w.onClick(410);w.onClick(406);w._pool.drain();self.assertTrue(w._closed)
    def test_remote_control_graph_reaches_sources_and_every_button_at_720_and_1080(self):
        root=ET.parse(ADDON/'resources/skins/Default/720p/XCMateEPGManager53.xml').getroot()
        controls={int(n.get('id')):n for n in root.findall('.//control') if n.get('id') and n.get('type') in ('button','list')}
        seen=set();todo=[410]
        while todo:
            cid=todo.pop()
            if cid in seen:continue
            seen.add(cid)
            todo.extend(int(controls[cid].findtext('on'+k)) for k in ('up','down','left','right'))
        self.assertEqual(seen,set(controls))
        for scale in (1,1.5):
            for n in controls.values():
                self.assertLessEqual((int(n.findtext('top'))+int(n.findtext('height')))*scale,720*scale)
        button=controls[410];source=controls[200]
        self.assertLess(int(button.findtext('top'))+int(button.findtext('height')),int(source.findtext('top')))


class WidgetProvider58(Fixture,unittest.TestCase):
    def test_native_movies_and_series_do_not_apply_saved_non_provider_metadata(self):
        from media_overrides43 import save
        for kind,action in [('vod','widget_recent_vod'),('series','widget_recent_series')]:
            rows,_=importlib.import_module('widget_data41').snapshot(self.portal,kind)
            self.assertTrue(rows)
            self.assertTrue(save('p',kind,rows[0]['sid'],metadata={'plot':'MANUAL_NON_PROVIDER','year':1999}))
            self.added.clear();self.router._directory_done=False;self.router._params.update(action=action)
            with mock.patch('media_overrides43.apply_many',side_effect=AssertionError('widget manual lookup')):
                self.routes.dispatch(self.router)
            self.assertTrue(self.added)
            self.assertNotIn('MANUAL_NON_PROVIDER',str([li.info for _,li,_ in self.added]))
            self.assertTrue(list(self.folder.rglob('media_choices43/*.json')))
    def test_widget_art_ignores_manual_choice_but_keeps_provider_cached_image(self):
        from widget_art44 import art
        row=dict(sid='1',kind='vod',name='Provider',cover='https://images.example.test/provider.png')
        with mock.patch('media_overrides43.cached_art',side_effect=AssertionError('non-provider art')),mock.patch('media_art.cached',return_value='/provider-cached.png'):
            self.assertEqual(art(row,{})['poster'],'/provider-cached.png')
    def test_missing_kind_is_normalized_at_shared_widget_descriptor(self):
        from widget_items45 import describe
        with mock.patch('media_overrides43.cached_art',side_effect=AssertionError('non-provider art')):
            value=describe(self.portal,'series',dict(sid='1',name='Provider'),{})
        self.assertTrue(value['art']['poster'].endswith('series.png'))
    def test_shared_asset_source_has_explicit_provider_only_boundary(self):
        from programme_assets47 import sources
        row=dict(sid='1',kind='series',name='Provider',cover='https://images.example.test/provider.png')
        with mock.patch('media_overrides43.cached_art',return_value={'poster':'/manual.png'}):
            self.assertEqual(sources(row)['poster'],'/manual.png')
            self.assertEqual(sources(row,provider_only=True)['poster'],row['cover'])
    def test_widget_renderer_never_queries_helper_or_tmdb(self):
        from widget_render47 import values
        for kind in ('vod','series'):
            with mock.patch('programme_helper57.lookup',side_effect=AssertionError('Helper lookup')),mock.patch('media_overrides43.cached_art',side_effect=AssertionError('non-provider override')):
                result=values(self.portal,kind,[dict(sid='1',kind=kind,name='Provider')],{})
            self.assertEqual(len(result),1)


class Consumer58(Fixture,unittest.TestCase):
    def setUp(self):
        super().setUp();self.consumer=importlib.import_module('widget_consumer58')
        self.profile=self.folder/'profile';self.skin=self.folder/'skin';self.generated=self.folder/'generated.xml'
        self.prop=self.profile/'addon_data/script.skinshortcuts/skin.titan.bingie.mod.properties';self.prop.parent.mkdir(parents=True)
        self.rows=[]
        for slot,kind in enumerate(('vod','series')):
            suffix='.'+str(slot) if slot else '';action='widget_recent_'+kind
            for key,val in dict(widget='Addon',widgetName=kind,widgetType='movies' if kind=='vod' else 'tvshows',widgetTarget='videos',widgetPath='plugin://plugin.video.xtreammate/?action='+action+'&pid=p').items():self.rows.append(['mainmenu','10000',key+suffix,val])
        self.prop.write_text(repr(self.rows))
        self.generated.write_text('<includes><include name="Widgets"><control type="panel" id="510"><content>plugin://plugin.video.xtreammate/?action=widget_recent_vod&amp;pid=p</content></control><control type="panel" id="511"><content>plugin://plugin.video.xtreammate/?action=widget_recent_series&amp;pid=p</content></control></include></includes>')
    def inspect(self,probe=None):return self.consumer.inspect(self.profile,self.skin,self.generated,'p',probe)
    def test_saved_and_generated_are_distinct_from_actual_home_and_pixels(self):
        before={str(p):p.read_bytes() for p in self.folder.rglob('*') if p.is_file()}
        result=self.inspect()
        for kind in ('vod','series'):
            v=result['kinds'][kind];self.assertEqual(v['binding'],'BINDING_PRESENT');self.assertEqual(v['consumer'],'GENERATED_CONSUMER_PRESENT');self.assertEqual(v['home'],'NOT_OBSERVED');self.assertEqual(v['pixels'],'NOT_TESTED')
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.folder.rglob('*') if p.is_file()})
    def test_existing_bindings_missing_generated_consumers_are_not_reported_unbound(self):
        self.generated.write_text('<includes/>');result=self.inspect()
        self.assertEqual(result['kinds']['vod']['binding'],'BINDING_PRESENT');self.assertEqual(result['kinds']['vod']['consumer'],'SKIN_CONSUMER_MISSING')
    def test_hidden_actual_home_consumer_is_not_directory_success(self):
        result=self.inspect(lambda cid:dict(visible=False,items=24))
        self.assertEqual(result['kinds']['vod']['home'],'SKIN_CONSUMER_HIDDEN')
    def test_visible_nonempty_home_still_does_not_claim_decoded_cover_pixels(self):
        result=self.inspect(lambda cid:dict(visible=True,items=24))
        self.assertEqual(result['kinds']['series']['home'],'HOME_ITEMS_PRESENT');self.assertEqual(result['kinds']['series']['pixels'],'NOT_TESTED')
    def test_unbound_live_home_is_distinct_from_failed_media_widgets(self):
        self.assertEqual(self.inspect()['kinds']['live']['binding'],'BINDING_NOT_FOUND')
    def test_foreign_portal_cannot_satisfy_home_consumer(self):
        self.generated.write_bytes(self.generated.read_bytes().replace(b'pid=p',b'pid=other'))
        self.assertEqual(self.inspect()['kinds']['vod']['generated_consumers'],0)
    def test_invalid_widget_type_is_identified_without_repairing_profile(self):
        self.rows[2][3]='videos';self.prop.write_text(repr(self.rows));before=self.prop.read_bytes()
        self.assertEqual(self.inspect()['kinds']['vod']['binding'],'BINDING_INVALID');self.assertEqual(before,self.prop.read_bytes())
    def test_stock_bingie_parametric_consumer_is_resolved_without_skin_edits(self):
        import zipfile
        fixture=Path(__file__).parent/'fixtures/bingie223_reference50.zip'
        with zipfile.ZipFile(fixture) as z:
            name=next(n for n in z.namelist() if n.endswith('xml/IncludesHomeWidgets.xml'))
            layout=z.read(name)
        (self.skin/'xml').mkdir(parents=True);(self.skin/'xml/IncludesHomeWidgets.xml').write_bytes(layout)
        self.generated.write_text('<includes><include content="widget_base"><param name="widgetid" value="1510"/><param name="contentStyle" value="normal"/><param name="widgetTarget" value="videos"/><param name="widgetPath" value="plugin://plugin.video.xtreammate/?action=widget_recent_vod&amp;pid=p"/></include></includes>')
        result=self.inspect(lambda cid:dict(visible=cid==1510,items=24))
        self.assertEqual(result['kinds']['vod']['home'],'HOME_ITEMS_PRESENT')
        self.assertEqual((self.skin/'xml/IncludesHomeWidgets.xml').read_bytes(),layout)
    def test_unknown_parametric_pipeline_is_unverified_not_missing_or_success(self):
        self.generated.write_text('<includes><include content="widget_base"><param name="widgetid" value="1510"/><param name="widgetPath" value="plugin://plugin.video.xtreammate/?action=widget_recent_vod&amp;pid=p"/></include></includes>')
        value=self.inspect()['kinds']['vod']
        self.assertEqual(value['binding'],'BINDING_PRESENT');self.assertEqual(value['consumer'],'SKIN_CONSUMER_UNVERIFIED')
        self.assertEqual(value['include_declarations'],1)
    def test_malicious_properties_and_xml_entities_rejected(self):
        raw=self.prop.read_bytes();self.prop.write_text("__import__('os').getcwd()")
        with self.assertRaises(ValueError):self.inspect()
        self.prop.write_bytes(raw);self.generated.write_text('<!DOCTYPE x><includes/>')
        with self.assertRaises(ValueError):self.inspect()


class StopEvidence58(unittest.TestCase):
    def setUp(self):
        import test_xcmate_live_stop_02942 as old
        self.m=old.LiveStop42(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.observer=importlib.import_module('live_stop58');self.observer._last.clear()
    def test_native_deadlock_is_latched_and_reported_without_player_or_gui_queries(self):
        self.m.native_hang=True;self.m.request();self.m.release();self.m.release();self.m.timeout()
        value=self.m.jobs.state();self.assertTrue(value['native_posted']);self.assertFalse(value.get('worker_done'));self.assertTrue(self.m.jobs.blocked())
        with mock.patch.object(self.m.xbmc,'Player',side_effect=AssertionError('player lock')),mock.patch.object(self.m.gui,'getCurrentWindowId',side_effect=AssertionError('GUI query')),mock.patch.object(self.m.xbmc,'executebuiltin',side_effect=AssertionError('second Stop')):
            self.observer.observe(value);self.observer.observe(value)
        messages=[s for s in self.m.logs if '[STOP58]' in s]
        self.assertEqual(len(messages),1);self.assertIn('NATIVE_QUEUE_UNRETURNED',messages[0]);self.assertIn('fullscreen42',messages[0])
    def test_worker_done_without_fifo_property_is_never_native_ack(self):
        value=dict(token=['live',{'nonce':'synthetic'}],phase='timeout',native_posted=True,worker_done=True,strategy42='direct41')
        self.observer.observe(value)
        self.assertIn('NATIVE_QUEUE_UNRETURNED',self.m.logs[-1]);self.assertIn('native_ack=0',self.m.logs[-1])
    def test_late_fifo_property_is_distinguished_without_posting_anything(self):
        nonce='1'*32;self.m.m.properties['XCMate.NativeStopAck41']=nonce
        value=dict(token=['live',{'nonce':'synthetic'}],phase='timeout',native_posted=True,native_ack=nonce,strategy42='fullscreen42')
        with mock.patch.object(self.m.xbmc,'executebuiltin',side_effect=AssertionError('repeat Stop')):self.observer.observe(value)
        self.assertIn('STOP_RETURNED_LATE',self.m.logs[-1]);self.assertIn('native_ack=1',self.m.logs[-1])
    def test_prepare_queue_timeout_and_native_timeout_are_different(self):
        self.m.request();self.m.timeout();self.observer.observe(self.m.jobs.state())
        self.assertIn('PREPARE_QUEUE_UNRETURNED',self.m.logs[-1]);self.assertNotIn('NATIVE_QUEUE_UNRETURNED',self.m.logs[-1])
    def test_never_exposes_session_payload_or_urls(self):
        value=dict(token=['live',{'nonce':'PRIVATE_NONCE','url':'https://private.invalid/token'}],phase='timeout',native_posted=True,strategy42='direct41')
        self.observer.observe(value);message=self.m.logs[-1]
        for secret in ('PRIVATE_NONCE','private.invalid','https://','token='):self.assertNotIn(secret,message)
    def test_media_exit_and_healthy_live_are_not_touched(self):
        for value in (None,dict(token=['vod',{}],phase='timeout'),dict(token=['live',{}],phase='complete')):self.observer.observe(value)
        self.assertFalse([s for s in self.m.logs if '[STOP58]' in s])
    def test_service_observes_timeout_before_suspending_player_queries(self):
        tree=ast.parse((ADDON/'service.py').read_text());run=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='run')
        calls=[n for n in ast.walk(run) if isinstance(n,ast.Call) and isinstance(n.func,ast.Name)]
        observe=next(n.lineno for n in calls if n.func.id=='observe_stop58');blocked=next(n.lineno for n in calls if n.func.id=='stop_blocked')
        self.assertLess(observe,blocked)


class ProviderImport58(unittest.TestCase):
    def setUp(self):
        import test_xcmate_epg_02952 as old
        self.m=old.EPG52(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
        self.m.portal.update(provider_epg_enabled=True,epg_url='https://provider.example.test/authorized.xml')
        self.m.config['sources']=self.m.config['sources'][:1]
        sys.modules['epg']._save_disk=mock.Mock();sys.modules['epg']._mem_set=mock.Mock()
        sys.modules['epg_status'].update=mock.Mock();sys.modules['epg_status'].source_key=lambda s:s['id']
        sys.modules['epg_sources']._channels_cache_key=lambda pid:'synthetic'
        self.seen=[]
    def refresh(self):
        import contextlib,io
        @contextlib.contextmanager
        def source(record,**kwargs):
            self.seen.append(record.get('uri'))
            title='Provider event' if record.get('uri')==self.m.portal['epg_url'] else 'External event'
            yield io.BytesIO(self.m.xml('a',[self.m.event(title=title)]))
        with mock.patch('epg_gate46.access',return_value='READY'),mock.patch.object(self.m.stream,'active_streams',return_value=iter([self.m.channel])),mock.patch.object(self.m.stream,'source_stream',source):
            return self.m.stream.refresh(self.m.portal,force=True)
    def test_enabled_provider_and_external_are_committed_to_existing_source_qualified_guide(self):
        self.assertTrue(self.refresh());self.assertEqual(len(self.seen),2)
        stats=importlib.import_module('epg_report53').statistics('p')
        self.assertEqual(next(r for r in stats['sources'] if r['id']=='provider')['programmes'],1)
        self.assertEqual(next(r for r in stats['sources'] if r['id']=='provider')['channels'],1)
        binding=importlib.import_module('epg_binding48');local=importlib.import_module('local_epg')
        provider=binding.preview({},'1','a','provider')
        self.assertEqual(local.now_next('p',[self.m.channel],provider,self.m.now)['1']['now'],'Provider event')
        from guide_publish44 import source_id
        external=binding.preview({},'1','a',source_id(self.m.config['sources'][0],1))
        self.assertEqual(local.now_next('p',[self.m.channel],external,self.m.now)['1']['now'],'External event')
    def test_disabled_provider_is_not_downloaded_and_existing_provider_rows_are_retained(self):
        self.refresh();self.seen.clear();self.m.portal['provider_epg_enabled']=False
        self.refresh();self.assertEqual(self.seen,[self.m.config['sources'][0]['uri']])
        self.assertEqual(next(r for r in importlib.import_module('epg_report53').statistics('p')['sources'] if r['id']=='provider')['programmes'],1)
