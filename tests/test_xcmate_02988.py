""".88 production regressions; host simulation, never physical Android PASS."""
import hashlib,io,json,threading,time,unittest
from unittest import mock
from PIL import Image
from xcmate027_fixture import Fixture

def png(size=(160,80)):
 b=io.BytesIO();Image.new('RGB',size,(28,122,194)).save(b,format='PNG');return b.getvalue()
class Fix88(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.options.update(programme_tmdb46=True,tmdb_research43=True);self.assets=__import__('decoded_assets88');self.assets.shutdown()
  self.event=dict(pid='p',sid='1',key='event88',title='Scrubs',start=int(time.time())-100,stop=int(time.time())+1200)
 def tearDown(self):
  self.assets.shutdown();super().tearDown()
 def test_public_http_and_https_without_credentials_only(self):
  m=__import__('station_logos88')
  for uri in ('http://images.example.org/station.png','https://images.example.org/station.png?w=160'):
   self.assertTrue(m.network_safe(self.portal,uri))
  for uri in ('http://127.0.0.1/a.png','http://169.254.169.254/a.png','http://localhost/a.png','http://images.example.org:8080/a.png','https://user:pass@images.example.org/a.png','https://images.example.org/../a.png','https://images.example.org/%2e%2e/a.png','https://images.example.org/a.png?token=secret','ftp://images.example.org/a.png'):
   self.assertFalse(m.network_safe(self.portal,uri),uri)
 def test_image_wrapper_is_unwrapped_once_and_traversal_rejected(self):
  m=__import__('station_logos88');self.assertEqual(m.normalize('image://https%3A%2F%2Fimages.example.org%2Fa.png/'),'https://images.example.org/a.png')
  for uri in ('image://image%3A%2F%2Ffoo/','https://images.example.org/a.png|header=secret','special://profile/../../secrets.png'):
   with self.assertRaises(ValueError):(m.local_file(uri) if uri.startswith('special:') else m.normalize(uri))
 def test_verified_bytes_are_served_but_arbitrary_paths_never_fetch_remote(self):
  import urllib.request
  record=self.assets.put('logo88',png(),time.time()+600,kind='logo')
  with urllib.request.urlopen(record['uri'],timeout=3) as response:self.assertEqual(response.read(),png())
  with self.assertRaises(Exception):urllib.request.urlopen(record['uri']+'?url=https://example.org/',timeout=3)
  self.assertEqual(record['storage'],'RAM_ONLY');self.assertTrue(self.assets.valid('logo88',record['uri'],record['sha256']))
  self.assertFalse(self.assets.valid('other',record['uri']))
 def test_invalid_image_and_budget_are_not_published(self):
  with self.assertRaises(__import__('media_sources43').SourceError):self.assets.put('bad',b'fake',time.time()+30)
  with mock.patch.object(self.assets,'MAX_BYTES',1):
   with self.assertRaises(OSError):self.assets.put('budget',png(),time.time()+30)
  self.assertIsNone(self.assets.read('budget'))
 def test_low_space_uses_decoded_ram_without_persisted_claim(self):
  m=__import__('station_logos88');m._due.clear();m._cursor.clear();row=dict(sid='88',name='Station',stream_icon='http://images.example.org/a.png')
  failure=__import__('art_storage').ArtworkFailure('DISK_FULL','RESERVE_BLOCKED',dict(free=239800320,reserve=1073741824,budget=0))
  with mock.patch.object(m,'fetch',return_value=png()) as fetch,mock.patch('art_storage.check',side_effect=failure):
   self.assertEqual(m.prepare(self.portal,[row]),'READY');uri=m.read(self.portal,[row])['88'];m.prepare(self.portal,[row]);self.assertEqual(fetch.call_count,1)
  self.assertTrue(uri.startswith('http://127.0.0.1:'));self.assertEqual(json.loads(self.properties['XCMate.Logos87.Last'])['code'],'STORAGE_RESERVE_BLOCKED')
  self.assertFalse(m.read(self.portal,[dict(row,stream_icon='http://other.example.org/a.png')]))
 def art(self):
  from programme_requests68 import identity,scope
  return dict(key=self.event['key'],fingerprint=__import__('programme_art46').fingerprint(self.event),code='READY',source='tmdb_series',match='EXACT_UNIQUE_TV_TITLE66',image='https://image.tmdb.org/t/p/w500/a.png'+__import__('programme_urls55').OPTIONS,source_url='https://image.tmdb.org/t/p/w500/a.png',url_verified69=True,url_version55=1,until=time.time()+30,decoded77=True,scope69=identity(self.event),profile69=scope(),policy69=__import__('programme_policy68').negative_scope({}))
 def test_sticky_survives_45s_negative_recheck_and_network_loss_for_five_minutes(self):
  m=__import__('sticky_art88');value=self.art();start=time.time()
  saved=m.remember(self.event,value,png((960,540)));self.assertTrue(saved.get('decoded88'))
  with mock.patch('time.time',return_value=start+301),mock.patch('programme_transport77.verified',side_effect=AssertionError('no repeated remote fetch')):
   self.assertTrue(__import__('programme_image69').eligible(saved,self.event))
   self.assertEqual(__import__('programme_requests68').result(self.event,dict(code='IMAGE_LOOKUP_TIMEOUT',source='placeholder'))['image'],saved['image'])
  # This is fake-clock host coverage, not a five-minute native capture.
 def test_event_mapping_account_consent_and_revocation_invalidate_pin(self):
  m=__import__('sticky_art88');saved=m.remember(self.event,self.art(),png((960,540)))
  self.assertFalse(m.valid(saved,dict(self.event,sid='other')))
  self.assertFalse(m.valid(saved,dict(self.event,start=self.event['start']-1)))
  with mock.patch('programme_policy68.negative_scope',return_value='other'):self.assertFalse(m.valid(saved,self.event))
  with mock.patch('widget_refs74.revoked',return_value=True):self.assertFalse(m.valid(saved,self.event))
  self.portal['xc_user']='changed';self.assertFalse(m.valid(saved,self.event))
 def test_status_transport_does_not_strip_verified_session_image(self):
  m=__import__('sticky_art88');saved=m.remember(self.event,self.art(),png((960,540)))
  req=__import__('programme_requests68');req.status(self.event,'LOCAL_IMAGE_READY',saved)
  raw=req._read('status.'+str(int(req.identity(self.event)[:8],16)%req.SLOTS));self.assertEqual(raw['art']['image'],saved['image'])
 def test_bookmark_toggle_is_persistent_idempotent_and_preserves_other_entries(self):
  m=__import__('programme_actions88');self.assertTrue(m.toggle(self.event));self.assertTrue(m.toggle(dict(self.event,sid='2')))
  self.assertFalse(m.toggle(self.event));entries=__import__('guide_bookmarks').entries('p');self.assertEqual([e['sid'] for e in entries],['2'])
  before=(self.folder/'guide_bookmarks_v1.json').read_bytes()
  with self.assertRaises(InterruptedError):m.toggle(self.event,lambda:True)
  self.assertEqual(before,(self.folder/'guide_bookmarks_v1.json').read_bytes())
 def test_timeline_before_during_after_and_real_rating_only(self):
  m=__import__('programme_actions88');e=dict(start=1000,stop=2500)
  self.assertEqual(m.timeline(e,900)[1],0);self.assertIn('beginnt',m.timeline(e,900)[0]);self.assertEqual(m.timeline(e,1750)[1],50);self.assertIn('beendet',m.timeline(e,2600)[0])
  self.assertEqual(m.rating(dict(source='tmdb_series',vote_average88=7.8,vote_count88=20)),'TMDB 7,8/10')
  for value in (dict(source='tvmaze',vote_average88=8,vote_count88=5),dict(source='tmdb_series',vote_average88=8),dict(source='tmdb_series',vote_average88=float('nan'),vote_count88=2)):
   self.assertEqual(m.rating(value),'')
 def test_detail_remote_buttons_and_tune_use_parent_owner_handoff(self):
  import xml.etree.ElementTree as E
  from xcmate027_fixture import ADDON
  r=E.parse(ADDON/'resources/skins/Default/720p/XCMateProgramme46.xml')
  self.assertEqual([r.find(".//control[@id='"+str(cid)+"']/onright").text for cid in (501,502,503)],['502','503','501'])
  parent=mock.Mock();parent._entry_player=(False,'');parent._generation=3;parent._pending_future=None
  with mock.patch('window_lifecycle.capture',return_value={}),mock.patch('guide_playback.request',return_value={'sid':'1'}):
   self.assertTrue(__import__('programme_actions88').tune(parent,self.portal,dict(sid='1',name='Station')))
   self.assertEqual(parent._play_request,{'sid':'1'});self.assertTrue(parent._leaving)
 def test_group_headers_are_not_real_stations(self):
  m=__import__('station_rows88')
  self.assertTrue(m.header(dict(name='##### GERMANY HEVC #####')));self.assertFalse(m.header(dict(name='RTL HD',sid='3')))

class Epg88(Fixture,unittest.TestCase):
 def test_reader_queries_close_their_own_connections_no_facade_close(self):
  reader=__import__('library_index').Reader('p');self.assertFalse(hasattr(reader,'close'))
  db=mock.MagicMock();db.execute.return_value.fetchOne=None
  with mock.patch('library_index.connect',return_value=db):reader._query('SELECT 1')
  db.close.assert_called_once()
 def test_epg_worker_reader_without_close_stays_singleflight_until_shutdown(self):
  m=__import__('epg_refresh74');m._stop.clear();m._wanted.clear();m._due.clear();m._failures86.clear()
  m._wanted[(__import__('epg_handoff63').profile_scope(),'p','1')]=time.monotonic()
  monitor=mock.Mock();monitor.abortRequested.side_effect=[False,False,False,True]
  reader=mock.Mock(spec=['get']);reader.get.return_value=dict(sid='1',name='Station')
  with mock.patch('xbmc.Monitor',return_value=monitor),mock.patch('library_index.Reader',return_value=reader),mock.patch('local_epg.now_next',return_value={'1':{'now':'Same programme'}}),mock.patch('programme_read47.session',return_value=__import__('contextlib').nullcontext()):
   m._run()
  self.assertFalse(m._failures86);reader.get.assert_called_once_with('live','1')

class Transport88(Fixture,unittest.TestCase):
 def test_http_custom_port_is_scoped_to_existing_provider_origin(self):
  m=__import__('station_logos88');portal=dict(self.portal,xc_host='http://provider.example.org:8080')
  self.assertTrue(m.network_safe(portal,'http://provider.example.org:8080/logos/1.png'))
  self.assertFalse(m.network_safe(portal,'http://other.example.org:8080/logos/1.png'))
 def test_cross_host_redirect_is_rejected_without_forwarding_credentials(self):
  m=__import__('station_logos88');response=mock.Mock(status=302,headers={'Location':'https://other.example.org/a.png'})
  with self.assertRaises(__import__('media_sources43').SourceError) as failure:
   m.fetch(self.portal,'https://images.example.org/a.png',connect=lambda *a:response,resolver=lambda url:['93.184.216.34'])
  self.assertEqual(failure.exception.code,'REDIRECT_BLOCKED');response.close.assert_called()
 def test_redirect_loop_invalid_image_and_mime_fail_closed(self):
  m=__import__('station_logos88')
  for response in (mock.Mock(status=302,headers={'Location':'/a.png'}),mock.Mock(status=200,headers={'Content-Type':'text/html'})):
   with self.assertRaises(__import__('media_sources43').SourceError):m.fetch(self.portal,'https://images.example.org/a.png',connect=lambda *a:response,resolver=lambda url:['93.184.216.34'])
 def test_actual_dns_rebinding_to_private_or_mixed_addresses_is_rejected(self):
  m=__import__('station_logos88');connect=mock.Mock(side_effect=AssertionError('SSRF request'))
  with mock.patch('socket.getaddrinfo',return_value=[(2,1,6,'',('127.0.0.1',80))]):
   with self.assertRaises(Exception):m.fetch(self.portal,'http://images.example.org/a.png',connect=connect)
  connect.assert_not_called()
 def test_low_space_bridge_is_not_written_as_persistent_metadata(self):
  m=__import__('programme_session69');value=dict(decoded88=True,image='http://127.0.0.1:1/capability')
  with mock.patch('programme_index46.publish_result69',side_effect=AssertionError('RAM receipt is not durable')):result=m.persist({},value)
  self.assertFalse(result['persisted69']);self.assertEqual(result['storage69'],'RAM_ONLY')
 def test_storage_inventory_is_read_only_and_does_not_claim_unknown_pool(self):
  m=__import__('storage_report88')
  with mock.patch('os.replace',side_effect=AssertionError('no writes')),mock.patch('os.unlink',side_effect=AssertionError('no deletion')):
   result=m.collect()
  self.assertEqual(result['logos']['pool_comparison'],'TARGET_VOLUME_UNVERIFIED')
  self.assertNotIn('path',json.dumps(result));self.assertTrue(all(v['orphan_status']=='NOT_PROVEN' for v in result['inventory']))
 def test_ram_logo_reaches_hero_with_scoped_proof_and_separate_persisted_count(self):
  assets=__import__('decoded_assets88');row=dict(sid='1',name='Station',stream_icon='http://images.example.org/a.png');key=__import__('logo_manifest86').key(self.portal,row)
  assets.put(key,png(),time.time()+600,kind='logo')
  try:
   item=__import__('live_rail86').values(self.portal,[row])[0]
   self.assertEqual(item['props']['XCMate.HeroArtSource63'],'station_logo');self.assertEqual(item['props']['XCMate.HeroImage63'],item['art']['poster'])
   receipt=json.loads(self.properties['XCMate.Home86.Rail']);self.assertEqual((receipt['local'],receipt['ram']),(0,1))
   bad=dict(item['props'],**{'XCMate.MediaId':'other'});self.assertEqual(__import__('station_logos88').reference(bad),'')
  finally:assets.shutdown()
