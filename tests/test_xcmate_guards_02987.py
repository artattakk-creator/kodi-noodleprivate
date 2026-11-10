"""P0-F: native API guards, owner cancellation and revision-scoped retries.

Synthetic host evidence; physical Android acceptance remains separate.
"""
import importlib,json,threading,time,types,unittest
from concurrent.futures import ThreadPoolExecutor
from unittest import mock
from xcmate027_fixture import Fixture,Control,ListItem

class Navigation86(Fixture,unittest.TestCase):
 def guard(self):return importlib.import_module('gui_guard86')
 def test_native_directory_count_does_not_authorize_unexposed_python_list(self):
  control=mock.Mock();control.size.return_value=0
  self.assertIsNone(self.guard().item(control,0,expected=24,ident=2520))
  control.getListItem.assert_not_called()
 def test_negative_and_stale_positions_never_touch_native_item(self):
  control=mock.Mock();control.size.return_value=24
  for index in (-1,24,100):self.assertIsNone(self.guard().item(control,index,expected=24))
  view=types.SimpleNamespace(_closed=False,_generation=2,mode='detail')
  self.assertIsNone(self.guard().item(control,0,view,generation=1))
  view._closed=True;self.assertIsNone(self.guard().item(control,0,view,generation=2))
  control.getListItem.assert_not_called()
 def test_generation_change_during_native_read_does_not_publish_returned_item(self):
  view=types.SimpleNamespace(_closed=False,_generation=1)
  def read(index):view._generation=2;return ListItem('stale')
  control=mock.Mock(getListItem=read);control.size.return_value=1
  self.assertIsNone(self.guard().item(control,0,view,generation=1,expected=1))
 def test_changed_control_length_after_read_discards_old_reference(self):
  control=mock.Mock();control.size.side_effect=[1,0]
  self.assertIsNone(self.guard().item(control,0,expected=1))
 def test_invalid_native_focus_is_not_python_negative_index(self):
  control=mock.Mock();control.size.return_value=1;control.getSelectedPosition.return_value=-1
  self.assertIsNone(self.guard().position(control,[dict(id=1)]))
 def test_native_bridge_exception_is_contained_without_exception_text(self):
  control=mock.Mock();control.size.return_value=1;control.getListItem.side_effect=IndexError('PRIVATE_URL_PASSWORD')
  import xbmc
  with mock.patch.object(xbmc,'log',create=True) as log,mock.patch.object(xbmc,'LOGINFO',0,create=True):
   self.guard()._seen.clear();self.assertIsNone(self.guard().item(control,0,ident=201,route='media_detail'))
  output=' '.join(str(c) for c in log.call_args_list)
  self.assertIn('IndexError',output);self.assertNotIn('PRIVATE_URL_PASSWORD',output);self.assertIn('thread',output)
 def test_one_hundred_detail_back_cycles_under_delayed_refresh_keep_focus(self):
  windows=[self.media_window('vod'),self.media_window('series')]
  for cycle in range(100):
   w=windows[cycle%2];position=cycle%min(3,len(w.rows));w.getControl(110).selectItem(position);w._last_position=position
   w.native(7);self.assertEqual(w.mode,'detail')
   # Leave half of the real model jobs pending until after Back.
   if cycle%3:self.settle(w)
   w.native(92);self.settle(w);w._refresh_art()
   self.assertEqual((w.mode,w._last_position,w.getFocusId()),('landing',position,110))
   self.assertEqual(w.getControl(110).getSelectedPosition(),position)
 def test_closed_owner_does_not_apply_pending_result(self):
  w=self.media_window();applied=[];w._request(lambda:'late',applied.append);w.close();w._pool.drain();w.pump()
  self.assertEqual(applied,[])
 def test_existing_worker_cancels_on_generation_change_without_second_worker_lane(self):
  m=importlib.import_module('ui_jobs86');view=types.SimpleNamespace(_closed=False,_generation=1);entered=threading.Event()
  def job():entered.set();m.wait(10)
  with ThreadPoolExecutor(max_workers=1) as pool:
   future=pool.submit(m.run,view,1,job);self.assertTrue(entered.wait(1));started=time.monotonic();view._generation=2
   with self.assertRaises(InterruptedError):future.result(timeout=1)
   self.assertLess(time.monotonic()-started,.5)
 def test_ui_http_policy_is_bounded_and_does_not_change_service_or_other_threads(self):
  m=importlib.import_module('ui_jobs86');self.assertEqual(m.policy(5,10,2),(5,10,2))
  with m.scope(lambda:False):
   timeout,seconds,retries=m.policy(5,10,2);self.assertLessEqual(timeout,1);self.assertLessEqual(seconds,4);self.assertEqual(retries,0)
   with ThreadPoolExecutor(max_workers=1) as pool:self.assertEqual(pool.submit(m.policy,5,10,2).result(),(5,10,2))
  self.assertFalse(m.active());self.assertEqual(m.policy(5,10,2),(5,10,2))
 def test_owner_deadline_and_closed_window_cancel_before_new_network_work(self):
  m=importlib.import_module('ui_jobs86')
  with self.assertRaises(InterruptedError):
   with m.scope(lambda:True):self.fail('must cancel before work')
  with self.assertRaises(InterruptedError):
   with m.scope(lambda:False,seconds=.005):time.sleep(.01);m.check()
 def test_real_slow_http_releases_existing_owner_pool_before_five_second_kill(self):
  import ast
  from http.server import ThreadingHTTPServer,BaseHTTPRequestHandler
  from pathlib import Path
  arrived=threading.Event();release=threading.Event()
  class Slow(BaseHTTPRequestHandler):
   def do_GET(inner):
    inner.send_response(200);inner.send_header('Content-Length','10');inner.end_headers();arrived.set();release.wait(3)
   def log_message(inner,*args):pass
  server=ThreadingHTTPServer(('127.0.0.1',0),Slow);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
  self.addCleanup(server.server_close);self.addCleanup(server.shutdown);self.addCleanup(release.set)
  # Execute the production transport function, with only settings/backend
  # globals supplied; keep real socket reads, cancellation and timeouts.
  from xcmate027_fixture import LIB
  node=next(n for n in ast.parse((LIB/'utils.py').read_text()).body if isinstance(n,ast.FunctionDef) and n.name=='http_get')
  import sys,network_io
  namespace=dict(sys=sys,time=time,MAX_HTTP_BYTES=network_io.MAX_HTTP_BYTES,read_http_chunks=network_io.read_http_chunks,setting_int=lambda k,d:d,setting_bool=lambda k,d:d,_default_headers=lambda:{},_httpx_available=lambda:False)
  exec(compile(ast.Module(body=[node],type_ignores=[]),'utils.py','exec'),namespace)
  m=importlib.import_module('ui_jobs86');view=types.SimpleNamespace(_closed=False,_generation=1)
  pool=ThreadPoolExecutor(max_workers=1);self.addCleanup(pool.shutdown)
  future=pool.submit(m.run,view,1,lambda:namespace['http_get']('http://127.0.0.1:'+str(server.server_port),timeout=5,max_seconds=10))
  self.assertTrue(arrived.wait(1));started=time.monotonic();view._closed=True
  with self.assertRaises((InterruptedError,TimeoutError,OSError)):future.result(timeout=2)
  self.assertLess(time.monotonic()-started,1.6);pool.shutdown(wait=True)
 def test_negative_diagnostics_are_cross_invoker_and_revision_scoped(self):
  m=importlib.import_module('diagnostic_rate86');event=dict(key='synthetic',source_key46='source1',fact_revision46='r1')
  self.assertTrue(m.admit('NO_SOURCE_FACTS',event,'NO_SOURCE_FACTS'))
  for _ in range(1485):self.assertFalse(m.admit('NO_SOURCE_FACTS',event,'NO_SOURCE_FACTS'))
  m=importlib.reload(m);self.assertFalse(m.admit('NO_SOURCE_FACTS',event,'NO_SOURCE_FACTS'))
  self.assertTrue(m.admit('NO_SOURCE_FACTS',dict(event,fact_revision46='r2'),'NO_SOURCE_FACTS'))
  self.assertTrue(m.admit('NO_SOURCE_FACTS',dict(event,source_key46='source2'),'NO_SOURCE_FACTS'))
  self.assertNotIn('synthetic',json.dumps(self.properties))
 def test_unchanged_home_generation_does_not_repeat_688_cache_ready_events(self):
  m=importlib.import_module('home_metrics82');m._seen.clear();import xbmc
  with mock.patch.object(xbmc,'log',create=True) as log,mock.patch.object(xbmc,'LOGINFO',0,create=True):
   for _ in range(688):m.note('CACHED_ITEMS_READY','vod',count=24,generation='a'*64)
   self.assertEqual(log.call_count,1)
   m.note('CACHED_ITEMS_READY','vod',count=24,generation='b'*64);self.assertEqual(log.call_count,2)
 def test_known_long_android_pipeline_cannot_block_identity_rail(self):
  rail=importlib.import_module('live_rail86');rows=[dict(sid=str(i),name='Station',stream_icon='') for i in range(88)]
  # Measured .85 log intervals are input facts, not .86 Android measurements.
  for old_ready_ms in (463372,147811):
   with mock.patch('logo_manifest86.read',return_value={}),mock.patch('epg_handoff63.get',return_value=None),mock.patch('widget_assets69.read',side_effect=AssertionError('slow background '+str(old_ready_ms))):
    started=time.monotonic();result=rail.values(self.portal,rows);self.assertEqual(len(result),88);self.assertLess(time.monotonic()-started,.25)
 def test_abort_is_cancellation_not_dispatch_failure(self):
  m=importlib.import_module('boot_diagnostics');import xbmc
  with mock.patch.object(xbmc,'Monitor',return_value=types.SimpleNamespace(abortRequested=lambda:True)),mock.patch.object(m,'mark') as mark:
   with self.assertRaises(SystemExit):
    with m.phase('DISPATCH'):raise SystemExit()
  self.assertEqual(mark.call_args.args[0],'ROUTE_CANCELLED')

class Refresh86(Fixture,unittest.TestCase):
 def test_negative_epg_backoff_is_bounded_and_revision_change_releases_it(self):
  import sys
  m=importlib.reload(importlib.import_module('epg_refresh74'));m._wanted.clear();m._due.clear();m._failures86.clear()
  import xbmc,epg_status
  monitor=types.SimpleNamespace(abortRequested=lambda:False,waitForAbort=lambda n:False)
  key=(__import__('epg_handoff63').profile_scope(),'p','missing')
  fake=mock.Mock();fake.get.return_value=None
  with mock.patch.object(xbmc,'Monitor',return_value=monitor),mock.patch('library_index.Reader',return_value=fake),mock.patch.object(m._wake,'wait'),mock.patch.object(m.time,'monotonic',return_value=100),mock.patch.object(epg_status,'revision',return_value='r1'):
   for delay in (30,60,180,300,300):
    m._wanted[key]=100;m._run();self.assertEqual(m._due[key],100+delay)
   fake.close.assert_called()
   m._thread=mock.Mock();m._thread.is_alive.return_value=True
   m.request('p','missing');self.assertFalse(m._wanted)
   with mock.patch.object(epg_status,'revision',return_value='r2'):m.request('p','missing')
   self.assertIn(key,m._wanted);self.assertNotIn(key,m._failures86)
