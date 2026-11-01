"""Visible media status entry, worker-only reads and explicit per-group controls."""
import importlib,json,unittest
from unittest import mock
from xcmate027_fixture import Fixture
class IndexUI65(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.status65=importlib.import_module('catalog_status65')
 def test_film_and_series_root_expose_index_status_in_existing_context_menu(self):
  import types
  for kind in ('vod','series'):
   window=self.media_window(kind);window.setFocusId(120)
   with mock.patch('menu_icons45.select',return_value=0),mock.patch('catalog_status65.manage',return_value=None) as shown:
    window.onAction(types.SimpleNamespace(getId=lambda:117));self.settle(window);shown.assert_called_once()
   self.assertEqual(window.getFocusId(),120);window.close()
 def test_disabled_is_distinct_from_zero_and_does_not_reenable_by_category_name(self):
  self.index.replace_catalog('p','vod',[dict(stream_id='fixture',category_id='10',name='Fixture title')],[dict(category_id='10',category_name='Adult Zone')],authoritative=False)
  importlib.import_module('group_selection').save('p',[],kind='vod',known=['10'])
  data=self.status65.snapshot(self.portal,'vod');row=next(v for v in data['rows'] if v['cid']=='10')
  self.assertEqual(row['name'],'Adult Zone');self.assertFalse(row['enabled']);self.assertEqual(row['local_count'],1)
  self.assertIn('Deaktiviert',self.status65.details(row));self.assertIn('nicht ermittelt',self.status65.details(row))
 def test_cached_positive_count_is_not_presented_as_current_provider_count(self):
  row=dict(name='Fixture group',enabled=True,updated=None,local_count=48,job={},evidence=dict(code='CACHED',transport='LOCAL_CACHE',received=48,stored=48,discarded=0))
  text=self.status65.details(row);self.assertIn('Provider-Titelzahl: nicht ermittelt',text);self.assertIn('Lokal gespeichert: 48',text)
 def test_cancelling_one_category_preserves_other_pending_jobs(self):
  delta=importlib.import_module('catalog_delta');delta.request_many(self.portal,'vod',['a','b'],retry=True)
  self.status65.cancel_one('p','vod','a')
  rows={row['cid']:row for row in delta.states('p','vod')};self.assertEqual(rows['a']['code'],'CANCELLED');self.assertEqual(rows['b']['code'],'PENDING')
