"""Reserve-blocked persistence is independent of source identity and Kodi cache."""
import hashlib,importlib,json,time,unittest
from unittest import mock
from PIL import Image
from xcmate027_fixture import Fixture

class Logos87(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.m=importlib.import_module('station_logos87');self.man=importlib.import_module('logo_manifest86')
  self.rows=[dict(sid=str(i),name='Station '+str(i),stream_icon='https://example.org/logo'+str(i)+'.png') for i in range(88)]
 def test_provider_logo_wins_over_movie_poster_and_never_uses_movie_image(self):
  row=dict(self.rows[0],cover='https://example.org/movie.png',movie_image='https://example.org/not-logo.png')
  self.assertEqual(self.m.source(row),row['stream_icon'])
  self.assertEqual(self.m.source(dict(sid='1',movie_image=row['movie_image'])), '')
  self.assertEqual(self.m.source(dict(sid='1',cover=row['cover'],cover_big=row['cover'])), '')
 def test_safe_dynamic_logo_is_published_under_zero_archive_write_budget(self):
  a=__import__('widget_assets69');dns=__import__('artwork_visible')
  dns._dns_cache[('example.org',443)]=(time.monotonic()+30,True)
  with mock.patch('home_schedule75.applicable',return_value=True),mock.patch('artwork_visible.public_dns',return_value=True),mock.patch('art_storage.check',side_effect=__import__('art_storage').ArtworkFailure('DISK_FULL','RESERVE_BLOCKED',dict(free=240*1024**2,reserve=1024**3,budget=0))),mock.patch('station_logos88.fetch',return_value=__import__('test_xcmate_02988').png()),mock.patch('programme_transport77.verified',side_effect=AssertionError('no new persistence download')):
   a._references82(self.portal,'live',self.rows)
   self.man.prepare(self.portal,self.rows[:2])
   result=self.man.remote(self.portal,self.rows)
  self.assertEqual(len(result),5);self.assertTrue(all(value[0].startswith(self.rows[int(sid)]['stream_icon']) for sid,value in result.items()))
  diag=json.loads(self.properties['XCMate.Logos87.Last']);self.assertEqual(diag['code'],'STORAGE_RESERVE_BLOCKED');self.assertEqual(diag['reserve'],1024**3)
  self.assertNotIn('example.org',json.dumps(diag));self.assertNotIn('SECRET',json.dumps(diag))
 def test_http_private_host_credentials_and_port_are_not_freed_by_storage_failure(self):
  a=__import__('widget_assets69');bad=['http://example.org/l.png','https://127.0.0.1/l.png','https://example.org:8080/l.png','https://example.org/SECRET/l.png','https://example.org/l.png?token=SECRET']
  with mock.patch('home_schedule75.applicable',return_value=True),mock.patch('artwork_visible.public_dns',side_effect=AssertionError('unsafe URL must fail before DNS')):
   for i,url in enumerate(bad):
    row=dict(sid=str(i),stream_icon=url);a._references82(self.portal,'live',[row]);self.assertFalse(self.man.remote(self.portal,[row]))
 def test_full_kodi_decode_receipt_can_be_reused_without_persistent_write(self):
  file=self.folder/'decoded.png';Image.new('RGB',(320,160),(80,130,170)).save(file)
  row=self.rows[0];record=dict(file=str(file),width=320,height=160,sha256=hashlib.sha256(file.read_bytes()).hexdigest())
  with mock.patch('xbmc.executeJSONRPC',create=True,return_value=json.dumps(dict(result=dict(textures=[dict(url=row['stream_icon'])])))),mock.patch('widget_cache82.decoded',return_value=record),mock.patch('sqlite3.connect',side_effect=AssertionError('no artwork SQL')):
   self.m.recover(self.portal,[row])
  self.assertEqual(self.man.read(self.portal,[row])['0'],str(file))
  self.assertEqual(json.loads(self.properties['XCMate.Logos87.Last'])['code'],'TEXTURE_CACHED')
  self.assertFalse(self.m.read(self.portal,[dict(row,stream_icon='https://example.org/other.png')]))
  file.write_bytes(b'corrupt replacement');self.assertFalse(self.m.read(self.portal,[row]))
 def test_foreign_or_invalid_texture_receipt_never_becomes_a_logo(self):
  with mock.patch('xbmc.executeJSONRPC',create=True,return_value=json.dumps(dict(result=dict(textures=[dict(url='https://example.org/foreign.png')])))),mock.patch('widget_cache82.decoded',side_effect=AssertionError('foreign')):
   self.m.recover(self.portal,self.rows[:1])
  self.assertFalse(self.m.read(self.portal,self.rows))
 def test_all_88_sender_names_survive_without_logos_or_artwork_database(self):
  with mock.patch('logo_manifest86.read',return_value={}),mock.patch('logo_manifest86.remote',return_value={}),mock.patch('epg_handoff63.get',return_value=None),mock.patch('sqlite3.connect',side_effect=AssertionError('no SQL')):
   rows=__import__('live_rail86').values(self.portal,self.rows)
  self.assertEqual(len(rows),88);self.assertEqual([row['label'] for row in rows],[row['name'] for row in self.rows]);self.assertTrue(all(row['url'] for row in rows))
 def test_kodi_texture_readability_does_not_claim_own_archive_persistence(self):
  image=self.folder/'kodi.png';Image.new('RGB',(120,60),(20,80,140)).save(image)
  with mock.patch('station_logos87.read',return_value={'0':str(image)}),mock.patch('art_storage.check',side_effect=__import__('art_storage').ArtworkFailure('DISK_FULL','RESERVE_BLOCKED')):
   self.assertEqual(self.man.read(self.portal,self.rows[:1])['0'],str(image))
   self.assertEqual(self.man.read(self.portal,self.rows[:1],with_fallback=False),{})
   self.assertEqual(self.man.prepare(self.portal,self.rows[:1]),'READY')
   self.assertEqual(self.man.read(self.portal,self.rows[:1],with_fallback=False),{})
 def test_auth_scope_is_distinct_from_scheme_host_failure_without_logging_credentials(self):
  for url in ('https://user:SECRET@example.org/logo.png','https://example.org/SECRET/logo.png','https://example.org/logo.png?token=SECRET'):
   self.assertEqual(self.m.blocked_reason(self.portal,url),'AUTH_SCOPE')
  for url in ('http://example.org/logo.png','https://127.0.0.1/logo.png','https://example.org:8080/logo.png'):
   self.assertEqual(self.m.blocked_reason(self.portal,url),'URL_SCHEME_OR_HOST_BLOCKED')
