"""Pause/reserve/expiry cannot downgrade a verified unchanged catalogue rail."""
import copy,hashlib,io,json,time,unittest
from pathlib import Path
from unittest import mock
class Publication82(unittest.TestCase):
 def setUp(self):
  from test_xcmate_home_02974 import Home74
  self.h=Home74(methodName='runTest');self.h.setUp();self.addCleanup(self.h.doCleanups)
 def test_same_revision_missing_provider_metadata_retains_real_confirmed_local_cover(self):
  h=self.h;import render_cache81 as cache
  from PIL import Image
  body=io.BytesIO();Image.new('RGB',(160,90),(20,80,130)).save(body,'PNG')
  rows=h.rows(24);__import__('artwork_config').choose('dynamic')
  with mock.patch('programme_art46.space'),mock.patch('artwork_health82.guard'):
   for row in rows:cache.store(cache.identity(h.portal,'vod',row,'poster',row['cover']),body.getvalue())
  h.d.store(h.d.files('p','vod')[0],h.d.policy(h.portal,'vod'),rows,['r',1]);h.w.publish(h.portal,'vod',rows)
  first=h.w.read('p','vod');self.assertEqual(first['art_status74'],'REFERENCE_READY')
  missing=[dict(r,cover='') for r in rows];h.d.store(h.d.files('p','vod')[0],h.d.policy(h.portal,'vod'),missing,['r',1])
  for _ in range(3):
   with mock.patch('programme_assets47.read_many',return_value={}):self.assertTrue(h.w.publish(h.portal,'vod',missing))
   current=h.w.read('p','vod');self.assertEqual(current['art_status74'],'REFERENCE_READY')
   self.assertEqual([r['art']['poster'] for r in current['items']],[r['art']['poster'] for r in first['items']])
  # A real revision change authorizes a no-source result; no stale image rescue.
  h.d.store(h.d.files('p','vod')[0],h.d.policy(h.portal,'vod'),missing,['r',2])
  with mock.patch('programme_assets47.read_many',return_value={}):h.w.publish(h.portal,'vod',missing)
  self.assertNotEqual(h.w.read('p','vod')['art_status74'],'REFERENCE_READY')
 def test_cached_rails_publish_before_network_warming_admission(self):
  h=self.h;from widget_fast69 import prepare
  import widget_fast69 as fast
  fast._next=0;fast._published.clear();rows=h.rows(24)
  for kind in ('vod','series'):h.d.store(h.d.files('p',kind)[0],h.d.policy(h.portal,kind),rows,['r',1])
  calls=[]
  with mock.patch('skin_upgrade80.prepare'),mock.patch('widget_runtime79.prepare'),mock.patch('portals.get_active',return_value=[h.portal]),mock.patch('home_schedule75.configure'),mock.patch('home_schedule75.allowed',return_value=False),mock.patch('home_schedule75.focused_rows',return_value=[]),mock.patch('widget_assets69.prepare',side_effect=AssertionError('premature new downloads')),mock.patch('widget_live47.publish',side_effect=lambda p,k,r,c: calls.append((k,len(r))) or True):
   prepare()
  self.assertEqual(calls,[('vod',24),('series',24)])
