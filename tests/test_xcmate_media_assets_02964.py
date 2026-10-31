"""Series publications must consume the same provider asset references as movies."""
import importlib,time,unittest
from pathlib import Path
from unittest import mock
from PIL import Image
from xcmate050_fixture import Fixture50
class Series64(Fixture50,unittest.TestCase):
 def setUp(self):
  super().setUp();self.assets=importlib.import_module('programme_assets47');self.pub=importlib.import_module('widget_refresh45')
  self.row=dict(sid='1',name='Provider fixture series',kind='series',cover='https://images.example.test/series64.png')
  self.image=self.folder/'provider-series64.png';Image.new('RGB',(120,180),(100,50,20)).save(self.image)
 def prepare(self):
  self.assertTrue(self.assets._store('p','series',[('1','poster',self.assets.fingerprint(self.row['cover']),dict(uri=str(self.image),mode='local',code='LOCAL_HEADER_VALID',until=time.time()+86400))]))
 def test_shared_asset_reference_updates_series_publication_without_metadata_change(self):
  with mock.patch('widget_art44.read',return_value={}):self.pub.publish(self.portal,'series',[self.row])
  before=self.pub.read('p','series');self.prepare()
  with mock.patch('widget_art44.read',return_value={}),mock.patch('media_sources43.get',side_effect=AssertionError('VOD metadata network')):self.pub.publish(self.portal,'series',[self.row])
  after=self.pub.read('p','series')
  self.assertNotEqual(before['signature'],after['signature'])
  self.assertEqual(after['items'][0]['art']['poster'],str(self.image))
  self.assertIn('kind=series',after['items'][0]['url']);self.assertEqual(after['items'][0]['props']['XCMate.SeriesArt64'],'SERIES_ART_URI_READY')
 def test_expired_reference_is_not_extended_or_treated_as_missing_provider_data(self):
  self.assets._store('p','series',[('1','poster',self.assets.fingerprint(self.row['cover']),dict(uri=self.row['cover'],mode='dynamic',code='DYNAMIC_APPROVED',until=time.time()-1))])
  self.assertEqual(self.assets.read_many('p','series',[self.row],provider_only=True),{})
  check=importlib.import_module('series_art64').inspect
  self.assertEqual(check(self.row,dict(poster='series.png')),'SERIES_ASSET_CACHE_MISS')
 def test_diagnosis_distinguishes_missing_source_rejection_binding_and_confirmed_decode_failure(self):
  check=importlib.import_module('series_art64').inspect
  self.assertEqual(check(dict(sid='1'),{}),'SERIES_PROVIDER_ART_MISSING')
  self.assertEqual(check(dict(self.row,cover='https://localhost/private.png'),{}),'SERIES_ART_URI_REJECTED')
  self.assertEqual(check(dict(self.row,kind='vod'),{}),'SERIES_WIDGET_BINDING_MISMATCH')
  self.assertEqual(check(self.row,dict(poster=str(self.image)),decoded=False),'SERIES_TEXTURE_DECODE_FAIL')
  self.assertEqual(check(self.row,dict(poster=str(self.image))),'SERIES_ART_URI_READY')
