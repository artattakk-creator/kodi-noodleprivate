"""Cold provider covers: real decode of existing Kodi cache, no new downloads."""
import importlib,json,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
class Cache79(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.m=importlib.import_module('widget_cache79');self.root=self.folder/'Thumbnails';self.root.mkdir();self.file=self.root/'a.png'
  from PIL import Image
  Image.new('RGB',(160,90),(20,80,140)).save(self.file)
  self.source='https://public.example.org/a.png';self.row=dict(sid='1',name='Synthetic',cover=self.source)
  self.patch=mock.patch('xbmcvfs.translatePath',side_effect=lambda p:str(self.root/p[len('special://thumbnails/'):]) if p.startswith('special://thumbnails/') else p);self.patch.start();self.addCleanup(self.patch.stop)
  def rpc(raw):
   req=json.loads(raw);url=req['params']['filter']['value'];return json.dumps(dict(result=dict(textures=[dict(url=url,cachedurl='a.png',sizes=[dict(width=160,height=90)])])))
  self.rpc=mock.patch('xbmc.executeJSONRPC',side_effect=rpc,create=True);self.rpc.start();self.addCleanup(self.rpc.stop)
 def capture(self):self.m.prepare(self.portal,'vod',[self.row]);return self.m.read(self.portal,'vod',[self.row])
 def test_positive_texture_survives_two_module_restarts_and_remote_lease_expiry(self):
  self.assertEqual(self.capture()['1']['poster'],str(self.file))
  wall=time.time()
  for elapsed in (3600,7200):
   self.m=importlib.reload(self.m)
   with mock.patch('time.time',return_value=wall+elapsed),mock.patch('socket.getaddrinfo',side_effect=AssertionError('NO_NETWORK_ON_READ')):self.assertEqual(self.m.read(self.portal,'vod',[self.row])['1']['poster'],str(self.file))
 def test_real_kodi_lowercase_escaped_wrapper_includes_http_options(self):
  from urllib.parse import quote
  from artwork_visible import KODI_OPTIONS
  import re
  wrapped='image://'+re.sub(r'%[0-9A-F]{2}',lambda m:m[0].lower(),quote(self.source+KODI_OPTIONS,safe=''))+'/'
  def actual(raw):
   wanted=json.loads(raw)['params']['filter']['value']
   return json.dumps(dict(result=dict(textures=[dict(url=wrapped,cachedurl='a.png')] if wanted==wrapped else [])))
  with mock.patch('xbmc.executeJSONRPC',side_effect=actual):self.assertEqual(self.capture()['1']['poster'],str(self.file))
 def test_wrong_source_portal_or_item_cannot_inherit_cached_picture(self):
  self.capture();self.assertEqual(self.m.read(self.portal,'vod',[dict(self.row,cover=self.source+'other')]),{});self.assertEqual(self.m.read(dict(self.portal,xc_pass='different'),'vod',[self.row]),{});self.assertEqual(self.m.read(self.portal,'vod',[dict(self.row,sid='other')]),{})
 def test_deleted_changed_and_corrupt_texture_never_claim_decode(self):
  self.capture();self.file.write_bytes(b'corrupted');self.assertEqual(self.m.read(self.portal,'vod',[self.row]),{})
  self.m._due.clear();self.m.prepare(self.portal,'vod',[self.row]);self.assertEqual(self.m.read(self.portal,'vod',[self.row]),{});self.file.unlink();self.assertEqual(self.m.read(self.portal,'vod',[self.row]),{})
 def test_remote_or_traversing_cachedurl_is_rejected_without_fetch(self):
  for bad in ('../private.png','https://public.example.org/remote.png','/etc/passwd'):
   with mock.patch('xbmc.executeJSONRPC',return_value=json.dumps(dict(result=dict(textures=[dict(url=self.source,cachedurl=bad)])))):self.assertIsNone(self.m.probe(self.source))
 def test_journal_is_private_and_does_not_delete_image_or_change_mode(self):
  options=dict(self.options);self.capture();filename,_=self.m.path(self.portal,'vod');self.assertEqual(Path(filename).stat().st_mode&0o777,0o600);self.assertTrue(self.file.exists());self.assertEqual(self.options,options)
 def test_uri_admission_prefers_exact_local_cache_over_temporary_public_reference(self):
  self.capture();a=importlib.import_module('widget_assets69')
  with mock.patch('artwork_config.persistent',return_value=False):self.assertEqual(a.read(self.portal,'vod',[self.row])['1']['poster'],str(self.file))
