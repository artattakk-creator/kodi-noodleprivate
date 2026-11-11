"""P0-G: real owned files/readback, local poster retention and real catalogue jobs."""
import hashlib,importlib,json,time,unittest
from unittest import mock
from xcmate027_fixture import Fixture
from test_xcmate_02988 import png
class PostersG89(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.m=__import__('poster_store89');self.rows=[dict(sid=str(i),name='Media '+str(i),year='2024',cover='https://images.example.org/'+str(i)+'.png') for i in range(5)]
  self.measure=mock.patch('art_storage82.capacity',return_value=dict(capacity82='SAME_VOLUME_VERIFIED',free=228114432,total=4034297856,volume82='same-volume'));self.measure.start()
 def tearDown(self):self.measure.stop();super().tearDown()
 def seed(self):
  for kind in ('vod','series'):
   for row in self.rows:self.m.store(self.portal,kind,row,'poster',row['cover'],png((300,450)))
 def test_five_movies_five_series_cold_reuse_without_any_network_or_changed_bytes(self):
  self.seed();before={p.name:p.read_bytes() for p in self.m.location().iterdir()};importlib.reload(self.m)
  with mock.patch('programme_transport77.verified',side_effect=AssertionError('no repeated download')),mock.patch('widget_cache79.read',return_value={}):
   for kind in ('vod','series'):
    self.assertEqual(len(self.m.read(self.portal,kind,self.rows)),5);self.m.prepare(self.portal,kind,self.rows)
  self.assertEqual(before,{p.name:p.read_bytes() for p in self.m.location().iterdir()})
 def test_local_cover_survives_5_30_45_90_306_seconds_and_metadata_sql_dns_failure(self):
  self.seed();now=time.time();original=self.m.read(self.portal,'vod',self.rows)
  for seconds in (5,30,45,90,306):
   with mock.patch('time.time',return_value=now+seconds),mock.patch('widget_refs74.revoked',return_value=False),mock.patch('sqlite3.connect',side_effect=AssertionError('local poster read needs no SQL')),mock.patch('artwork_visible.public_dns',side_effect=AssertionError('no DNS extension')):
    self.assertEqual(self.m.read(self.portal,'vod',self.rows),original)
 def test_changed_source_keeps_last_good_until_verified_replacement_only_one_item_changes(self):
  self.seed();old=self.m.read(self.portal,'vod',self.rows);changed=dict(self.rows[0],cover='https://images.example.org/new.png');rows=[changed]+self.rows[1:]
  self.assertEqual(self.m.read(self.portal,'vod',rows),old)
  self.m.store(self.portal,'vod',changed,'poster',changed['cover'],png((301,451)))
  current=self.m.read(self.portal,'vod',rows);self.assertNotEqual(old['0'],current['0']);self.assertEqual({k:v for k,v in old.items() if k!='0'},{k:v for k,v in current.items() if k!='0'})
 def test_true_revocation_manual_hide_account_and_identity_changes_never_keep_wrong_poster(self):
  self.seed()
  with mock.patch('widget_refs74.revoked',return_value=True):self.assertFalse(self.m.read(self.portal,'vod',self.rows))
  for portal,rows in ((dict(self.portal,xc_user='other'),self.rows),(self.portal,[dict(r,name='different edition') for r in self.rows]),(self.portal,[dict(r,_no_art86=True) for r in self.rows])):self.assertFalse(self.m.read(portal,'vod',rows))
 def test_low_floor_or_failed_new_manifest_preserves_existing_poster(self):
  self.seed();before={p.name:p.read_bytes() for p in self.m.location().iterdir()}
  with mock.patch('art_storage82.capacity',return_value=dict(capacity82='SAME_VOLUME_VERIFIED',free=20*1024**2,total=4034297856)),self.assertRaisesRegex(OSError,'POSTER_SAFETY_FLOOR'):
   self.m.store(self.portal,'vod',self.rows[0],'poster',self.rows[0]['cover'],png((301,451)))
  self.assertEqual(before,{p.name:p.read_bytes() for p in self.m.location().iterdir()})

class CatalogG89(unittest.TestCase):
 def setUp(self):
  from test_xcmate_catalog_02973 import Catalog73
  self.c=Catalog73();self.c.setUp();self.addCleanup(self.c.doCleanups);self.addCleanup(self.c.tearDown)
  self.c.portal.update(include_vod=True,include_series=True);self.c.pm.save_all([self.c.portal])
  __import__('test_xcmate_vodsync_02972').load_real('widget_refresh45')
 def finish(self):self.c.finish();return self.c.row()
 def test_two_new_movies_and_two_series_commit_readback_and_widget_generation_without_auto_prefetch(self):
  c=self.c;c.options['xc_background_prefetch']=False;c.jobs.request(c.portal,['vod','series']);self.finish()
  c.responses['get_vod_streams'] += [dict(stream_id='m'+str(i),category_id='v',name='Movie '+str(i),added=1794000000+i,stream_icon='https://images.example.org/movie'+str(i)+'.png') for i in (2,3)]
  c.responses['get_series'] += [dict(series_id='s'+str(i),category_id='s',name='Series '+str(i),added=1794000000+i,cover='https://images.example.org/series'+str(i)+'.png') for i in (2,3)]
  c.jobs.request(c.portal,['vod','series']);job=self.finish()
  self.assertEqual(job['readback'],dict(vod=3,series=3));self.assertEqual(job['delta81']['vod']['new'],2);self.assertEqual(job['delta81']['series']['new'],2)
  for kind in ('vod','series'):
   self.assertEqual(job['widgets89'][kind]['code'],'WIDGET_ITEMS_PRESENT',job['widgets89'][kind]);self.assertEqual(job['readback89'][kind]['count'],3)
  self.assertFalse(c.options['xc_background_prefetch']);self.assertEqual(c.live_digest(),c.live_before)
 def test_empty_remote_update_retains_rows_old_cover_references_and_no_false_full_sync(self):
  c=self.c;c.jobs.request(c.portal,['vod','series']);self.finish();before={k:c.index.Reader('p').page(k,limit=24)[0] for k in ('vod','series')}
  c.responses['get_vod_streams']=[];c.responses['get_series']=[];c.jobs.request(c.portal,['vod','series']);job=self.finish()
  self.assertEqual(job.get('last_full_sync81'),{})
  for kind in ('vod','series'):self.assertEqual(c.index.Reader('p').page(kind,limit=24)[0],before[kind])
