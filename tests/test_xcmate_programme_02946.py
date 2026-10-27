"""Shared local events and transactional rich metadata. No device/user data."""
import importlib,io,json,os,sqlite3,sys,time,unittest,contextlib,hashlib
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ADDON,LIB

class ProgrammeEvents46(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.store=importlib.import_module('programme_store46');self.events=importlib.import_module('programme_events46');self.guide=importlib.import_module('guide_store')
  self.channel=dict(sid='1',name='Example News',epg_channel_id='xml',kind='live',cover='')
  self.event=dict(channel='xml',name='Evening Report',descr='Saved local description',start_timestamp=self.now-60,stop_timestamp=self.now+600,_source_index=1)
 def save(self,**extra):
  e=dict(self.event,**extra);self.assertTrue(self.guide.import_cache('p',{'xml':[e]},'fixture46',now=self.now));return e
 def test_rich_source_facts_persist_in_separate_database_and_survive_restart(self):
  self.save(sub_title='Real episode',category='Series',screenshot_uri='https://images.invalid/episode.jpg',season=2,episode_number=3,year=2024,cast=['Actual actor'])
  value=self.events.load(self.portal,self.channel,now=self.now)
  self.assertEqual((value['subtitle'],value['season'],value['episode'],value['year'],value['cast']),('Real episode',2,3,2024,['Actual actor']))
  self.assertTrue(Path(self.store.path()).is_file());self.assertNotEqual(self.store.path(),self.guide.path());self.assertEqual(value['description'],'Saved local description')
  again=importlib.reload(self.events).load(self.portal,self.channel,now=self.now);self.assertEqual(again['key'],value['key']);self.assertEqual(again['xmltv_image'],value['xmltv_image'])
 def test_no_sidecar_for_plain_large_feed_records(self):
  self.save();self.assertFalse(Path(self.store.path()).exists());self.assertEqual(self.events.load(self.portal,self.channel,now=self.now)['title'],'Evening Report')
 def test_unpublished_metadata_never_visible(self):
  self.save();stage=self.store.Stage('p','uncommitted',1);stage.add(dict(self.event,screenshot_uri='https://bad.invalid/wrong.png'));stage.flush()
  value=self.events.load(self.portal,self.channel,now=self.now);self.assertNotIn('xmltv_image',value);stage.finish(False);self.assertNotIn('xmltv_image',self.events.load(self.portal,self.channel,now=self.now))
 def test_same_channel_id_different_sources_and_portals_do_not_cross(self):
  for pid,source,url in [('p',1,'https://a.invalid/1.png'),('p',2,'https://b.invalid/2.png'),('other',1,'https://other.invalid/3.png')]:
   stage=self.store.Stage(pid,pid+str(source),source);stage.add(dict(self.event,_source_index=source,screenshot_uri=url));stage.finish(True)
  e=dict(start=self.event['start_timestamp'],stop=self.event['stop_timestamp'],title=self.event['name'],source=2)
  self.assertEqual(self.store.read('p','xml',e)['xmltv_image'],'https://b.invalid/2.png');self.assertEqual(self.store.read('other','xml',dict(e,source=1))['xmltv_image'],'https://other.invalid/3.png')
 def test_title_interval_and_source_must_match_before_using_picture(self):
  self.save(screenshot_uri='https://a.invalid/exact.png');v=self.events.load(self.portal,self.channel,now=self.now)
  for changes in ({'title':'Different show'},{'start':v['start']+1},{'stop':v['stop']+1},{'source':2}):self.assertEqual(self.store.read('p','xml',dict(v,**changes)),{})
 def test_manual_mapping_wins_over_provider_and_stream_alias(self):
  self.save(screenshot_uri='https://a.invalid/wrong.png')
  import epg_sources
  self.guide.import_cache('p',{'manual':[dict(self.event,channel='manual',name='Manual source show',screenshot_uri='https://a.invalid/right.png')]},'second',now=self.now)
  with mock.patch.object(epg_sources,'configuration',return_value=dict(mappings={'1':'manual'})):v=self.events.load(self.portal,self.channel,now=self.now)
  self.assertEqual(v['title'],'Manual source show');self.assertEqual(v['xmltv_image'],'https://a.invalid/right.png')
 def test_missing_xmltv_has_neutral_readonly_offline_view(self):
  before=set(self.folder.iterdir());value=self.events.load(self.portal,self.channel,now=self.now)
  self.assertEqual(value['code'],'NO_EPG');self.assertTrue(Path(value['placeholder']).is_file());self.assertEqual(set(self.folder.iterdir()),before);sys.modules['utils'].http_get.assert_not_called()
 def test_details_reads_preserve_guide_bytes_schema_aliases_and_settings(self):
  self.save(category='News');before=Path(self.guide.path()).read_bytes();settings=dict(self.options)
  with sqlite3.connect(self.guide.path()) as db:schema=db.execute("SELECT sql FROM sqlite_master ORDER BY name").fetchall()
  for _ in range(20):self.events.load(self.portal,self.channel,now=self.now)
  self.assertEqual(Path(self.guide.path()).read_bytes(),before);self.assertEqual(self.options,settings)
  with sqlite3.connect(self.guide.path()) as db:self.assertEqual(db.execute("SELECT sql FROM sqlite_master ORDER BY name").fetchall(),schema)
 def test_sidecar_capacity_failure_never_rolls_back_epg_text(self):
  with mock.patch.object(self.store,'connect',side_effect=OSError('synthetic full')):self.save(category='News',screenshot_uri='https://a.invalid/a.jpg')
  self.assertEqual(self.events.load(self.portal,self.channel,now=self.now)['title'],'Evening Report')
 def test_event_key_changes_at_programme_boundary_and_is_portal_scoped(self):
  self.save();a=self.events.load(self.portal,self.channel,now=self.now)
  self.assertNotEqual(a['key'],self.events.key('foreign','1',a));self.assertNotEqual(a['key'],self.events.key('p','2',a));self.assertNotEqual(a['key'],self.events.key('p','1',dict(a,start=a['start']+1)))
 def test_stale_widget_detail_key_never_opens_another_programme(self):
  self.save();a=self.events.load(self.portal,self.channel,now=self.now)
  value=self.events.load(self.portal,self.channel,dict(start=a['start'],stop=a['stop'],key='f'*64),now=self.now);self.assertEqual(value['code'],'NO_EPG')
 def test_reading_existing_history_does_not_refresh_or_delete(self):
  self.save();old=dict(self.event,name='Yesterday',start_timestamp=self.now-86400,stop_timestamp=self.now-85000)
  self.guide.import_cache('p',{'xml':[old]},'past',now=self.now)
  value=self.events.load(self.portal,self.channel,dict(start=old['start_timestamp'],stop=old['stop_timestamp']),now=self.now)
  self.assertEqual(value['title'],'Yesterday');self.assertFalse(self.builtins)
 def test_legacy_loaded_rich_cache_only_used_for_exact_source_event(self):
  self.save();import epg
  with mock.patch.object(epg,'_mem_get',create=True,return_value={'xml':[dict(self.event,screenshot_uri='https://a.invalid/legacy.jpg')]}):self.assertEqual(self.events.load(self.portal,self.channel,now=self.now)['xmltv_image'],'https://a.invalid/legacy.jpg')
  with mock.patch.object(epg,'_mem_get',create=True,return_value={'xml':[dict(self.event,_source_index=2,screenshot_uri='https://wrong.invalid/legacy.jpg')]}):self.assertNotIn('xmltv_image',self.events.load(self.portal,self.channel,now=self.now))
 def test_sax_retains_real_episode_image_subtitle_date_cast_without_network(self):
  parser=importlib.import_module('xmltv_stream');rows=[]
  raw=b'<tv><channel id="xml"><display-name>Station</display-name><icon src="https://logo.invalid/station.png"/></channel><programme channel="xml" start="20261027200000 +0000" stop="20261027210000 +0000"><title>Series</title><sub-title>Episode title</sub-title><date>2024</date><category>Drama</category><credits><actor>Actor One</actor><actor>Actor Two</actor></credits><episode-num system="xmltv_ns">1.2.</episode-num><icon src="https://image.invalid/episode.png"/></programme></tv>'
  parser.parse(io.BytesIO(raw),lambda *a:None,rows.append)
  self.assertEqual((rows[0]['season'],rows[0]['episode_number'],rows[0]['sub_title'],rows[0]['date'],rows[0]['cast']),(2,3,'Episode title','2024',['Actor One','Actor Two']));self.assertEqual(rows[0]['screenshot_uri'],'https://image.invalid/episode.png')
 def test_failed_xml_source_does_not_publish_rich_metadata_or_replace_guide(self):
  self.save();import stream_epg
  raw=b'<tv><channel id="xml"><display-name>Station</display-name></channel><programme channel="xml" start="20261027200000 +0000" stop="20261027210000 +0000"><title>Changed</title><icon src="https://bad.invalid/a.png"/></programme><broken>'
  def snapshot():
   with sqlite3.connect(self.guide.path()) as db:return {table:db.execute('SELECT * FROM '+table+' ORDER BY 1,2,3').fetchall() for table in ('programmes','guide_meta','guide_alias','guide44_inputs')}
  before=snapshot()
  with mock.patch.object(sys.modules['epg_sources'],'_channel_name_key',create=True,side_effect=lambda v:str(v).casefold()),mock.patch.object(stream_epg,'source_stream',return_value=contextlib.nullcontext(io.BytesIO(raw))):
   with self.assertRaises(__import__('xmltv_stream').XMLTVSyntaxError):stream_epg.import_source('p',dict(uri='https://unused.invalid/feed'),1,[self.channel],{})
  self.assertEqual(snapshot(),before)
 def test_committed_stream_generation_publishes_metadata_only_after_guide_commit(self):
  self.save();import stream_epg
  def stamp(t):return time.strftime('%Y%m%d%H%M%S +0000',time.gmtime(t))
  raw=('<tv><channel id="xml"><display-name>Station</display-name></channel><programme channel="xml" start="'+stamp(self.now-60)+'" stop="'+stamp(self.now+600)+'"><title>New committed show</title><desc>New text</desc><icon src="https://a.invalid/exact.png"/><sub-title>Actual episode</sub-title></programme></tv>').encode()
  with mock.patch.object(sys.modules['epg_sources'],'_channel_name_key',create=True,side_effect=lambda v:str(v).casefold()),mock.patch.object(stream_epg,'source_stream',return_value=contextlib.nullcontext(io.BytesIO(raw))):stage=stream_epg.import_source('p',dict(id='source-A',uri='https://unused.invalid/feed'),1,[self.channel],{},stage_only=True)
  self.assertEqual(self.events.load(self.portal,self.channel,now=self.now)['title'],'Evening Report')
  stream_epg.publish_stages44('p',[stage]);value=self.events.load(self.portal,self.channel,now=self.now)
  self.assertEqual(value['title'],'New committed show');self.assertEqual(value['xmltv_image'],'https://a.invalid/exact.png');self.assertTrue(value['epg_source46'].startswith('external:'))
 def test_ambiguous_source_archive_never_guesses_an_episode_picture(self):
  self.save(screenshot_uri='https://a.invalid/source-A.png')
  db=self.guide.connect(write=True)
  try:
   with db:db.execute('INSERT INTO guide44_inputs VALUES(?,?,?,?,?,?,?,?)',('p','external:another','xml',self.event['start_timestamp'],self.event['stop_timestamp'],self.event['name'],self.event['descr'],1))
  finally:db.close()
  value=self.events.load(self.portal,self.channel,now=self.now)
  self.assertEqual(value['title'],'Evening Report');self.assertEqual(value['metadata_code46'],'SOURCE_AMBIGUOUS_OR_BUDGET');self.assertNotIn('xmltv_image',value)
 def test_conflicting_same_slot_metadata_must_match_authoritative_description(self):
  self.save(screenshot_uri='https://correct.invalid/first.png')
  stage=self.store.Stage('p','different-episode',1);stage.add(dict(self.event,descr='Another episode description',episode_number=8,season=1,screenshot_uri='https://wrong.invalid/episode.png'));stage.finish(True)
  value=self.events.load(self.portal,self.channel,now=self.now);self.assertEqual(value['metadata_code46'],'TEXT_IDENTITY_MISMATCH');self.assertNotIn('xmltv_image',value)
 def test_legacy_guide_without_verified_backup_refuses_import_before_new_metadata(self):
  filename=self.folder/'legacy.sqlite'
  with sqlite3.connect(filename) as db:db.execute('CREATE TABLE programmes(pid TEXT,cid TEXT,start INTEGER,stop INTEGER,title TEXT,description TEXT,source INTEGER)')
  before=filename.read_bytes();from guide_publish44 import BackupRequired
  with self.assertRaises(BackupRequired):self.guide.import_cache('p',{'xml':[dict(self.event,screenshot_uri='https://a.invalid/x.png')]},filename=str(filename))
  self.assertEqual(filename.read_bytes(),before);self.assertFalse(Path(self.store.path(str(filename))).exists())
