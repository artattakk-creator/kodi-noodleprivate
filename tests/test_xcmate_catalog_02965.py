"""Synthetic category fixtures only; preserve all IDs, selections and heads."""
import importlib,json,time,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class Catalog65(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.selection=importlib.import_module('group_selection')
  self.groups=[dict(category_id='10',category_name='Adult Zone'),dict(category_id='20',category_name='Other fixture group')]
  self.selection.save('p',['10'],kind='vod',known=['10','20'])
  self.selection.save('p',['10'],kind='series',known=['10','20'])
 def rows(self,n,kind='vod',cid='10'):
  key='series_id' if kind=='series' else 'stream_id'
  return [dict({key:str(i)},name='Fixture title '+str(i),category_id=cid,genre='Drama',added=self.now-i) for i in range(n)]
 def client65(self,remote,cache=None):
  def iterator(action,cid=None,cached_only=False,cancel=lambda:False):
   value=cache if cached_only else remote
   if isinstance(value,BaseException):raise value
   return iter(value or [])
  return types.SimpleNamespace(get_cached_catalog=lambda action:self.groups,_get_json=lambda *a,**kw:self.groups,iter_catalog=iterator)
 def seed(self,n,kind='vod',cid='10',pid='p'):
  return self.index.import_group(pid,kind,cid,self.rows(n,kind,cid))
 def total(self,kind='vod',cid='10',pid='p'):
  return self.index.Reader(pid).page(kind,category=cid,limit=100)[1]
 def test_zero_one_48_100_1205_film_and_series_cover_every_id_across_pages_and_portals(self):
  for kind in ('vod','series'):
   for n in (1,48,100,1205):
    for pid in ('p','q'):
     with self.subTest(kind=kind,n=n,pid=pid):
      self.seed(n,kind,pid=pid);reader=self.index.Reader(pid);found=[]
      for offset in range(0,n,100):
       page,total=reader.page(kind,category='10',offset=offset,limit=100)
       self.assertEqual(total,n);found.extend(row['sid'] for row in page)
      self.assertEqual(set(found),{str(i) for i in range(n)});self.assertEqual(len(found),n)
  with self.assertRaises(ValueError):self.index.import_group('p','vod','10',[])
  self.assertEqual(self.total(),1205)
 def test_numeric_zero_category_and_title_id_are_not_treated_as_empty(self):
  self.selection.save('p',['0'],kind='vod',known=['0'])
  self.index.import_group('p','vod','0',[dict(stream_id=0,category_id=0,name='Fixture zero')])
  self.assertEqual(self.index.Reader('p').get('vod','0')['category_id'],'0')
 def test_title_search_category_and_widget_all_see_successful_generation(self):
  self.seed(1205);self.seed(1205,'series')
  for kind in ('vod','series'):
   reader=importlib.import_module('media_catalog43').Reader('p')
   self.assertEqual(reader.page(kind,query='Fixture title',category='10',limit=100)[1],1205)
   rows,code=importlib.import_module('widget_data41').snapshot(self.portal,kind)
   self.assertIn(code,('READY','CACHE'));self.assertEqual(len(rows),24);self.assertEqual(len({v['sid'] for v in rows}),24)
 def test_empty_authoritative_category_keeps_last_good_and_records_source_empty(self):
  self.seed(48);self.index.sync_kind(self.portal,self.client65([]),'vod',force=True,only_categories={'10'})
  self.assertEqual(self.total(),48)
  state=next(r for r in self.index.sync_state('p','vod') if r['cid']=='10')
  self.assertEqual(state['code'],'SOURCE_EMPTY');self.assertEqual(state['received'],0)
 def test_provider_ignoring_category_cannot_publish_other_group_as_requested_group(self):
  self.seed(2,cid='20');before=self.index.Reader('p')._query("SELECT generation FROM heads WHERE pid='p' AND kind='vod' AND cid='20'")[0]
  self.index.sync_kind(self.portal,self.client65(self.rows(48,cid='20')),'vod',force=True,only_categories={'10'})
  self.assertEqual(self.total(),0);after=self.index.Reader('p')._query("SELECT generation FROM heads WHERE pid='p' AND kind='vod' AND cid='20'")[0]
  self.assertEqual(before,after);self.assertEqual(self.index.sync_state('p','vod')[0]['code'],'SOURCE_FILTERED')
 def test_offline_cold_cache_is_marked_cached_and_never_claims_current_remote_availability(self):
  self.index.sync_kind(self.portal,self.client65(OSError('offline'),self.rows(48)),'vod',only_categories={'10'})
  self.assertEqual(self.total(),48);self.assertEqual(self.index.sync_state('p','vod')[0]['code'],'CACHED')
  db=self.index.connect()
  try:value=json.loads(db.execute("SELECT data FROM catalog_evidence65 WHERE pid='p' AND kind='vod' AND cid='10'").fetchone()[0])
  finally:db.close()
  self.assertEqual(value['transport'],'LOCAL_CACHE');self.assertEqual(value['code'],'CACHED')
 def test_partial_legacy_refresh_does_not_drop_published_heads_or_other_legacy_titles(self):
  self.seed(48);head=self.index.Reader('p')._query("SELECT generation FROM heads WHERE pid='p' AND kind='vod' AND cid='10'")[0]
  self.index.replace_catalog('p','vod',[dict(stream_id='new-fixture',category_id='a',name='Fixture delta')],[dict(category_id='a')],authoritative=False)
  self.assertEqual(self.total(),48);self.assertEqual(self.index.Reader('p')._query("SELECT generation FROM heads WHERE pid='p' AND kind='vod' AND cid='10'")[0],head)
  db=self.index.connect()
  try:self.assertGreaterEqual(db.execute("SELECT count(*) FROM titles WHERE pid='p' AND kind='vod' AND cid='a'").fetchone()[0],100)
  finally:db.close()
 def test_deactivated_or_new_unselected_category_is_not_imported_by_name(self):
  self.selection.save('p',[],kind='vod',known=['10'])
  client=self.client65(self.rows(48));client.iter_catalog=mock.Mock(wraps=client.iter_catalog)
  self.index.sync_kind(self.portal,client,'vod',force=True)
  client.iter_catalog.assert_not_called();self.assertEqual(self.total(),0)
  self.assertEqual(self.selection.enabled_ids('p','vod',self.groups),set())
 def test_failed_or_cancelled_staging_preserves_previous_complete_generation(self):
  self.seed(48)
  def broken():
   yield from self.rows(300)
   raise OSError('synthetic source failure')
  with self.assertRaises(OSError):self.index.import_group('p','vod','10',broken())
  self.assertEqual(self.total(),48)
  with self.assertRaises(InterruptedError):self.index.import_group('p','vod','10',self.rows(1205),cancel=lambda:True)
  self.assertEqual(self.total(),48)
 def test_active_lease_does_not_consume_durable_sync_request(self):
  self.index.request_sync(self.portal,'vod')
  db=self.index.connect(write=True)
  try:
   with db:db.execute('INSERT OR REPLACE INTO sync_leases VALUES(?,?,?,?)',('p','vod','other-owner',time.time()+330))
  finally:db.close()
  worker=importlib.import_module('catalog_sync');self.assertFalse(worker.run_next())
  self.assertEqual(len(self.index.Reader('p')._query('SELECT * FROM sync_requests')),1)
 def test_process_failure_keeps_intent_for_restart(self):
  self.index.request_sync(self.portal,'vod')
  with mock.patch('library_index.sync_kind',side_effect=SystemExit('fixture process exit')),self.assertRaises(SystemExit):importlib.import_module('catalog_sync').run_next()
  self.assertEqual(len(self.index.Reader('p')._query('SELECT * FROM sync_requests')),1)
 def test_explicit_delta_waits_for_lease_without_spending_retry_budget(self):
  delta=importlib.import_module('catalog_delta');delta.request(self.portal,'vod','10')
  db=self.index.connect(write=True)
  try:
   with db:db.execute('INSERT OR REPLACE INTO sync_leases VALUES(?,?,?,?)',('p','vod','other-owner',time.time()+330))
  finally:db.close()
  with mock.patch('xtream.XtreamClient',return_value=self.client65(self.rows(48))):self.assertTrue(delta.run_next())
  state=delta.states('p','vod')[0];self.assertEqual(state['code'],'PENDING');self.assertEqual(state['attempts'],0)
 def test_explicit_delta_refetches_recent_head_and_never_marks_old_head_as_new_success(self):
  self.seed(1);delta=importlib.import_module('catalog_delta');delta.request(self.portal,'vod','10')
  with mock.patch('xtream.XtreamClient',return_value=self.client65(self.rows(48))):self.assertTrue(delta.run_next())
  self.assertEqual(self.total(),48);self.assertEqual(delta.states('p','vod')[0]['code'],'READY')
 def test_explicit_empty_source_reports_empty_without_creating_phantom_head(self):
  delta=importlib.import_module('catalog_delta');delta.request(self.portal,'vod','10')
  with mock.patch('xtream.XtreamClient',return_value=self.client65([])):self.assertTrue(delta.run_next())
  self.assertEqual(delta.states('p','vod')[0]['code'],'EMPTY_SOURCE');self.assertEqual(self.total(),0)
 def test_restart_after_head_commit_does_not_download_same_completed_intent_again(self):
  delta=importlib.import_module('catalog_delta');delta.request(self.portal,'vod','10')
  self.index.sync_kind(self.portal,self.client65(self.rows(48)),'vod',force=True,only_categories={'10'})
  key=json.dumps(['p','vod','10'])
  value=delta._read();value['jobs'][key].update(code='RUNNING',next_at=0);delta._save(value)
  client=self.client65(self.rows(100));client.iter_catalog=mock.Mock(wraps=client.iter_catalog)
  with mock.patch('xtream.XtreamClient',return_value=client):self.assertTrue(delta.run_next())
  client.iter_catalog.assert_not_called();self.assertEqual(self.total(),48);self.assertEqual(delta.states('p','vod')[0]['code'],'READY')
 def test_deactivation_during_fast_import_is_checked_again_before_head_swap(self):
  self.seed(1)
  def changed():
   yield from self.rows(48)
   self.selection.save('p',[],kind='vod',known=['10','20'])
  self.index.sync_kind(self.portal,self.client65(changed()),'vod',force=True,only_categories={'10'})
  db=self.index.connect()
  try:self.assertEqual(db.execute("SELECT count(*) FROM items_v2 i JOIN heads h USING(pid,kind,cid,generation) WHERE pid='p' AND kind='vod' AND cid='10'").fetchone()[0],1)
  finally:db.close()
  self.assertEqual(self.index.sync_state('p','vod')[0]['code'],'CANCELLED')
 def test_explicit_retry_really_calls_source_again_after_failed_attempt(self):
  delta=importlib.import_module('catalog_delta');delta.request(self.portal,'vod','10')
  client=self.client65(OSError('synthetic offline'));client.iter_catalog=mock.Mock(wraps=client.iter_catalog)
  with mock.patch('xtream.XtreamClient',return_value=client):
   delta.run_next();before=client.iter_catalog.call_count
   value=delta._read()
   for row in value['jobs'].values():row['next_at']=0
   delta._save(value);delta.run_next()
  self.assertGreater(client.iter_catalog.call_count,before);self.assertEqual(delta.states('p','vod')[0]['attempts'],2)
