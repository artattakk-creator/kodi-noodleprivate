"""Native media release/ACK, stop races and progress preservation."""
import importlib,json,time,unittest
from unittest import mock
import test_xcmate_exit_040 as legacy

class MediaStop77(unittest.TestCase):
 def setUp(self):
  self.m=legacy.ExitTests(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
  import sys
  sys.modules.pop('exit_jobs',None)
  self.jobs=importlib.import_module('exit_jobs');self.native=importlib.import_module('native_stop41');self.media=importlib.import_module('media_stop77')
  self.commands=[]
  self.builtin=mock.patch('xbmc.executebuiltin',side_effect=lambda command,**kw:self.commands.append(command));self.builtin.start();self.addCleanup(self.builtin.stop)
 def tick(self):
  value=self.jobs.state()
  if value and value['phase']=='pending':value['not_before']=0;self.jobs.save(value)
  self.jobs.poll()
  if self.jobs._thread:self.jobs._thread.join(1)
 def post(self):
  self.assertTrue(self.jobs.request(self.m.player,reason='USER_BACK'));self.tick();self.assertTrue(self.jobs.state()['checkpoint77']);self.tick()
 def ack(self):
  value=self.jobs.state();self.m.playing=False;self.m.properties[self.native.ACK]=value['native_ack'];self.jobs.poll()
 def test_twenty_vod_and_episode_stops_checkpoint_then_exactly_one_native_ack(self):
  for kind in ('vod','episode'):
   for index in range(20):
    self.commands.clear();self.m.playing=True;self.m.session.update(kind=kind,nonce=kind+str(index),series_id='series',season='1',episode='1');self.m.media_id=self.m.session['nonce'];self.m.properties[self.m.progress.PROPERTY]=json.dumps(self.m.session)
    self.post();self.assertEqual(self.commands.count('PlayerControl(Stop)'),1)
    self.assertFalse(self.m.stops);self.assertNotEqual(self.jobs.state()['phase'],'complete');self.ack();self.assertEqual(self.jobs.state()['phase'],'complete')
    self.assertEqual(self.m.state.progress('p',kind,'1','series','1')['position'],743)
 def test_android_fullscreen_is_released_and_acknowledged_before_stop(self):
  window=[12005];visible=[True]
  with mock.patch('xbmcgui.getCurrentWindowId',side_effect=lambda:window[0]),mock.patch('xbmc.getCondVisibility',side_effect=lambda expr:expr=='System.Platform.Android' or expr=='Window.IsVisible(fullscreenvideo)' and visible[0]):
   self.jobs.request(self.m.player,reason='USER_BACK');self.tick();self.tick();self.assertEqual(self.commands[0],'ActivateWindow(Videos)');self.assertNotIn('PlayerControl(Stop)',self.commands)
   value=self.jobs.state();window[0]=10025;visible[0]=False;self.tick();self.assertNotIn('PlayerControl(Stop)',self.commands)
   self.m.properties[self.media.ACK]=value['prepare_ack77'];self.tick();self.assertEqual(self.commands.count('PlayerControl(Stop)'),1)
 def test_timeout_never_reposts_or_queries_player_and_late_ack_is_honest(self):
  self.post();value=self.jobs.state();value['deadline']=0;self.jobs.save(value)
  with mock.patch('xbmc.Player',side_effect=AssertionError('PLAYER_MUTEX')):
   self.jobs.poll();self.assertTrue(self.jobs.blocked());self.assertFalse(self.jobs.request(expected=tuple(value['token'])));self.jobs.poll()
  self.assertEqual(self.commands.count('PlayerControl(Stop)'),1);self.assertEqual(self.jobs.state()['phase'],'timeout')
  self.ack();self.assertTrue(self.jobs.state()['worker_done']);self.assertEqual(self.jobs.state()['result'],'complete');self.assertEqual(self.jobs.state()['phase'],'timeout')
 def test_foreign_replacement_after_checkpoint_is_not_stopped(self):
  self.jobs.request(self.m.player);self.tick();self.m.media_id='foreign';self.tick();self.assertNotIn('PlayerControl(Stop)',self.commands);self.assertEqual(self.jobs.state()['phase'],'failed')
 def test_checkpoint_error_still_stops_and_queues_bounded_retry_after_ack(self):
  import sqlite3
  with mock.patch.object(self.m.state,'save_progress',side_effect=sqlite3.OperationalError('locked')):
   self.post();self.ack()
  self.assertEqual(self.commands.count('PlayerControl(Stop)'),1)
 def test_timeout_blocks_media_osd_and_progress_before_any_player_query(self):
  self.post();value=self.jobs.state();value['deadline']=0;self.jobs.save(value);self.jobs.poll()
  with mock.patch('xbmc.Player',side_effect=AssertionError('PLAYER_MUTEX')):
   importlib.import_module('media_progress').poll()
   with mock.patch('xbmcgui.WindowDialog',object,create=True):importlib.import_module('media_osd').poll()
 def test_explicit_exit_callback_does_not_query_native_player_or_start_next(self):
  self.post();autoplay=importlib.import_module('media_autoplay');events=autoplay.Events();events.active=dict(self.m.session,autoplay_chain='own')
  player=mock.Mock();player.isPlayingVideo.side_effect=AssertionError('CALLBACK_PLAYER_MUTEX')
  events.terminal('stopped',player);self.assertEqual(events.drain()[0][0],'stopped')
 def test_wrong_session_ack_and_duplicate_back_never_complete_or_double_stop(self):
  self.post();self.assertTrue(self.jobs.request(expected=tuple(self.jobs.state()['token'])));self.m.properties[self.native.ACK]='a'*32;self.jobs.poll();self.assertEqual(self.jobs.state()['phase'],'running');self.assertEqual(self.commands.count('PlayerControl(Stop)'),1)

 def test_foreign_modal_appearing_after_prepare_blocks_native_post(self):
  self.jobs.request(self.m.player);self.tick();value=self.jobs.state();value.update(media_native77=True,checkpoint77=True,prepare_ready77=True)
  with mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=13003):
   self.assertFalse(self.media.can_post(value,tuple(value['token'])))
  self.assertNotIn('PlayerControl(Stop)',self.commands)

if __name__=='__main__':unittest.main()
