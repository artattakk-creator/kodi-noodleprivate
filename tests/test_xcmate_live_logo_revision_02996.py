"""Real override commits must reach an existing Live Channel without GUI I/O."""
import importlib
import io
import sys
import unittest
from contextlib import ExitStack
from pathlib import Path
from types import SimpleNamespace
from unittest import mock
from PIL import Image
from xcmate027_fixture import Fixture
from test_xcmate_02988 import png


class LiveLogoRevision96(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp()
  self.logo=importlib.import_module('logo_overrides96')
  self.row=dict(sid='1',stream_id='1',category_id='a',name='Station',stream_icon='https://images.example.org/provider.png')
  self.provider,_=importlib.import_module('logo_store89').persist(self.portal,self.row,self.picture((20,30,40)))
  self.original=self.logo.save(self.portal,self.row,png(),confirmed=True)
  self.model=importlib.import_module('live_prepare47').model(self.portal,self.client,[dict(category_id='a',category_name='Group')],[self.row])
  self.channel=self.model['channels'][0]
  self.assertEqual(self.channel.logo,self.original)
  with mock.patch.dict(sys.modules),mock.patch('xbmcgui.WindowDialog',new=type('WindowDialog',(),{}),create=True):
   sys.modules.pop('live_overlay',None)
   self.navigator=importlib.import_module('live_overlay').LiveNavigator
  self.nav=SimpleNamespace(portal=self.portal,_media='/bundled/media',_theme=None,mode='channels')
 def picture(self,color):
  result=io.BytesIO();Image.new('RGB',(32,16),color).save(result,'PNG');return result.getvalue()
 def resolve_without_io(self,expected):
  with ExitStack() as stack:
   for name in ('builtins.open','os.stat','pathlib.Path.stat','hashlib.sha256','sqlite3.connect','logo_overrides96.read','logo_cache.local_logo'):
    stack.enter_context(mock.patch(name,side_effect=AssertionError('GUI logo resolution must remain RAM-only: '+name)))
   for mode in ('info','channels'):
    self.nav.mode=mode
    self.assertEqual(self.navigator._local_logo(self.nav,self.channel),expected)
 def test_reset_reaches_same_live_channel_without_catalog_reload(self):
  self.logo.reset(self.portal,self.row,confirmed=True)
  self.assertEqual(self.logo.read(self.portal,[self.row]),{})
  self.resolve_without_io(self.provider)
  self.assertIs(self.model['channels'][0],self.channel)
  self.assertEqual(self.row['stream_icon'],'https://images.example.org/provider.png')
 def test_replacement_reaches_same_live_channel_across_interpreter_reload(self):
  replacement=self.logo.save(self.portal,self.row,self.picture((200,10,90)),confirmed=True)
  self.assertNotEqual(replacement,self.original)
  self.logo=importlib.reload(self.logo)
  self.resolve_without_io(replacement)
  self.assertIs(self.model['channels'][0],self.channel)
 def test_other_account_and_other_sid_commits_do_not_replace_existing_channel(self):
  self.logo.save(dict(self.portal,xc_user='other'),self.row,self.picture((200,10,90)),confirmed=True)
  self.logo.save(self.portal,dict(self.row,sid='2',stream_id='2'),self.picture((2,4,6)),confirmed=True)
  self.resolve_without_io(self.original)
 def test_same_portal_id_after_account_or_profile_switch_rejects_old_receipt(self):
  self.nav.portal=dict(self.portal,xc_user='different-account')
  self.resolve_without_io('/bundled/media/tv.png')
  self.nav.portal=self.portal
  with mock.patch('xbmcvfs.translatePath',return_value='/different-profile/'):
   self.resolve_without_io('/bundled/media/tv.png')
 def test_provider_cache_completed_after_model_is_still_used_without_gui_disk_reads(self):
  self.logo.reset(self.portal,self.row,confirmed=True)
  self.channel.extra['logo_base96']=''
  cache=importlib.import_module('logo_cache')
  with mock.patch.dict(cache._READY,{self.row['stream_icon']:self.provider}),mock.patch('artwork_config.read',side_effect=AssertionError('GUI config file read')),mock.patch('hashlib.sha256',side_effect=AssertionError('GUI hashing')):
   self.assertEqual(self.navigator._local_logo(self.nav,self.channel),self.provider)
 def test_scope_binding_repr_contains_no_account_secrets(self):
  rendered=repr(self.channel.extra)
  self.assertIn('<LogoScope96>',rendered)
  for field in ('xc_host','xc_user','xc_pass'):
   if self.portal.get(field):self.assertNotIn(str(self.portal[field]),rendered)
 def test_legacy_constructor_binding_observes_reset_using_existing_provider_cache(self):
  from concurrent.futures import Future
  future=Future();future.set_result(([dict(category_id='a',category_name='Group')],[self.row]))
  nav=SimpleNamespace(portal=self.portal,xc=self.client,sid='1',_catalog_future39=future,_catalog_ready=False,
                      _media='/bundled/media',_theme=None,mode='channels')
  self.assertTrue(self.navigator._load_catalog_from_disk(nav))
  channel=nav.channels[0]
  self.assertEqual(self.navigator._local_logo(nav,channel),self.original)
  self.logo.reset(self.portal,self.row,confirmed=True)
  cache=importlib.import_module('logo_cache')
  with mock.patch.dict(cache._READY,{self.row['stream_icon']:self.provider}),mock.patch('logo_overrides96.read',side_effect=AssertionError('GUI disk read')),mock.patch('artwork_config.read',side_effect=AssertionError('GUI settings read')):
   self.assertEqual(self.navigator._local_logo(nav,channel),self.provider)
