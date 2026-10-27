"""Backup proof, legacy profile fast path and anonymous identity-bound timings."""
import hashlib,importlib,json,sqlite3,sys,threading,time,types,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,LIB


class GateFlow46(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.g=importlib.import_module('guide_store');self.gate=importlib.import_module('epg_gate46')
  self.flow=importlib.import_module('flow46');self.logs=[]
  sys.modules['xbmc'].LOGINFO=1;sys.modules['xbmc'].log=lambda s,*a:self.logs.append(s)
 def populate(self):self.g.import_cache('p',{'xml':[dict(name='Stored',channel='xml',start_timestamp=self.now-30,stop_timestamp=self.now+300)]})
 def test_populated_guide_schema_alone_is_not_backup_authorization(self):
  self.populate();before=Path(self.g.path()).read_bytes();self.assertEqual(importlib.import_module('guide_publish44').access(self.g.path()),'READY')
  self.assertEqual(self.gate.access(self.g.path()),'BACKUP_REQUIRED');self.assertEqual(Path(self.g.path()).read_bytes(),before)
 def test_real_sqlite_wal_backup_receipt_allows_readonly_gate(self):
  self.populate();backup=importlib.import_module('guide_backup44');result=backup.authorize(self.g.path())
  self.assertEqual(result['code'],'BACKUP_VERIFIED');before=Path(self.g.path()).read_bytes()
  self.assertEqual(self.gate.access(self.g.path()),'READY');self.assertEqual(Path(self.g.path()).read_bytes(),before)
 def test_missing_or_tampered_backup_receipt_refuses_refresh(self):
  self.populate();result=importlib.import_module('guide_backup44').authorize(self.g.path())
  receipt=self.folder/'guide_backups44'/(result['backup']+'.json');value=json.loads(receipt.read_text());value['sha256']='f'*64;receipt.write_text(json.dumps(value))
  self.assertEqual(self.gate.access(self.g.path()),'BACKUP_REQUIRED')
 def test_empty_new_guide_and_missing_database_are_distinct_safe_states(self):
  self.assertEqual(self.gate.access(self.g.path()),'NOT_CREATED');self.g.connect().close();self.assertEqual(self.gate.access(self.g.path()),'READY')
 def test_existing_artwork_mode_needs_no_exclusive_lock_or_directory_scan(self):
  config=importlib.import_module('artwork_config');(self.folder/'box-a-cover.jpg').write_bytes(b'keep')
  config.initialize();config.choose('internal');before=(self.folder/config.NAME).read_bytes()
  with mock.patch.object(config,'locked',side_effect=AssertionError('lock on stable profile')),mock.patch.object(config.os,'listdir',side_effect=AssertionError('scan on stable profile')):
   for _ in range(20):self.assertEqual(config.initialize()['mode'],'internal')
  self.assertEqual((self.folder/config.NAME).read_bytes(),before);self.assertEqual((self.folder/'box-a-cover.jpg').read_bytes(),b'keep')
 def test_anonymous_phase_chain_records_first_video_only_for_exact_own_item(self):
  self.flow.begin('live','private-account','private-sender',force=True)
  session=dict(pid='private-account',sid='private-sender',nonce='private-nonce',at=time.time());self.flow.bind('live',session)
  with mock.patch('playback_exit.identity',return_value=('live',dict(session,nonce='foreign'))):self.flow.observe()
  self.assertNotIn('FIRST_VIDEO',self.flow.read()['marks'])
  sys.modules['xbmc'].Player=lambda:types.SimpleNamespace(getTime=lambda:1)
  with mock.patch('playback_exit.identity',return_value=('live',session)):
   self.flow.observe();self.flow.observe()
  self.assertEqual(sum('phase=FIRST_VIDEO ' in s for s in self.logs),1)
  for private in ('private-account','private-sender','private-nonce'):self.assertNotIn(private,' '.join(self.logs))
 def test_invalid_phase_and_status_payload_are_not_logged(self):
  self.flow.begin('live','p','1',force=True);n=len(self.logs);self.flow.mark('https://private.invalid/SECRET')
  self.assertEqual(len(self.logs),n)
  value=self.flow.read();value['kind']='SECRET';self.flow.save(value);self.assertIsNone(self.flow.read())
 def test_stale_or_other_portal_cannot_receive_media_detail_timing(self):
  self.flow.begin('media','p','1',force=True);self.flow.mark('DETAIL_READY',pid='foreign',sid='1');self.assertNotIn('DETAIL_READY',self.flow.read()['marks'])
  self.flow.mark('DETAIL_READY',pid='p',sid='other');self.assertNotIn('DETAIL_READY',self.flow.read()['marks'])
 def test_optional_import_warmup_never_waits_on_gui_thread(self):
  spec=importlib.util.spec_from_file_location('isolated_import46',LIB/'app_imports46.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  entered=threading.Event();release=threading.Event();owners=[]
  def slow(name):owners.append(threading.get_ident());entered.set();release.wait(2)
  with mock.patch.object(module.importlib,'import_module',side_effect=slow):
   started=time.monotonic();self.assertFalse(module.ensure());self.assertLess(time.monotonic()-started,.1);self.assertTrue(entered.wait(1))
   self.assertFalse(module.ensure());release.set();module._thread.join(2)
  self.assertTrue(module.ensure());self.assertTrue(all(n!=threading.get_ident() for n in owners))
 def test_service_poll_does_no_profile_or_skin_io_for_widget_refresh(self):
  notice=importlib.import_module('widget_notice46');notice._next=0
  sys.modules['xbmc'].getSkinDir=lambda:'skin.titan.bingie.mod'
  with mock.patch.object(sys.modules['xbmcgui'],'getCurrentWindowId',return_value=10000),mock.patch.object(sys.modules['xbmcgui'],'getCurrentWindowDialogId',return_value=0),mock.patch.object(sys.modules['xbmc'],'getCondVisibility',return_value=False),mock.patch('builtins.open',side_effect=AssertionError('disk IO on GUI')),mock.patch('portals.get_by_id',side_effect=AssertionError('profile IO')):
   notice.poll()
 def test_timing_analyser_exports_only_whitelisted_aggregates_not_private_lines(self):
  spec=importlib.util.spec_from_file_location('flow_analyser46',LIB.parents[3]/'tools/analyse_xcmate_flow46.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  lines=['PRIVATE_URL SECRET account password', '[XCMate][FLOW46] id='+'a'*32+' kind=live phase=FIRST_VIDEO ms=100', '[XCMate][FLOW46] id='+'b'*32+' kind=live phase=FIRST_VIDEO ms=200']
  result=module.analyse(lines);self.assertEqual(result['samples'],[dict(kind='live',phase='FIRST_VIDEO',n=2,p50_ms=100,p95_ms=200)])
  self.assertNotIn('SECRET',json.dumps(result));self.assertNotIn('a'*32,json.dumps(result))
