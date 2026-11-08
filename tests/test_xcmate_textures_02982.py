"""Actual bounded Kodi-file decode/hash and batched RPC, no image download."""
import importlib,io,json,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
class Textures82(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.cache=importlib.import_module('widget_cache82');self.cache._due.clear();self.cache._cursor.clear()
  self.root=self.folder/'Thumbnails';self.root.mkdir();self.source='https://image.tmdb.org/t/p/w500/synthetic82.png'
 def pixels(self):
  from PIL import Image
  out=io.BytesIO();Image.new('RGB',(160,90),(20,80,130)).save(out,'PNG');return out.getvalue()
 def translate(self,path):return str(self.root/path.removeprefix('special://thumbnails/')) if path.startswith('special://thumbnails/') else str(self.folder)
 def test_88_logos_recovered_in_six_rpcs_while_art_db_is_paused(self):
  import xbmc,xbmcvfs
  rows=[dict(sid=str(i),name='Synthetic '+str(i),cover='https://image.tmdb.org/t/p/w500/logo82_'+str(i)+'.png') for i in range(88)]
  for i in range(88):(self.root/(str(i)+'.png')).write_bytes(self.pixels())
  calls=[]
  def rpc(raw):
   request=json.loads(raw);calls.append(request);wanted={r['value'] for r in request['params']['filter']['or']}
   return json.dumps(dict(result=dict(textures=[dict(url=row['cover'],cachedurl=str(i)+'.png') for i,row in enumerate(rows) if row['cover'] in wanted])))
  with mock.patch.object(xbmc,'executeJSONRPC',side_effect=rpc,create=True),mock.patch.object(xbmcvfs,'translatePath',side_effect=self.translate),mock.patch('artwork_db.connect',side_effect=AssertionError('DB dependency')):
   for n in range(6):
    with mock.patch('widget_cache82.time.monotonic',return_value=1000+n):self.cache.prepare(self.portal,'live',rows)
   self.assertEqual(len(self.cache.read(self.portal,'live',rows)),88)
  self.assertEqual(len(calls),6)
  self.assertTrue(all(len(c['params']['filter']['or'])<=96 for c in calls))
 def test_no_receipt_write_space_keeps_verified_ram_and_existing_image(self):
  import xbmc,xbmcvfs
  from import_budget import ReserveBlocked
  f=self.root/'one.png';f.write_bytes(self.pixels());row=dict(sid='1',cover=self.source)
  rpc=json.dumps(dict(result=dict(textures=[dict(url=self.source,cachedurl='one.png')])))
  with mock.patch.object(xbmc,'executeJSONRPC',return_value=rpc,create=True),mock.patch.object(xbmcvfs,'translatePath',side_effect=self.translate),mock.patch('import_budget.check_space',side_effect=ReserveBlocked(10,32*1024**2,4096)):
   self.cache.prepare(self.portal,'vod',[row]);self.assertEqual(self.cache.read(self.portal,'vod',[row])['1']['poster'],str(f))
   self.assertEqual(self.cache.read(dict(self.portal,xc_user='changed'),'vod',[row]),{})
  self.assertEqual(f.read_bytes(),self.pixels())
 def test_wrong_url_or_corrupt_texture_is_not_admitted(self):
  import xbmc,xbmcvfs
  f=self.root/'broken.png';f.write_bytes(b'not-an-image');row=dict(sid='1',cover=self.source)
  rpc=json.dumps(dict(result=dict(textures=[dict(url=self.source,cachedurl='broken.png'),dict(url='https://other.invalid/image.png',cachedurl='broken.png')])))
  with mock.patch.object(xbmc,'executeJSONRPC',return_value=rpc,create=True),mock.patch.object(xbmcvfs,'translatePath',side_effect=self.translate):
   self.cache.prepare(self.portal,'series',[row]);self.assertEqual(self.cache.read(self.portal,'series',[row]),{})
 def test_malformed_native_rpc_response_does_not_kill_the_worker(self):
  import xbmc
  row=dict(sid='1',cover=self.source)
  for payload in (None,{},'invalid',[dict(url=[])]):
   self.cache._due.clear()
   with mock.patch.object(xbmc,'executeJSONRPC',return_value=json.dumps(dict(result=dict(textures=payload))),create=True):
    self.cache.prepare(self.portal,'series',[row])
