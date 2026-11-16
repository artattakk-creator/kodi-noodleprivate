"""Explicit Hub navigation forwards the chosen existing station to details."""
import importlib,unittest
from unittest import mock
from xcmate027_fixture import Fixture

class Hub96(Fixture,unittest.TestCase):
 def test_manual_entry_uses_chosen_local_station_without_rewriting_provider(self):
  self.index.import_group('p','live','a',[dict(stream_id='1',category_id='a',name='Chosen')]);before=dict(self.portal)
  module=importlib.import_module('manual_image96')
  with mock.patch('menu_icons45.select',side_effect=[0,0,-1]),mock.patch('artwork_ui.job',side_effect=lambda fn:fn(lambda:False,lambda *a:None)),mock.patch('programme_window46.show') as show:
   module.manage()
  self.assertEqual(show.call_args[0][1]['sid'],'1');self.assertTrue(show.call_args.kwargs['manual96']);self.assertEqual(self.portal,before)
