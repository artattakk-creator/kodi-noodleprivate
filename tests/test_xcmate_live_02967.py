"""Live-only transport, credential-safe diagnostics and bounded source failures."""
import importlib,io,json,types,unittest,urllib.error
from unittest import mock
from xcmate027_fixture import Fixture,ListItem
class Item67(ListItem):
 def setPath(self,v):self.path=v
 def getPath(self):return self.path
 def setMimeType(self,v):self.mime=v
 def setContentLookup(self,v):self.lookup=v
class Live67(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.player=importlib.import_module('player')
  import importlib.util
  from xcmate027_fixture import LIB
  spec=importlib.util.spec_from_file_location('actual_xtream67',LIB/'xtream.py');self.xcmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.xcmod)
  self.client=self.xcmod.XtreamClient('https://provider.example.test','synthetic','fixture')
 def item(self,url,live=True):
  with mock.patch.object(self.player.xbmcgui,'ListItem',Item67),mock.patch.object(self.player,'_isa_available',return_value=True):
   return self.player.build_playable_item(url,live67=live)
 def test_known_ts_uses_native_transport_and_skips_content_head_lookup(self):
  item=self.item(self.client.live_stream_url('1'));self.assertNotIn('inputstream',item.props);self.assertEqual(item.mime,'video/mp2t');self.assertFalse(item.lookup)
 def test_extensionless_live_does_not_invent_an_hls_manifest(self):
  item=self.item('https://provider.example.test/live/u/p/1')
  self.assertNotIn('inputstream',item.props)
 def test_explicit_hls_keeps_isa_and_both_header_paths(self):
  item=self.item('https://provider.example.test/live/u/p/2.m3u8|Referer=https%3A%2F%2Fprovider.example.test')
  self.assertEqual(item.props['inputstream'],'inputstream.adaptive')
  self.assertIn('Referer=',item.props['inputstream.adaptive.manifest_headers'])
  self.assertEqual(item.mime,'application/vnd.apple.mpegurl')
 def test_vod_default_handling_does_not_receive_live_mime_or_properties(self):
  item=self.item('https://provider.example.test/movie/u/p/3.mp4',False)
  self.assertNotIn('XCMate.LiveTransport67',item.props);self.assertFalse(hasattr(item,'mime'))
 def test_reserved_credentials_are_one_encoded_path_segment(self):
  client=type(self.client)('https://provider.example.test','synthetic/u','fixture#?%+')
  from urllib.parse import urlsplit,unquote
  url=client.live_stream_url('1');p=urlsplit(url)
  self.assertFalse(p.fragment or p.query);self.assertEqual(unquote(p.path.split('/')[2]),'synthetic/u')
 def test_short_epg_http_failure_creates_portal_cooldown_without_retries(self):
  import short_epg67
  short_epg67._state.clear()
  error=urllib.error.HTTPError('https://secret.invalid/user/pass',504,'secret',{},None)
  with mock.patch.object(self.xcmod,'http_get',side_effect=error) as get:
   for sid in range(24):self.client.get_short_epg(str(sid),force_refresh=True)
  self.assertEqual(get.call_count,1);self.assertEqual(get.call_args.kwargs['retry_limit'],0)
  self.assertIn('live/',self.client.live_stream_url('1'))
 def test_probe_http_504_does_not_reveal_response_url_or_body(self):
  from live_probe67 import probe
  opener=mock.Mock();opener.open.side_effect=urllib.error.HTTPError('https://secret.invalid/user/pass',504,'secret',{},None)
  value=probe('https://provider.example.test/live/u/p/1.ts',opener=opener)
  self.assertEqual(value['code'],'HTTP_504');self.assertNotIn('secret',json.dumps(value));self.assertEqual(opener.open.call_count,1)
 def test_probe_distinguishes_ts_hls_and_html_without_reading_whole_stream(self):
  from live_probe67 import probe
  for body,mime,code in [(bytes([71])+bytes(187)+bytes([71])+bytes(187)+bytes([71]),'video/mp2t','STREAM_PREFIX'),(b'#EXTM3U\n','application/vnd.apple.mpegurl','STREAM_PREFIX'),(b'<html>login','text/html','NOT_A_STREAM')]:
   response=mock.Mock(status=200,headers={'Content-Type':mime});response.read.return_value=body
   opener=mock.Mock();opener.open.return_value=response
   self.assertEqual(probe('https://provider.example.test/live/u/p/1',opener=opener)['code'],code)
   response.read.assert_called_once_with(1024);response.close.assert_called_once()
 def test_tvmaze_is_opt_in_and_verifies_independent_identity(self):
  from programme_tvmaze67 import candidate
  event=dict(title='Synthetic Series',genre='Serie',year=2020)
  with mock.patch('media_sources43.get',side_effect=AssertionError('DISABLED_NETWORK')):self.assertIsNone(candidate(event))
  self.options['programme_tvmaze67']=True
  rows=[{'show':dict(id=67,name=event['title'],premiered='2020-01-01')}]
  details=dict(id=67,name=event['title'],premiered='2020-01-01',image=dict(original='https://static.tvmaze.com/uploads/images/original_untouched/1/67.jpg'))
  with mock.patch('media_sources43.get',side_effect=[rows,details]):
   value=candidate(event)
  self.assertEqual(value['source'],'tvmaze_series');self.assertEqual(value['image_scope57'],'series_fallback');self.assertNotIn('TMDB',value['attribution'])
