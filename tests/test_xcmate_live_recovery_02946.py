"""#241: native timeout remains failure; confirmed late return recovers once."""
import importlib,json,sys,types,unittest
from unittest import mock
import test_xcmate_live_stop_02917 as old


class LateReturn46(unittest.TestCase):
 def setUp(self):
  self.m=old.StopTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
  self.jobs=importlib.import_module('exit_jobs');self.native=importlib.import_module('native_stop41')
  self.recovery=importlib.import_module('live_recovery46')
  sys.modules['xbmc'].Monitor=lambda:types.SimpleNamespace(abortRequested=lambda:False)
 def timeout(self,ack=False):
  self.assertTrue(self.m.exit.request(self.m.nav));self.m.ready();self.m.exit._poll(self.m.nav)
  v=self.jobs.state();v['not_before']=0;self.jobs.save(v);self.jobs.poll();self.jobs._thread.join(2)
  v=self.jobs.state();v['deadline']=0;self.jobs.save(v);self.jobs.poll()
  self.m.exit._poll(self.m.nav);self.assertTrue(self.jobs.blocked())
  if ack:
   self.m.playing=False;self.m.properties[self.native.ACK]=v['native_ack'];self.jobs.poll()
   self.m.exit._poll(self.m.nav);self.assertEqual(self.m.exit.state()['phase'],'failed')
 def tick(self,n=4):
  for _ in range(n):self.m.exit._poll(self.m.nav)
 def test_confirmed_late_queue_return_recovers_home_once_without_second_stop(self):
  self.timeout(True);before=list(self.m.native_builtins);self.tick(20)
  self.assertEqual(self.jobs.state()['phase'],'timeout');self.assertTrue(self.jobs.state()['worker_done'])
  self.assertEqual(self.m.exit.state()['phase'],'complete');self.assertEqual(self.m.exit.state()['recovery46'],'LATE_ACK_VERIFIED')
  self.assertEqual(self.m.native_builtins,before);self.assertEqual(len(self.m.builtins),1)
 def test_no_barrier_no_player_mutex_query_stop_retry_or_gui_action(self):
  self.timeout()
  self.m.player.isPlayingVideo=mock.Mock(side_effect=AssertionError('native player mutex'))
  self.m.player.isPlaying=self.m.player.isPlayingVideo
  self.tick(20);self.assertTrue(self.jobs.blocked());self.assertFalse(self.m.builtins)
  self.assertEqual(len(self.m.native_builtins),2)
 def test_foreign_modal_defers_recovery_and_is_never_closed(self):
  self.timeout(True)
  with mock.patch.object(sys.modules['xbmcgui'],'getCurrentWindowDialogId',return_value=10138):self.tick(10)
  self.assertEqual(self.m.exit.state()['phase'],'failed');self.assertFalse(self.m.builtins)
  self.tick();self.assertEqual(self.m.exit.state()['phase'],'complete')
 def test_new_live_announcement_is_not_erased_or_navigated(self):
  self.timeout(True);new=dict(self.m.session,nonce='new',sid='2')
  self.m.properties[self.m.exit.SESSION]=json.dumps(new);self.tick()
  self.assertEqual(json.loads(self.m.properties[self.m.exit.SESSION]),new);self.assertFalse(self.m.builtins)
 def test_foreign_media_after_native_return_never_receives_stop_or_home(self):
  self.timeout(True);self.m.playing=True;self.m.tag='foreign';self.tick(10)
  self.assertFalse(self.m.builtins);self.assertEqual(len(self.m.native_builtins),2)
 def test_ack_tamper_cannot_recover_stale_worker_done(self):
  self.timeout(True);self.m.properties[self.native.ACK]='f'*32;self.tick(10)
  self.assertEqual(self.m.exit.state()['phase'],'failed');self.assertFalse(self.m.builtins)
 def test_media_or_other_session_job_cannot_release_live_tombstone(self):
  self.timeout(True);v=self.jobs.state();v['token'][0]='media'
  self.assertFalse(self.recovery.resume(self.m.exit.state(),v));v['token'][0]='live';v['token'][1]['nonce']='other'
  self.assertFalse(self.recovery.resume(self.m.exit.state(),v));self.assertFalse(self.m.builtins)
 def test_shutdown_and_unrelated_window_hold_late_recovery(self):
  self.timeout(True)
  with mock.patch.object(sys.modules['xbmc'],'Monitor',return_value=types.SimpleNamespace(abortRequested=lambda:True)):self.tick()
  with mock.patch.object(sys.modules['xbmcgui'],'getCurrentWindowId',return_value=10100):self.tick()
  self.assertFalse(self.m.builtins);self.assertEqual(self.m.exit.state()['phase'],'failed')
 def test_navigation_lease_holds_recovery_until_actual_owner_release(self):
  self.timeout(True);self.m.properties['XCMate.NavigationLease']='a'*32
  self.tick(10);self.assertFalse(self.m.builtins)
  self.m.properties.pop('XCMate.NavigationLease');self.tick();self.assertEqual(self.m.exit.state()['phase'],'complete')
