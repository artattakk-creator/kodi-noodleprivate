"""Actual host storage/owner transitions; synthetic sources, no Android claims."""
import importlib,json,sqlite3,threading,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,QueuedPool,ADDON,LIB

def real_epg():
 spec=importlib.util.spec_from_file_location("gate95_real_epg",LIB/"epg.py");module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
import test_xcmate_epg_resume_02954 as resume

class GateUI95(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.g=importlib.import_module('guide_store');self.m=importlib.import_module('epg_gate95')
  self.g.import_cache('p',{'xml':[dict(name='Synthetic',channel='xml',start_timestamp=self.now-30,stop_timestamp=self.now+1800)]})
 def test_stale_gui_backup_verified_never_authorizes_without_db_proof(self):
  import xbmcgui
  xbmcgui.Window(10000).setProperty('XCMate.GuideBackup44Status',json.dumps(dict(code='BACKUP_VERIFIED')))
  self.assertEqual(self.m.inspect(self.g.path())['code'],'DB_AUTHORIZATION_MISSING')
  status=importlib.import_module('epg_status');status.update=mock.Mock()
  epg=real_epg();self.assertFalse(epg.request_refresh('p',dict(epg_show=True)))
  self.assertEqual(status.update.call_args.args[2],'DB_AUTHORIZATION_MISSING')
 def test_missing_schema_is_not_claimed_missing_backup(self):
  p=self.folder/'old-schema.sqlite'
  with sqlite3.connect(p) as db:db.execute('CREATE TABLE programmes(id INTEGER)')
  self.assertEqual(self.m.inspect(p)['code'],'DB_SCHEMA_MISSING')
 def test_sqlite_interruption_is_distinct_and_sanitized(self):
  exc=sqlite3.OperationalError('PRIVATE_PATH TOKEN');exc.sqlite_errorcode=sqlite3.SQLITE_INTERRUPT
  with mock.patch.object(self.m.sqlite3,'connect',side_effect=exc):r=self.m.inspect(self.g.path())
  self.assertEqual(r['code'],'DB_INTERRUPTED');self.assertNotIn('TOKEN',json.dumps(r));self.assertNotIn('PRIVATE_PATH',json.dumps(r))
 def test_cancel_does_not_authorize_or_modify_guide(self):
  before=Path(self.g.path()).read_bytes();self.assertEqual(self.m.inspect(self.g.path(),cancel=lambda:True)['code'],'CANCELLED');self.assertEqual(Path(self.g.path()).read_bytes(),before)
 def test_low_space_before_explicit_backup_preserves_existing_database_and_archives(self):
  module=importlib.import_module('guide_backup44');before=Path(self.g.path()).read_bytes()
  folder=self.folder/'guide_backups44';folder.mkdir();old=folder/'USER_BACKUP';old.write_bytes(b'keep')
  with mock.patch('import_budget.check_space',side_effect=OSError(28,'synthetic full')):
   with self.assertRaises(OSError):module.authorize(self.g.path())
  self.assertEqual(Path(self.g.path()).read_bytes(),before);self.assertEqual(list(folder.iterdir()),[old]);self.assertEqual(old.read_bytes(),b'keep')
 def test_single_flight_probe_runs_off_owner_thread(self):
  entered=threading.Event();release=threading.Event();done=threading.Event();owners=[];owner=threading.get_ident()
  def slow(*a,**k):owners.append(threading.get_ident());entered.set();release.wait(2);return dict(code='DB_BUSY')
  with mock.patch.object(self.m,'inspect',side_effect=slow):
   start=time.monotonic();self.assertTrue(self.m.request(self.g.path(),lambda value:done.set()));self.assertLess(time.monotonic()-start,.1)
   self.assertTrue(entered.wait(1));self.assertFalse(self.m.request(self.g.path()));release.set();self.assertTrue(done.wait(2))
  self.assertEqual(len(owners),1);self.assertNotEqual(owners[0],owner)
 def test_manager_click_defers_gate_and_old_job_cannot_hide_rejection(self):
  manager=importlib.import_module('epg_manager53');calls=[]
  with mock.patch.object(manager,'ThreadPoolExecutor',QueuedPool):
   w=manager.Manager53('XCMateEPGManager53.xml',str(ADDON),'Default','720p');w.configure(dict(id='p',epg_show=True))
  self.addCleanup(w.close);w.show();w._pool.drain();w.pump()
  with mock.patch('epg_config94.confirm_enable',return_value=True),mock.patch.dict('sys.modules',{'epg':real_epg()}),mock.patch('epg.request_refresh',side_effect=lambda *a,**k:calls.append('worker') or False),mock.patch('epg_status.read',return_value={'refresh':{'code':'DB_BUSY'}}):
   w.onClick(402);self.assertEqual(calls,[]);w._pool.drain();w.pump()
  self.assertEqual(calls,['worker']);self.assertIn('DB_BUSY',w.getControl(102).label)
  w._job_loaded94(dict(requested=0,state='DONE',sources={}));self.assertIn('DB_BUSY',w.getControl(102).label)
 def test_concurrent_source_revision_change_during_backup_is_not_authorized(self):
  module=importlib.import_module('guide_backup44');real=module.hashlib.sha256;changed=[]
  def race(*args,**kw):
   if not changed:
    changed.append(True)
    with sqlite3.connect(self.g.path()) as db:db.execute("UPDATE guide_meta SET revision='CONCURRENT_WRITER'")
   return real(*args,**kw)
  with mock.patch.object(module.hashlib,'sha256',side_effect=race):
   with self.assertRaisesRegex(ValueError,'GUIDE_CHANGED_RETRY_BACKUP'):module.authorize(self.g.path())
  with sqlite3.connect(self.g.path()) as db:self.assertEqual(db.execute('SELECT count(*) FROM guide44_authorization').fetchone()[0],0)
 def test_gate_cannot_trust_locator_after_archive_moves_and_recovers_after_manual_restore(self):
  backup=importlib.import_module('guide_backup44').authorize(self.g.path());self.assertEqual(self.m.inspect(self.g.path())['code'],'IMPORT_AUTHORIZED')
  folder=self.folder/'guide_backups44';moved=self.folder/'USER_MOVED_BACKUPS';folder.rename(moved)
  self.assertEqual(self.m.inspect(self.g.path())['code'],'BACKUP_DIR_UNAVAILABLE')
  moved.rename(folder);self.m=importlib.reload(self.m);self.assertEqual(self.m.inspect(self.g.path())['code'],'IMPORT_AUTHORIZED')

class GatePipeline95(unittest.TestCase):
 setUp=resume.EPG54.setUp
 backup=resume.EPG54.backup
 def test_real_wal_backup_gate_accepts_next_request_and_two_source_readback(self):
  self.assertEqual(self.mod.run(self.portal)['phase'],'READY');from guide_store import path
  result=importlib.import_module('guide_backup44').authorize(path());self.assertEqual(result['code'],'BACKUP_VERIFIED')
  self.assertEqual(importlib.import_module('epg_gate46').access(path()),'READY')
  self.assertTrue(real_epg().request_refresh(self.portal['id'],self.portal))
  state=self.mod.run(self.portal);self.assertEqual(state['phase'],'READY');self.assertEqual(len(state['sources']),2)
  for source in state['sources']:self.assertEqual(self.mod.stored(self.portal,source)['rows'],1)
 def test_cancel_and_offline_after_proof_keep_existing_programmes(self):
  self.mod.run(self.portal);self.backup();from guide_store import path
  def rows():
   with sqlite3.connect(path()) as db:return db.execute('SELECT * FROM programmes ORDER BY pid,cid,start').fetchall()
  before=rows()
  with self.assertRaises(InterruptedError):self.mod.run(self.portal,cancel=lambda:True)
  self.assertEqual(rows(),before)
  state=self.mod.read(self.portal);state['sources'].clear();state['phase']='PARTIAL';self.mod.write(self.portal,state)
  for file in self.files:file.unlink()
  state=self.mod.run(self.portal)
  self.assertNotEqual(state['phase'],'READY');self.assertEqual(rows(),before)
