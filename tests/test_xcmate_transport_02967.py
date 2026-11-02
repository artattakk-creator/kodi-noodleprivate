"""Explicit live preferences and per-portal bounded short EPG failures."""
import importlib,sys,types,unittest
from unittest import mock
from xcmate027_fixture import Fixture
from test_xcmate_live_02967 import Item67
class Transport67(Fixture,unittest.TestCase):
 def test_format_selection_is_explicit_and_default_remains_ts(self):
  from live_format67 import extension
  self.assertEqual(extension(),'ts')
  for value,expected in ((0,'ts'),(1,'ts'),(2,'m3u8')):
   self.options['live_stream_format67']=value;self.assertEqual(extension(),expected)
 def test_existing_hls_native_preference_is_respected_without_changing_media_default(self):
  import player
  self.options['use_inputstream_hls']=False
  with mock.patch.object(player.xbmcgui,'ListItem',Item67),mock.patch.object(player,'_isa_available',return_value=True):
   self.assertNotIn('inputstream',player.build_playable_item('https://synthetic.invalid/live/u/p/1.m3u8',live67=True).props)
   self.assertEqual(player.build_playable_item('https://synthetic.invalid/movie/u/p/1.m3u8').props['inputstream'],'inputstream.adaptive')
 def test_short_epg_429_retry_after_is_bounded_and_does_not_block_another_portal(self):
  import short_epg67 as m
  m._state.clear();a=types.SimpleNamespace(_cache_key=lambda action:'a');b=types.SimpleNamespace(_cache_key=lambda action:'b')
  with mock.patch.object(m.time,'monotonic',return_value=100):
   m.failed(a,types.SimpleNamespace(code=429,headers={'Retry-After':'99999'}))
   self.assertFalse(m.permit(a));self.assertTrue(m.permit(b));self.assertEqual(m._state['a'][0],1000)
   m.success(a);self.assertTrue(m.permit(a))
 def test_diagnostic_redirect_is_not_followed_or_forwarded(self):
  from live_probe67 import NoRedirect
  self.assertIsNone(NoRedirect().redirect_request(None,None,302,'Found',{},'https://other.invalid/secret'))
 def test_diagnostic_rejects_header_injection_before_network(self):
  from live_probe67 import probe
  opener=mock.Mock()
  self.assertEqual(probe('https://synthetic.invalid/stream',{'Referer':'bad\r\nX-Token: private'},opener)['code'],'UNSAFE_HEADER')
  opener.open.assert_not_called()
 def test_native_error_callback_never_stops_or_retries_and_ignores_changed_session(self):
  import json,time
  import live_feedback67 as m
  with mock.patch.object(sys.modules['xbmcgui'],'WindowDialog',object,create=True):
   SESSION_KEY=importlib.import_module('live_overlay').SESSION_KEY
  class Native:
   def isPlayingVideo(self):return False
  xbmc=sys.modules['xbmc'];m._seen.clear();m._pending=None
  first=dict(pid='p',sid='1',nonce='first',at=time.time())
  self.properties[SESSION_KEY]=json.dumps(first)
  with mock.patch.object(xbmc,'Player',Native),mock.patch.object(xbmc,'log',mock.Mock(),create=True),mock.patch.object(xbmc,'LOGWARNING',2,create=True):
   events=m.monitor();events.onPlayBackError()
   self.assertIsNotNone(m._pending)
   self.properties[SESSION_KEY]=json.dumps(dict(first,nonce='changed'))
   m.poll();self.dialog.notification.assert_not_called()
   self.properties[SESSION_KEY]=json.dumps(first)
   events.onPlayBackError();m.poll();m.poll()
   self.assertEqual(self.dialog.notification.call_count,1)
  self.assertFalse(self.builtins);self.assertFalse(self.native_builtins)
 def test_native_format_enum_exposes_three_real_options(self):
  import xml.etree.ElementTree as E
  from xcmate027_fixture import ADDON
  node=E.parse(ADDON/'resources/settings.xml').getroot().find(".//setting[@id='live_stream_format67']")
  self.assertEqual(len(node.get('values').split('|')),3);self.assertEqual(node.get('default'),'0')
