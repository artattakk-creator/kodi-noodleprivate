"""Six independently bounded rows, real saved source semantics, no profile writes."""
import ast,copy,json,unittest
from pathlib import Path
from unittest import mock
from xml.etree import ElementTree as E
from xcmate050_fixture import Fixture50
from test_widget_clock50_consumer_91 import fixture
import test_widget_media_spinner as spinner_fixture

class SixRows(Fixture50,unittest.TestCase):
 def source_records(self):
  rows=[]
  for slot,action,label in (('', 'widget_live_start_group','Live-TV'),('.1','widget_recent_vod','Filme'),('.2','widget_recent_series','Serien')):
   for key,value in [('widgetName',label),('widgetPath','plugin://plugin.video.xtreammate/?action='+action+'&pid=p')]:rows.append(['mainmenu','own-home',key+slot,value])
  sources=[('movies','', 'Im Kino','plugin://plugin.video.themoviedb.helper/?info=now_playing&tmdb_type=movie&widget=true&reload=$INFO[Window(Home).Property(TMDbHelper.Widgets.Reload)]'),('shows','', 'Diese Woche im Trend','plugin://plugin.video.themoviedb.helper/?info=trending_week&tmdb_type=tv'),('shows','.1','Disney Plus','plugin://plugin.video.themoviedb.helper/?info=discover&tmdb_type=movie&with_id=True&with_watch_providers=337&watch_region=DE')]
  for identity,slot,label,uri in sources:
   rows.extend([['mainmenu',identity,'widgetName'+slot,label],['mainmenu',identity,'widgetPath'+slot,uri]])
  self.prop.write_text(repr(rows))
  self.menu.write_text('<shortcuts><shortcut><label>Audio</label><action>ActivateWindow(Music,plugin://plugin.audio.m3sr2019/,return)</action></shortcut></shortcuts>')
  return rows
 def plan(self):
  from widget_six_sources import discover
  self.source_records();return discover(self.profile,'p',lambda addon:True)
 def generated(self):
  tree=E.fromstring(fixture());tree.remove(tree[-1])
  for node in tree.findall('include'):
   action=node.find("param[@name='widgetName']").get('value')
   if action=='Live-TV':node.set('content','XCMate50.LiveRow')
   for key,value in [('up75',{'Live-TV':'900','Filme':'1510','Serien':'1520'}[action]),('down75',{'Live-TV':'1520','Filme':'1530','Serien':'1540'}[action]),('submenuid','own-menu'),('visibility','true')]:E.SubElement(node,'param',name=key,value=value)
  E.SubElement(tree,'include',content='foreign_preserved').text='Do not touch: user widget'
  return E.tostring(tree)
 def test_actual_source_contracts_discovered_without_editing_private_profile(self):
  from widget_six_sources import discover,public_summary,EXTRAS
  self.source_records();before={p.name:p.read_bytes() for p in self.native.iterdir()}
  plan=discover(self.profile,'p',lambda addon:True)
  self.assertEqual(plan['code'],'READY')
  self.assertEqual([v['title'] for v in plan['sources'].values()],['Im Kino','Disney','Diese Woche im Trend','MP3s'])
  for kind,_,_,target in EXTRAS:self.assertEqual((plan['sources'][kind]['code'],plan['sources'][kind]['target']),('WAITING',target))
  self.assertIn('trending_week',plan['sources']['trend']['uri']);self.assertNotIn('$INFO',plan['sources']['cinema']['uri'])
  self.assertEqual(plan['sources']['mp3']['uri'],'plugin://plugin.audio.m3sr2019/')
  self.assertEqual(before,{p.name:p.read_bytes() for p in self.native.iterdir()})
  self.assertNotIn('plugin://',json.dumps(public_summary(plan)))
 def test_xcmate_token_does_not_enable_a_separate_foreign_addon(self):
  from widget_six_sources import discover
  self.source_records();plan=discover(self.profile,'p',lambda addon:False)
  self.assertTrue(all(row['code']=='SOURCE_UNAVAILABLE' and not row['uri'] for row in plan['sources'].values()))
 def test_foreign_source_selection_is_ambiguous_instead_of_overwriting_a_choice(self):
  from widget_six_sources import discover
  rows=self.source_records();rows.append(['mainmenu','other','widgetPath','plugin://plugin.video.themoviedb.helper/?info=now_playing&tmdb_type=movie&region=FR']);self.prop.write_text(repr(rows))
  result=discover(self.profile,'p',lambda addon:True)['sources']['cinema']
  self.assertEqual(result['code'],'SOURCE_AMBIGUOUS');self.assertFalse(result['uri'])
 def test_audio_is_browse_only_and_never_runs_mutating_or_autoplay_routes(self):
  from widget_six_sources import uri
  for path in ('musicmp3/clear_cache','musicmp3/play','musicmp3/play_album','fav/remove','shuffle','search_songs'):
   with self.subTest(path=path),self.assertRaises(ValueError):uri('plugin://plugin.audio.m3sr2019/'+path,'mp3')
  self.assertTrue(uri('plugin://plugin.audio.m3sr2019/favourites/song','mp3'))
 def test_source_allowlist_rejects_wrong_lists_tokens_and_executable_macros(self):
  from widget_six_sources import uri
  for value,kind in [('plugin://plugin.video.themoviedb.helper/?info=top_rated&tmdb_type=movie','cinema'),('plugin://plugin.video.themoviedb.helper/?info=trending_week&tmdb_type=movie','trend'),('plugin://plugin.video.themoviedb.helper/?info=discover&tmdb_type=movie&with_watch_providers=999&watch_region=DE','disney'),('plugin://foreign.addon/?info=now_playing','cinema'),('plugin://plugin.video.themoviedb.helper/?info=now_playing&tmdb_type=movie&token=PRIVATE','cinema'),('plugin://plugin.video.themoviedb.helper/?info=now_playing&tmdb_type=movie&reload=$INFO[System.Exec(foo)]','cinema')]:
   with self.subTest(value=value),self.assertRaises(ValueError):uri(value,kind)
 def test_missing_and_multiple_own_home_groups_fail_closed(self):
  from widget_six_sources import discover
  self.source_records();self.assertEqual(discover(self.profile,'different')['code'],'OWN_HOME_MISSING')
  rows=ast.literal_eval(self.prop.read_text());rows.extend([[r[0],'second',r[2],r[3]] for r in rows if r[1]=='own-home']);self.prop.write_text(repr(rows))
  self.assertEqual(discover(self.profile,'p')['code'],'OWN_HOME_AMBIGUOUS')
 def test_generated_cache_insertion_has_exact_order_and_does_not_mutate_saved_sources(self):
  from widget_reload78 import candidate
  from widget_six_consumer import runtime_binding
  before=self.generated();saved=self.prop.read_bytes();changed=candidate(before,True,True);root=E.fromstring(changed)
  visible=[n for n in root.findall('include') if n.get('content') in ('XCMate80.MediaRow','XCMate.SixRows.Row')]
  self.assertEqual([n.find("param[@name='widgetName']").get('value') for n in visible],['Filme','Serien','Im Kino','Disney','Diese Woche im Trend','MP3s'])
  self.assertEqual(candidate(changed,True,True),changed)
  self.assertEqual(runtime_binding(changed),dict(pid='',live=1510,vod=1520,series=1530,tail=1540))
  self.assertEqual(root.find("include[@content='foreign_preserved']").text,'Do not touch: user widget')
  self.assertEqual(self.prop.read_bytes(),saved)
  for n in visible[-4:]:self.assertEqual(n.find("param[@name='widgetTarget']").get('value'),'music' if n.find("param[@name='xcmateKind']").get('value')=='mp3' else 'videos')
 def test_extra_calls_are_opt_in_to_the_confirmed_skin_contract(self):
  from widget_reload78 import candidate
  self.assertNotIn(b'XCMate.SixRows.Row',candidate(self.generated(),True))
 def test_existing_control_collision_and_unreviewed_extra_edit_block_atomically(self):
  from widget_reload78 import candidate
  data=self.generated().replace(b'</includes>',b'<include><param name="widgetid" value="29761" /></include></includes>')
  with self.assertRaisesRegex(ValueError,'COLLISION'):candidate(data,True,True)
  changed=candidate(self.generated(),True,True)
  with self.assertRaises(ValueError):candidate(changed.replace(b'value="Im Kino"',b'value="Injected"'),True,True)
 def test_each_row_has_a_bounded_actual_load_and_no_parallel_source_starts(self):
  from widget_six_runtime import step
  sources=self.plan()['sources'];rows={};observed={kind:(0,False) for kind in sources}
  rows=step(rows,sources,observed,100,False);self.assertTrue(all(r['state']=='WAITING' for r in rows.values()))
  rows=step(rows,sources,observed,101,True);self.assertEqual([k for k,r in rows.items() if r['state']=='LOADING'],['cinema'])
  observed['cinema']=(0,True);rows=step(rows,sources,observed,120,True)
  self.assertEqual(rows['disney']['state'],'WAITING')
  observed['cinema']=(24,False);rows=step(rows,sources,observed,121,True)
  self.assertEqual(rows['cinema']['state'],'READY');self.assertEqual(rows['disney']['state'],'LOADING')
  self.assertEqual(rows['cinema']['path'],sources['cinema']['uri'])
 def test_empty_failed_and_timeout_sources_stop_spinner_without_claiming_success(self):
  from widget_six_runtime import step
  sources=self.plan()['sources'];observed={k:(0,False) for k in sources};rows=step({},sources,observed,100,True)
  observed['cinema']=(0,True);rows=step(rows,sources,observed,101,True)
  observed['cinema']=(0,False);rows=step(rows,sources,observed,102,True)
  self.assertEqual(rows['cinema']['state'],'EMPTY_OR_ERROR');self.assertEqual(rows['disney']['state'],'LOADING')
  observed['disney']=(0,True);rows=step(rows,sources,observed,163,True)
  self.assertEqual(rows['disney']['state'],'TIMEOUT');self.assertEqual(rows['trend']['state'],'WAITING')
  observed['disney']=(0,False);rows=step(rows,sources,observed,164,True)
  self.assertEqual(rows['trend']['state'],'LOADING')
 def test_unchanged_inventory_does_not_reset_last_good_items_or_restart_a_source(self):
  from widget_six_runtime import step
  sources=self.plan()['sources'];observed={k:(24,False) for k in sources};rows={}
  for now in range(100,110):
   current={k:(v[0],False,'result-'+k if k in rows and rows[k]['state'] in ('LOADING','READY') else 'prior-'+k) for k,v in observed.items()}
   rows=step(rows,sources,current,now,True)
  self.assertTrue(all(r['state']=='READY' for r in rows.values()))
  self.assertEqual(step(rows,copy.deepcopy(sources),observed,99999,True),rows)
 def test_source_unavailability_is_not_a_busy_or_ready_status(self):
  from widget_six_sources import discover
  from widget_six_runtime import step
  self.source_records();sources=discover(self.profile,'p',lambda addon:False)['sources'];rows=step({},sources,{},100,True)
  self.assertTrue(all(r['state']=='SOURCE_UNAVAILABLE' and not r['path'] for r in rows.values()))
 def test_all_six_headers_share_the_verified_native_animation_and_have_no_item_count_gate(self):
  instance=spinner_fixture.MediaSpinner();instance.setUp()
  try:
   files=instance.graph();root=E.fromstring(files['xml/IncludesHomeWidgets.xml'])
   for title in ('XCMate80.MediaRow','XCMate.SixRows.Row'):
    row=root.find("include[@name='%s']"%title);heading=row.find("control/control[@type='grouplist']")
    self.assertIsNone(heading.find('visible'));self.assertEqual(heading.findtext('itemgap'),'12')
    spinners=heading.findall("control[@type='multiimage']");self.assertEqual(len(spinners),6)
    for kind,n in zip(('vod','series','cinema','disney','trend','mp3'),spinners):
     self.assertIn(kind+'.Busy),true)',n.findtext('visible'));self.assertEqual(n.findtext('timeperimage'),'85')
     self.assertIn('$PARAM[xcmateKind].Kind)',n.findtext('visible'));self.assertNotIn('String.IsEqual("$PARAM',n.findtext('visible'))
     self.assertEqual(n.findtext('width'),'24')
   self.assertIn('XCMate.SixRows.Contract',files['xml/IncludesVariables.xml'].decode())
   import widget_six_skin
   self.assertEqual(widget_six_skin.upgrade(files),files)
   bad=dict(files);bad['xml/IncludesHomeWidgets.xml']=bad['xml/IncludesHomeWidgets.xml'].replace(b'name="XCMate.SixRows.Cards"><left>130',b'name="XCMate.SixRows.Cards"><left>131')
   with self.assertRaises(ValueError):widget_six_skin.upgrade(bad)
  finally:
   instance.tearDown();instance.doCleanups()

 def test_native_last_good_items_are_not_mistaken_for_a_new_directory_ack(self):
  from widget_six_runtime import step
  sources=self.plan()['sources'];observed={k:(24,False,'OLD') for k in sources}
  rows=step({},sources,observed,100,True)
  rows=step(rows,sources,observed,101,True)
  self.assertEqual(rows['cinema']['state'],'LOADING')
  observed['cinema']=(24,False,'NEW')
  rows=step(rows,sources,observed,102,True)
  self.assertEqual(rows['cinema']['state'],'READY')
 def test_temporary_addon_failure_retains_an_already_loaded_path(self):
  from widget_six_runtime import step
  sources=self.plan()['sources'];observed={k:(0,False) for k in sources}
  rows=step({},sources,observed,100,True)
  observed['cinema']=(24,False);rows=step(rows,sources,observed,101,True)
  saved=rows['cinema']['path'];sources['cinema']['code']='SOURCE_UNAVAILABLE';sources['cinema']['uri']=''
  rows=step(rows,sources,observed,102,True)
  self.assertEqual(rows['cinema']['state'],'SOURCE_UNAVAILABLE');self.assertEqual(rows['cinema']['path'],saved)

 def test_real_tmdb_helper_refresh_macro_is_observed_without_pulsing_global_hooks(self):
  from widget_six_sources import discover
  self.source_records();before=self.prop.read_bytes()
  first=discover(self.profile,'p',lambda addon:True,lambda name:'refresh-1')
  second=discover(self.profile,'p',lambda addon:True,lambda name:'refresh-2')
  self.assertIn('reload=refresh-1',first['sources']['cinema']['uri'])
  self.assertNotEqual(first['sources']['cinema']['source_hash'],second['sources']['cinema']['source_hash'])
  self.assertEqual(before,self.prop.read_bytes())

 def test_waiting_empty_headers_do_not_push_the_last_populated_row_offscreen(self):
  instance=spinner_fixture.MediaSpinner();instance.setUp()
  try:
   root=E.fromstring(instance.graph()['xml/IncludesHomeWidgets.xml'])
   row=root.find("include[@name='XCMate.SixRows.Row']")
   body,compact=row.findall('control')
   self.assertEqual((body.findtext('height'),compact.findtext('height')),('244','26'))
   self.assertIn('.Expanded),true)',body.findtext('visible'))
   self.assertIn('!String.IsEqual',compact.findtext('visible'))
   self.assertIsNotNone(compact.find("control[@type='grouplist']/control[@type='label']"))
   # The visible body is admitted by explicit state, not by NumItems which
   # would prevent a cold native directory from ever being consumed.
   self.assertNotIn('NumItems',body.findtext('visible'))
  finally:
   instance.tearDown();instance.doCleanups()

 def test_all_generated_control_info_ids_fit_kodis_24_bit_data_field(self):
  from widget_six_sources import EXTRAS
  for _,_,cid,_ in EXTRAS:
   for prefix in ('75','76','84','85','86','87','88','89','90','94','95','96','97','98','99','100'):
    self.assertLess(int(prefix+str(cid)),1<<24)

 def test_legacy_pidless_sources_use_the_existing_active_portal_preference(self):
  from widget_six_runtime import selected_portal
  from home_menu import active_portal
  portals=[dict(id='first',enabled=True),dict(id='preferred',enabled=True),dict(id='disabled',enabled=False)]
  self.options['active_portal_id']='preferred'
  self.assertEqual(selected_portal(portals,''),active_portal(portals))
  self.assertEqual(selected_portal(portals,'first'),portals[0])
  self.assertIsNone(selected_portal(portals,'disabled'))
  self.assertIsNone(selected_portal(portals,'missing'))
 def test_gui_poll_reads_ram_and_native_labels_without_files_database_network_or_threads(self):
  import widget_six_runtime as runtime,epg_handoff63,sys
  sources=self.plan()['sources'];xbmc=sys.modules['xbmc'];gui=sys.modules['xbmcgui']
  plan=dict(binding=dict(series=1530,tail=1540),scope=('fixture','p'),profile_scope=epg_handoff63.profile_scope(),sources=sources)
  def label(value):return 'READY' if value=='$VAR[XCMate.SixRows.Contract]' else '0' if value.endswith('.NumItems') else ''
  with mock.patch.object(runtime,'_plan',plan),mock.patch.object(runtime,'_rows',{}),mock.patch.object(runtime,'_scope',None),mock.patch.object(xbmc,'getInfoLabel',side_effect=label),mock.patch.object(xbmc,'getCondVisibility',return_value=False),mock.patch.object(gui,'getCurrentWindowId',return_value=10000),mock.patch.object(gui,'getCurrentWindowDialogId',return_value=9999),mock.patch('home_schedule75.rest_allowed',return_value=True),mock.patch.object(Path,'stat',side_effect=AssertionError('GUI_DISK_IO')),mock.patch('builtins.open',side_effect=AssertionError('GUI_FILE_IO')),mock.patch('sqlite3.connect',side_effect=AssertionError('GUI_SQLITE_IO')),mock.patch('socket.getaddrinfo',side_effect=AssertionError('GUI_DNS')),mock.patch('threading.Thread',side_effect=AssertionError('GUI_THREAD')):
   runtime.poll()
  self.assertEqual(self.properties.get('XCMate.SixRows.cinema.Kind'),'cinema')
  self.assertEqual(self.properties.get('XCMate.SixRows.cinema.Busy'),'true')
  self.assertEqual(self.properties.get('XCMate.SixRows.disney.Busy',''),'')
  self.assertEqual(self.properties.get('XCMate.SixRows.cinema.Expanded'),'true')
  self.assertEqual(self.properties.get('XCMate.SixRows.disney.Expanded',''),'')
 def test_retired_profile_plan_cannot_publish_or_start_a_foreign_source(self):
  import widget_six_runtime as runtime
  saved=dict(self.properties)
  with mock.patch.object(runtime,'_plan',dict(profile_scope='another-profile')),mock.patch('epg_handoff63.profile_scope',return_value='current-profile'):
   runtime.poll()
  self.assertEqual(self.properties,saved)

 def test_core_spinner_deadline_expires_without_a_running_data_worker(self):
  import home_loading85 as loading
  with mock.patch.object(loading,'visible',return_value=[]),mock.patch.object(loading.time,'monotonic',return_value=100):
   loading.update(self.portal,'vod',[],'WAITING',pending=True)
  self.assertEqual(self.properties.get('XCMate.Home85.vod.Busy'),'true')
  with mock.patch.object(loading.time,'monotonic',return_value=161),mock.patch('builtins.open',side_effect=AssertionError('GUI_IO')),mock.patch('sqlite3.connect',side_effect=AssertionError('GUI_DB')):
   loading.expire()
  self.assertEqual(self.properties.get('XCMate.Home85.vod.Busy'),'')
  self.assertEqual(self.properties.get('XCMate.Home85.vod.State'),'ERROR_RETRYABLE')
 def test_expiry_of_an_old_frame_does_not_cancel_a_new_generation(self):
  import home_loading85 as loading
  with mock.patch.object(loading,'visible',return_value=[]),mock.patch.object(loading.time,'monotonic',return_value=100):
   loading.update(self.portal,'vod',[],'WAITING',pending=True)
  with mock.patch.object(loading,'visible',side_effect=lambda portal,kind,rows:rows),mock.patch.object(loading.time,'monotonic',return_value=150):
   loading.update(self.portal,'vod',[dict(sid='new',name='New generation')],'READY',pending=True)
  with mock.patch.object(loading.time,'monotonic',return_value=161):loading.expire()
  self.assertEqual(self.properties.get('XCMate.Home85.vod.Busy'),'true')
 def test_missing_deadline_after_service_restart_cannot_leave_a_forever_spinner(self):
  import home_loading85 as loading
  self.properties.update({'XCMate.Home85.series.Busy':'true','XCMate.Home85.series.State':'LOADING_ART'})
  loading.expire()
  self.assertEqual(self.properties.get('XCMate.Home85.series.Busy'),'')
  self.assertEqual(self.properties.get('XCMate.Home85.series.State'),'ERROR_RETRYABLE')
