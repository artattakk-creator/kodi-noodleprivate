"""Real mapping files and bounded worker intents, synthetic identities only."""
import importlib,json,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture

class Manual87(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.q=importlib.import_module('work_requests86');self.m=importlib.import_module('programme_mapping85')
  self.event=dict(pid='p',sid='1',title='Charmed',canonical='xml',start=self.now,stop=self.now+3600)
  self.candidate=dict(id=1980,source='tmdb',title='Charmed',year=1998,country=['US'],verified85=True,media_type86='tv',role='backdrop',url='https://image.tmdb.org/t/p/w1280/charmed.png',poster='https://image.tmdb.org/t/p/w500/charmed.png')
 def test_source_and_epg_are_revalidated_after_slow_verification_before_commit(self):
  error=__import__('media_sources43').SourceError('EPG_REVISION_CHANGED')
  with mock.patch.object(self.q,'authoritative',side_effect=[self.event,error]),mock.patch('work_search86.details',return_value=self.candidate),mock.patch.object(self.m,'set_mapping') as write:
   with self.assertRaisesRegex(Exception,'EPG_REVISION_CHANGED'):self.q.save(self.event,dict(candidate=self.candidate),self.q.binding(self.event))
  write.assert_not_called();self.assertFalse(self.m.path().exists())
 def test_tv_tmdb_tvmaze_and_movie_save_have_cold_readback_and_no_repeat_lookup(self):
  for source,kind in (('tmdb','tv'),('tvmaze','tv'),('tmdb','movie')):
   selected=dict(self.candidate,source=source,media_type86=kind)
   if source=='tvmaze':selected.update(url='https://static.tvmaze.com/uploads/images/original_untouched/a.png',poster='https://static.tvmaze.com/uploads/images/original_untouched/p.png')
   with mock.patch.object(self.q,'authoritative',return_value=self.event),mock.patch('work_search86.details',return_value=selected):
    nonce=self.q.request(self.event,'save',candidate=selected);self.q.drain()
   self.assertEqual(self.q.result(nonce)['code'],'SAVED');self.m.publish(self.m.read())
   self.assertTrue(self.m.reload());record=self.m.read()['records'][self.m.namespace(self.event)]
   self.assertEqual((record['source'],record['id'],record['media_type86'],record['work87']['role']),(source,1980,kind,'backdrop'))
   self.options.update(programme_tmdb46=True,tmdb_research43=True,programme_tvmaze67=True)
   with mock.patch('work_search86.details',side_effect=AssertionError('saved verified work must not need another network lookup')),mock.patch('programme_candidates85.details',side_effect=AssertionError('no repeat TV lookup')):
    value=__import__('programme_candidates85').candidate(self.event)
   self.assertEqual(value['match'],'MANUAL_CONFIRMED');self.assertEqual(value['role81'],'backdrop')
   self.q.cancel(nonce)
 def test_cancel_immediately_before_replace_preserves_prior_file_and_cleans_only_own_temp(self):
  self.m.set_mapping(self.event,self.candidate);before=self.m.path().read_bytes()
  with self.assertRaisesRegex(Exception,'CANCELLED'):
   self.m.set_mapping(self.event,dict(self.candidate,id=2018,year=2018),cancel=mock.Mock(side_effect=[False,True]))
  self.assertEqual(self.m.path().read_bytes(),before);self.assertFalse(list(self.folder.glob('.manual85-*')))
 def test_real_storage_failure_is_not_user_cancel_and_preserves_mapping(self):
  self.m.set_mapping(self.event,self.candidate);before=self.m.path().read_bytes()
  with mock.patch.object(self.q,'authoritative',return_value=self.event),mock.patch('work_search86.details',return_value=self.candidate),mock.patch('import_budget.check_space',side_effect=OSError('private storage detail')):
   nonce=self.q.request(self.event,'save',candidate=self.candidate);self.q.drain()
  self.assertEqual(self.q.result(nonce)['code'],'PERSISTENCE_BLOCKED');self.assertEqual(self.m.path().read_bytes(),before)
  self.assertNotIn('private storage detail',json.dumps(self.q.result(nonce)))
 def test_saved_receipt_wins_over_cancellation_after_commit(self):
  def committed(*args,**kwargs):
   self.q.cancel(nonce);return True
  nonce=self.q.request(self.event,'save',candidate=self.candidate)
  with mock.patch.object(self.q,'save',side_effect=committed):self.q.drain()
  self.assertEqual(self.q.result(nonce)['code'],'SAVED')
 def test_operation_trace_records_actual_save_milestones_without_titles_urls_or_token(self):
  with mock.patch.object(self.q,'authoritative',return_value=self.event),mock.patch('work_search86.details',return_value=self.candidate):
   nonce=self.q.request(self.event,'save',candidate=self.candidate);self.q.drain()
  trace=json.loads(self.properties['XCMate.Work87.Trace'])
  self.assertEqual(list(trace['stages']),['ENQUEUED','PICKED','CANDIDATE_SELECTED','SOURCE_REVERIFIED','EPG_SCOPE_REVALIDATED','WRITE_COMMITTED','WRITE_READBACK','DELIVERED'])
  self.assertNotIn('Charmed',json.dumps(trace));self.assertNotIn('https',json.dumps(trace));self.assertNotIn(nonce,json.dumps(trace))
 def wait(self,cancel=False,abort=False,picked=False,worker='WORKER_BUSY',answer=None):
  monitor=types.SimpleNamespace(abortRequested=lambda:abort,waitForAbort=lambda n:False)
  progress=types.SimpleNamespace(create=mock.Mock(),close=mock.Mock(),iscanceled=lambda:cancel)
  # Force a deadline without spending thirty seconds in each host test.
  with mock.patch('xbmc.Monitor',return_value=monitor),mock.patch('xbmcgui.DialogProgress',create=True,return_value=progress),mock.patch('work_manager86.time',types.SimpleNamespace(monotonic=mock.Mock(side_effect=[0,31]))),mock.patch('work_requests86.result',return_value=answer),mock.patch('work_trace87.picked',return_value=picked),mock.patch('work_trace87.worker',return_value=worker):
   result=__import__('work_manager86').wait(self.event,'save',candidate=self.candidate)
  return result,progress
 def test_thirty_second_timeout_busy_worker_stopped_and_explicit_cancel_are_distinct(self):
  for kwargs,expected in [(dict(cancel=True),'USER_CANCELLED'),(dict(abort=True),'KODI_STOPPED'),(dict(picked=True),'REQUEST_TIMEOUT'),(dict(worker='WORKER_BUSY'),'WORKER_BUSY'),(dict(worker='WORKER_STOPPED'),'WORKER_STOPPED')]:
   value,dialog=self.wait(**kwargs);self.assertEqual(value['code'],expected);dialog.close.assert_called_once()
 def test_save_dialog_has_save_text_and_consumes_verified_result_before_cancel(self):
  value,dialog=self.wait(cancel=True,answer=dict(code='SAVED'))
  self.assertEqual(value['code'],'SAVED');self.assertIn('speicher',dialog.create.call_args.args[1].lower())
 def test_priority_worker_drains_confirmed_manual_intent_before_any_live_warmup(self):
  module=__import__('programme_requests68');events=[]
  monitor=types.SimpleNamespace(abortRequested=lambda:False,waitForAbort=lambda n:True)
  def manual(*args):
   if self.q.pending():events.append('manual');self.q.cancel(nonce)
  nonce=self.q.request(self.event,'save',candidate=self.candidate)
  with mock.patch('xbmc.Monitor',return_value=monitor),mock.patch('startup48.suspended',return_value=False),mock.patch('service_runtime.pressure',return_value=False),mock.patch('work_requests86.drain',side_effect=manual),mock.patch('programme_consent77.ensure'),mock.patch('live_warm68.prepare',side_effect=lambda cancel:events.append('warm')):
   module._run()
  self.assertEqual(events,['manual','warm'])
 def test_background_warmup_receives_cooperative_manual_priority_cancellation(self):
  module=__import__('programme_requests68');observed=[]
  monitor=types.SimpleNamespace(abortRequested=lambda:False,waitForAbort=lambda n:True)
  def warm(cancel):
   self.q.request(self.event,'save',candidate=self.candidate);observed.append(cancel())
  with mock.patch('xbmc.Monitor',return_value=monitor),mock.patch('startup48.suspended',return_value=False),mock.patch('service_runtime.pressure',return_value=False),mock.patch('programme_consent77.ensure'),mock.patch('live_warm68.prepare',side_effect=warm),mock.patch('programme_requests68.drain') as regular:
   module._run()
  self.assertEqual(observed,[True]);regular.assert_not_called()
 def test_inflight_scope_change_cannot_publish_to_new_nonce(self):
  first=self.q.request(self.event,query='Monk');second=self.q.request(self.event,query='Charmed')
  self.assertTrue(self.q.cancelled(first));self.assertFalse(self.q.cancelled(second));self.assertTrue(self.q.pending())
 def test_real_five_and_thirty_second_worker_block_do_not_falsely_report_user_cancel_or_late_save(self):
  import threading,time
  # Actual elapsed waits test the production 30-second GUI deadline and the
  # one existing worker's cooperative intent ordering, not fake clock ticks.
  for delay,expected in ((5,'SAVED'),(30.5,'WORKER_BUSY')):
   module=__import__('programme_requests68');entered=threading.Event();release=threading.Event();shutdown=threading.Event();failed=[]
   monitor=types.SimpleNamespace(abortRequested=shutdown.is_set,waitForAbort=lambda n:shutdown.wait(n))
   progress=types.SimpleNamespace(create=mock.Mock(),close=mock.Mock(),iscanceled=lambda:False)
   def warm(cancel):entered.set();release.wait(33)
   def regular(cancel):pass
   with mock.patch('xbmc.Monitor',return_value=monitor),mock.patch('xbmcgui.DialogProgress',create=True,return_value=progress),mock.patch('startup48.suspended',return_value=False),mock.patch('service_runtime.pressure',return_value=False),mock.patch('programme_consent77.ensure'),mock.patch('live_warm68.prepare',side_effect=warm),mock.patch.object(module,'drain',side_effect=regular),mock.patch.object(self.q,'authoritative',return_value=self.event),mock.patch('work_search86.details',return_value=self.candidate):
    worker=threading.Thread(target=module._run);worker.start()
    try:
     self.assertTrue(entered.wait(2));timer=threading.Timer(delay,release.set);timer.start();began=time.monotonic()
     value=__import__('work_manager86').wait(self.event,'save',candidate=self.candidate)
     elapsed=time.monotonic()-began;self.assertEqual(value['code'],expected);self.assertGreaterEqual(elapsed,4.8 if delay==5 else 29.8);self.assertLess(elapsed,32)
     if expected=='WORKER_BUSY':self.assertFalse(self.q.pending())
    finally:shutdown.set();release.set();worker.join(2);timer.cancel()
    self.assertFalse(worker.is_alive())
 def test_busy_existing_network_lane_is_reported_as_worker_busy_not_generic_cancel(self):
  nonce=self.q.request(self.event,'search',query='Monk')
  with mock.patch('work_search86.search',side_effect=__import__('media_sources43').SourceError('RESEARCH_BUSY')):self.q.drain()
  self.assertEqual(self.q.result(nonce)['code'],'WORKER_BUSY')
