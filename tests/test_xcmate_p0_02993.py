"""Real files/SQLite; Android player/volume/render assertions stay separate."""
import importlib,hashlib,json,os,sqlite3,time,unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from xcmate027_fixture import Fixture

class P093(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();patch=mock.patch('utils.addon_data_dir',return_value=str(self.folder));patch.start();self.addCleanup(patch.stop)
 def test_start_resolution_keeps_configured_id_on_locked_or_partial_catalogue(self):
  m=importlib.import_module('live_start');portal=dict(id='p',type='xtream',start_stream_id='42',start_group_id='4k')
  with mock.patch.object(m,'channel',return_value=None):r=m.resolve(portal,object())
  self.assertEqual(r['code'],'START_TEMPORARILY_UNAVAILABLE');self.assertEqual(portal['start_stream_id'],'42')
  self.assertEqual(m.resolve(dict(portal,start_stream_id=''),object())['code'],'START_NOT_CONFIGURED')
 def test_resumable_inventory_does_not_report_budget_zero_as_empty(self):
  m=importlib.import_module('storage_scan93');folder=self.folder/'scan';folder.mkdir()
  for n in range(35):(folder/str(n)).write_bytes(b'0123456789')
  scanner=m.Scan(folder);first=scanner.step(time.monotonic()-1)
  self.assertFalse(first['complete']);self.assertEqual(first['scan_status'],'PARTIAL')
  result=scanner.step(time.monotonic()+2)
  self.assertTrue(result['complete']);self.assertEqual(result['files'],35);self.assertEqual(result['bytes'],350)
 def test_inventory_skips_symlink_and_labels_read_failure(self):
  m=importlib.import_module('storage_scan93');target=self.folder/'outside';target.write_bytes(b'USER')
  link=self.folder/'link';link.symlink_to(target)
  result=m.Scan(link).step(time.monotonic()+1);self.assertEqual(result['files'],0);self.assertEqual(target.read_bytes(),b'USER')
  scanner=m.Scan(self.folder)
  with mock.patch.object(m.os,'scandir',side_effect=PermissionError()):r=scanner.step(time.monotonic()+1)
  self.assertFalse(r['complete']);self.assertEqual(r['scan_status'],'UNREADABLE')
 def test_storage_report_marks_partial_zero_unknown_quota_and_no_raw_json(self):
  m=importlib.import_module('storage_report93')
  with mock.patch.object(m,'tr',side_effect=lambda key,*a:str(key)+(' '+str(a) if a else '')):
   text=m.report(dict(categories=[dict(category='KODI_PACKAGES',files=0,bytes=0,complete=False,volume={})]))
  self.assertIn('38738',text);self.assertIn('38747',text);self.assertNotIn('"categories"',text);self.assertEqual(m.amount(1024**3),'1.0 GiB')
 def backup(self,name,source):
  folder=self.folder/'guide_backups44';folder.mkdir(exist_ok=True);target=folder/name
  output=sqlite3.connect(target)
  try:source.backup(output)
  finally:output.close()
  raw=target.read_bytes()
  value=dict(code='BACKUP_VERIFIED',sha256=hashlib.sha256(raw).hexdigest(),bytes=len(raw),events=source.execute('SELECT count(*) FROM programmes').fetchone()[0],backup=name,source_config_sha256=None)
  Path(str(target)+'.json').write_text(json.dumps(value));return value
 def seed_backups(self):
  db=sqlite3.connect(self.folder/'guide_v1.sqlite');db.executescript('CREATE TABLE guide_meta(pid,revision);INSERT INTO guide_meta VALUES("p","r");CREATE TABLE programmes(pid,start,stop,title);CREATE TABLE guide44_authorization(kind,backup_sha,created);')
  db.execute('INSERT INTO programmes VALUES(?,?,?,?)',('p',1,2,'FIRST'));db.commit()
  old=self.backup('guide-1000000000000000001.sqlite',db)
  db.execute('INSERT INTO programmes VALUES(?,?,?,?)',('p',3,4,'SECOND'));db.commit()
  keeper=self.backup('guide-1000000000000000002.sqlite',db)
  db.execute('INSERT INTO guide44_authorization VALUES(?,?,?)',('VERIFIED_BACKUP',keeper['sha256'],2));db.commit();db.close()
  return old,keeper
 def test_real_backup_retention_preserves_latest_and_offline_events(self):
  m=importlib.import_module('epg_cleanup93');old,keep=self.seed_backups();journal=[]
  result=m.prune(journal=lambda v:journal.append(dict(v)))
  self.assertEqual(result['code'],'VERIFIED_BACKUP_RETENTION');self.assertEqual(result['deleted_files'],1);self.assertGreater(result['deleted_bytes'],0)
  self.assertEqual(result['raw_deleted_bytes'],0);self.assertTrue(journal[0]['pending'])
  root=self.folder/'guide_backups44';self.assertFalse((root/old['backup']).exists());self.assertTrue((root/keep['backup']).exists())
  db=sqlite3.connect(root/keep['backup']);self.assertEqual(db.execute('SELECT count(*) FROM programmes').fetchone()[0],2);db.close()
  self.assertEqual(m.prune()['deleted_files'],0)
 def test_backup_retention_fails_closed_on_corrupt_keeper_and_journal_error(self):
  m=importlib.import_module('epg_cleanup93');old,keep=self.seed_backups();folder=self.folder/'guide_backups44'
  before=(folder/old['backup']).read_bytes()
  result=m.prune(journal=lambda v:(_ for _ in ()).throw(OSError('JOURNAL_DENIED')))
  self.assertEqual(result['code'],'RECOVERY_PROOF_BLOCKED');self.assertEqual((folder/old['backup']).read_bytes(),before)
  (folder/keep['backup']).write_bytes(b'CORRUPT');self.assertEqual(m.prune()['code'],'RECOVERY_PROOF_BLOCKED');self.assertTrue((folder/old['backup']).exists())
 def test_unknown_raw_local_xml_and_backup_are_never_deleted(self):
  m=importlib.import_module('epg_cleanup93');self.seed_backups();folder=self.folder/'guide_backups44'
  unknown=folder/'my-guide.sqlite';unknown.write_bytes(b'USER');local=self.folder/'epg.xml';local.write_text('<tv/>')
  m.prune();self.assertEqual(unknown.read_bytes(),b'USER');self.assertEqual(local.read_text(),'<tv/>')
 def test_lost_primary_stop_ack_requires_actual_later_native_fifo_progress(self):
  import xbmcgui,xbmc
  m=importlib.import_module('stop_barrier93');window=xbmcgui.Window(10000);window.clearProperty(m.ACK)
  value=dict(token=['live',dict(nonce='s')],native_posted=True,commands_enqueued93=True,worker_done=False,posted_at75=time.monotonic()-6)
  with mock.patch('exit_jobs.save'),mock.patch('exit_jobs.trace'),mock.patch.object(xbmc,'executebuiltin') as post:
   m.observe(value);m.observe(value)
  self.assertEqual(post.call_count,1);self.assertNotIn('Stop',post.call_args[0][0].replace(m.ACK,''));self.assertFalse(m.returned(value))
  window.setProperty(m.ACK,'wrong');self.assertFalse(m.returned(value))
  window.setProperty(m.ACK,value['progress_nonce93']);self.assertTrue(m.returned(value))
  self.assertFalse(m.returned(dict(value,commands_enqueued93=False)))
 def test_primary_ack_never_replaced_by_player_stopped_assumption(self):
  import xbmc
  m=importlib.import_module('stop_barrier93');v=dict(token=['live',{}],native_posted=True,worker_done=False,posted_at75=time.monotonic()-120)
  with mock.patch.object(xbmc,'executebuiltin') as post:m.observe(v)
  post.assert_not_called();self.assertFalse(m.returned(v))
 def test_exact_preview_handoff_rejects_changed_source_event_and_epoch(self):
  m=importlib.import_module('programme_preview67');event={'pid':'p','sid':'s','start':10,'stop':20,'title':'Galileo'};art=dict(code='READY',image='/tmp/fake')
  from programme_requests68 import identity
  with mock.patch('programme_image69.eligible',return_value=True),mock.patch('programme_lastgood80.file_valid',return_value=True):
   m._shared93[identity(event)]=(time.monotonic(),art)
   self.assertEqual(m.shared(event),art);self.assertEqual(m.shared(dict(event,source_key46='OTHER')),{})
   self.assertEqual(m.shared(dict(event,start=11)),{})
 def test_targeted_group_loads_137_channels_without_epg_or_waiting_full_catalog(self):
  m=importlib.import_module('live_group93');self.index.import_group('p','live','b',[dict(stream_id=str(100+i),name='4K '+str(i),category_id='b') for i in range(137)])
  nav=SimpleNamespace(portal=self.portal,xc=self.client,category_id='b',enabled={'a','b'})
  self.assertIsNone(m.rows(nav));task=nav._group_task93[1];task.result(3)
  rows=m.rows(nav);self.assertEqual(len(rows),137);self.assertTrue(all(r.extra['category_id']=='b' for r in rows))
  nav.category_id='disabled';self.assertIsNone(m.rows(nav))
 def test_busy_group_does_not_latch_false_empty_and_retries_are_bounded(self):
  m=importlib.import_module('live_group93');nav=SimpleNamespace(portal=self.portal,xc=self.client,category_id='b',enabled={'b'})
  with mock.patch('live_catalog46.read',side_effect=OSError('BUSY')) as read:
   self.assertIsNone(m.rows(nav))
   try:nav._group_task93[1].result(2)
   except OSError:pass
   self.assertIsNone(m.rows(nav))
   for _ in range(20):self.assertIsNone(m.rows(nav))
   self.assertEqual(read.call_count,1);self.assertGreater(nav._group_retry93,time.monotonic())
 def test_small_xmltv_image_survives_bingie_detail_policy_and_manual_lookup_failure(self):
  from media_sources43 import SourceError
  from programme_events46 import describe
  urls=importlib.import_module('programme_urls55')
  event=describe(self.portal,dict(sid='1',name='Station'),dict(title='Galileo',start=self.now-10,stop=self.now+600),'xml')
  event.update(xmltv_image='https://image.tmdb.org/t/p/w500/galileo.jpg',_detail93=True)
  # Use existing transport/cache pipeline; only the external lookup fails.
  import artwork_visible
  def dns(url):
   artwork_visible._dns_cache[('image.tmdb.org',443)]=(time.monotonic()+30,True);return True
  with mock.patch('artwork_visible.public_dns',side_effect=dns),mock.patch('home_schedule75.applicable',return_value=True),mock.patch('programme_mapping85.current',return_value={'id':1}),mock.patch('programme_candidates85.candidate',side_effect=SourceError('TIMEOUT')):
   value=urls.resolve(event,allow_lookup=True,url_mode69=True,check=lambda *a,**kw:dict(decoded77=True,width=320,height=180))
  self.assertEqual(value['source'],'xmltv_event');self.assertEqual(value['code'],'READY');self.assertEqual(value['source_url'],event['xmltv_image'])
  self.assertTrue(importlib.import_module('programme_image69').eligible(value,event))
 def test_detail_context_does_not_change_event_identity(self):
  m=importlib.import_module('programme_requests68');event=dict(pid='p',sid='1',title='Galileo',start=self.now,stop=self.now+100)
  self.assertEqual(m.identity(event),m.identity(dict(event,_detail93=True)))
 def test_120_simulated_stop_receipts_cannot_ack_early_or_repost(self):
  import xbmcgui,xbmc
  m=importlib.import_module('stop_barrier93');window=xbmcgui.Window(10000)
  with mock.patch('exit_jobs.save'),mock.patch('exit_jobs.trace'),mock.patch.object(xbmc,'executebuiltin') as post:
   for n in range(120):
    window.clearProperty(m.ACK)
    v=dict(token=['live',dict(nonce=str(n))],native_posted=True,commands_enqueued93=True,worker_done=False,posted_at75=time.monotonic())
    m.observe(v);self.assertFalse(v.get('progress_posted93'));self.assertFalse(m.returned(v))
    v['posted_at75']-=6;m.observe(v);m.observe(v)
    self.assertFalse(m.returned(v));window.setProperty(m.ACK,v['progress_nonce93']);self.assertTrue(m.returned(v))
   self.assertEqual(post.call_count,120);self.assertTrue(all('PlayerControl' not in c.args[0] for c in post.call_args_list))
 def test_open_backup_is_protected_and_resumes_after_handle_release(self):
  m=importlib.import_module('epg_cleanup93');old,keep=self.seed_backups();file=self.folder/'guide_backups44'/old['backup']
  with file.open('rb') as opened:
   self.assertTrue(opened.read(1));r=m.prune();self.assertEqual(r['deleted_files'],0);self.assertTrue(file.exists())
  r=m.prune();self.assertEqual(r['deleted_files'],1);self.assertFalse(file.exists())
 def test_detail_request_can_replace_home_quality_negative_without_waiting_its_ttl(self):
  q=importlib.import_module('programme_requests68');self.options.update(programme_tmdb46=True,tmdb_research43=True)
  from programme_policy68 import negative_scope
  event=dict(pid='p',sid='1',title='Galileo',start=self.now-10,stop=self.now+100,code='LOCAL_EVENT')
  q.status(event,'NO_IMAGE',dict(code='NO_IMAGE',source='placeholder',until=time.time()+300,policy69=negative_scope({})))
  self.assertTrue(q.request(dict(event,_detail93=True),priority=True))
  with mock.patch('programme_events46.load',return_value=event),mock.patch('programme_urls55.enqueue',return_value=True) as enqueue,mock.patch('programme_reference84.tick'),mock.patch('series_requests85.drain'),mock.patch('tmdb_token61.effective_tmdb_read_token',return_value='synthetic'):
   q.drain()
  enqueue.assert_called_once();self.assertTrue(enqueue.call_args.args[0]['_detail93'])
 def test_manual_mapping_never_falls_back_to_an_old_automatic_work(self):
  from programme_events46 import describe
  from media_sources43 import SourceError
  q=importlib.import_module('programme_urls55')
  event=describe(self.portal,dict(sid='1',name='Station'),dict(title='Galileo',start=self.now,stop=self.now+600),'xml');event['_detail93']=True
  old=dict(code='READY',source='tmdb_series',source_url='https://image.tmdb.org/t/p/w500/WRONG_WORK.jpg',fingerprint='WRONG',until=time.time()+300,match='EXACT_UNIQUE_TV_TITLE66')
  with mock.patch('programme_mapping85.current',return_value={'id':1}),mock.patch('programme_candidates85.candidate',side_effect=SourceError('TIMEOUT')),mock.patch('programme_index46.art',return_value=old),mock.patch('event_art81.prior',return_value=None),mock.patch.object(q,'probe',side_effect=AssertionError('old work fallback')):
   value=q.resolve(event,allow_lookup=True,url_mode69=True)
  self.assertNotEqual(value.get('source'),'tmdb_series')
 def test_malformed_backup_manifest_is_skipped_without_worker_exception(self):
  m=importlib.import_module('epg_cleanup93');old,keep=self.seed_backups();folder=self.folder/'guide_backups44'
  receipt=Path(str(folder/old['backup'])+'.json')
  for value in ([],None,{'sha256':17},'bad'):
   receipt.write_text(json.dumps(value));r=m.prune()
   self.assertEqual(r['deleted_files'],0);self.assertTrue((folder/old['backup']).exists())
