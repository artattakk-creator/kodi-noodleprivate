"""Real SQLite/failed-write and URL-only regressions; no private provider data."""
import importlib,json,os,sqlite3,sys,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class Capacity69(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp()
  for name in ('programme_writes69','programme_session69','programme_image69','programme_requests68','programme_urls55'):sys.modules.pop(name,None)
 def event(self):
  from programme_events46 import describe
  return describe(self.portal,dict(sid='1',name='Synthetic'),dict(title='Synthetic Film',start=self.now-30,stop=self.now+1800,genre='Spielfilm',year=2024),'a',('revision',1))
 def test_reserve_guard_is_not_real_enospc(self):
  import import_budget
  from programme_writes69 import classify
  with mock.patch('import_budget.shutil.disk_usage',return_value=types.SimpleNamespace(free=16*1024*1024)):
   with self.assertRaises(OSError) as caught:import_budget.check_space(str(self.folder/'metadata.sqlite'),65536)
  self.assertEqual(classify(caught.exception),'SAFE_RESERVE_BLOCKED')
  self.assertEqual(classify(OSError(28,'synthetic actual ENOSPC')),'REAL_ENOSPC')
 def test_sqlite_busy_and_read_deadline_are_distinct(self):
  from programme_writes69 import classify
  busy=sqlite3.OperationalError('synthetic');busy.sqlite_errorname='SQLITE_BUSY'
  timeout=sqlite3.OperationalError('synthetic');timeout.sqlite_errorname='SQLITE_INTERRUPT'
  self.assertEqual(classify(busy),'SQLITE_BUSY_LOCKED')
  self.assertEqual(classify(timeout,read=True),'EPG_READ_TIMEOUT')
 def test_persistent_capacity_backoff_is_bounded_and_scoped(self):
  import programme_writes69 as cb
  filename=str(self.folder/'programmes.sqlite')
  with mock.patch('programme_writes69.time.time',return_value=1000):
   cb.record(filename,OSError(28,'synthetic'))
   self.assertFalse(cb.permit(filename,1001))
   self.assertTrue(cb.permit(str(self.folder/'other.sqlite'),1001))
   self.assertEqual(cb.state(filename)['until'],1030)
 def test_write_circuit_recovers_after_measured_capacity_increase(self):
  import programme_writes69 as cb
  from import_budget import ReserveBlocked
  filename=str(self.folder/'metadata.sqlite')
  with mock.patch('programme_writes69.time.time',return_value=1000),mock.patch('shutil.disk_usage',return_value=types.SimpleNamespace(free=16*1024*1024)):
   cb.record(filename,ReserveBlocked(16*1024*1024,32*1024*1024,65536))
  with mock.patch('shutil.disk_usage',return_value=types.SimpleNamespace(free=80*1024*1024)):
   self.assertTrue(cb.permit(filename,1030))
 def test_deferred_failure_does_not_extend_backoff_or_restart_lookup(self):
  import programme_writes69 as cb
  filename=str(self.folder/'metadata.sqlite')
  with mock.patch('programme_writes69.time.time',return_value=1000):
   cb.record(filename,OSError(28,'synthetic'));before=cb.state(filename)
   for _ in range(18):cb.record(filename,cb.Deferred('REAL_ENOSPC',1030))
   self.assertEqual(cb.state(filename),before)
 def test_url_mode_keeps_verified_ram_reference_when_db_write_fails(self):
  from programme_urls55 import resolve,OPTIONS
  from programme_image69 import eligible
  event=self.event()
  candidate=dict(url='https://image.tmdb.org/t/p/w500/SYNTHETIC.jpg',source='tmdb_movie',match='EXACT_TITLE_YEAR',attribution='TMDB',remote_id=69)
  with mock.patch('programme_index46.publish_result69',return_value=False),mock.patch('programme_writes69.last',return_value='SAFE_RESERVE_BLOCKED'),mock.patch('programme_art46.prepare',side_effect=AssertionError('FORCED_LOCAL_DOWNLOAD')):
   value=resolve(event,allow_lookup=True,url_mode69=True,match=lambda *a,**kw:candidate,check=mock.Mock())
  self.assertEqual(value['code'],'READY');self.assertEqual(value['storage69'],'RAM_ONLY')
  self.assertEqual(value['storage_code69'],'SAFE_RESERVE_BLOCKED');self.assertEqual(value['image'],candidate['url']+OPTIONS)
  self.assertTrue(eligible(value,event))
 def test_same_event_is_resolved_once_across_18_failed_persistence_requests(self):
  from programme_urls55 import resolve
  event=self.event();lookup=mock.Mock(return_value=dict(url='https://image.tmdb.org/t/p/w500/SYNTHETIC.jpg',source='tmdb_movie',match='EXACT_TITLE_YEAR',attribution='TMDB'))
  with mock.patch('programme_index46.publish_result69',return_value=False),mock.patch('programme_writes69.last',return_value='REAL_ENOSPC'):
   for _ in range(18):resolve(event,allow_lookup=True,url_mode69=True,match=lookup,check=mock.Mock())
  self.assertEqual(lookup.call_count,1)
 def test_remote_image_requires_proof_and_exact_source_revision(self):
  from programme_urls55 import resolve
  from programme_image69 import eligible
  event=self.event();found=dict(url='https://image.tmdb.org/t/p/w500/SYNTHETIC.jpg',source='tmdb_movie',match='EXACT_TITLE_YEAR',attribution='TMDB')
  with mock.patch('programme_index46.publish_result69',return_value=False):
   art=resolve(event,allow_lookup=True,url_mode69=True,match=lambda *a,**kw:found,check=mock.Mock())
  self.assertTrue(eligible(art,event));self.assertFalse(eligible(dict(art,url_verified69=False),event))
  self.assertFalse(eligible(art,dict(event,sid='different')))
  self.assertFalse(eligible(art,dict(event,revision=('revision',2))))
 def test_expired_remote_reference_is_never_ready(self):
  from programme_image69 import eligible
  self.assertFalse(eligible(dict(code='READY',source='tmdb_movie',image='https://image.tmdb.org/t/p/w500/SYNTHETIC.jpg')))
 def test_no_credential_or_private_url_is_admitted(self):
  from programme_urls55 import safe
  for url in ('https://user:secret@image.tmdb.org/t/p/w500/a.jpg','https://127.0.0.1/a.jpg','http://image.tmdb.org/t/p/w500/a.jpg','https://image.tmdb.org/t/p/w500/a.jpg?token=secret'):
   self.assertFalse(safe(url))

 def test_real_sqlite_exclusive_lock_is_classified_without_reset(self):
  from programme_writes69 import classify
  path=str(self.folder/'locked.sqlite')
  first=sqlite3.connect(path);second=sqlite3.connect(path,timeout=.01)
  try:
   first.execute('CREATE TABLE protected(value TEXT)');first.commit();first.execute('BEGIN EXCLUSIVE')
   with self.assertRaises(sqlite3.OperationalError) as caught:second.execute('INSERT INTO protected VALUES(?)',('keep',))
   self.assertEqual(classify(caught.exception,path),'SQLITE_BUSY_LOCKED')
  finally:first.rollback();first.close();second.close()
 def test_real_sqlite_full_is_not_misreported_as_filesystem_enospc(self):
  from programme_writes69 import classify
  path=str(self.folder/'full.sqlite');db=sqlite3.connect(path)
  try:
   db.execute('PRAGMA max_page_count=2');db.execute('CREATE TABLE protected(value BLOB)')
   with self.assertRaises(sqlite3.OperationalError) as caught:db.execute('INSERT INTO protected VALUES(?)',(b'a'*32768,))
   self.assertEqual(caught.exception.sqlite_errorname,'SQLITE_FULL')
   self.assertEqual(classify(caught.exception,path),'SQLITE_FULL_UNKNOWN')
  finally:db.close()
 def test_real_atomic_result_persistence_keeps_existing_rows(self):
  from programme_index46 import publish_result69,art
  first=self.event();second=dict(first,key='synthetic-second',sid='2')
  self.assertTrue(publish_result69(first,dict(code='NO_MATCH',source='placeholder',until=time.time()+300)))
  self.assertTrue(publish_result69(second,dict(code='NO_ARTWORK',source='placeholder',until=time.time()+300)))
  self.assertEqual(art(first)['code'],'NO_MATCH');self.assertEqual(art(second)['code'],'NO_ARTWORK')

 def test_reserve_diagnostic_is_available_before_db_creation(self):
  from programme_storage68 import inspect
  with mock.patch('programme_storage68.shutil.disk_usage',return_value=types.SimpleNamespace(free=16*1024*1024,total=64*1024*1024,used=48*1024*1024)):
   value=inspect()
  self.assertEqual(value['code'],'NOT_CREATED');self.assertEqual(value['capacity_code69'],'SAFE_RESERVE_BLOCKED')
 def test_remote_proof_is_revoked_by_source_policy_change_without_io(self):
  from programme_urls55 import resolve
  from programme_image69 import eligible
  event=self.event();found=dict(url='https://image.tmdb.org/t/p/w500/SYNTHETIC.jpg',source='tmdb_movie',match='EXACT_TITLE_YEAR',attribution='TMDB')
  with mock.patch('programme_index46.publish_result69',return_value=False):
   art=resolve(event,allow_lookup=True,url_mode69=True,match=lambda *a,**kw:found,check=mock.Mock())
  self.assertTrue(eligible(art,event));self.options['programme_tvmaze67']=True
  with mock.patch('builtins.open',side_effect=AssertionError('GUI_IO')),mock.patch('sqlite3.connect',side_effect=AssertionError('GUI_SQL')):self.assertFalse(eligible(art,event))
