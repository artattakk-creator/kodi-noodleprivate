"""Actual file generations and SQLite; fake Kodi only, no Android PASS."""
import contextlib,hashlib,importlib,json,os,sqlite3,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture

class Profile95(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.module=importlib.import_module('portal_snapshot');self.file=self.folder/'portals.json';self.file.write_text(json.dumps([self.portal]));self.types=['xtream','m3u','stb']
 @contextlib.contextmanager
 def busy(self):
  import fcntl
  fd=os.open(self.folder/'.xcmate-config.lock',os.O_CREAT|os.O_RDWR,0o600);fcntl.flock(fd,fcntl.LOCK_EX)
  try:yield
  finally:os.close(fd)
 def test_cold_root_uses_only_previously_verified_same_file_generation(self):
  self.assertEqual(self.module.Snapshot().read(str(self.file),self.types),[self.portal]);before=self.file.read_bytes()
  with self.busy():self.assertEqual(self.module.Snapshot().read(str(self.file),self.types),[self.portal])
  self.assertEqual(self.file.read_bytes(),before)
 def test_replaced_file_cannot_inherit_old_proof_during_profile_write(self):
  self.module.Snapshot().read(str(self.file),self.types)
  changed=self.file.with_suffix('.new');changed.write_text(json.dumps([dict(self.portal,name='Incomplete new generation')]));os.replace(changed,self.file)
  with self.busy(),self.assertRaises(self.module.PortalReadError) as error:self.module.Snapshot().read(str(self.file),self.types)
  self.assertEqual(error.exception.reason,'PROFILE_BUSY')
 def test_no_proof_never_creates_fake_empty_profile_when_busy(self):
  with self.busy(),self.assertRaises(self.module.PortalReadError):self.module.Snapshot().read(str(self.file),self.types)
 def test_proof_has_no_second_copy_of_credentials_and_private_permissions(self):
  self.module.Snapshot().read(str(self.file),self.types);p=Path(str(self.file)+'.snapshot95.json');raw=p.read_text()
  self.assertNotIn(self.portal['xc_pass'],raw);self.assertNotIn(self.portal['xc_host'],raw);self.assertEqual(p.stat().st_mode&0o777,0o600)
 def test_reminder_transaction_does_not_wait_for_unrelated_profile_writer(self):
  lock=importlib.import_module('reminder_transaction95')
  with self.busy(),lock.writing():pass
 def test_idle_reminder_poll_does_not_create_timer_database_or_write_profile(self):
  runtime=importlib.import_module('reminder_runtime89')
  with mock.patch('profile_transaction.writing',side_effect=AssertionError('GLOBAL_PROFILE_LOCK')),mock.patch('guide_timers.db',side_effect=AssertionError('IDLE_WRITE')):runtime.worker(now=int(time.time()))
  self.assertFalse((self.folder/'guide_timers_v1.sqlite').exists())

class Inventory95(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.g=importlib.import_module('guide_store');self.g.connect().close();self.m=importlib.import_module('epg_inventory95')
 def seed(self,sources=2,each=3):
  with sqlite3.connect(self.g.path()) as db:
   for s in range(sources):db.executemany('INSERT INTO guide44_inputs VALUES(?,?,?,?,?,?,?,?)',(('p',str(s),'c'+str(i//1000),self.now+i*10,self.now+i*10+60,'SYNTHETIC','',s) for i in range(each)))
 def test_120000_stored_rows_are_read_in_indexed_source_pages(self):
  self.seed(each=60000);r=self.m.collect('p',self.g.path())
  self.assertEqual(r['code'],'READY');self.assertEqual([x['programmes'] for x in r['sources']],[60000,60000]);self.assertEqual(r['sources'][0]['channels'],60)
 def test_budget_is_unknown_count_not_false_empty(self):
  self.seed();r=self.m.collect('p',self.g.path(),source_seconds=0)
  self.assertEqual(r['code'],'PARTIAL');self.assertTrue(all(s['programmes'] is None for s in r['sources']))
 def test_one_slow_source_does_not_invalidate_other_completed_source(self):
  self.seed();real=sqlite3.connect
  class Slow(sqlite3.Connection):
   def execute(self,sql,params=(),*args,**kw):
    if sql.startswith('SELECT cid,start,stop') and len(params)>1 and params[1]=='0':time.sleep(.06)
    return super().execute(sql,params,*args,**kw)
  with mock.patch.object(sqlite3,'connect',side_effect=lambda *a,**kw:real(*a,**dict(kw,factory=Slow))):r=self.m.collect('p',self.g.path(),source_seconds=.04)
  self.assertEqual(r['code'],'PARTIAL');self.assertEqual(r['sources'][1]['code'],'READY');self.assertEqual(r['sources'][1]['programmes'],3)
 def test_unchanged_inventory_is_cached_but_database_write_invalidates_it(self):
  self.seed();self.m.collect('p',self.g.path())
  with mock.patch.object(sqlite3,'connect',side_effect=AssertionError('UNCHANGED_RECOUNT')):self.assertEqual(self.m.collect('p',self.g.path())['sources'][0]['programmes'],3)
  with sqlite3.connect(self.g.path()) as db:db.execute('DELETE FROM guide44_inputs WHERE source_id=?',('0',))
  self.assertEqual(len(self.m.collect('p',self.g.path())['sources']),1)
 def test_busy_inventory_does_not_revoke_historical_verified_source(self):
  report=importlib.import_module('epg_report53');item=dict(id='provider',key='provider',name='Provider',rank=0,enabled=True)
  run=dict(sources=[dict(id='provider',code='READY',started=1,finished=2,verified=37,verified_first=100,verified_last=200)])
  with mock.patch.object(report,'statistics',return_value=dict(code='DB_BUSY',sources=[])),mock.patch.object(report,'configured',return_value=[item]),mock.patch.object(report,'history',return_value=[run]):rows=report.overview(self.portal)
  self.assertEqual(rows[0]['code'],'READY');self.assertEqual(rows[0]['saved']['programmes'],37);self.assertTrue(rows[0]['historical95']);self.assertEqual(rows[0]['inventory95'],'DB_BUSY')
