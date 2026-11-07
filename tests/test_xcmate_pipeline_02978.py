"""Exact-source HTTPS, existing widgets, native anchor and late ACK evidence."""
import importlib,io,time,types,unittest
from unittest import mock
from pathlib import Path
from xcmate027_fixture import Fixture
import test_xcmate_home_02974 as old_home
import test_xcmate_media_stop_02977 as old_exit

class References78(Fixture,unittest.TestCase):
 def test_public_http_reference_is_upgraded_without_plaintext_request(self):
  m=importlib.import_module('image_reference78')
  self.assertEqual(m.canonical('http://pictures.example.org/a b.png?width=640'),'https://pictures.example.org/a%20b.png?width=640')
  for url in ('http://localhost/x.png','https://10.0.0.1/x.png','https://user:pass@public.example.org/a.png','https://public.example.org/a.png?token=private','https://public.example.org/../x.png','https://public.example.org/x.png|Authorization=private'):
   self.assertFalse(m.canonical(url))
 def test_unicode_source_and_resize_parameters_without_host_wildcard(self):
  m=importlib.import_module('image_reference78');self.assertEqual(m.canonical('https://images.example.org/Ä.png?width=640&amp;height=360'),'https://images.example.org/%C3%84.png?width=640&height=360')
  assets=importlib.import_module('widget_assets69');self.assertTrue(assets.safe(self.portal,'https://public.example.org/cover.png?width=640'));self.assertFalse(assets.safe(self.portal,'https://public.example.org/cover.png?auth=secret'))
 def test_exact_xmltv_reference_verified_over_https_and_shared(self):
  from PIL import Image
  out=io.BytesIO();Image.new('RGB',(160,90),(50,120,80)).save(out,'PNG');data=out.getvalue();seen=[]
  event=dict(pid='p',sid='1',canonical='xml',key='a'*64,title='Synthetic current programme',start=int(time.time())-30,stop=int(time.time())+3600,xmltv_image='http://pictures.example.org/current.png',placeholder='')
  transport=importlib.import_module('programme_transport77');urls=importlib.import_module('programme_urls55')
  def connect(url,ips,headers):
   self.assertEqual(url,'https://pictures.example.org/current.png');self.assertNotIn('Authorization',headers);seen.append(url);stream=io.BytesIO(data)
   return types.SimpleNamespace(status=200,headers={'Content-Type':'image/png'},read=stream.read,close=stream.close)
  def probe(url,cancel=lambda:False):return transport.verified(url,cancel,connect=connect,resolver=lambda u:['93.184.216.34'])
  with mock.patch.object(urls,'probe',side_effect=probe):result=urls.resolve(event,allow_lookup=False,url_mode69=True)
  self.assertEqual(result['code'],'READY');self.assertTrue(result['decoded77']);self.assertEqual(len(seen),1);self.assertEqual(result['source'],'xmltv_event')
 def test_temporary_dns_retains_verified_cover_but_private_dns_revokes(self):
  refs=importlib.import_module('widget_refs74');visible=importlib.import_module('artwork_visible');row=dict(sid='1',name='Synthetic',cover='https://public.example.org/cover.png')
  refs.remember_many(self.portal,'vod',[('1','poster',row['cover'],30)])
  key=('public.example.org',443);visible._dns_cache.pop(key,None)
  with mock.patch('socket.getaddrinfo',side_effect=OSError('temporary')):self.assertFalse(visible.public_dns(row['cover']))
  self.assertIn('1',refs.read(self.portal,'vod',[row]));self.assertFalse(refs.revoked(row['cover']))
  visible._dns_cache.pop(key,None)
  with mock.patch('socket.getaddrinfo',return_value=[(2,1,6,'',('10.0.0.5',443))]):self.assertFalse(visible.public_dns(row['cover']))
  self.assertNotIn('1',refs.read(self.portal,'vod',[row]));self.assertTrue(refs.revoked(row['cover']))

class Reload78(Fixture,unittest.TestCase):
 def test_only_own_generated_paths_receive_reload_foreign_cinema_unchanged(self):
  m=importlib.import_module('widget_reload78');foreign=b'<control id="999"><label>Neu im Kino</label><content target="videos">plugin://foreign.cinema/?mode=now_playing</content></control>'
  original=b'<includes><control id="2510"><content target="videos">plugin://plugin.video.xtreammate/?action=widget_recent_vod&amp;pid=p</content></control>'+foreign+b'</includes>'
  result=m.candidate(original);self.assertIn(foreign,result);self.assertIn(b'XCMate.Widget45.Reload.vod',result);self.assertEqual(m.candidate(result),result)
 def test_builtin_misused_as_directory_unwrapped_only_for_own_plugin(self):
  m=importlib.import_module('widget_reload78');raw=b'<includes><control id="2520"><content target="videos">ActivateWindow(Videos,&quot;plugin://plugin.video.xtreammate/?action=widget_recent_series&amp;pid=p&quot;,return)</content></control></includes>'
  result=m.candidate(raw);self.assertNotIn(b'ActivateWindow',result);self.assertIn(b'action=widget_recent_series',result);self.assertIn(b'Reload.series',result)
 def test_pidless_existing_sources_resolve_only_the_actual_active_portal(self):
  m=importlib.import_module('widget_consumer58');url='plugin://plugin.video.xtreammate/?action=widget_recent_vod'
  with mock.patch('portals.get_active',return_value=[self.portal]):
   self.assertEqual(m.identity(url,'p'),'vod');self.assertIsNone(m.identity(url,'other'));self.assertIsNone(m.identity(url+'&pid=other','p'))
 def test_root_home_is_native_anchor_without_reentrant_dispatch(self):
  nav=importlib.import_module('window_navigation');router=types.SimpleNamespace(_handle=-1,url=mock.Mock(side_effect=AssertionError('recursive root dispatch')))
  with mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('xbmcgui.getCurrentWindowDialogId',return_value=9999),mock.patch('xbmc.getInfoLabel',return_value=''),mock.patch('xbmc.executebuiltin') as call:
   self.assertTrue(nav._anchor_home(router,self.portal,'a'*32));call.assert_not_called()
 def test_uri_boundary_quotes_once_and_rejects_injection(self):
  nav=importlib.import_module('navigation_builtin78');url='plugin://plugin.video.xtreammate/?action=xcmate_home&pid=p'
  self.assertEqual(nav.activate(nav.activate(url)),nav.activate(url))
  for value in ('plugin://foreign.addon/','plugin://plugin.video.xtreammate/"),RunScript(evil)','RunScript(evil)'):
   with self.assertRaises(ValueError):nav.activate(value)

class Generations78(unittest.TestCase):
 def test_same_size_stale_writer_never_replaces_committed_catalogue(self):
  m=old_home.Home74(methodName='runTest');m.setUp();self.addCleanup(m.doCleanups)
  old=m.rows();m.frame(old,revision=1);new=[dict(row,sid=str(100+i)) for i,row in enumerate(m.rows())];m.frame(new,revision=2)
  before=Path(m.w.path('p','vod')).read_bytes();m.w.publish(m.portal,'vod',old)
  self.assertEqual(Path(m.w.path('p','vod')).read_bytes(),before);self.assertEqual([v['props']['XCMate.MediaId'] for v in m.w.read('p','vod')['items']],[v['sid'] for v in new])
 def test_late_ack_finishes_original_job_without_second_stop(self):
  m=old_exit.MediaStop77(methodName='runTest');m.setUp();self.addCleanup(m.doCleanups);m.post();value=m.jobs.state();value['deadline']=0;m.jobs.save(value)
  with mock.patch('xbmc.Player',side_effect=AssertionError('native mutex')):m.jobs.poll();self.assertTrue(m.jobs.blocked())
  self.assertEqual(m.jobs.state()['result'],'AWAITING_NATIVE_ACK');self.assertEqual(m.commands.count('PlayerControl(Stop)'),1)
  m.ack();self.assertEqual(m.jobs.state()['phase'],'complete');self.assertTrue(m.jobs.state()['late_ack78']);self.assertEqual(m.commands.count('PlayerControl(Stop)'),1)

class Alias78(Fixture,unittest.TestCase):
 def test_noncurrent_stream_alias_does_not_mask_current_provider_programme(self):
  events=importlib.import_module('programme_events46');now=int(time.time())
  class View(dict):canonical={'sid':'expired','xml':'provider'};revision=1
  def row(title,start,stop):return dict(name=title,descr='',start_timestamp=start,stop_timestamp=stop)
  view=View(sid=[row('Old',now-1000,now-900)],xml=[row('Current',now-30,now+600)])
  with mock.patch('local_epg.channel_keys',return_value=('1',['sid','xml'])),mock.patch('local_epg.window',return_value=view),mock.patch.object(events,'describe',side_effect=lambda p,c,e,k,r:dict(event=e,canonical=k)):
   result=events.load(self.portal,dict(sid='1',name='Station'),now=now)
  self.assertEqual(result['event']['title'],'Current');self.assertEqual(result['canonical'],'provider')
 def test_static_reload_value_is_preserved_and_real_reload_hook_added(self):
  m=importlib.import_module('widget_reload78');raw=b'<includes><content>plugin://plugin.video.xtreammate/?action=widget_recent_vod&amp;pid=p&amp;reload=keep-movies</content></includes>'
  value=m.candidate(raw);self.assertIn(b'reload=keep-movies',value);self.assertIn(b'XCMate.Widget45.Reload.vod',value);self.assertEqual(m.candidate(value),value)
