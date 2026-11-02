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
