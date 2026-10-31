"""Hero images are materialized by the existing event worker, never on focus."""
import importlib,io,os,unittest
from pathlib import Path
from unittest import mock
from PIL import Image
from xcmate027_fixture import Fixture,ADDON

class ProgrammeBuffer63(Fixture,unittest.TestCase):
 def event(self):
  events=importlib.import_module('programme_events46')
  value=events.describe(self.portal,dict(sid='1',name='Fixture station'),dict(title='Buffered fixture event',start=self.now-60,stop=self.now+600))
  value['xmltv_image']='https://image.tmdb.org/t/p/w780/provider63.png'
  return value
 def test_exact_provider_event_is_downloaded_once_and_shared_as_a_verified_local_file(self):
  urls=importlib.import_module('programme_urls55');art=importlib.import_module('programme_art46');event=self.event()
  out=io.BytesIO();Image.new('RGB',(320,180),(30,90,140)).save(out,'PNG');raw=out.getvalue()
  with mock.patch('media_sources43.get',return_value=raw) as get,mock.patch.object(urls,'probe',side_effect=AssertionError('URL-only preflight')):
   value=urls.resolve(event,local_image63=True)
   again=urls.resolve(event,local_image63=True)
  self.assertEqual(value['code'],'READY');self.assertEqual(value['source'],'xmltv_event')
  self.assertTrue(Path(value['image']).is_file());self.assertEqual(Path(value['image']).read_bytes(),raw)
  self.assertEqual(get.call_count,1);self.assertEqual(again['image'],value['image'])
  self.assertEqual(art.cached(event)['image'],value['image'])
  props={'XCMate.ProgrammeImage46':value['image'],'XCMate.ProgrammeArtSource57':value['source']}
  importlib.import_module('live_text63')._hero(props)
  self.assertEqual(props['XCMate.HeroImage63'],art.cached(event)['image'])
 def test_pending_remote_image_is_neutral_without_losing_epg_or_starting_network(self):
  text=importlib.import_module('live_text63');views=importlib.import_module('epg_views')
  info=views.guide_for_channel({'x':[dict(name='Actual local text',start_timestamp=self.now-60,stop_timestamp=self.now+600)]},'x',now=self.now)
  info=importlib.import_module('programme_snapshot47').bind('p',dict(sid='1'),info)
  item=dict(props={'XCMate.ProgrammeKey47':info['programme_key47'],'XCMate.ProgrammeImage46':'https://image.tmdb.org/t/p/w780/provider63.png','XCMate.ProgrammeArtSource57':'xmltv_event'})
  with mock.patch('media_sources43.get',side_effect=AssertionError('focus network')):text.apply(item,self.portal,dict(sid='1'),info)
  self.assertEqual(item['props']['XCMate.ProgrammeTitle46'],'Actual local text')
  self.assertIn('neutral.png',item['props']['XCMate.HeroImage63']);self.assertEqual(item['props']['XCMate.HeroArtSource63'],'')
  self.assertEqual(item['props']['XCMate.ProgrammeImage46'],'https://image.tmdb.org/t/p/w780/provider63.png')
  self.assertEqual(item['props']['XCMate.ProgrammeArtSource57'],'xmltv_event')
 def test_local_generic_series_image_keeps_its_honest_fallback_label(self):
  text=importlib.import_module('live_text63');views=importlib.import_module('epg_views')
  info=views.guide_for_channel({'x':[dict(name='Actual local series',start_timestamp=self.now-60,stop_timestamp=self.now+600,descr='Actual local description')]},'x',now=self.now)
  info=importlib.import_module('programme_snapshot47').bind('p',dict(sid='1'),info)
  item=dict(props={'XCMate.ProgrammeKey47':info['programme_key47'],'XCMate.ProgrammeImage46':str(ADDON/'resources/media/programme46/series.png'),'XCMate.ProgrammeArtSource57':'tmdb_helper','XCMate.ProgrammeImageScope57':'series_fallback'})
  text.apply(item,self.portal,dict(sid='1'),info)
  from localization import tr
  self.assertTrue(item['props']['XCMate.ProgrammeDescription46'].startswith(tr(36542)))
  self.assertIn('Actual local description',item['props']['XCMate.ProgrammeDescription46'])
 def test_failed_download_does_not_mislabel_an_old_url_as_a_stale_local_image(self):
  urls=importlib.import_module('programme_urls55');event=self.event()
  legacy=urls.resolve(event,check=lambda *a,**kw:None)
  self.assertEqual(legacy['code'],'READY');self.assertTrue(legacy['image'].startswith('https://'))
  from media_sources43 import SourceError
  with mock.patch('media_sources43.get',side_effect=SourceError('HTTP_TIMEOUT')):
   blocked=urls.resolve(event,local_image63=True)
  self.assertEqual(blocked['code'],'HTTP_TIMEOUT');self.assertEqual(blocked['source'],'placeholder')
  self.assertEqual(blocked['image'],event['placeholder'])
