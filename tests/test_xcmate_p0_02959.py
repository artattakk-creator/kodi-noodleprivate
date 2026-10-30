"""#281: regular import despite wizard checkpoint; ACK then transient GUI barrier."""
import contextlib,importlib,io,json,sys,time,types,unittest
from unittest import mock
from pathlib import Path
from xcmate027_fixture import Fixture,ADDON,QueuedPool


class Provider59(unittest.TestCase):
 def setUp(self):
  import test_xcmate_epg_manager_02953 as old
  self.m=old.Manager53Tests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
  self.data=self.m.m;self.data.portal.update(provider_epg_enabled=True)
 def manager(self):
  module=importlib.import_module('epg_manager53')
  with mock.patch.object(module,'ThreadPoolExecutor',QueuedPool):
   w=module.Manager53('XCMateEPGManager53.xml',str(ADDON),'Default','720p');w.configure(self.data.portal)
  self.addCleanup(w.close);w.show();w._pool.drain();w.pump();return w
 def test_pending_setup_does_not_replace_explicit_regular_refresh(self):
  with mock.patch('wizard_epg54.pending',return_value=True):w=self.manager()
  self.assertTrue(w.getControl(411).enabled);self.assertEqual(w.getControl(402).label,'Jetzt aktualisieren')
  with mock.patch('epg.request_refresh',create=True,return_value=True) as request:w.onClick(402)
  request.assert_called_once_with('p',self.data.portal,force=True)
  self.assertFalse(w._closed);self.assertIsNone(w.next_action)
 def test_resume_remains_explicit_and_separate(self):
  with mock.patch('wizard_epg54.pending',return_value=True):w=self.manager()
  with mock.patch('epg.request_refresh',create=True) as request:w.onClick(411)
  self.assertTrue(w._closed);self.assertEqual(w.next_action,'resume_epg54');request.assert_not_called()
 def test_resume_button_disabled_without_pending_setup(self):
  with mock.patch('wizard_epg54.pending',return_value=False):w=self.manager()
  self.assertFalse(w.getControl(411).enabled)
 def test_progress_is_newer_than_old_success_not_overwritten_by_history(self):
  self.data.put('a',[self.data.event()],1)
  run=self.m.run_record();run['sources'][0]['finished']=time.time()-30;self.m.report.store('p',run)
  state={self.m.report.configured(self.m.portal)[1]['key']:dict(at=time.time(),code='PARSING',bytes=4096,programmes=17,count=9)}
  with mock.patch('epg_status.read',return_value=state):rows=self.m.report.overview(self.m.portal)
  row=rows[1];self.assertEqual(row['code'],'PARSING');self.assertEqual(row['progress59']['count'],9)
 def test_stage_messages_distinguish_source_network_xml_and_mapping(self):
  text=[self.m.report.meaning(code) for code in ('SOURCE_UNAVAILABLE','DOWNLOAD_FAILED','INVALID_XMLTV','EMPTY_GUIDE','NO_CHANNEL_MATCH')]
  self.assertEqual(len(set(text)),5)
  self.assertIn('Senderzuordnung',text[-1]);self.assertNotIn('Aktualisierung fehlgeschlagen',str(text))
 def test_no_matching_channels_is_not_empty_feed_or_invalid_xml(self):
  from epg_errors import EmptyGuideError,failure_details
  empty=EmptyGuideError('synthetic');mismatch=EmptyGuideError('synthetic');mismatch.xcmate_no_match59=True
  self.assertEqual(failure_details(empty,'MERGE')[0],'EMPTY_GUIDE')
  self.assertEqual(failure_details(mismatch,'MERGE')[0],'NO_CHANNEL_MATCH')
 def test_http_status_is_kept_without_exception_url_or_password(self):
  from epg_errors import failure_details
  error=OSError('https://private.invalid/password');error.code=403
  code,fields=failure_details(error,'DOWNLOAD')
  self.assertEqual(fields['http_status'],403);self.assertEqual(code,'DOWNLOAD_FAILED');self.assertNotIn('private.invalid',str(fields))


class Return59(unittest.TestCase):
 def setUp(self):
  import test_xcmate_live_exit_02941 as old
  self.m=old.LiveExit41(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
  self.s=self.m.m;self.jobs=self.m.jobs;self.xbmc=sys.modules['xbmc'];self.gui=sys.modules['xbmcgui']
 def stopped(self):
  self.assertTrue(self.s.exit.request(self.s.nav));self.s.ready();self.s.exit._poll(self.s.nav)
  value=self.jobs.state();value['not_before']=0;self.jobs.save(value);self.jobs.poll();self.jobs._thread.join(2)
  self.s.playing=False;self.m.ack()
  value=self.s.exit.state();value['deadline']=time.monotonic()-10;self.s.exit._save(value)
  self.s.exit._poll(self.s.nav);self.assertEqual(self.s.exit.state()['phase'],'home')
 def test_confirmed_stop_then_modal_after_original_deadline_resumes_once(self):
  self.stopped();native=list(self.s.native_builtins)
  with mock.patch.object(self.xbmc,'getCondVisibility',side_effect=lambda cond:cond=='System.HasActiveModalDialog'):
   for _ in range(20):self.s.exit._poll(self.s.nav)
  self.assertEqual(self.s.exit.state()['phase'],'home');self.assertFalse(self.s.builtins)
  for _ in range(10):self.s.exit._poll(self.s.nav)
  self.assertEqual(self.s.exit.state()['phase'],'complete');self.assertEqual(len(self.s.builtins),1);self.assertEqual(native,self.s.native_builtins)
 def test_foreign_dialog_id_blocks_even_when_modal_boolean_temporarily_false(self):
  self.stopped()
  with mock.patch.object(self.gui,'getCurrentWindowDialogId',return_value=10138):
   for _ in range(8):self.s.exit._poll(self.s.nav)
  self.assertEqual(self.s.exit.state()['phase'],'home');self.assertFalse(self.s.builtins)
  self.s.exit._poll(self.s.nav);self.assertEqual(self.s.exit.state()['phase'],'complete')
 def test_new_player_during_gui_wait_does_not_receive_old_return_or_stop(self):
  self.stopped();self.s.playing=True
  with mock.patch('playback_exit.identity',return_value=('media',dict(self.s.session,kind='vod',nonce='foreign'))):self.s.exit._poll(self.s.nav)
  self.assertEqual(self.s.exit.state()['phase'],'failed');self.assertFalse(self.s.builtins)
 def test_owner_lease_is_not_cleared_or_ignored(self):
  self.stopped();self.s.properties['XCMate.NavigationLease']='f'*32
  for _ in range(4):self.s.exit._poll(self.s.nav)
  self.assertEqual(self.s.properties['XCMate.NavigationLease'],'f'*32);self.assertFalse(self.s.builtins)
  self.s.properties.pop('XCMate.NavigationLease');self.s.exit._poll(self.s.nav)
  self.assertEqual(self.s.exit.state()['phase'],'complete')
 def test_confirmed_stop_invalidated_player_api_does_not_become_permanent_failure(self):
  self.stopped()
  with mock.patch.object(self.s.player,'isPlayingVideo',side_effect=RuntimeError('synthetic invalidated tag')):
   self.s.exit.poll(self.s.nav)
  self.assertEqual(self.s.exit.state()['phase'],'home')
  self.s.exit._poll(self.s.nav);self.assertEqual(self.s.exit.state()['phase'],'complete')
 def test_competing_home_commit_during_gui_probe_is_not_overwritten(self):
  self.stopped();lifecycle=importlib.import_module('window_lifecycle')
  def competing():
   value=self.s.exit.state();value['phase']='complete';self.s.exit._save(value)
   return dict(window=10025,dialog=10138,modal=True,updating=False)
  with mock.patch.object(lifecycle,'state',side_effect=competing):self.s.exit._poll(self.s.nav)
  self.assertEqual(self.s.exit.state()['phase'],'complete');self.assertFalse(self.s.builtins)
 def test_missing_actual_ack_remains_unconfirmed(self):
  self.stopped();value=self.s.exit.state();self.s.properties[self.m.native.ACK]='f'*32
  from live_return59 import stop_confirmed
  self.assertFalse(stop_confirmed(value,self.jobs.state()))


class RefreshQueue59(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp()
  import importlib.util
  spec=importlib.util.spec_from_file_location('real_epg59',ADDON/'resources/lib/epg.py')
  self.real=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.real)
 def test_busy_existing_worker_does_not_consume_a_new_explicit_refresh(self):
  request=dict(pid='p',nonce='1'*32,at=time.time(),force=True)
  self.properties['XtreamMate.EPGRefreshRequest']=json.dumps(request)
  with mock.patch.object(self.real,'warmup_async',side_effect=[False,True]) as warmup:
   self.real.poll_refresh_request();self.assertNotEqual(self.real._LAST_REFRESH_REQUEST,request['nonce'])
   self.real.poll_refresh_request();self.assertEqual(self.real._LAST_REFRESH_REQUEST,request['nonce'])
   self.real.poll_refresh_request();self.assertEqual(warmup.call_count,2)
 def test_regular_service_refresh_rereads_latest_saved_provider_activation(self):
  self.properties['XtreamMate.EPGRefreshRequest']=json.dumps(dict(pid='p',nonce='2'*32,at=time.time(),force=True))
  self.portal['provider_epg_enabled']=True
  with mock.patch.object(self.real,'warmup_async',return_value=True) as worker:self.real.poll_refresh_request()
  self.assertTrue(worker.call_args.args[1]['provider_epg_enabled'])


class Images59(Fixture,unittest.TestCase):
 def test_missing_event_and_missing_image_are_different(self):
  from programme_diagnostics59 import message
  self.assertIn('Keine Programmdaten',message({},dict(code='NO_IMAGE')))
  event=dict(title='Actual event',start=1,stop=2)
  self.assertIn('Sendungsdaten vorhanden',message(event,dict(code='NO_IMAGE')))
 def test_present_but_blocked_url_explains_safe_source_policy(self):
  from programme_diagnostics59 import message
  self.assertIn('nicht freigegeben',message(dict(title='Actual',start=1,stop=2),dict(code='BLOCKED_IMAGE_HOST_OR_URL')))
 def test_reference_ready_is_not_pixel_success(self):
  from programme_diagnostics59 import message
  text=message(dict(title='Actual',start=1,stop=2),dict(image='https://image.example.test/test.png',source='xmltv',code='READY'))
  self.assertIn('Darstellung durch Kodi',text);self.assertNotIn('PASS',text)


class HomeProbe59(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.probe=importlib.import_module('widget_home_probe59');self.probe._plans.clear();self.probe._observed.clear()
  self.xbmc=sys.modules['xbmc'];self.gui=sys.modules['xbmcgui'];self.xbmc.getSkinDir=lambda:'skin.titan.bingie.mod'
  self.gui.getCurrentWindowId=lambda:10000;self.gui.getCurrentWindowDialogId=lambda:9999
  self.probe._plans['p']=(time.monotonic(),dict(vod=dict(control_ids59=[510]),series=dict(control_ids59=[520])))
 def test_actual_home_samples_do_not_do_file_network_sql_or_player_work(self):
  self.xbmc.getInfoLabel=lambda key:'24';self.xbmc.getCondVisibility=lambda key:True
  with mock.patch('builtins.open',side_effect=AssertionError('GUI IO')),mock.patch('sqlite3.connect',side_effect=AssertionError('GUI SQL')),mock.patch.object(self.xbmc,'Player',side_effect=AssertionError('Player work')):self.probe.poll()
  self.assertEqual(self.probe._observed[('p','vod')]['code'],'NATIVE_HOME_ITEMS')
  self.assertEqual(self.probe._observed[('p','series')]['decode_verified'],-1)
 def test_empty_hidden_and_unobservable_are_distinct(self):
  self.xbmc.getInfoLabel=lambda key:'0';self.xbmc.getCondVisibility=lambda key:True;self.probe.poll()
  self.assertEqual(self.probe._observed[('p','vod')]['code'],'NATIVE_HOME_EMPTY')
  self.xbmc.getCondVisibility=lambda key:False;self.probe.poll();self.assertEqual(self.probe._observed[('p','vod')]['code'],'NATIVE_HOME_HIDDEN')
  self.xbmc.getInfoLabel=lambda key:'';self.probe.poll();self.assertEqual(self.probe._observed[('p','vod')]['code'],'NATIVE_HOME_UNVERIFIED')
 def test_foreign_dialog_is_not_measured_as_hidden_home(self):
  self.gui.getCurrentWindowDialogId=lambda:13001;self.probe.poll();self.assertFalse(self.probe._observed)
