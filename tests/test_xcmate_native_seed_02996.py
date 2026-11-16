"""Execute unchanged native Home fixture seed blocks through the real pipeline.

The native probe runs this under Estuary before selecting BINGIE. No Kodi
receiver/pixel/playback assertion is removed or simulated by these host tests.
"""
import ast
import importlib
import io
import json
import sys
import unittest
from pathlib import Path
from unittest import mock
from urllib.parse import urlsplit
from PIL import Image
from xcmate027_fixture import Fixture
ROOT=Path(__file__).resolve().parents[1]


class NativeSeed96(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp()
  self.options.update(programme_tmdb46=True,tmdb_research43=True,tmdb_read_token43='SYNTHETIC_FIXTURE_NOT_A_TOKEN',programme_art_local69=True,programme_helper57=False,programme_catalog57=False)
  importlib.import_module('cinematic_images96')._cache.clear()
  self.art=importlib.import_module('programme_art46')
  Path(self.art.root()).mkdir(exist_ok=True)
  self.stations=[dict(stream_id=str(i),name='Station '+str(i),category_id='a',epg_channel_id='xml'+str(i)) for i in range(3)]
  events={}
  for i in range(3):
   title='MacGyver' if i==2 else 'Synthetic film '+str(i)
   events['xml'+str(i)]=[dict(name=title,title=title,channel='xml'+str(i),category='Krimiserie' if i==2 else 'Spielfilm',year=2016 if i==2 else 2024,start_timestamp=self.now-600,stop_timestamp=self.now+7200)]
  importlib.import_module('guide_store').import_cache(self.portal['id'],events,'synthetic-home60',now=self.now,trusted_feed=True)
  self.load=importlib.import_module('programme_events46').load
 def block(self,kind):
  tree=ast.parse((ROOT/'tools/kodi_home74_host/fixture66.py').read_text())
  seed=next(n for n in tree.body if isinstance(n,ast.If)).body
  movie=next(i for i,n in enumerate(seed) if isinstance(n,ast.For) and isinstance(n.target,ast.Name) and n.target.id=='i' and isinstance(n.iter,ast.Tuple))
  end=next(i for i in range(movie+1,len(seed)) if isinstance(seed[i],ast.Expr) and isinstance(seed[i].value,ast.Call) and isinstance(seed[i].value.func,ast.Name) and seed[i].value.func.id=='check_series66')
  return ast.Module(body=[seed[movie]] if kind=='movie' else seed[movie+1:end],type_ignores=[])
 def run_seed(self,kind):
  import media_sources43
  calls=[];original=media_sources43.get
  def profile(frame,event,arg):
   if event=='call' and frame.f_code.co_filename=='native-fixture74' and frame.f_code.co_name=='<lambda>':
    url=frame.f_locals['a'][0];kw=frame.f_locals['kw'];calls.append((urlsplit(url).path,bool(kw.get('api',False))))
  def owned_path(value):
   value=str(value)
   return self.folder/Path(value).name if value.startswith('/root/') else Path(value)
  def check(condition,detail='NATIVE_FIXTURE64_CONTRACT'):
   self.assertTrue(condition,detail)
  namespace=dict(portal=self.portal,stations=self.stations,load=self.load,resolve=importlib.import_module('programme_urls55').resolve,
                 media_sources43=media_sources43,io=io,Image=Image,Path=owned_path,json=json,check64=check)
  previous=sys.getprofile()
  try:
   sys.setprofile(profile)
   with mock.patch('home_schedule75.applicable',return_value=False):
    exec(compile(self.block(kind),'native-fixture74','exec'),namespace)
  except StopIteration:
   self.fail('Native cold seed exhausted its search/details/image transport: '+repr(calls))
  finally:sys.setprofile(previous)
  self.assertIs(media_sources43.get,original)
  return namespace,calls
 def test_native_movie_seed_uses_search_details_then_one_local_image(self):
  namespace,calls=self.run_seed('movie')
  self.assertEqual(calls,[('/3/search/movie',True),('/3/movie/100',True),('/t/p/w500/epg0.png',False),('/3/search/movie',True),('/3/movie/101',True),('/t/p/w500/epg1.png',False)])
  for i in (0,1):
   result=json.loads((self.folder/('seed60-'+str(i)+'.json')).read_text())
   self.assertEqual(result['art']['code'],'READY');self.assertTrue(Path(result['art']['image']).is_file())
 def test_native_tv_seed_keeps_exact_series_fallback_local_image_chain(self):
  namespace,calls=self.run_seed('tv')
  self.assertEqual(calls,[('/3/search/tv',True),('/3/tv/6602',True),('/t/p/w500/tv66.png',False)])
  result=json.loads((self.folder/'art66.json').read_text())
  self.assertEqual(result['source'],'tmdb_series');self.assertEqual(result['scope'],'series_fallback');self.assertTrue(Path(result['image']).is_file())
