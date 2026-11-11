"""P0-F: lock only after real local hash plus native bank/control acknowledgement."""
import hashlib,time,unittest
from unittest import mock
from xcmate027_fixture import Fixture
from test_xcmate_02988 import png
class LockF89(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.options.update(programme_tmdb46=True,tmdb_research43=True,programme_tvmaze67=True)
  self.m=__import__('programme_lock89');self.event=dict(pid='p',sid='1',canonical='xml',title='Monk',key='event89',start=time.time()-60,stop=time.time()+3600,placeholder='')
  self.file=self.folder/'verified.png';self.file.write_bytes(png((960,540)));self.digest=hashlib.sha256(self.file.read_bytes()).hexdigest()
  from programme_requests68 import identity,scope
  self.art=dict(code='READY',key=self.event['key'],source='tmdb_series',match='EXACT_UNIQUE_TV_TITLE66',role81='backdrop',image='https://image.tmdb.org/t/p/w1280/a.png',source_url='https://image.tmdb.org/t/p/w1280/a.png',image_width77=960,image_height77=540,scope69=identity(self.event),profile69=scope(),fingerprint=__import__('programme_art46').fingerprint(self.event),until=time.time()+30)
 def lock(self):
  self.m.propose(self.event,self.art,dict(file=str(self.file),sha256=self.digest));win=self.m.window();win.setProperty('XCMate.Hero63.Active','A');win.setProperty('XCMate.Hero63.A.Image',self.art['image'])
  with mock.patch('xbmcgui.getCurrentWindowId',return_value=10000),mock.patch('xbmc.getInfoLabel',side_effect=lambda label:'live' if 'WidgetKind41' in label else '1'),mock.patch('xbmc.getCondVisibility',return_value=True):self.assertTrue(self.m.acknowledge(self.event,win))
  return win
 def test_no_lock_from_uri_or_ready_property_without_verified_file_and_native_ack(self):
  self.m.propose(self.event,self.art,dict(file='/missing.png',sha256=self.digest));self.assertIsNone(self.m.current(self.event))
  self.m.propose(self.event,self.art,dict(file=str(self.file),sha256=self.digest));self.assertIsNone(self.m.current(self.event))
 def test_tmdb_remains_over_306_seconds_when_xmltv_and_negative_rechecks_arrive(self):
  win=self.lock();now=time.time()
  for seconds in (5,30,45,90,306):
   with mock.patch('time.time',return_value=now+seconds),mock.patch('programme_transport77.verified',side_effect=AssertionError('no repeat source search')):
    event=dict(self.event,revision='refresh-'+str(seconds));held=self.m.current(event,worker=True);self.assertEqual(held['sha256'],self.digest)
    value=__import__('hero_render86').choose(event,dict(code='SOURCE_MISSING'),{},win);self.assertEqual(value['Image'],str(self.file));self.assertEqual(value['ArtSource'],'tmdb_series')
    self.assertEqual(__import__('programme_urls55').resolve(event,allow_lookup=True,url_mode69=True)['sha256'],self.digest)
 def test_true_event_policy_file_integrity_and_manual_mapping_changes_unlock(self):
  self.lock();self.assertIsNone(self.m.current(dict(self.event,sid='2')));self.assertIsNone(self.m.current(dict(self.event,start=self.event['start']+1)))
  with mock.patch('programme_mapping85.epoch',return_value=1):self.assertIsNone(self.m.current(self.event))
  self.options['programme_tmdb_optout77']=True;self.assertIsNone(self.m.current(self.event));self.options['programme_tmdb_optout77']=False
  self.file.write_bytes(b'corrupt');self.m._checked.clear();self.assertIsNone(self.m.current(self.event,worker=True))
 def test_native_home_request_without_derived_key_uses_same_locked_asset(self):
  win=self.lock();event={k:v for k,v in self.event.items() if k!='key'}
  held=self.m.current(event);self.assertEqual(held['sha256'],self.digest)
  self.assertEqual(held['key'],__import__('programme_events46').key('p','1',event))
  shown=__import__('hero_render86').choose(event,dict(code='SOURCE_MISSING'),{},win)
  self.assertEqual(shown['Image'],str(self.file))
