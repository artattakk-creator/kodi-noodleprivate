"""Display references survive a 27 MiB archive block; Android is NOT_TESTED."""
import importlib,json,os,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture

class Visible84(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.a=importlib.import_module('widget_assets69');self.display=importlib.import_module('artwork_display84')
  self.config=importlib.import_module('artwork_config');self.config.initialize();self.config.choose('internal')
  self.rows=[dict(sid=str(i),name='Synthetic '+str(i),cover='https://images.example.org/poster-'+str(i)+'.jpg',kind='vod') for i in range(24)]
 def low(self):
  cap=dict(free=27*1024**2,total=4*1024**3,reserve=1024**3,storage_availability='AVAILABLE')
  with mock.patch('art_storage.capacity',return_value=cap):self.assertTrue(self.display.observe(force=True))
 def approve(self,kind='vod',rows=None):
  import artwork_visible
  def dns(url):
   from urllib.parse import urlsplit
   artwork_visible._dns_cache[(urlsplit(url).hostname,443)]=(time.monotonic()+30,True);return True
  with mock.patch.object(artwork_visible,'public_dns',side_effect=dns):self.a._references82(self.portal,kind,rows or self.rows)
 def test_twenty_four_internal_posters_reach_real_listitems_without_optional_files(self):
  self.low();before=self.config.read();files={p:p.read_bytes() for p in self.folder.rglob('*') if p.is_file()}
  with mock.patch('tempfile.mkstemp',side_effect=AssertionError('optional metadata write')):self.approve()
  result=self.a.read(self.portal,'vod',self.rows);self.assertEqual(len(result),24)
  from widget_items45 import describe,item
  for row in self.rows:
   value=describe(self.portal,'vod',row,{},assets47=result[row['sid']])
   self.assertTrue(value['art']['poster'].startswith(row['cover']+'|redirect-limit=0'))
   self.assertEqual(item(value).art['poster'],value['art']['poster'])
  self.assertEqual(self.config.read(),before)
  self.assertEqual({p:p.read_bytes() for p in self.folder.rglob('*') if p.is_file()},files)
 def test_healthy_internal_mode_does_not_admit_uncached_remote_uri(self):
  self.approve();self.assertEqual(self.a.read(self.portal,'vod',self.rows),{})
 def test_expired_dns_lease_cannot_be_reused_on_a_new_widget_request(self):
  self.low();self.approve();future=time.time()+31
  with mock.patch('time.time',return_value=future):self.assertEqual(self.a.read(self.portal,'vod',self.rows),{})
 def test_private_hosts_and_provider_credentials_never_reach_display(self):
  self.low()
  urls=['https://127.0.0.1/private.jpg','https://internal.local/logo.jpg','https://public.example.org/'+str(self.portal.get('xc_pass') or 'private')+'/x.jpg','https://public.example.org/x.jpg?token=secret']
  rows=[dict(sid=str(i),name='Unsafe',cover=url,kind='vod') for i,url in enumerate(urls)]
  self.approve(rows=rows);self.assertEqual(self.a.read(self.portal,'vod',rows),{})
 def test_changed_account_or_sid_cannot_reuse_approved_source(self):
  self.low();self.approve()
  self.assertEqual(self.a.read(dict(self.portal,xc_pass='changed-private-value'),'vod',self.rows),{})
  self.assertEqual(self.a.read(self.portal,'vod',[dict(self.rows[0],sid='other')]),{})
 def test_source_block_is_not_a_claim_of_kodi_texture_success(self):
  self.low()
  with mock.patch('artwork_visible.public_dns',return_value=False):self.a._references82(self.portal,'vod',self.rows)
  self.assertEqual(self.a.read(self.portal,'vod',self.rows),{})
 def test_low_space_stops_new_archive_enrolment_without_resetting_jobs_or_mode(self):
  self.low();import media_art
  before=dict(media_art._inbox)
  with mock.patch('threading.Thread',side_effect=AssertionError('archive enrol restarted')):media_art.request(self.rows)
  self.assertEqual(media_art._inbox,before);self.assertEqual(self.config.read()['mode'],'internal')
 def test_live_gate_changes_when_a_provider_reference_becomes_available(self):
  import widget_live47
  before=widget_live47.signature(self.portal,self.rows[:1]);self.low();self.approve(kind='live',rows=self.rows[:1])
  self.assertNotEqual(before,widget_live47.signature(self.portal,self.rows[:1]))

class EventDisplay84(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.display=importlib.import_module('programme_display84');self.art=importlib.import_module('programme_art46')
  self.options.update(programme_tmdb46=True,tmdb_research43=True,programme_tvmaze67=True)
  self.channel=dict(sid='1',name='Synthetic channel',stream_icon='https://images.example.org/logo.jpg')
  self.raw=dict(title='Synthetic Film',start=self.now-30,stop=self.now+1800,genre='Spielfilm',year=2024,_metadata_verified48=True,xmltv_image='https://image.tmdb.org/t/p/w500/synthetic84.png')
  self.event=importlib.import_module('programme_events46').describe(self.portal,self.channel,self.raw,'canonical',('revision',1))
  self.uri=self.raw['xmltv_image']
 def approved(self):
  from programme_requests68 import identity,scope
  from programme_policy68 import negative_scope
  from programme_urls55 import OPTIONS
  return dict(key=self.event['key'],fingerprint=self.art.fingerprint(self.event),code='READY',source='xmltv_event',match='EXACT_EVENT',source_url=self.uri,image=self.uri+OPTIONS,thumbnail=self.uri+OPTIONS,url_version55=1,url_verified69=True,scope69=identity(self.event),profile69=scope(),policy69=negative_scope({}),until=time.time()+300,decoded77=True,image_width77=320,image_height77=180)
 def dns(self,url):
  from urllib.parse import urlsplit
  import artwork_visible
  artwork_visible._dns_cache[(urlsplit(url).hostname,443)]=(time.monotonic()+30,True);return True
 def publish(self):
  with mock.patch('artwork_visible.public_dns',side_effect=self.dns):return self.display.remember(self.event,self.approved())
 def test_ram_only_event_is_admitted_for_at_most_thirty_seconds_without_db(self):
  value=self.publish();self.assertTrue(value['display84']);self.assertEqual(value['storage69'],'RAM_ONLY')
  self.assertLessEqual(value['until']-time.time(),30)
  with mock.patch('sqlite3.connect',side_effect=AssertionError('optional DB')),mock.patch('socket.getaddrinfo',side_effect=AssertionError('GUI DNS')):
   self.assertEqual(self.art.cached(self.event)['image'],value['image'])
 def test_expired_reference_is_rejected_and_worker_can_renew_without_refetch(self):
  value=self.publish();now=time.time()
  with mock.patch('time.time',return_value=now+31):
   self.assertEqual(self.display.read(self.event),{})
   with mock.patch('artwork_visible.public_dns',side_effect=self.dns),mock.patch('programme_transport77.verified',side_effect=AssertionError('unnecessary refetch')):
    renewed=self.display.renew(self.event)
   self.assertTrue(renewed);self.assertLessEqual(renewed['until']-(now+31),30)
  with mock.patch('time.time',return_value=now+301):self.assertIsNone(self.display.renew(self.event))
 def test_wrong_event_channel_edition_source_and_mapping_never_inherit_image(self):
  self.publish()
  for field,changed in (('sid','2'),('start',self.event['start']+1),('title','Other Film'),('year',2025),('epg_source46','different'),('xmltv_image',self.uri+'different'),('revision',('revision',2))):
   self.assertEqual(self.display.read(dict(self.event,**{field:changed})),{},field)
 def test_changed_source_consent_and_token_policy_revokes_display(self):
  self.publish();self.options['programme_tvmaze67']=False
  self.assertEqual(self.display.read(self.event),{})
 def test_unsafe_dns_after_success_cannot_renew_a_display_lease(self):
  value=self.publish()
  with mock.patch('artwork_visible.public_dns',return_value=False):self.assertIsNone(self.display.renew(self.event))
  self.assertEqual(self.display.read(self.event)['image'],value['image'])
 def test_placeholder_update_cannot_erase_unexpired_exact_event_lease(self):
  value=self.publish()
  with mock.patch('programme_requests68.result',return_value=dict(code='CACHE_ERROR',source='placeholder',until=time.time()+20)):
   self.assertEqual(self.art.cached(self.event)['image'],value['image'])
 def test_real_decoded_png_resolve_reaches_cross_interpreter_properties_with_no_archive(self):
  import io,types
  from PIL import Image
  out=io.BytesIO();Image.new('RGB',(320,180),(30,100,150)).save(out,'PNG');body=out.getvalue()
  def check(url,cancel=lambda:False):
   stream=io.BytesIO(body)
   response=types.SimpleNamespace(status=200,headers={'Content-Type':'image/png'},read=stream.read,close=stream.close)
   return importlib.import_module('programme_transport77').verified(url,cancel=cancel,connect=lambda *a:response,resolver=lambda u:['93.184.216.34'],keep_data81=True)
  usage=types.SimpleNamespace(free=27*1024**2,total=4*1024**3,used=4*1024**3-27*1024**2)
  before={p:p.read_bytes() for p in self.folder.rglob('*') if p.is_file()}
  with mock.patch('shutil.disk_usage',return_value=usage),mock.patch('artwork_visible.public_dns',side_effect=self.dns):
   result=importlib.import_module('programme_urls55').resolve(self.event,url_mode69=True,check=check)
  self.assertTrue(result['decoded77']);self.assertTrue(result['display84']);self.assertEqual(result['storage69'],'RAM_ONLY')
  importlib.import_module('programme_requests68').completed(self.event,result)
  self.assertEqual(self.art.cached(self.event)['image'],result['image'])
  self.assertEqual({p:p.read_bytes() for p in self.folder.rglob('*') if p.is_file()},before)
 def test_ram_only_data_without_image_decode_is_not_promoted_to_display_proof(self):
  value=self.approved();value.pop('decoded77')
  with mock.patch('artwork_visible.public_dns',side_effect=AssertionError('unverified body')):
   self.assertNotIn('display84',self.display.remember(self.event,value))

class Recovery84(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.assets=importlib.import_module('widget_assets69');self.display=importlib.import_module('artwork_display84')
  self.config=importlib.import_module('artwork_config');self.config.initialize();self.config.choose('internal')
  cap=dict(free=27*1024**2,total=4*1024**3,reserve=1024**3,storage_availability='AVAILABLE')
  with mock.patch('art_storage.capacity',return_value=cap):self.display.observe(force=True)
  self.rows=[dict(sid=str(i),name='Synthetic '+str(i),cover='https://images.example.org/poster-'+str(i)+'.png',kind='vod') for i in range(24)]
 def approve(self,kind='vod',rows=None,portal=None):
  from urllib.parse import urlsplit
  import artwork_visible
  def dns(url):artwork_visible._dns_cache[(urlsplit(url).hostname,443)]=(time.monotonic()+30,True);return True
  with mock.patch('artwork_visible.public_dns',side_effect=dns):self.assets._references82(portal or self.portal,kind,rows or self.rows)
 def test_readonly_publication_uses_existing_routes_and_no_snapshot_or_sql_writes(self):
  self.approve();from widget_live47 import publish
  with mock.patch('tempfile.mkstemp',side_effect=AssertionError('snapshot file write')),mock.patch('programme_assets47.writer',side_effect=AssertionError('SQLite writer')):
   self.assertTrue(publish(self.portal,'vod',self.rows))
  receipt=importlib.import_module('home_prepared76').proof(self.portal,'vod',self.rows)
  self.assertEqual((receipt['count'],receipt['images']),(24,24))
  self.assertIsNone(importlib.import_module('home_prepared76').proof(self.portal,'vod',[dict(self.rows[0],cover='https://other.example.org/p.png')]+self.rows[1:]))
 def test_first_live_listitem_already_has_hero_logo_before_event_image_ready(self):
  row=dict(self.rows[0],kind='live');self.approve('live',[row]);refs=self.assets.read(self.portal,'live',[row])['0']
  value=importlib.import_module('live_items62').values(self.portal,[row])[0]
  self.assertEqual(value['props']['XCMate.HeroImage63'],refs['poster'])
  self.assertEqual(value['props']['XCMate.HeroArtSource63'],'station_logo')
 def test_visible_five_logos_are_checked_before_the_rest_of_88(self):
  rows=[dict(sid=str(i),name='Station '+str(i),cover='https://images.example.org/logo-'+str(i)+'.png',kind='live') for i in range(88)]
  portal=dict(self.portal,start_stream_id='17')
  self.approve('live',rows,portal);first=self.assets.read(portal,'live',rows)
  self.assertEqual(set(first),{'17','18','19','20','21'})
  self.approve('live',rows,portal);self.assertEqual(len(self.assets.read(portal,'live',rows)),88)
 def test_logo_fallback_is_proven_separately_and_not_counted_as_event_image(self):
  row=dict(self.rows[0],kind='live');self.approve('live',[row])
  uri=self.assets.read(self.portal,'live',[row])['0']['poster']
  props={'XCMate.PortalId':self.portal['id'],'XCMate.MediaId':'0','XCMate.ProgrammeLogo46':uri,'XCMate.ProgrammeImage46':'','XCMate.ProgrammeKey47':'none'}
  props['XCMate.LogoProof84']=self.display.logo_proof(self.portal,row,uri)
  importlib.import_module('live_text63')._hero(props)
  self.assertEqual(props['XCMate.HeroImage63'],uri);self.assertEqual(props['XCMate.HeroArtSource63'],'station_logo')
  props['XCMate.MediaId']='other';importlib.import_module('live_text63')._hero(props)
  self.assertFalse(props['XCMate.HeroImage63'])
 def test_expired_logo_cannot_be_admitted_as_new_hero_fallback(self):
  row=dict(self.rows[0],kind='live');self.approve('live',[row]);uri=self.assets.read(self.portal,'live',[row])['0']['poster']
  props={'XCMate.PortalId':self.portal['id'],'XCMate.MediaId':'0','XCMate.ProgrammeLogo46':uri,'XCMate.LogoProof84':self.display.logo_proof(self.portal,row,uri)}
  with mock.patch('time.time',return_value=time.time()+31):self.assertEqual(self.display.logo_reference(props),'')
 def test_texture_decode_failure_is_not_promoted_to_a_local_picture(self):
  from widget_cache82 import decoded
  with mock.patch('widget_cache79.permitted',return_value=False):self.assertIsNone(decoded(dict(cachedurl='/unapproved/foreign.png'),'https://images.example.org/p.png'))
 def test_rollover_keeps_real_logo_and_updates_text_instead_of_old_event_image(self):
  from PIL import Image
  logo=self.folder/'real-logo.png';old=self.folder/'old-event.png'
  Image.new('RGB',(160,80),(20,100,150)).save(logo);Image.new('RGB',(320,180),(130,20,10)).save(old)
  props={'XCMate.ProgrammeKey47':'old-event','XCMate.ProgrammeImage46':str(old),'XCMate.ProgrammeLogo46':str(logo),'XCMate.ProgrammeArtSource57':'xmltv_event'}
  info=dict(programme_key47='new-event',now='New programme',next='Next programme',description='Current plot',progress=.4,remaining=600,start=self.now,stop=self.now+1000,now_time='10:00',now_end_time='11:00',next_time='11:00',next_end_time='12:00')
  value=importlib.import_module('live_text63').apply(dict(props=props),self.portal,dict(sid='0'),info,labels=('No EPG','{} min'))
  self.assertEqual(value['props']['XCMate.HeroImage63'],str(logo));self.assertEqual(value['props']['XCMate.HeroArtSource63'],'station_logo')
  self.assertEqual(value['props']['XCMate.ProgrammeTitle46'],'New programme');self.assertEqual(value['props']['XCMate.ProgrammePercent46'],'40')
 def test_expired_remote_logo_uses_verified_exact_kodi_file_without_reload(self):
  from PIL import Image
  row=dict(self.rows[0],kind='live');self.approve('live',[row]);uri=self.assets.read(self.portal,'live',[row])['0']['poster']
  props={'XCMate.PortalId':self.portal['id'],'XCMate.MediaId':'0','XCMate.ProgrammeLogo46':uri,'XCMate.LogoProof84':self.display.logo_proof(self.portal,row,uri)}
  picture=self.folder/'cached-logo.png';Image.new('RGB',(160,80),(20,100,150)).save(picture)
  from widget_cache82 import remember
  st=picture.stat();record=dict(file=str(picture),source=row['cover'],sha256='a'*64,stamp=[st.st_mtime_ns,st.st_size],state='POSITIVE_LOCAL')
  remember(self.portal,'live',row,'poster',row['cover'],record)
  with mock.patch('widget_cache79.permitted',return_value=True),mock.patch('time.time',return_value=time.time()+31),mock.patch('socket.getaddrinfo',side_effect=AssertionError('offline GUI DNS')):
   self.assertEqual(self.display.logo_reference(props),str(picture))
   props['XCMate.MediaId']='different';self.assertEqual(self.display.logo_reference(props),'')
 def test_cold_event_recovers_only_its_exact_xmltv_texture_without_network_or_db(self):
  import io
  from PIL import Image
  out=io.BytesIO();Image.new('RGB',(160,90),(20,100,140)).save(out,'PNG');body=out.getvalue()
  textures=self.folder/'Thumbnails';textures.mkdir();picture=textures/'cold84.png';picture.write_bytes(body)
  event=importlib.import_module('programme_events46').describe(self.portal,dict(sid='1',name='Station'),dict(title='Synthetic movie',start=self.now-30,stop=self.now+1800,icon='https://image.tmdb.org/t/p/w500/cold84.png'),'xml',1)
  # Trusted source metadata is available in the local EPG, independent of the
  # optional artwork DB. Texture ownership and full PNG decode remain real.
  event['xmltv_image']='https://image.tmdb.org/t/p/w500/cold84.png'
  source=event['xmltv_image'];record=dict(url=source,cachedurl=str(picture),sizes=[dict(width=160,height=90)])
  import xbmc,xbmcvfs
  def translate(value):return str(textures) if value.startswith('special://thumbnails') else value
  response=json.dumps(dict(result=dict(textures=[record])))
  def kodi21(request):
   data=json.loads(request);self.assertEqual(data['method'],'Textures.GetTextures')
   self.assertEqual(set(data['params']),{'properties','filter'})
   return response
  with mock.patch.object(xbmc,'executeJSONRPC',side_effect=kodi21,create=True),mock.patch.object(xbmcvfs,'translatePath',side_effect=translate),mock.patch('socket.getaddrinfo',side_effect=AssertionError('cold network')),mock.patch('sqlite3.connect',side_effect=AssertionError('cold SQL writer')):
   result=importlib.import_module('programme_display84').recover(event)
   self.assertEqual(result['image'],str(picture));self.assertEqual(result['storage69'],'KODI_TEXTURE_CACHE')
   self.assertIsNone(importlib.import_module('programme_display84').recover(dict(event,xmltv_image=source+'?width=300')))
  self.assertEqual(picture.read_bytes(),body);self.assertEqual(self.config.read()['mode'],'internal')

class Isolation84(Fixture,unittest.TestCase):
 def setUp(self):
  Fixture.setUp(self);self.display=importlib.import_module('programme_display84');self.art=importlib.import_module('programme_art46')
  self.options.update(programme_tmdb46=True,tmdb_research43=True,programme_tvmaze67=True)
  self.channel=dict(sid='1',name='Synthetic channel',stream_icon='https://images.example.org/logo.jpg')
  self.raw=dict(title='Synthetic Film',start=self.now-30,stop=self.now+1800,genre='Spielfilm',year=2024,_metadata_verified48=True,xmltv_image='https://image.tmdb.org/t/p/w500/synthetic84.png')
  self.event=importlib.import_module('programme_events46').describe(self.portal,self.channel,self.raw,'canonical',('revision',1))
  self.uri=self.raw['xmltv_image']
 publish=EventDisplay84.publish
 approved=EventDisplay84.approved
 dns=EventDisplay84.dns
 def test_definitive_dns_rejection_revokes_a_previously_approved_event(self):
  self.publish()
  import artwork_visible
  artwork_visible._dns_cache[('image.tmdb.org',443)]=(time.monotonic()+30,False)
  self.assertEqual(self.display.read(self.event),{})
 def test_new_account_cannot_read_old_event_receipt(self):
  self.publish()
  with mock.patch('portals.get_by_id',return_value=dict(self.portal,xc_pass='changed-only-in-test')):
   self.assertEqual(self.display.read(self.event),{})
 def test_other_kodi_profile_cannot_read_event_receipt(self):
  self.publish()
  with mock.patch('programme_requests68.scope',return_value='another-profile'):
   self.assertEqual(self.display.read(self.event),{})
 def test_missing_pressure_receipt_does_not_admit_internal_provider_urls(self):
  from artwork_display84 import state,enabled
  self.assertEqual(state(),{});self.assertFalse(enabled())
