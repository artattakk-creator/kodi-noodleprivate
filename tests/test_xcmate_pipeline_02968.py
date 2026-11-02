"""Visible-event producer, exact source isolation, UI and storage regressions."""
import importlib,json,sqlite3,sys,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture

class Pipeline68(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp()
  for name in ('programme_requests68','live_group68','live_warm68','programme_storage68','programme_settings68','programme_urls55'):
   sys.modules.pop(name,None)
  import programme_requests68
  self.b=programme_requests68
 def event(self,**values):
  e=dict(pid='p',sid='1',title='Synthetic Programme',start=self.now-60,stop=self.now+3600,canonical='a',revision=['guide',1],epg_source46='provider',source_key46='provider')
  e.update(values);return e
 def test_ui_intent_and_status_do_no_disk_sql_or_network(self):
  e=self.event()
  with mock.patch('builtins.open',side_effect=AssertionError('GUI_FILE')),mock.patch('sqlite3.connect',side_effect=AssertionError('GUI_SQL')),mock.patch('media_sources43.get',side_effect=AssertionError('GUI_HTTP')):
   self.assertTrue(self.b.request(e,priority=True));self.assertEqual(self.b.result(e),{})
  self.assertTrue(any('request.' in k for k in self.properties))
 def test_all_intents_are_bounded_to_64_slots(self):
  for i in range(1000):self.b.request(self.event(sid=str(i)),priority=True)
  requests=[v for k,v in self.properties.items() if 'Programme68.request.' in k]
  self.assertLessEqual(len(requests),64);self.assertTrue(all(len(v.encode())<=8192 for v in requests))
 def test_invalid_event_never_enqueues(self):
  for event in ({},self.event(stop=0),self.event(title=''),self.event(title='x'*2048)):
   self.assertFalse(self.b.request(event))
  self.assertEqual(self.properties,{})
 def test_completion_is_exact_source_revision_and_profile_scoped(self):
  e=self.event()
  art=dict(code='READY',source='tmdb_series',image='/synthetic/valid.png',until=time.time()+60)
  self.b.completed(e,art);self.assertEqual(self.b.result(e)['status68'],'LOCAL_IMAGE_READY')
  for other in (self.event(sid='2'),self.event(source_key46='external:other'),self.event(revision=['guide',2])):
   self.assertEqual(self.b.result(other),{})
  with mock.patch('programme_requests68.scope',return_value='different-profile'):self.assertEqual(self.b.result(e),{})
 def test_completion_never_publishes_private_source_urls(self):
  self.b.completed(self.event(),dict(code='HTTP_AUTH',source='placeholder',source_url='https://SECRET@private.invalid',token='SECRET'))
  self.assertNotIn('SECRET',str(self.properties));self.assertNotIn('private.invalid',str(self.properties))
 def test_placeholder_never_reports_success(self):
  self.b.completed(self.event(),dict(code='NO_MATCH',source='placeholder',image='/placeholder.png'))
  self.assertEqual(self.b.result(self.event())['code'],'NO_MATCH')
 def test_expired_local_image_is_not_reblessed(self):
  self.b.completed(self.event(),dict(code='READY',source='tmdb_series',image='/synthetic/old.png',until=time.time()-1))
  self.assertEqual(self.b.result(self.event())['code'],'CACHE_MISMATCH')
 def test_worker_reloads_local_event_and_enqueues_outside_home_start_group(self):
  e=self.event(sid='outside-home');self.b.request(e,priority=True)
  current=dict(e,code='LOCAL_EVENT',key='event',placeholder='/synthetic/placeholder.png')
  reader=types.SimpleNamespace(get=lambda kind,sid:dict(sid=sid,name='Other group',category_id='b'),close=lambda:None)
  self.options.update(programme_tmdb46=True,tmdb_research43=True)
  with mock.patch('library_index.Reader',return_value=reader),mock.patch('programme_events46.load',return_value=current),mock.patch('tmdb_token61.effective_tmdb_read_token',return_value=''),mock.patch('programme_urls55.enqueue',return_value=True) as enqueue:
   self.assertEqual(self.b.drain(),1)
   self.b.drain()
  enqueue.assert_called_once_with(current,allow_lookup=True,local_image63=True,priority68=True)
 def test_stale_event_binding_cannot_enqueue_another_source(self):
  e=self.event();self.b.request(e)
  reader=types.SimpleNamespace(get=lambda *a:dict(sid='1'),close=lambda:None)
  wrong=dict(e,code='LOCAL_EVENT',canonical='other')
  with mock.patch('library_index.Reader',return_value=reader),mock.patch('programme_events46.load',return_value=wrong),mock.patch('tmdb_token61.effective_tmdb_read_token',return_value=''),mock.patch('programme_urls55.enqueue') as enqueue:
   self.b.drain()
  enqueue.assert_not_called();self.assertEqual(self.b.result(e)['code'],'CACHE_MISMATCH')
 def test_worker_cancellation_never_reads_catalogue(self):
  self.b.request(self.event())
  with mock.patch('library_index.Reader',side_effect=AssertionError('CANCELLED_SQL')):self.assertEqual(self.b.drain(lambda:True),0)
 def test_queue_priority_promotes_existing_job_without_duplicate(self):
  import programme_urls55 as q
  q._thread=mock.Mock();q._thread.is_alive.return_value=True
  e=dict(self.event(),key='one')
  self.assertTrue(q.enqueue(e))
  self.assertFalse(q.enqueue(e,allow_lookup=True,local_image63=True,priority68=True))
  self.assertEqual(len(q._queue),1);self.assertEqual(q._queue['one'][1:3],(True,True));self.assertIn('one',q._urgent68)
 def test_queue_full_accepts_visible_event_without_exceeding_24(self):
  import programme_urls55 as q
  q._thread=mock.Mock();q._thread.is_alive.return_value=True
  for i in range(24):self.assertTrue(q.enqueue(dict(self.event(),key=str(i))))
  self.assertTrue(q.enqueue(dict(self.event(),key='focused'),local_image63=True,priority68=True))
  self.assertEqual(len(q._pending),24);self.assertEqual(len(q._queue),24)
 def test_unknown_profile_or_expired_intents_never_read_local_db(self):
  self.b.request(self.event())
  key=next(iter(self.properties));value=json.loads(self.properties[key]);value['scope']='foreign'
  self.properties[key]=json.dumps(value)
  with mock.patch('library_index.Reader',side_effect=AssertionError('FOREIGN_SQL')):self.assertEqual(self.b.drain(),0)
 def test_short_404_has_long_unsupported_cooldown(self):
  import short_epg67
  short_epg67._state.clear();error=types.SimpleNamespace(code=404)
  with mock.patch('short_epg67.time.monotonic',return_value=10):short_epg67.failed(self.client,error)
  with mock.patch('short_epg67.time.monotonic',return_value=5000):self.assertFalse(short_epg67.permit(self.client))
  with mock.patch('short_epg67.time.monotonic',return_value=22000):self.assertTrue(short_epg67.permit(self.client))
 def test_token_presence_does_not_auto_enable_lookup(self):
  from programme_settings68 import state
  self.options.update(programme_tmdb46=False,tmdb_research43=False)
  with mock.patch('tmdb_token61.status',return_value='FILE_VALID'):
   self.assertEqual(state()['token'],'TOKEN_PRESENT');self.assertEqual(state()['lookup'],'TMDB_LOOKUP_DISABLED')
  self.assertFalse(self.options['programme_tmdb46']);self.assertFalse(self.options['tmdb_research43'])
 def test_partial_legacy_consent_is_reported_disabled(self):
  from programme_settings68 import state
  self.options.update(programme_tmdb46=True,tmdb_research43=False)
  with mock.patch('tmdb_token61.status',return_value='FILE_VALID'):self.assertEqual(state()['lookup'],'TMDB_LOOKUP_DISABLED')
 def test_read_only_storage_diagnostic_preserves_bytes(self):
  from programme_index46 import connect,path
  from programme_storage68 import inspect
  db=connect(True);db.close()
  from pathlib import Path
  filename=Path(path());before=filename.read_bytes()
  value=inspect()
  self.assertEqual(value['policy_bytes'],128*1024*1024);self.assertGreater(value['page_count'],0)
  self.assertIsInstance(value['disk_free_bytes'],int);self.assertEqual(value['write_probe'],'NOT_PERFORMED')
  self.assertEqual(filename.read_bytes(),before)
 def test_storage_diagnostic_does_not_create_missing_database(self):
  from programme_storage68 import inspect
  from programme_index46 import path
  from pathlib import Path
  self.assertEqual(inspect()['code'],'NOT_CREATED');self.assertFalse(Path(path()).exists())

class Dynamic68(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.dbfile=str(self.folder/'live68.sqlite')
  with sqlite3.connect(self.dbfile) as db:
   db.executescript('CREATE TABLE groups(pid TEXT,kind TEXT,cid TEXT,ordinal INTEGER); CREATE TABLE heads(pid TEXT,kind TEXT,cid TEXT,generation TEXT); CREATE TABLE items_v2(pid TEXT,kind TEXT,cid TEXT,generation TEXT,sid TEXT,title TEXT,payload TEXT,ordinal INTEGER); CREATE TABLE titles(pid TEXT,kind TEXT,cid TEXT,sid TEXT,title TEXT,payload TEXT,ordinal INTEGER); CREATE INDEX group_order_v2 ON items_v2(pid,kind,cid,generation,ordinal); CREATE INDEX category_titles ON titles(pid,kind,cid,ordinal);')
 def group(self,pid,cid,count,first=0,ordinal=0):
  with sqlite3.connect(self.dbfile) as db:
   db.execute('INSERT INTO groups VALUES(?,?,?,?)',(pid,'live',cid,ordinal))
   db.execute('INSERT INTO heads VALUES(?,?,?,?)',(pid,'live',cid,'generation'))
   for i in range(count):
    sid=str(first+i);value=dict(sid=sid,name='Channel '+sid,category_id=cid)
    db.execute('INSERT INTO items_v2 VALUES(?,?,?,?,?,?,?,?)',(pid,'live',cid,'generation',sid,value['name'],json.dumps(value),i))
 def read(self,**portal):
  from live_home62 import read
  return read(dict(self.portal,**portal),self.dbfile)[0]
 def test_complete_sizes_zero_to_256_and_page_boundaries(self):
  for n in (0,1,5,16,17,63,64,65,88,120,127,128,129,256):
   with self.subTest(n=n):
    with sqlite3.connect(self.dbfile) as db:
     for table in ('groups','heads','items_v2'):db.execute('DELETE FROM '+table)
    self.group('p','a',n)
    self.assertEqual([r['sid'] for r in self.read()],[str(i) for i in range(n)])
 def test_star_reads_enabled_groups_in_provider_order_without_duplicates(self):
  self.group('p','a',129,ordinal=1);self.group('p','b',128,first=100,ordinal=2)
  self.assertEqual([r['sid'] for r in self.read(start_group_id='*')],[str(i) for i in range(228)])
  from group_selection import save
  save('p',['b'],known=['a','b'])
  self.assertEqual([r['sid'] for r in self.read(start_group_id='*')],[str(i) for i in range(100,228)])
 def test_other_portal_never_leaks_into_star(self):
  self.group('p','a',5);self.group('other','a',5,first=100)
  self.assertEqual([r['sid'] for r in self.read(start_group_id='*')],['0','1','2','3','4'])
 def test_unknown_group_does_not_fall_back_to_all_channels(self):
  self.group('p','a',5)
  from live_home62 import Failure
  with self.assertRaises(Failure):self.read(start_group_id='removed')
 def test_dynamic_group_change_during_runtime(self):
  self.group('p','a',5);self.group('p','b',17,first=100)
  self.assertEqual(len(self.read()),5);self.assertEqual(len(self.read(start_group_id='b')),17)
 def test_zero_enabled_groups_returns_empty(self):
  self.group('p','a',5)
  from group_selection import save
  save('p',[],known=['a'])
  self.assertEqual(self.read(start_group_id='*'),[])
 def test_policy_changes_with_start_group_portal_identity_and_generation(self):
  from widget_data41 import policy
  a=policy(self.portal,'live')
  self.assertNotEqual(a,policy(dict(self.portal,start_group_id='b'),'live'))
  self.assertNotEqual(a,policy(dict(self.portal,xc_host='https://different.invalid'),'live'))
  with mock.patch('widget_data41.path',return_value=self.dbfile):
   b=policy(self.portal,'live');self.group('p','a',5);self.assertNotEqual(b,policy(self.portal,'live'))
