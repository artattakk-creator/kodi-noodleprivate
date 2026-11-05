"""Home LKG, exact provenance, atomic rows and independently bounded leases."""
import importlib,json,os,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture

class Home74(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.w=importlib.import_module('widget_refresh45');self.p=importlib.import_module('home_publication74');self.d=importlib.import_module('widget_data41');self.refs=importlib.import_module('widget_refs74')
 def rows(self,n=24):return [dict(sid=str(i),name='Synthetic title '+str(i),category_id='a',cover='https://public.example.test/poster-'+str(i)+'.jpg',added_at=self.now-i) for i in range(n)]
 def frame(self,rows,revision=1,kind='vod'):
  self.d.store(self.d.files('p',kind)[0],self.d.policy(self.portal,kind),rows,['r',revision])
  with mock.patch('programme_assets47.read_many',return_value={}):self.assertTrue(self.w.publish(self.portal,kind,rows))
  return self.w.read('p',kind)
 def test_missing_images_never_remove_twenty_four_title_rows(self):
  frame=self.frame(self.rows());self.assertEqual(len(frame['items']),24)
  self.assertEqual([i['props']['XCMate.MediaId'] for i in frame['items']],[str(i) for i in range(24)])
 def test_transient_seven_of_twenty_four_never_replaces_full_generation(self):
  self.frame(self.rows());self.w.publish(self.portal,'vod',self.rows(7));self.assertEqual(len(self.w.read('p','vod')['items']),24)
 def test_true_committed_provider_deletion_is_visible(self):
  self.frame(self.rows());self.assertEqual(len(self.frame(self.rows(7),revision=2)['items']),7)
 def test_authoritative_empty_new_revision_clears_removed_catalog(self):
  self.frame(self.rows());frame=self.frame([],revision=2);self.assertEqual(frame['items'],[]);self.assertTrue(frame['empty_authoritative74'])
 def test_unknown_empty_is_not_evidence_for_deletion(self):
  self.frame(self.rows());before=Path(self.w.path('p','vod')).read_bytes();self.assertFalse(self.w.publish(self.portal,'vod',[]));self.assertEqual(Path(self.w.path('p','vod')).read_bytes(),before)
 def test_same_revision_empty_retains_previous_rows(self):
  self.frame(self.rows());self.assertEqual(len(self.frame([],revision=1)['items']),24)
 def test_identical_publication_is_not_rewritten_every_poll(self):
  self.frame(self.rows());path=Path(self.w.path('p','vod'));before=(path.stat().st_mtime_ns,path.read_bytes());self.w.publish(self.portal,'vod',self.rows());self.assertEqual((path.stat().st_mtime_ns,path.read_bytes()),before)
 def test_policy_stable_across_unrelated_sqlite_wal_writes(self):
  before=self.d.policy(self.portal,'live');Path(self.index.path()+'-wal').write_bytes(b'Unrelated write');self.assertEqual(self.d.policy(self.portal,'live'),before)
 def test_credentials_and_portal_selection_invalidate_all_three_kinds(self):
  for kind in ('live','vod','series'):
   before=self.d.policy(self.portal,kind);self.assertNotEqual(before,self.d.policy(dict(self.portal,xc_pass='changed-canary74'),kind));self.assertNotEqual(before,self.d.policy(dict(self.portal,start_group_id='other'),kind));self.assertNotIn('changed-canary74',before)
 def test_known_old_frame_not_reused_after_account_change(self):
  self.frame(self.rows());self.assertIsNone(self.p.old_frame(dict(self.portal,xc_user='different'), 'vod'))
 def test_new_frame_is_available_to_separate_reader_interpreter(self):
  old=self.frame(self.rows());self.assertEqual(json.loads(Path(self.w.path('p','vod')).read_text())['signature'],old['signature'])
 def test_stale_provider_reference_requires_exact_sid_role_and_source(self):
  row=self.rows(1)[0];uri=row['cover'];self.refs.remember_many(self.portal,'vod',[('0','poster',uri,30)])
  self.assertIn('0',self.refs.read(self.portal,'vod',[row]));self.assertEqual(self.refs.read(self.portal,'vod',[dict(row,sid='other')]),{});self.assertEqual(self.refs.read(self.portal,'vod',[dict(row,cover=uri+'different')]),{})
 def test_stale_public_lease_bridges_thirty_seconds_but_expires_after_grace(self):
  row=self.rows(1)[0];wall=time.time();self.refs.remember_many(self.portal,'vod',[('0','poster',row['cover'],30)])
  with mock.patch('time.time',return_value=wall+31):self.assertIn('0',self.refs.read(self.portal,'vod',[row]))
  with mock.patch('time.time',return_value=wall+331):self.assertEqual(self.refs.read(self.portal,'vod',[row]),{})
 def test_confirmed_unsafe_dns_revokes_grace_immediately(self):
  row=self.rows(1)[0];self.refs.remember_many(self.portal,'vod',[('0','poster',row['cover'],30)])
  import artwork_visible
  with mock.patch.dict(artwork_visible._dns_cache,{('public.example.test',443):(time.monotonic()+30,False)},clear=True):self.assertEqual(self.refs.read(self.portal,'vod',[row]),{})
 def test_reference_journal_failure_cannot_terminate_worker(self):
  with mock.patch('widget_refs74._remember_many',side_effect=OSError(28,'synthetic')):self.assertIsNone(self.refs.remember_many(self.portal,'vod',[('0','poster','https://public.example.test/x.jpg',30)]))
 def test_publication_accepts_keyword_arguments(self):
  rows=self.rows(1);self.d.store(self.d.files('p','vod')[0],self.d.policy(self.portal,'vod'),rows,1)
  with mock.patch('programme_assets47.read_many',return_value={}):self.assertTrue(self.w.publish(self.portal,kind='vod',rows=rows))
 def test_busy_frame_lock_defers_without_overwriting(self):
  import fcntl
  self.frame(self.rows());path=Path(self.w.path('p','vod'));before=path.read_bytes()
  with open(str(path)+'.publish74.lock','a') as handle:
   fcntl.flock(handle,fcntl.LOCK_EX|fcntl.LOCK_NB);self.assertFalse(self.w.publish(self.portal,'vod',self.rows(4)))
  self.assertEqual(path.read_bytes(),before)
 def test_diagnostics_have_fixed_codes_and_no_account_secret(self):
  with mock.patch('xbmc.LOGINFO',1,create=True),mock.patch('xbmc.log',create=True) as log:self.p.note(self.portal,'vod','HOLD_PARTIAL',None,7,123)
  self.assertIn('old_count=',log.call_args.args[0]);self.assertIn('old_art_status=',log.call_args.args[0]);self.assertNotIn(str(self.portal.get('xc_pass') or 'PRIVATE_CANARY74'),log.call_args.args[0])
 def test_immutable_pages_keep_old_reader_valid_across_three_writer_generations(self):
  rows=[dict(sid=str(i),name='Live '+str(i),category_id='a') for i in range(88)]
  with mock.patch('programme_assets47.read_many',return_value={}):
   first=self.frame(rows,revision=1,kind='live');old=list(first['items'])
   second=self.frame([dict(r,name='Updated '+r['sid']) for r in rows],revision=2,kind='live')
   third=self.frame([dict(r,name='Third '+r['sid']) for r in rows],revision=3,kind='live')
  self.assertEqual(len(third['items']),88);self.assertEqual(list(first['items']),old)
  self.assertTrue(first['immutable74']);self.assertNotEqual(first['generation46'],second['generation46'])
 def test_corrupt_immutable_page_is_rejected_not_partially_displayed(self):
  rows=[dict(sid=str(i),name='Live '+str(i),category_id='a') for i in range(88)]
  with mock.patch('programme_assets47.read_many',return_value={}):frame=self.frame(rows,kind='live')
  filename=Path(self.w.path('p','live'));(filename.parent/frame['pages46'][0]['name']).write_text('{}')
  self.assertIsNone(self.w.read('p','live'))

 def test_corrupt_optional_reference_journal_cannot_break_widget_directory(self):
  filename,context=self.refs.path(self.portal,'vod')
  for value in ([],None,dict(context=context,refs=[]),dict(context=context,refs={'0':[]})):
   Path(filename).write_text(json.dumps(value));self.refs._cache.clear()
   self.assertEqual(self.refs.read(self.portal,'vod',self.rows(1)),{})
   self.assertIsNone(self.refs.remember_many(self.portal,'vod',[('0','poster',self.rows(1)[0]['cover'],30)]))
 def test_local_last_good_art_cannot_cross_a_changed_provider_source(self):
  image=self.folder/'known.png';image.write_bytes(b'synthetic verified by prior pipeline')
  rows=self.rows(1);first=self.frame(rows)
  item=first['items'][0];item['art']['poster']=str(image)
  first['source_refs74']=self.p.source_refs(rows)
  current=dict(item,art={'poster':''},props=dict(item['props']),info=dict(item['info']))
  with mock.patch('widget_refs74.read',return_value={}):
   merged,_=self.p.merge(self.portal,'vod',[current],[dict(rows[0],cover='https://public.example.test/different.jpg')],first)
  self.assertFalse(merged[0]['art']['poster'])

 def test_picture_diagnostics_distinguish_reference_states_from_row_count(self):
  frame=self.frame(self.rows());self.assertEqual(frame['art_status74'],'REFERENCE_PENDING')
  values=[dict(art={'poster':'/synthetic/approved.jpg'}),dict(art={'poster':''})]
  self.assertEqual(self.p.art_status(values),'REFERENCE_PARTIAL')
  self.assertEqual(self.p.art_status(values[:1]),'REFERENCE_READY')
  self.assertEqual(self.p.art_status([]),'EMPTY')
