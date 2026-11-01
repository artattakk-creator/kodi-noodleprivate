"""Real local 88-channel cold coverage and safe full-source publication."""
import contextlib,importlib,io,json,sqlite3,sys,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
import test_xcmate_epg_02952 as data52
class Coverage66(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.guide=importlib.import_module('guide_store');self.local=importlib.import_module('local_epg')
  self.rows=[dict(sid=str(i),name='Fixture channel '+str(i),epg_channel_id='xml'+str(i),category_id='a',kind='live') for i in range(88)]
  self.config=dict(sources=[],mappings={});sys.modules['epg_sources'].configuration=lambda pid:self.config
 def populate(self):
  cache={r['epg_channel_id']:[dict(channel=r['epg_channel_id'],name='Now '+r['sid'],descr='Actual stored fixture',start_timestamp=self.now-60,stop_timestamp=self.now+600),dict(channel=r['epg_channel_id'],name='Next '+r['sid'],descr='Next stored fixture',start_timestamp=self.now+600,stop_timestamp=self.now+1200)] for r in self.rows}
  self.assertTrue(self.guide.import_cache('p',cache,'fixture66',now=self.now,trusted_feed=True))
 def test_all_88_never_focused_channels_are_served_from_persistent_guide_offline(self):
  self.populate();before=Path(self.guide.path()).read_bytes();infos={}
  with mock.patch('urllib.request.urlopen',side_effect=AssertionError('GUI_NETWORK')):
   for i in range(0,88,16):infos.update(self.local.now_next('p',self.rows[i:i+16],{},now=self.now,display_only65=True))
  self.assertEqual(len(infos),88)
  for row in self.rows:
   self.assertEqual(infos[row['sid']]['now'],'Now '+row['sid']);self.assertEqual(infos[row['sid']]['next'],'Next '+row['sid'])
  self.assertEqual(Path(self.guide.path()).read_bytes(),before)
 def test_whole_start_group_warms_before_artwork_cursor_and_without_focus(self):
  self.populate();coverage=importlib.import_module('epg_coverage66');coverage._seen.clear()
  with mock.patch('urllib.request.urlopen',side_effect=AssertionError('WARM_NETWORK')):
   self.assertTrue(coverage.warm(self.portal,self.rows));self.assertFalse(coverage.warm(self.portal,self.rows))
  from epg_handoff63 import get
  for row in self.rows:self.assertEqual(get('p',row['sid'],now=self.now,mappings={})['now'],'Now '+row['sid'])
 def test_three_configured_sources_import_all_88_before_any_focus(self):
  import contextlib,io
  stream=importlib.import_module('stream_epg');sys.modules['epg_sources']._channel_name_key=lambda name:str(name).casefold()
  stamp=lambda value:time.strftime('%Y%m%d%H%M%S +0000',time.gmtime(value))
  for index,ids in ((0,range(44)),(1,range(44,87)),(2,range(87,88))):
   xml='<tv>'+''.join('<channel id="xml'+str(i)+'"><display-name>Fixture channel '+str(i)+'</display-name></channel><programme channel="xml'+str(i)+'" start="'+stamp(self.now-60)+'" stop="'+stamp(self.now+600)+'"><title>Imported '+str(i)+'</title></programme><programme channel="xml'+str(i)+'" start="'+stamp(self.now+600)+'" stop="'+stamp(self.now+1200)+'"><title>Next '+str(i)+'</title></programme>' for i in ids)+'</tv>'
   @contextlib.contextmanager
   def source(*a,**k):yield io.BytesIO(xml.encode())
   with mock.patch.object(stream,'source_stream',source):
    stream.import_source('p',dict(id='source-'+str(index),uri='https://fixture.invalid/source'),index,self.rows,{})
  infos={}
  for offset in range(0,88,16):infos.update(self.local.now_next('p',self.rows[offset:offset+16],{},now=self.now,display_only65=True))
  self.assertEqual(len(infos),88)
  self.assertEqual({sid:value['now'] for sid,value in infos.items()},{str(i):'Imported '+str(i) for i in range(88)})
 def test_utc_offsets_keep_repeated_dst_wall_clock_times_distinct(self):
  from epg import _parse_xmltv_ts
  one=_parse_xmltv_ts('20261025023000 +0200');two=_parse_xmltv_ts('20261025023000 +0100')
  self.assertEqual(two-one,3600)
 def test_mapping_and_profile_invalidation_cannot_reuse_another_sender(self):
  self.populate();mappings={'7':'xml8'}
  info=self.local.now_next('p',[self.rows[7]],mappings,now=self.now,display_only65=True)['7']
  self.assertEqual(info['now'],'Now 8')
  other=self.local.now_next('another',[self.rows[7]],{},now=self.now,display_only65=True)['7']
  self.assertFalse(other.get('now'))
 def test_precise_missing_event_codes_do_not_fabricate_programmes(self):
  classify=importlib.import_module('epg_coverage66').classify
  cases=[({},False,None,None,'UNMAPPED'),({},True,None,None,'SOURCE_EMPTY'),({},True,self.now-1000,self.now-1,'STALE'),({},True,self.now+100,self.now+500,'EVENT_OUT_OF_WINDOW')]
  for info,mapped,first,last,code in cases:self.assertEqual(classify(info,mapped,first,last,self.now),code)
  self.assertEqual(classify({},True,now=self.now,readable=False),'DB_UNAVAILABLE')
 def test_report_is_readonly_and_covers_every_active_channel(self):
  self.populate();before=Path(self.guide.path()).read_bytes()
  rows=importlib.import_module('epg_coverage66').report(self.portal,self.rows,now=self.now)
  self.assertEqual(len(rows),88);self.assertEqual({r['code'] for r in rows},{'READY'})
  self.assertEqual(Path(self.guide.path()).read_bytes(),before)
class Publication66(unittest.TestCase):
 def setUp(self):
  self.m=data52.EPG52(methodName='runTest');self.m.setUp();self.addCleanup(self.m.doCleanups)
 def test_source_receipt_has_actual_normalized_revision_counts_and_horizon(self):
  counts=self.m.put('a',[self.m.event(),self.m.event(2)],1)
  self.assertEqual(counts['mapped_channels66'],1);self.assertEqual(counts['stored_unique66'],2)
  self.assertEqual(len(counts['revision66']),64);self.assertGreater(counts['max_end66'],self.m.now+86400);self.assertLess(counts['max_end66'],self.m.now+3*86400)
 def test_verified_same_source_time_correction_keeps_other_valid_events(self):
  old=self.m.event(title='MacGyver fixture',description='Unique episode identity fixture')
  future=self.m.event(2,'Other valid programme');self.m.put('a',[old,future],1)
  changed=dict(old,start=old['start']+120,stop=old['stop']+120)
  result=self.m.put('a',[changed],1);rows=self.m.master()
  self.assertEqual(len(rows),2);self.assertEqual(rows[0][1:3],(changed['start'],changed['stop']));self.assertEqual(rows[1][3],'Other valid programme');self.assertGreaterEqual(result['corrected'],1)
 def test_short_or_ambiguous_description_does_not_shift_published_slot(self):
  old=self.m.event(title='Repeated episode',description='Generic')
  self.m.put('a',[old],1);before=self.m.master()
  self.m.put('a',[dict(old,start=old['start']+120,stop=old['stop']+120)],1)
  self.assertEqual(self.m.master(),before)
 def test_adjacent_same_title_episodes_are_distinct_and_not_collapsed(self):
  one=self.m.event(title='MacGyver',description='First legitimate episode')
  two=dict(one,start=one['stop'],stop=one['stop']+1800,description='Second legitimate episode')
  self.m.put('a',[one,two],1);self.assertEqual(len(self.m.master()),2)
 def test_failed_source_does_not_erase_committed_multisource_guide(self):
  self.m.put('a',[self.m.event()],1);before=self.m.master()
  @contextlib.contextmanager
  def broken(*a,**k):yield io.BytesIO(b'<tv><programme')
  with mock.patch.object(self.m.stream,'source_stream',broken):
   with self.assertRaises(Exception):self.m.stream.import_source('p',dict(self.m.config['sources'][1]),2,[self.m.channel],{})
  self.assertEqual(self.m.master(),before)
 def test_cancelled_time_correction_rolls_back_every_published_row(self):
  old=self.m.event(title='Episode',description='Unique episode identity fixture')
  self.m.put('a',[old],1);before=self.m.master()
  db=sqlite3.connect(self.m.g.path());generation='a'*32
  try:
   db.execute('INSERT INTO xml_stage VALUES(?,?,?,?,?,?)',(generation,'a',old['start']+120,old['stop']+120,old['title'],old['description']));db.commit()
   from guide_publish44 import publish,source_id
   calls=[0]
   def cancel():calls[0]+=1;return calls[0]>=3
   with self.assertRaises(InterruptedError):
    with db:publish(db,'p','xml_stage','generation=?',(generation,),source=source_id(self.m.config['sources'][0],1),rank=1,correct_times66=True,cancel=cancel)
  finally:db.close()
  self.assertEqual(self.m.master(),before)
 def test_shared_database_time_cannot_certify_multiple_undated_sources(self):
  self.m.put('a',[self.m.event()],1);self.m.put('a',[self.m.event(2)],2)
  self.assertEqual(importlib.import_module('epg_source66').restart_anchors('p'),{})
