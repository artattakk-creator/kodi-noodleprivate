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
  with mock.patch.object(m,'fetch',return_value=png()) as fetch,mock.patch('art_storage.check',side_effect=failure),mock.patch('art_storage82.capacity',return_value=dict(capacity82='SAME_VOLUME_VERIFIED',free=20*1024**2,total=4034297856)):
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


 def test_exact_event_cache_recovers_after_restart_without_http_or_new_metadata(self):
  m=__import__('event_cache88');m._due.clear();m._ram.clear();sticky=__import__('sticky_art88')
  art=dict(code='READY',source='tmdb_series',match='EXACT_UNIQUE_TV_TITLE66',role81='backdrop',image_scope57='series_fallback',decoded77=True,image='https://image.tmdb.org/t/p/w1280/a.png'+__import__('programme_urls55').OPTIONS,source_url='https://image.tmdb.org/t/p/w1280/a.png',url_version55=1,url_verified69=True,until=time.time()+20,scope69=__import__('programme_requests68').identity(self.event),profile69=__import__('programme_requests68').scope(),fingerprint=__import__('programme_art46').fingerprint(self.event),policy69=__import__('programme_policy68').negative_scope({}),vote_average88=8.2,vote_count88=200)
  saved=sticky.remember(self.event,art,png((960,540)));self.assertTrue(saved.get('decoded88'));self.assertIn('event88=',saved['image'])
  # The capability contains no raw URL, title, account or token.
  proof=__import__('urllib.parse',fromlist=['parse_qs']).parse_qs(__import__('urllib.parse',fromlist=['urlsplit']).urlsplit(saved['image']).query)['proof88'][0]
  decoded=__import__('base64').urlsafe_b64decode(proof+'='*(-len(proof)%4)).decode()
  for secret in ('https://','image.tmdb.org','Scrubs'):self.assertNotIn(secret,decoded)
  self.assets.shutdown();self.properties.clear()
  file=self.folder/'kodi-event.png';file.write_bytes(png((960,540)))
  record=dict(file=str(file),sha256=hashlib.sha256(file.read_bytes()).hexdigest(),width=960,height=540)
  reply=json.dumps(dict(result=dict(textures=[dict(url=saved['image'],cachedurl='synthetic')])) )
  with mock.patch('xbmc.executeJSONRPC',create=True,return_value=reply),mock.patch('widget_cache82.decoded',return_value=record),mock.patch('programme_transport77.verified',side_effect=AssertionError('no HTTP')),mock.patch('art_storage.check',side_effect=AssertionError('no archive write')):
   recovered=m.recover(self.event);self.assertEqual(recovered['image'],str(file));self.assertEqual(recovered['source'],'tmdb_series');self.assertEqual(recovered['vote_average88'],8.2)
   self.assertFalse(recovered['persisted69']);self.assertEqual(recovered['storage69'],'KODI_TEXTURE_CACHE')
   self.assertIsNone(m.recover(dict(self.event,sid='foreign')))
   self.options['programme_tmdb_optout77']=True;self.assertIsNone(m.recover(self.event));self.options['programme_tmdb_optout77']=False
   m._due.clear()
   with mock.patch('programme_mapping85.epoch',return_value=2):self.assertIsNone(m.recover(self.event))
   with mock.patch('epg_handoff63.profile_scope',return_value='different-profile'):self.assertIsNone(m.recover(self.event))
   with mock.patch('event_cache88.clean',side_effect=ValueError('invalid')):self.assertIsNone(m.recover(self.event))
  self.assertIsNone(m.recover(dict(self.event,stop=time.time()-1)))
  for bad in (saved['image'].replace('127.0.0.1','attacker.example.org'),saved['image']+'&event88=duplicate',saved['image'].replace('body88=','body88=f'),saved['image'].split('&proof88=')[0]+'&proof88=invalid'):
   m._due.clear();m._ram.clear()
   with mock.patch('xbmc.executeJSONRPC',create=True,return_value=json.dumps(dict(result=dict(textures=[dict(url=bad,cachedurl='synthetic')])))),mock.patch('widget_cache82.decoded',side_effect=AssertionError('reject before filesystem')):self.assertIsNone(m.recover(self.event))
  # An invalid older texture entry must not hide a valid later candidate.
  m._due.clear();m._ram.clear()
  with mock.patch('xbmc.executeJSONRPC',create=True,return_value=json.dumps(dict(result=dict(textures=[dict(url=saved['image'],cachedurl='synthetic'),dict(url=bad,cachedurl='synthetic')])))),mock.patch('widget_cache82.decoded',return_value=record):self.assertIsNotNone(m.recover(self.event))

 def test_event_receipt_never_admits_unconfirmed_or_url_fields(self):
  m=__import__('event_cache88')
  with self.assertRaises(ValueError):m.clean(dict(source='tmdb_series',match='PROVISIONAL_TV85'))
  with self.assertRaises(ValueError):m.clean(dict(source='tmdb_series',match='EXACT_UNIQUE_TV_TITLE66',url='https://example.org/private'))

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
   with self.assertRaises(__import__('media_sources43').SourceError) as error:m.fetch(self.portal,'http://images.example.org/a.png',connect=connect)
  self.assertEqual(error.exception.code,'UNSAFE_SOURCE')
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
 def test_expiring_old_replacement_cannot_clear_the_current_receipt(self):
  m=__import__('decoded_assets88');now=time.time()
  try:
   first=m.put('replace88',png((80,40)),now+2)
   second=m.put('replace88',png((82,41)),now+600)
   with mock.patch('time.time',return_value=now+3):
    m.put('trigger88',png((84,42)),now+600)
    self.assertEqual(m.read('replace88')['uri'],second['uri']);self.assertFalse(m.valid('replace88',first['uri']))
  finally:m.shutdown()
 def test_visible_first_five_precede_unseen_cursor_jobs(self):
  m=__import__('station_logos88');rows=[dict(sid=str(i),name='Station',stream_icon='http://images.example.org/'+str(i)+'.png') for i in range(20)];m._due.clear();m._cursor[__import__('logo_manifest86').context(self.portal)]=15
  fetched=[]
  try:
   with mock.patch.object(m,'fetch',side_effect=lambda portal,uri,cancel:(fetched.append(uri) or png())),mock.patch('art_storage.check',side_effect=OSError('reserve')):m.prepare(self.portal,rows)
   self.assertEqual(fetched,[rows[0]['stream_icon'],rows[1]['stream_icon']])
  finally:__import__('decoded_assets88').shutdown()
 def test_profile_switch_eviction_clears_only_the_original_receipt(self):
  m=__import__('decoded_assets88')
  try:
   with mock.patch('epg_handoff63.profile_scope',return_value='profile-A'):
    old=m.put('same-row',png(),time.time()+600);old_slot=m.slot('same-row')
   with mock.patch('epg_handoff63.profile_scope',return_value='profile-B'):
    new=m.put('same-row',png((161,80)),time.time()+600)
    old_path=__import__('urllib.parse',fromlist=['urlsplit']).urlsplit(old['uri']).path
    m._remove(old_path,m._items[old_path])
    self.assertEqual(m.read('same-row')['uri'],new['uri'])
   self.assertFalse(self.properties.get(old_slot))
   with mock.patch('epg_handoff63.profile_scope',return_value='profile-A'):self.assertIsNone(m.read('same-row'))
  finally:m.shutdown()
 def test_native_texture_recovery_after_session_end_needs_no_network_or_metadata_write(self):
  m=__import__('station_logos88');assets=__import__('decoded_assets88');row=dict(sid='88',name='Station',stream_icon='http://images.example.org/logo.png');tag=__import__('logo_manifest86').key(self.portal,row)
  old=assets.put(tag,png(),time.time()+600,kind='logo');uri=old['uri'];assets.shutdown()
  file=self.folder/'kodi-decoded.png';file.write_bytes(png());record=dict(file=str(file),sha256=hashlib.sha256(png()).hexdigest(),width=160,height=80,stamp=[file.stat().st_mtime_ns,file.stat().st_size])
  with mock.patch('xbmc.executeJSONRPC',create=True,return_value=json.dumps(dict(result=dict(textures=[dict(url=uri,cachedurl='synthetic')])))),mock.patch('widget_cache82.decoded',return_value=record),mock.patch.object(m,'fetch',side_effect=AssertionError('no network')),mock.patch('art_storage.check',side_effect=AssertionError('no archive write')):
   m.recover(self.portal,[row])
  self.assertEqual(__import__('logo_manifest86').read(self.portal,[row])['88'],str(file))
  self.assertEqual(__import__('logo_manifest86').read(self.portal,[row],with_fallback=False),{})
  self.assertFalse(m.cached_capability(uri,__import__('logo_manifest86').key(self.portal,dict(row,sid='other'))))
  self.assertFalse(m.cached_capability(uri.replace('127.0.0.1','attacker.example.org'),tag))
 def test_rejected_dns_answer_is_a_source_failure_not_a_worker_crash(self):
  m=__import__('station_logos88');assets=__import__('decoded_assets88');m._due.clear();m._cursor.clear()
  bad=dict(sid='bad',name='Bad source',stream_icon='http://bad.example.org/logo.png');good=dict(sid='good',name='Good source',stream_icon='http://good.example.org/logo.png')
  original=m.fetch
  def dns(host,port,**kw):return [(2,1,6,'',('127.0.0.1' if host=='bad.example.org' else '93.184.216.34',port))]
  def response(*args):
   body=io.BytesIO(png());return __import__('types').SimpleNamespace(status=200,headers={'Content-Type':'image/png'},read=body.read,close=body.close)
  try:
   with mock.patch('socket.getaddrinfo',side_effect=dns),mock.patch.object(m,'fetch',side_effect=lambda p,u,c:original(p,u,c,connect=response)),mock.patch('art_storage.check',side_effect=OSError('reserve')):
    self.assertEqual(m.prepare(self.portal,[bad,good]),'PARTIAL')
   self.assertNotIn('bad',__import__('logo_manifest86').read(self.portal,[bad]));self.assertIn('good',__import__('logo_manifest86').read(self.portal,[good]))
  finally:assets.shutdown()
 def test_two_interpreters_share_one_byte_owner_without_invalidating_visible_images(self):
  import importlib.util,sys
  first=__import__('decoded_assets88');first.shutdown()
  spec=importlib.util.spec_from_file_location('decoded_assets88_second',first.__file__);second=importlib.util.module_from_spec(spec);spec.loader.exec_module(second)
  try:
   a=first.put('interpreter-A',png(),time.time()+600)
   b=second.put('interpreter-B',png((162,82)),time.time()+600)
   self.assertIsNone(second._server);self.assertTrue(first.valid('interpreter-A',a['uri']));self.assertTrue(first.valid('interpreter-B',b['uri']))
   second.shutdown();self.assertTrue(first.valid('interpreter-A',a['uri']))
   import urllib.request
   with urllib.request.urlopen(b['uri'],timeout=3) as response:self.assertEqual(response.read(),png((162,82)))
  finally:second.shutdown();first.shutdown()
