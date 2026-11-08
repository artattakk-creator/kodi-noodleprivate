"""Same-revision regressions: real provider file versus theme/partial frames."""
import copy,importlib,time,unittest
from unittest import mock

class Publication80(unittest.TestCase):
 def setUp(self):
  import test_xcmate_home_02974 as fixture
  self.h=fixture.Home74(methodName='runTest');self.h.setUp();self.addCleanup(self.h.doCleanups)
 def test_theme_fallback_cannot_replace_a_valid_same_source_provider_poster(self):
  h=self.h;rows=h.rows(1);old=h.frame(rows);picture=h.folder/'provider.jpg';picture.write_bytes(b'prior-validated-native-thumbnail')
  old['items'][0]['art'].update(poster=str(picture),thumb=str(picture),icon=str(picture),landscape=str(picture))
  old['items'][0]['props']['XCMate.ArtPending69']='false'
  old['items'][0]['_provider80']={'poster':{'source':importlib.import_module('programme_assets47').fingerprint(rows[0]['cover']),'uri':str(picture)}}
  current=copy.deepcopy(old['items']);current[0]['art'].update(poster='/theme/widget-movie.png',thumb='/theme/widget-movie.png');current[0]['props']['XCMate.ArtPending69']='true';current[0]['_provider80']={}
  values,_=h.p.merge(h.portal,'vod',current,rows,old)
  self.assertEqual(values[0]['art']['poster'],str(picture));self.assertEqual(values[0]['props']['XCMate.ArtPending69'],'false')
 def test_same_event_failed_refresh_does_not_replace_positive_session_art(self):
  import programme_session69 as session
  event=dict(pid='p',sid='1',key='event',title='Synthetic',start=1,stop=time.time()+600,canonical='cid')
  positive=dict(key='event',code='READY',source='xmltv_event',image=str(self.h.folder/'verified.jpg'),until=time.time()+120)
  from pathlib import Path
  Path(positive['image']).write_bytes(b'previously-verified')
  session.remember(event,positive,persisted=True)
  session.remember(event,dict(key='event',code='TIMEOUT',source='placeholder',until=time.time()+60))
  self.assertEqual(session.get(event)['image'],positive['image'])
 def test_invalid_positive_status_does_not_hide_still_valid_prior_image(self):
  import programme_requests68 as requests
  event=dict(pid='p',sid='1',key='event',title='Synthetic',start=1,stop=time.time()+600)
  previous=dict(key='event',code='READY',source='xmltv_event',image='/verified.jpg',until=time.time()+120)
  requests.status(event,'IMAGE_URL_READY',dict(previous,until=time.time()-1))
  self.assertEqual(requests.result(event,previous).get('image'),previous['image'])
 def test_forty_five_same_revision_partial_refreshes_never_republish_good_covers(self):
  h=self.h;rows=h.rows();h.d.store(h.d.files('p','vod')[0],h.d.policy(h.portal,'vod'),rows,['r',1])
  assets={}
  for row in rows:
   filename=h.folder/('poster-'+row['sid']+'.png');filename.write_bytes(b'prior-pipeline-verified-image');assets[row['sid']]={'poster':str(filename)}
  with mock.patch('widget_assets69.home',return_value=True),mock.patch('programme_assets47.read_many',return_value=assets):self.assertTrue(h.w.publish(h.portal,'vod',rows))
  from pathlib import Path
  target=Path(h.w.path('p','vod'));before=target.read_bytes();signature=h.w.read('p','vod')['signature']
  partial=dict(list(assets.items())[:18])
  for cycle in range(45):
   with mock.patch('widget_assets69.home',return_value=True),mock.patch('programme_assets47.read_many',return_value=partial if cycle%2 else assets):self.assertTrue(h.w.publish(h.portal,'vod',rows))
   self.assertEqual(h.w.read('p','vod')['signature'],signature)
  self.assertEqual(target.read_bytes(),before)
 def test_changed_source_and_deleted_file_cannot_be_frozen_as_last_good(self):
  h=self.h;rows=h.rows(1);old=h.frame(rows);picture=h.folder/'gone.jpg';picture.write_bytes(b'verified')
  old['items'][0]['art']['poster']=str(picture);old['items'][0]['_provider80']={'poster':dict(source=importlib.import_module('programme_assets47').fingerprint(rows[0]['cover']),uri=str(picture))}
  current=copy.deepcopy(old['items']);current[0]['art']['poster']='';current[0]['_provider80']={};picture.unlink()
  values,_=h.p.merge(h.portal,'vod',current,rows,old);self.assertFalse(values[0]['art']['poster'])
  picture.write_bytes(b'verified')
  current=copy.deepcopy(current);changed=[dict(rows[0],cover='https://public.example.test/new-image.jpg')]
  values,_=h.p.merge(h.portal,'vod',current,changed,old);self.assertFalse(values[0]['art']['poster'])
 def test_worker_rejects_deleted_or_changed_file_and_never_crosses_event(self):
  import hashlib,programme_lastgood80 as last
  event=dict(pid='p',sid='1',key='event',title='Synthetic',start=1,stop=time.time()+600)
  file=self.h.folder/'checked.jpg';file.write_bytes(b'verified')
  previous=dict(key='event',code='READY',source='xmltv_event',image=str(file),sha256=hashlib.sha256(b'verified').hexdigest(),until=time.time()+120)
  miss=dict(code='TIMEOUT',source='placeholder')
  self.assertEqual(last.choose(event,miss,previous,check_file=True)['image'],str(file))
  file.write_bytes(b'corrupt!');self.assertEqual(last.choose(event,miss,previous,check_file=True),miss)
  file.unlink();self.assertEqual(last.choose(event,miss,previous,check_file=True),miss)
  self.assertEqual(last.choose(dict(event,key='new-event'),miss,previous),miss)
  self.assertEqual(last.choose(event,miss,dict(previous,until=time.time()-1)),miss)
 def test_gui_last_good_admission_does_not_touch_disk(self):
  import programme_lastgood80 as last
  event=dict(pid='p',sid='1',key='event',title='Synthetic',start=1,stop=time.time()+600)
  previous=dict(key='event',code='READY',source='xmltv_event',image='/already-verified.jpg',until=time.time()+120)
  with mock.patch.object(last,'file_valid',side_effect=AssertionError('filesystem on GUI lane')):
   self.assertEqual(last.choose(event,dict(code='TIMEOUT'),previous)['image'],previous['image'])
 def test_negative_status_cannot_keep_an_expired_local_event_image(self):
  import programme_requests68 as requests
  event=dict(pid='p',sid='1',key='event',title='Synthetic',start=1,stop=time.time()+600)
  old=dict(key='event',code='READY',source='xmltv_event',image='/verified.jpg',until=time.time()-1)
  requests.status(event,'NO_MATCH',dict(code='NO_MATCH',source='placeholder'))
  result=requests.result(event,old)
  self.assertEqual(result.get('code'),'NO_MATCH')
