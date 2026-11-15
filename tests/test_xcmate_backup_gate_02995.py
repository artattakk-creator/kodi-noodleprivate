"""Real synthetic SQLite/WAL backup proofs, never device acceptance."""
import contextlib,hashlib,importlib,json,os,sqlite3,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture


class BackupGate95(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.g=importlib.import_module('guide_store');self.gate=importlib.import_module('epg_gate46')
  self.g.import_cache('p',{'xml':[dict(name='Synthetic',channel='xml',start_timestamp=self.now-30,stop_timestamp=self.now+1800)]})
  self.backup=importlib.import_module('guide_backup44');self.result=self.backup.authorize(self.g.path())
 def bytes(self):
  return {p.name:p.read_bytes() for p in self.folder.iterdir() if p.name.startswith('guide_v1.sqlite') and not p.name.endswith('-shm') or p.name=='guide_backups44' and p.is_file()}
 def test_verified_backup_slow_local_io_still_authorizes(self):
  real=sqlite3.connect
  class Slow(sqlite3.Connection):
   def execute(self,sql,*args,**kwargs):
    if sql.startswith('SELECT 1 FROM programmes'):time.sleep(.08)
    return super().execute(sql,*args,**kwargs)
  with mock.patch.object(sqlite3,'connect',side_effect=lambda *a,**k:real(*a,**dict(k,factory=Slow))):
   self.assertEqual(self.gate.access(self.g.path()),'READY')
 def test_manifest_after_129_unrelated_entries_still_authorizes(self):
  folder=self.folder/'guide_backups44'
  for i in range(150):(folder/('unrelated-'+str(i))).write_bytes(b'USER_DATA')
  original=os.scandir
  @contextlib.contextmanager
  def ordered(path):
   with original(path) as entries:rows=list(entries)
   yield iter(sorted(rows,key=lambda e:e.name.endswith('.sqlite.json')))
  with mock.patch.object(os,'scandir',ordered):self.assertEqual(self.gate.access(self.g.path()),'READY')
 def inspect(self,**kw):return importlib.import_module('epg_gate95').inspect(self.g.path(),**kw)
 def test_manifest_mismatch_is_not_busy_and_changes_no_existing_bytes(self):
  p=self.folder/'guide_backups44'/(self.result['backup']+'.json');v=json.loads(p.read_text());v['sha256']='f'*64;p.write_text(json.dumps(v))
  before=self.bytes();r=self.inspect();self.assertEqual(r['code'],'BACKUP_RECEIPT_MISMATCH');self.assertEqual(before,self.bytes())
 def test_missing_backup_and_missing_directory_have_distinct_codes(self):
  folder=self.folder/'guide_backups44';saved=folder/self.result['backup'];saved.rename(saved.with_suffix('.moved'))
  self.assertEqual(self.inspect()['code'],'BACKUP_MISSING')
  folder.rename(self.folder/'moved-backups');self.assertEqual(self.inspect()['code'],'BACKUP_DIR_UNAVAILABLE')
 def test_same_size_backup_tampering_cannot_use_cached_authorization(self):
  self.assertEqual(self.inspect()['code'],'IMPORT_AUTHORIZED')
  p=self.folder/'guide_backups44'/self.result['backup'];raw=p.read_bytes();p.write_bytes(raw[:-1]+bytes([raw[-1]^1]))
  self.assertEqual(self.inspect()['code'],'BACKUP_RECEIPT_MISMATCH')
 def test_exclusive_database_lock_is_busy_not_missing_backup(self):
  db=sqlite3.connect(self.g.path());db.execute('PRAGMA wal_checkpoint(TRUNCATE)');db.execute('PRAGMA journal_mode=DELETE');db.execute('BEGIN EXCLUSIVE')
  try:self.assertEqual(self.inspect()['code'],'DB_BUSY')
  finally:db.rollback();db.close()
 def test_expired_budget_fails_closed_without_requesting_another_backup(self):
  r=self.inspect(seconds=0);self.assertEqual(r['code'],'BACKUP_GATE_TIMEOUT')
 def test_new_reader_after_restart_rechecks_durable_authorization(self):
  module=importlib.import_module('epg_gate95');module=importlib.reload(module)
  before=self.bytes();self.assertEqual(module.inspect(self.g.path())['code'],'IMPORT_AUTHORIZED');self.assertEqual(before,self.bytes())
 def test_storage_error_is_reported_without_private_exception_message(self):
  m=importlib.import_module('epg_gate95')
  with mock.patch.object(m.os,'scandir',side_effect=PermissionError('PRIVATE_PATH SECRET TOKEN')):
   r=m.inspect(self.g.path())
  self.assertEqual(r['code'],'BACKUP_DIR_UNAVAILABLE');self.assertNotIn('PRIVATE',json.dumps(r));self.assertNotIn('SECRET',json.dumps(r))
 def test_existing_guide_and_backup_files_unchanged_after_successful_gate(self):
  paths=list(self.folder.glob('guide_v1.sqlite*'))+list((self.folder/'guide_backups44').iterdir())
  before={p:hashlib.sha256(p.read_bytes()).hexdigest() for p in paths if p.is_file() and not p.name.endswith('-shm')}
  self.assertEqual(self.inspect()['code'],'IMPORT_AUTHORIZED')
  self.assertEqual(before,{p:hashlib.sha256(p.read_bytes()).hexdigest() for p in before})
 def test_valid_receipt_after_150_other_backup_receipts_is_found(self):
  folder=self.folder/'guide_backups44'
  for i in range(150):
   name='guide-'+str(1000000000000000000+i)+'.sqlite'
   (folder/(name+'.json')).write_text(json.dumps(dict(code='BACKUP_VERIFIED',backup=name,bytes=0,sha256='f'*64)))
  original=os.scandir
  @contextlib.contextmanager
  def ordered(path):
   with original(path) as entries:rows=list(entries)
   yield iter(sorted(rows,key=lambda e:e.name==self.result['backup']+'.json'))
  with mock.patch.object(os,'scandir',ordered):self.assertEqual(self.inspect()['code'],'IMPORT_AUTHORIZED')
