import importlib,json,threading,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
class EpgMetadata89(Fixture,unittest.TestCase):
 def test_batch_keys_preserve_exact_legacy_generation_without_32_volume_stats(self):
  m=__import__('epg_poll77');p=__import__('epg_poll79');rows=[dict(sid=str(i),name='Station') for i in range(16)]
  expected={str(i):m.key('p',[row],{},True) for i,row in enumerate(rows)}
  with mock.patch.object(m.os,'stat',wraps=m.os.stat) as stat:self.assertEqual(p.keys('p',rows,{},True),expected)
  self.assertLessEqual(stat.call_count,2)
 def test_single_flight_never_opens_a_competing_reader_and_keeps_valid_warm_dto(self):
  m=__import__('epg_single89');entered=threading.Event();release=threading.Event();results=[];rows=[dict(sid='1',name='Station')]
  def read():entered.set();release.wait(2);return {'1':dict(now='Monk')}
  worker=threading.Thread(target=lambda:results.append(m.run('p',rows,{},self.now,True,read)));worker.start()
  try:
   self.assertTrue(entered.wait(1))
   with mock.patch('epg_handoff63.get',return_value=dict(now='Monk')),mock.patch('epg_poll77.read',return_value=None):
    value=m.run('p',rows,{},self.now,True,lambda:self.fail('parallel SQL'))
   self.assertEqual(value['1']['now'],'Monk')
  finally:release.set();worker.join(2)
  self.assertFalse(worker.is_alive());self.assertEqual(results,[{'1':dict(now='Monk')}]);self.assertFalse(m._active)
 def test_single_flight_exception_always_releases_lease(self):
  m=__import__('epg_single89')
  with self.assertRaises(OSError):m.run('p',[],{},self.now,True,lambda:(_ for _ in ()).throw(OSError('locked')))
  self.assertFalse(m._active)
 def test_small_verified_json_may_write_under_image_reserve_but_not_unknown_volume(self):
  m=__import__('metadata_store89');display=__import__('artwork_display84');file=self.folder/'programme_references84.json'
  facts=dict(capacity82='SAME_VOLUME_VERIFIED',free=228114432,total=4034297856,volume82='same')
  with mock.patch('art_storage82.capacity',return_value=facts),mock.patch('artwork_display84.state',return_value=dict(code='RESERVE_BLOCKED')):
   self.assertFalse(display.metadata_allowed());self.assertTrue(display.metadata_allowed(small89=True));m.check(str(file),1024)
   for candidate in (str(self.folder/'programme_images46/new.jpg'),str(self.folder/'guide_v1.sqlite')):
    with self.assertRaisesRegex(OSError,'METADATA_SCOPE_BLOCKED'):m.check(candidate,1024)
  with mock.patch('art_storage82.capacity',return_value=dict(facts,capacity82='CAPACITY_DISAGREEMENT')):
   with self.assertRaisesRegex(OSError,'METADATA_CAPACITY_UNKNOWN'):m.check(str(file),1024)
 def test_metadata_total_quota_and_low_floor_preserve_existing_file(self):
  m=__import__('metadata_store89');file=self.folder/'programme_references84.json';file.write_text('{}');before=file.read_bytes()
  with mock.patch('art_storage82.capacity',return_value=dict(capacity82='SAME_VOLUME_VERIFIED',free=20*1024**2,total=4034297856)):
   with self.assertRaisesRegex(OSError,'METADATA_SAFETY_FLOOR'):m.check(str(file),1024)
  self.assertEqual(file.read_bytes(),before)
