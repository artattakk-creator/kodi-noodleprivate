"""Real publisher bytes across three worker/cache cycles with 24 and 88 items."""
import io,time,unittest
from pathlib import Path
from unittest import mock
class Publication81(unittest.TestCase):
 def setUp(self):
  from test_xcmate_home_02974 import Home74
  self.h=Home74(methodName='runTest');self.h.setUp();self.addCleanup(self.h.doCleanups)
 def test_decoded_rails_do_not_republish_or_lose_rows_after_remote_lease_expiry(self):
  import render_cache81 as cache
  from PIL import Image
  data=io.BytesIO();Image.new('RGB',(160,90),(20,80,130)).save(data,'PNG')
  h=self.h
  __import__('artwork_config').choose('dynamic')
  for kind,count in (('vod',24),('series',24),('live',88)):
   with self.subTest(kind=kind):
    rows=h.rows(count)
    for row in rows:row.update(kind=kind,stream_icon=row['cover'])
    h.d.store(h.d.files('p',kind)[0],h.d.policy(h.portal,kind),rows,['same-source81',1])
    with mock.patch('programme_art46.space'):
     for row in rows:cache.store(cache.identity(h.portal,kind,row,'poster',row['cover']),data.getvalue())
    with mock.patch('widget_assets69.home',return_value=True):self.assertTrue(h.w.publish(h.portal,kind,rows))
    target=Path(h.w.path('p',kind));before=target.read_bytes();first=h.w.read('p',kind)
    self.assertEqual(first['art_status74'],'REFERENCE_READY');now=time.time()
    for delta in (330,660,990):
     with mock.patch('time.time',return_value=now+delta),mock.patch('widget_assets69.home',return_value=True):
      self.assertTrue(h.w.publish(h.portal,kind,rows));current=h.w.read('p',kind)
     self.assertEqual(current['signature'],first['signature'])
     self.assertEqual(list(current['items']),list(first['items']))
     self.assertEqual(len(current['items']),count)
