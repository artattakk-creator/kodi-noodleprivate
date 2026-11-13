"""Real image/file/manifest commits under the documented Android capacity."""
import hashlib,json,time,unittest
from unittest import mock
from xcmate027_fixture import Fixture
from test_xcmate_02988 import png
class Logo89(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.module=__import__('logo_store89');self.module._verified.clear();self.rows=[dict(sid=str(i),name='Station',stream_icon='https://images.example.org/logo-'+str(i)+'.png') for i in range(88)]
  self.measure=mock.patch('art_storage82.capacity',return_value=dict(capacity82='SAME_VOLUME_VERIFIED',free=228114432,total=4034297856,volume82='same-volume',mount82='fuse'));self.measure.start()
 def tearDown(self):self.measure.stop();super().tearDown()
 def test_all_88_are_persistent_and_cold_group_switch_needs_no_http_or_decode(self):
  from logo_manifest86 import read
  for row in self.rows:self.module.persist(self.portal,row,png())
  self.module._verified.clear()
  with mock.patch('media_sources43.validate_image',side_effect=AssertionError('no repeated decode')):
   self.assertEqual(len(read(self.portal,self.rows,with_fallback=False)),88)
   changed=dict(self.portal,selected_live_categories=['another'],start_group_id='different')
   self.assertEqual(len(read(changed,self.rows,with_fallback=False)),88)
  manifest=__import__('logo_manifest86').location()[1];data=json.loads(__import__('pathlib').Path(manifest).read_bytes());self.assertEqual(len(data['records']),88)
  self.assertTrue(all(v['storage89']=='PERSISTED_LOGO' for v in data['records'].values()))
 def test_widget_reader_uses_all_verified_cold_logos_without_dns_ram_or_repeat_fetch(self):
  from pathlib import Path
  from contextlib import ExitStack
  for row in self.rows:self.module.persist(self.portal,row,png())
  self.module._verified.clear();self.properties.clear()
  reader=__import__('widget_assets69')
  with ExitStack() as stack:
   for name in ('widget_refs74.read','widget_cache79.read','widget_cache82.read','render_cache81.references','poster_store89.read'):
    stack.enter_context(mock.patch(name,return_value={}))
   stack.enter_context(mock.patch('station_logos88.fetch',side_effect=AssertionError('cold logo must not refetch')))
   result=reader.read(self.portal,'live',self.rows)
   self.assertEqual(len(result),88);self.assertTrue(all(Path(row['poster']).is_file() for row in result.values()))
   changed=[dict(self.rows[0],stream_icon='https://images.example.org/changed.png')]
   self.assertEqual(reader.read(self.portal,'live',changed),{})
   with mock.patch('widget_refs74.revoked',return_value=True):self.assertEqual(reader.read(self.portal,'live',self.rows),{})
 def test_floor_unknown_volume_and_no_room_fail_without_disabling_global_reserve(self):
  from art_storage import reserve
  self.assertGreaterEqual(reserve(),1024*1024**2)
  for value in (dict(capacity82='CAPACITY_DISAGREEMENT',free=228114432,total=4034297856),dict(capacity82='SAME_VOLUME_VERIFIED',free=20*1024**2,total=4034297856)):
   with mock.patch('art_storage82.capacity',return_value=value),self.assertRaises(OSError):self.module.persist(self.portal,self.rows[0],png())
 def test_corruption_repaired_only_for_the_selected_hash(self):
  from pathlib import Path
  path,_=self.module.persist(self.portal,self.rows[0],png());Path(path).write_bytes(b'corrupt')
  self.assertEqual(__import__('logo_manifest86').read(self.portal,self.rows[:1],with_fallback=False),{})
  self.module.persist(self.portal,self.rows[0],png());self.assertEqual(hashlib.sha256(Path(path).read_bytes()).hexdigest(),hashlib.sha256(png()).hexdigest())
 def test_failed_manifest_readback_never_claims_persisted(self):
  with mock.patch('logo_manifest86.load',side_effect=lambda *a,**kw:{}):
   with self.assertRaisesRegex(OSError,'LOGO_MANIFEST_READBACK'):self.module.persist(self.portal,self.rows[0],png())
 def test_unchanged_logo_prepare_does_not_fetch_again(self):
  row=self.rows[0];self.module.persist(self.portal,row,png())
  m=__import__('station_logos88');m._due.clear()
  with mock.patch.object(m,'fetch',side_effect=AssertionError('no repeat HTTP')):self.assertEqual(m.prepare(self.portal,[row]),'READY')
