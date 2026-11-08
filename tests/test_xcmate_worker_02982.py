"""Real worker lifetime, guarded writes, deferred recovery, no private data."""
import importlib,io,json,sqlite3,threading,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
class Worker82(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.assets=importlib.reload(importlib.import_module('widget_assets69'));self.health=importlib.import_module('artwork_health82');self.health._backoff.clear()
  self.addCleanup(self.stop)
 def stop(self):
  self.assets.shutdown()
  if self.assets._thread:self.assets._thread.join(2)
 def png(self):
  from PIL import Image
  out=io.BytesIO();Image.new('RGB',(160,90),(20,80,130)).save(out,'PNG');return out.getvalue()
 def test_reproduced_store_used_sqlite_pause_is_a_controlled_defer(self):
  import render_cache81 as render
  from artwork_db import ArtworkDBUnavailable
  f=self.folder/'input.png';f.write_bytes(self.png());row=dict(sid='1',cover='https://image.tmdb.org/t/p/w500/synthetic82.png')
  self.options['media_art_budget_mb']=128
  with mock.patch('media_art.cached',return_value=str(f)),mock.patch('art_store.used',side_effect=ArtworkDBUnavailable('XM-ARTWORK-DB-PAUSED')),mock.patch('artwork_health82.guard'):
   with self.assertRaises(self.health.Deferred) as caught:render.prepare(self.portal,'vod',[row])
  self.assertGreater(caught.exception.retry_at82,time.time());self.assertTrue(f.exists())
 def test_443_polls_during_pause_keep_one_worker_then_recover(self):
  from artwork_db import ArtworkDBUnavailable
  __import__('artwork_config').choose('dynamic');row=dict(sid='1',cover='https://image.tmdb.org/t/p/w500/synthetic82.png')
  entered=threading.Event();recovered=threading.Event();pause={'code':'DB_PAUSED','reason':'BUSY','until':time.time()+1800}
  def render(*args):
   entered.set()
   if pause['code']!='READY':raise self.health.Deferred('DB_PAUSED',pause['until'],'BUSY')
   recovered.set()
  errors=[];old=threading.excepthook
  with mock.patch('widget_cache82.prepare',side_effect=lambda *a:entered.set()),mock.patch.object(self.assets,'_references82'),mock.patch('render_cache81.prepare',side_effect=render),mock.patch('media_hero81.prepare'),mock.patch.object(self.health,'status',side_effect=lambda:dict(pause)),mock.patch('home_schedule75.allowed',return_value=True),mock.patch.object(threading,'excepthook',side_effect=lambda a:errors.append(a.exc_type)):
   self.assertTrue(self.assets.prepare(self.portal,'vod',[row]));self.assertTrue(entered.wait(2));worker=self.assets._thread
   for _ in range(443):self.assertFalse(self.assets.prepare(self.portal,'vod',[row]))
   self.assertTrue(worker.is_alive());self.assertIs(worker,self.assets._thread);self.assertEqual(len(self.assets._pending),1)
   pause.update(code='READY',reason='READY',until=0);self.assertTrue(recovered.wait(2))
   self.stop();self.assertEqual(errors,[])
 def test_unlimited_budget_does_not_query_or_adopt_artwork_database(self):
  from programme_art46 import space
  self.options['media_art_budget_mb']=0
  with mock.patch('art_store.used',side_effect=AssertionError('unexpected DB/adoption')),mock.patch('art_storage.check'),mock.patch('artwork_health82.guard'):space(4096)
 def test_guard_blocks_new_persistent_write_but_keeps_existing_pixels(self):
  import render_cache81 as render
  with mock.patch('programme_art46.space'),mock.patch.object(self.health,'guard'):record=render.store('a'*64,self.png())
  with mock.patch.object(self.health,'status',return_value=dict(code='DB_PAUSED',reason='BUSY',until=time.time()+300)):
   self.assertEqual(render.read('a'*64)['file'],record['file'])
   with self.assertRaises(self.health.Deferred):render.store('b'*64,self.png())
  self.assertTrue(Path(record['file']).exists());self.assertIsNone(render.read('b'*64))
 def test_memory_failure_is_fatal_and_never_silently_respawned_or_successful(self):
  __import__('artwork_config').choose('dynamic');row=dict(sid='1',cover='https://image.tmdb.org/t/p/w500/synthetic82.png')
  with mock.patch('widget_cache82.prepare'),mock.patch.object(self.assets,'_references82'),mock.patch('artwork_health82.guard'),mock.patch('render_cache81.prepare',side_effect=MemoryError),mock.patch('home_schedule75.allowed',return_value=True),mock.patch.object(self.health,'note') as note:
   self.assets.prepare(self.portal,'vod',[row]);self.assets._thread.join(2)
   self.assertFalse(self.assets._thread.is_alive());self.assertTrue(self.assets._fatal82)
   for _ in range(20):self.assertFalse(self.assets.prepare(self.portal,'vod',[row]))
   self.assertTrue(any(c.args[0]=='FATAL' and c.kwargs['reason']=='MEMORY_ERROR' for c in note.call_args_list));self.assertFalse(any(c.args[0]=='RECOVERED' for c in note.call_args_list))
 def test_real_db_pause_receipt_respected_across_thirty_minutes_virtual_idle(self):
  import artwork_db as db
  filename=db.path();db._failures[filename]=dict(identity=db._identity(filename),code='BUSY',retry_after=2800)
  with mock.patch('time.time',return_value=1000):
   for i in range(443):self.assertEqual(self.health.status()['code'],'DB_PAUSED')
  with mock.patch('time.time',return_value=2799):self.assertEqual(self.health.status()['until'],2800)
  with mock.patch('time.time',return_value=2801):self.assertEqual(self.health.status()['code'],'READY')
  db._failures.pop(filename,None)
 def test_readonly_automatic_health_check_does_not_change_schema_or_bytes(self):
  import artwork_db as db
  connection=db.connect();connection.close();before=Path(db.path()).read_bytes()
  with mock.patch.object(db,'maintain',side_effect=AssertionError('automatic repair')),mock.patch.object(db,'_backup',side_effect=AssertionError('automatic backup')):
   self.assertEqual(db.inspect_readonly82()['code'],'READONLY_CHECKED')
  self.assertEqual(Path(db.path()).read_bytes(),before)
