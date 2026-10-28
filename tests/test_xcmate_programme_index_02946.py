"""#241 architecture addendum: actual shared WAL SQLite, 7 calendar days/+20.

Synthetic local files only. No device, feed download, reset or Android PASS.
"""
import contextlib,datetime,hashlib,importlib,io,json,os,sqlite3,sys,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ADDON


class ProgrammeIndex46(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.db=importlib.import_module('programme_index46');self.guide=importlib.import_module('guide_store');self.events=importlib.import_module('programme_events46')
  self.channel=dict(sid='1',name='Station',epg_channel_id='xml',kind='live')
 def item(self,day=0,title='Actual programme',**extra):
  start=self.guide.day_window(day,self.now)[0]+12*3600
  if day==0:start=self.now-60
  return dict(channel='xml',name=title,descr='Stored details '+title,start_timestamp=start,stop_timestamp=start+1800,**extra)
 def populate(self,rows=None):
  rows=rows if rows is not None else [self.item(0),self.item(20,'Day20',category='Series',season=2,episode_number=3,sub_title='Actual episode',screenshot_uri='https://images.invalid/day20.png')]
  self.assertTrue(self.guide.import_cache('p',{'xml':rows},'snapshot46',now=self.now));return rows
 def rows(self):
  db=self.db.connect(False)
  if db is None:return []
  try:return db.execute('SELECT cid,start,stop,titlehash,source_id,fingerprint,updated FROM facts ORDER BY start').fetchall()
  finally:db.close()
 def test_readonly_missing_cache_never_creates_database(self):
  self.assertIsNone(self.db.connect(False));self.assertEqual(self.db.window('p','xml',self.now,self.now+100),[])
  self.assertFalse(Path(self.db.path()).exists())
 def test_real_20day_feed_is_preserved_separately_without_extending_primary_guide(self):
  rows=self.populate();db=sqlite3.connect(self.guide.path())
  # .52 removes the obsolete ten-day master cap; same two retained events in both stores.
  self.assertEqual(db.execute('SELECT count(*) FROM programmes').fetchone()[0],2);db.close()
  self.assertEqual(len(self.rows()),2);before=Path(self.guide.path()).read_bytes()
  from local_epg import window
  result=window('p',[self.channel],{},rows[1]['start_timestamp'],rows[1]['stop_timestamp'])
  self.assertEqual(result['xml'][0]['name'],'Day20');self.assertEqual(Path(self.guide.path()).read_bytes(),before)
  self.assertEqual(self.db.available_days('p'),21)
 def test_large_grid_and_detail_use_same_actual_day20_record_and_episode(self):
  rows=self.populate();origin=rows[1]['start_timestamp']
  page=importlib.import_module('guide_grid_data').page(self.portal,0,origin,category='a')
  event=page['rows'][0]['events'][0];self.assertEqual(event['title'],'Day20')
  selected=self.events.load(self.portal,self.channel,event)
  self.assertEqual((selected['title'],selected['season'],selected['episode'],selected['subtitle']),('Day20',2,3,'Actual episode'))
 def test_sparse_later_source_result_never_deletes_other_future_events(self):
  rows=self.populate();future=self.rows()[1]
  self.guide.import_cache('p',{'xml':[self.item(0,'Updated current')]},'next',now=self.now)
  self.assertEqual(next(r for r in self.rows() if r[1]==rows[1]['start_timestamp']),future)
 def test_identical_feed_keeps_fact_fingerprint_and_updated_timestamp(self):
  rows=self.populate();before=self.rows();self.guide.import_cache('p',{'xml':rows},'snapshot46',now=self.now)
  self.assertEqual(self.rows(),before)
 def test_updating_one_feed_event_keeps_other_event_cache_unchanged(self):
  rows=self.populate();before=self.rows();changed=dict(rows[1],name='Corrected episode',descr='Corrected text')
  self.guide.import_cache('p',{'xml':[rows[0],changed]},'changed',now=self.now);after=self.rows()
  self.assertEqual(after[0],before[0]);self.assertNotEqual(after[1][3],before[1][3]);self.assertNotEqual(after[1][5],before[1][5])
 def test_history_includes_seven_complete_local_calendar_days_and_no_eighth(self):
  rows=[self.item(-8,'Too old'),self.item(-7,'Oldest full day'),self.item(0),self.item(20,'Last future'),self.item(21,'Too far')]
  self.populate(rows);data=self.rows();self.assertEqual(len(data),3)
  left,right=self.db.bounds();values=self.db.window('p','xml',left-86400,right+86400)
  self.assertEqual({v['name'] for v in values},{'Oldest full day','Actual programme','Last future'})
 def test_calendar_bounds_obey_berlin_dst_without_rolling_168hour_cutoff(self):
  old=os.environ.get('TZ')
  try:
   os.environ['TZ']='Europe/Berlin';time.tzset();now=time.mktime((2026,10,27,12,0,0,0,0,-1));left,right=self.db.bounds(now)
   self.assertEqual(datetime.date.fromtimestamp(left),datetime.date(2026,10,20));self.assertEqual(datetime.date.fromtimestamp(right),datetime.date(2026,11,17))
   self.assertEqual(int(now-self.guide.day_window(0,now)[0]),12*3600)
   self.assertEqual(self.guide.day_window(0,now)[0]-left,7*86400+3600)
  finally:
   if old is None:os.environ.pop('TZ',None)
   else:os.environ['TZ']=old
   time.tzset()
 def test_uncommitted_or_cancelled_source_stage_is_invisible(self):
  raw=self.item();stage=self.db.Stage('p','new');stage.add(raw,{},'provider');stage.flush()
  self.assertEqual(self.rows(),[]);self.db.finish('p','new',False);self.assertEqual(self.rows(),[])
 def test_wal_commit_and_transaction_rollback_keep_lastgood_after_interruption(self):
  self.populate();before=self.rows();db=self.db.connect(True);self.assertEqual(db.execute('PRAGMA journal_mode').fetchone()[0],'wal')
  db.execute("UPDATE facts SET fingerprint='not-committed'");db.close();self.assertEqual(self.rows(),before)
 def test_two_sources_same_channel_id_remain_distinct_and_follow_real_priority(self):
  cfg=sys.modules['epg_sources'];cfg.configuration=lambda pid:dict(mappings={},sources=[dict(id='one',enabled=True),dict(id='two',enabled=True)])
  source_id=importlib.import_module('guide_publish44').source_id
  for number,title in ((1,'First'),(2,'Second')):
   stage=self.db.Stage('p',str(number));stage.add(self.item(20,title),{},source_id(dict(id=('one','two')[number-1]),number));stage.flush();self.db.finish('p',str(number),True)
  left,right=self.guide.day_window(20);values=self.db.window('p','xml',left,right);self.assertEqual(values[0]['name'],'First');self.assertEqual(len(self.rows()),2)
 def test_manual_mapping_wins_for_day20_and_missing_mapping_has_no_provider_fallback(self):
  self.populate();from local_epg import window
  start,stop=self.guide.day_window(20)
  self.assertEqual(window('p',[self.channel],{'1':'not-present'},start,stop)['not-present'],[])
  self.assertEqual(window('p',[self.channel],{'1':'xml'},start,stop)['xml'][0]['name'],'Day20')
 def test_shared_prepared_event_is_read_by_widget_and_programme_details(self):
  self.populate();event=self.events.load(self.portal,self.channel);self.assertTrue(self.db.publish([event]))
  from local_epg import now_next
  info=now_next('p',[self.channel],{})['1'];widget=importlib.import_module('widget_items45').describe(self.portal,'live',self.channel,{},info)
  detail=self.events.load(self.portal,self.channel)
  self.assertEqual(widget['props']['XCMate.ProgrammeKey46'],detail['key']);self.assertEqual(detail['description'],event['description'])
  record=self.db.event(detail);self.assertEqual(record['key'],detail['key'])
 def test_art_record_has_source_confidence_local_thumbnail_ttl_and_version(self):
  self.populate();event=self.events.load(self.portal,self.channel);event['xmltv_image']='https://images.invalid/actual.png'
  art=importlib.import_module('programme_art46');from test_xcmate_media_choices_02943 import image
  Path(art.root()).mkdir(exist_ok=True)
  with mock.patch.object(art,'space'):value=art.prepare(event,fetch=lambda *a,**k:image(),match=lambda *a,**k:None)
  self.assertEqual(value['code'],'READY');record=self.db.art(event)
  self.assertEqual(record['thumbnail'],record['image']);self.assertEqual(record['match'],'EXACT_EVENT');self.assertEqual(record['source_url'],event['xmltv_image'])
  db=self.db.connect(False)
  try:self.assertEqual(db.execute('SELECT version FROM artwork').fetchone()[0],1)
  finally:db.close()
  self.assertFalse((Path(art.root())/(event['key']+'.json')).exists())
 def test_portrait_source_is_letterboxed_to_true_16by9_without_baked_logo(self):
  from PIL import Image
  out=io.BytesIO();Image.new('RGB',(300,600),(200,20,30)).save(out,'PNG')
  data=importlib.import_module('programme_art46').display_image(out.getvalue())
  with Image.open(io.BytesIO(data)) as result:
   self.assertEqual(result.width*9,result.height*16);self.assertEqual(result.getpixel((0,0)),(18,29,43));self.assertEqual(result.getpixel((result.width//2,result.height//2)),(200,20,30))
 def test_identical_verified_image_is_reused_across_events_without_network_or_new_file(self):
  self.populate();art=importlib.import_module('programme_art46');from test_xcmate_media_choices_02943 import image
  Path(art.root()).mkdir(exist_ok=True)
  first=dict(self.events.load(self.portal,self.channel),xmltv_image='https://images.invalid/shared.png')
  second=dict(first,start=first['stop'],stop=first['stop']+1800,title='Next declared event');second['key']=self.events.key('p','1',second)
  with mock.patch.object(art,'space'):
   one=art.prepare(first,fetch=lambda *a,**k:image(),match=lambda *a,**k:None)
   with mock.patch('media_sources43.get',side_effect=AssertionError('same verified URL already local')):two=art.prepare(second,match=lambda *a,**k:None)
  self.assertEqual(one['image'],two['image']);self.assertEqual(one['until'],two['until']);self.assertNotEqual(one['key'],two['key'])
 def test_local_backfill_reads_existing_guide_without_modifying_it(self):
  self.populate();before=Path(self.guide.path()).read_bytes();self.assertTrue(self.db.prepare_local(self.portal))
  self.assertEqual(Path(self.guide.path()).read_bytes(),before);self.assertFalse(self.db.prepare_local(self.portal))
 def test_stale_fact_metadata_cannot_survive_source_image_revision(self):
  rows=self.populate();start,stop=rows[1]['start_timestamp'],rows[1]['stop_timestamp']
  old=self.events.load(self.portal,self.channel,dict(start=start,stop=stop));self.db.event(old,write=True)
  changed=dict(rows[1],screenshot_uri='https://images.invalid/new.png');self.guide.import_cache('p',{'xml':[rows[0],changed]},'image-updated',now=self.now)
  current=self.events.load(self.portal,self.channel,dict(start=start,stop=stop))
  self.assertEqual(current['xmltv_image'],changed['screenshot_uri']);self.assertNotEqual(current['fact_revision46'],old['fact_revision46'])
 def test_abrupt_writer_process_exit_rolls_back_without_losing_published_rows(self):
  import subprocess
  self.populate();before=self.rows()
  code="import sqlite3,sys,os; d=sqlite3.connect(sys.argv[1]); d.execute(\"UPDATE facts SET fingerprint='uncommitted-crash'\"); os._exit(23)"
  result=subprocess.run([sys.executable,'-c',code,self.db.path()],timeout=5)
  self.assertEqual(result.returncode,23);self.assertEqual(self.rows(),before)
 def test_concurrent_wal_reader_sees_committed_snapshot_not_writer_changes(self):
  self.populate();before=self.rows();writer=self.db.connect(True)
  try:
   writer.execute("UPDATE facts SET fingerprint='not-committed'");self.assertEqual(self.rows(),before)
  finally:writer.rollback();writer.close()
 def test_cache_storage_failure_preserves_primary_guide_and_never_claims_publish(self):
  self.populate();before=Path(self.guide.path()).read_bytes()
  with mock.patch.object(self.db,'connect',side_effect=OSError(28,'synthetic ENOSPC')):
   self.assertFalse(self.db.publish([self.events.describe(self.portal,self.channel)]))
  self.assertEqual(Path(self.guide.path()).read_bytes(),before)
 def test_real_stream_parser_captures_day20_before_legacy_ten_day_filter(self):
  from xml.sax.saxutils import escape
  stream=importlib.import_module('stream_epg');sys.modules['epg_sources']._channel_name_key=lambda s:s.casefold()
  rows=[self.item(0),self.item(20,'Actual future episode')]
  def stamp(t):return time.strftime('%Y%m%d%H%M%S +0000',time.gmtime(t))
  raw='<tv><channel id="xml"><display-name>Station</display-name></channel>'+''.join('<programme channel="xml" start="'+stamp(v['start_timestamp'])+'" stop="'+stamp(v['stop_timestamp'])+'"><title>'+escape(v['name'])+'</title></programme>' for v in rows)+'</tv>'
  @contextlib.contextmanager
  def source(*a,**k):yield io.BytesIO(raw.encode())
  with mock.patch.object(stream,'source_stream',source):stream.import_source('p',dict(uri='https://synthetic.invalid/feed'),0,[self.channel],{})
  self.assertEqual(len(self.rows()),2)
  db=sqlite3.connect(self.guide.path())
  try:self.assertEqual(db.execute('SELECT count(*) FROM programmes').fetchone()[0],2)
  finally:db.close()
 def test_day_guide_can_open_real_day20_and_uses_cache_coverage(self):
  self.populate();module=importlib.import_module('guide_window')
  window=module.GuideWindow('XCMateGuide.xml',str(ADDON),'Default','720p');window.configure(self.router,self.portal);self.addCleanup(window.close);window.show();self.settle(window)
  self.assertEqual(window.days,21);window.day=20;window._load_events(0);self.settle(window)
  self.assertEqual(window.programmes[0]['title'],'Day20');self.assertEqual(window.event_total,1)
 def test_day20_without_actual_feed_data_stays_empty_not_fabricated(self):
  self.populate([self.item(0)]);start,stop=self.guide.day_window(20)
  self.assertEqual(self.db.window('p','xml',start,stop),[]);self.assertLess(self.db.available_days('p'),21)
 def test_unknown_database_at_cache_path_is_not_migrated_or_rewritten(self):
  path=self.db.path();db=sqlite3.connect(path);db.execute('CREATE TABLE private_original(value TEXT)');db.execute("INSERT INTO private_original VALUES('preserve')");db.commit();db.close();before=Path(path).read_bytes()
  with self.assertRaises(ValueError):self.db.connect(True)
  self.assertEqual(Path(path).read_bytes(),before);self.assertEqual(self.db.status()['code'],'BLOCKED_SCHEMA')
 def test_failed_local_backfill_neither_advances_cursor_nor_retries_every_tick(self):
  self.populate();key=(self.guide.path(),'p');self.db._scans.pop(key,None)
  with mock.patch.object(self.db,'connect',side_effect=OSError(28,'synthetic full cache')):
   self.assertFalse(self.db.prepare_local(self.portal))
  self.assertNotIn(key,self.db._scans)
  with mock.patch.object(self.db.sqlite3,'connect',side_effect=AssertionError('retry during cache backoff')):self.assertFalse(self.db.prepare_local(self.portal))
 def test_unchanged_prepared_page_does_not_rewrite_event_or_negative_ttl(self):
  self.populate();event=self.events.load(self.portal,self.channel);art=importlib.import_module('programme_art46');art.enqueue(event);self.db.publish([event])
  db=self.db.connect(False)
  try:before=(db.execute('SELECT updated FROM events').fetchall(),db.execute('SELECT checked,expires FROM artwork').fetchall())
  finally:db.close()
  art._memory.clear();art.enqueue(event);self.db.publish([event]);db=self.db.connect(False)
  try:after=(db.execute('SELECT updated FROM events').fetchall(),db.execute('SELECT checked,expires FROM artwork').fetchall())
  finally:db.close()
  self.assertEqual(after,before)
 def test_changed_tmdb_opt_in_invalidates_only_relevant_negative_policy(self):
  self.populate();event=self.events.load(self.portal,self.channel);art=importlib.import_module('programme_art46');before=art.fingerprint(event)
  self.options.update(programme_tmdb46=True,tmdb_research43=True,tmdb_read_token43='private-user-token')
  self.assertNotEqual(art.fingerprint(event),before);self.assertNotIn('private-user-token',art.fingerprint(event))
 def test_prepared_current_dto_is_actually_used_without_rebuilding_sidecar_metadata(self):
  self.populate();event=self.events.load(self.portal,self.channel);self.assertTrue(self.db.publish([event]))
  with mock.patch.object(self.db,'metadata',side_effect=AssertionError('prepared DTO should be read')),mock.patch('programme_store46.read',side_effect=AssertionError('no metadata reconstruction')):
   current=self.events.load(self.portal,self.channel)
  self.assertEqual(current['key'],event['key']);self.assertEqual(current['description'],event['description'])
