""".77 source consent, complete image decode and cache renewal contracts."""
import hashlib,importlib,io,json,sys,time,types,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture,ADDON

class Consent77(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.c=importlib.import_module('programme_consent77');self.c._next.clear()
  self.t=importlib.import_module('tmdb_token61');self.t._cache=None
  self.tokenfile=self.folder/'token.txt';self.tokenfile.write_bytes(b'a'*24+b'.'+b'b'*24+b'.'+b'c'*24+b'\n');self.tokenfile.chmod(0o600)
  self.tokenpath=mock.patch.object(self.t,'location',return_value=str(self.tokenfile));self.tokenpath.start();self.addCleanup(self.tokenpath.stop)
  self.boolpatch=mock.patch('utils.setting_bool',side_effect=lambda k,d=False:str(self.options.get(k,str(d))).lower()=='true');self.boolpatch.start();self.addCleanup(self.boolpatch.stop)
  self.off=mock.patch.object(self.c,'explicit_off',return_value=set());self.off.start();self.addCleanup(self.off.stop)
 def test_existing_valid_token_enables_both_gates_without_any_token_write(self):
  before=(self.tokenfile.read_bytes(),self.tokenfile.stat().st_mode,self.tokenfile.stat().st_mtime_ns)
  with mock.patch.object(self.t,'import_bytes',side_effect=AssertionError('REIMPORT')),mock.patch('os.replace',side_effect=AssertionError('TOKEN_REPLACE')):
   self.assertEqual(self.c.ensure(force=True),'TOKEN_FORMAT_VALID')
  self.assertEqual(before,(self.tokenfile.read_bytes(),self.tokenfile.stat().st_mode,self.tokenfile.stat().st_mtime_ns));self.assertEqual([self.options[k] for k in self.c.FLAGS],['true']*3)
 def test_explicit_tmdb_and_tvmaze_optout_survive_restart_and_import(self):
  self.options.update(programme_tmdb_optout77='true',programme_tvmaze_optout77='true')
  self.c.ensure(force=True);self.c._next.clear();self.c.ensure(force=True)
  import xbmcaddon
  self.assertFalse(importlib.import_module('tmdb_access61').activate(xbmcaddon.Addon(),automatic=True))
  self.assertNotEqual(self.options.get('programme_tmdb46'),'true');self.assertNotEqual(self.options.get('programme_tvmaze67'),'true')
 def test_completed_migration_never_reactivates_manual_disable(self):
  self.c.ensure(force=True);self.c.decision('tmdb',False);self.c.decision('tvmaze',False);self.c._next.clear();self.c.ensure(force=True)
  self.assertEqual([self.options[k] for k in self.c.FLAGS],['false']*3)
 def test_missing_invalid_token_never_enables_tmdb_and_is_not_overwritten(self):
  for raw in (b'',b'invalid'):
   self.options.clear();self.t._cache=None;self.tokenfile.write_bytes(raw)
   self.assertEqual(self.c.ensure(force=True),'TOKEN_INVALID');self.assertNotEqual(self.options.get('programme_tmdb46'),'true');self.assertEqual(self.tokenfile.read_bytes(),raw)
 def test_missing_file_valid_legacy_setting_is_read_only(self):
  self.tokenfile.unlink();raw='a'*24+'.'+'b'*24+'.'+'c'*24;self.options['tmdb_read_token43']=raw
  self.assertEqual(self.c.ensure(force=True),'TOKEN_FORMAT_VALID');self.assertEqual(self.options['tmdb_read_token43'],raw);self.assertFalse(self.tokenfile.exists())
 def test_explicit_persisted_false_distinguished_from_kodi_default(self):
  self.off.stop();path=self.folder/'settings.xml';path.write_text('<settings><setting id="programme_tmdb46" default="true">false</setting><setting id="programme_tvmaze67">false</setting></settings>')
  with mock.patch('xbmcvfs.translatePath',return_value=str(path)):self.assertEqual(self.c.explicit_off(),{'programme_tvmaze67'})
 def test_all_import_modes_auto_activate_without_touching_existing_token(self):
  # Real import-flow branching with synthetic source/transaction. No real user token.
  access=importlib.import_module('tmdb_access61')
  import xbmcaddon
  for mode in (0,6,7):
   with self.subTest(mode=mode):
    dialog=types.SimpleNamespace(input=lambda *a,**k:'a'*24+'.'+'b'*24+'.'+'c'*24,browseSingle=lambda *a,**k:'synthetic.txt',yesno=lambda *a,**k:True,ok=mock.Mock())
    tokens=types.SimpleNamespace(validate=lambda raw:raw.decode().strip(),location=lambda:'synthetic-private',TokenError=self.t.TokenError,import_bytes=mock.Mock(return_value='IMPORTED'),effective_tmdb_read_token=mock.Mock())
    with mock.patch('tmdb_import63.selected',return_value=b'a'*24+b'.'+b'b'*24+b'.'+b'c'*24),mock.patch('token_destination65.pre_read',return_value=None),mock.patch.object(access,'activate') as activate:
     access.imported(mode,dialog,xbmcaddon.Addon(),types.SimpleNamespace(),tokens)
    activate.assert_called_once_with(mock.ANY,automatic=True)

class Transport77(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.transport=importlib.import_module('programme_transport77');self.errors=importlib.import_module('media_sources43')
  from PIL import Image
  out=io.BytesIO();Image.new('RGB',(320,180),(20,100,150)).save(out,'PNG');self.data=out.getvalue();self.calls=[]
 def response(self,status=200,location='',data=None):
  stream=io.BytesIO(self.data if data is None else data)
  return types.SimpleNamespace(status=status,headers={'Content-Type':'image/png','Location':location},read=stream.read,close=stream.close)
 def run_transport(self,responses,url='https://image.tmdb.org/t/p/w500/a.png'):
  def connect(url,ips,headers):self.calls.append((url,headers));return responses.pop(0)
  return self.transport.verified(url,connect=connect,resolver=lambda uri:['93.184.216.34'])
 def test_complete_valid_image_is_decoded_before_reference_ready(self):
  result=self.run_transport([self.response()]);self.assertEqual((result['width'],result['height'],result['decoded77']),(320,180,True))
 def test_valid_header_with_corrupt_tail_does_not_pass_preflight(self):
  with self.assertRaises(self.errors.SourceError):self.run_transport([self.response(data=self.data[:50])])
 def test_known_cdn_redirect_is_returned_as_actual_render_url(self):
  result=self.run_transport([self.response(302,'https://image.tmdb.org/t/p/w500/b.png'),self.response()]);self.assertTrue(result['url'].endswith('/b.png'));self.assertEqual(len(self.calls),2)
  self.assertTrue(all('Authorization' not in h and 'Cookie' not in h for _,h in self.calls))
 def test_arbitrary_cross_origin_and_downgrade_never_connected(self):
  for target in ('https://unknown.example.org/p.png','http://image.tmdb.org/t/p/w500/b.png','https://image.tmdb.org/t/p/w500/a.png?token=private'):
   self.calls=[]
   with self.assertRaises(self.errors.SourceError):self.run_transport([self.response(302,target)])
   self.assertEqual(len(self.calls),1)
 def test_redirect_to_provider_credentials_is_rejected(self):
  with self.assertRaises(self.errors.SourceError):self.run_transport([self.response(302,'https://image.tmdb.org/t/p/w500/SECRET.png')])
 def test_dns_failure_never_reaches_transport(self):
  connect=mock.Mock()
  with self.assertRaises(self.errors.SourceError):self.transport.verified('https://image.tmdb.org/t/p/w500/a.png',connect=connect,resolver=mock.Mock(side_effect=OSError('private error')))
  connect.assert_not_called()
 def test_public_resize_query_is_supported_but_auth_query_never_is(self):
  query=importlib.import_module('programme_url77').public_query
  self.assertTrue(query('width=640&height=360&fit=crop&format=jpg'))
  for value in ('token=private','width=https://private','width=640&width=320','quality=101','auto=secret'):
   self.assertFalse(query(value))
  self.assertTrue(self.run_transport([self.response()],url='https://image.tmdb.org/t/p/w500/a.png?width=640')['decoded77'])
 def test_cancelled_or_non_image_response_has_no_decode_success(self):
  with self.assertRaises(self.errors.SourceError):self.transport.verified('https://image.tmdb.org/t/p/w500/a.png',cancel=lambda:True)
  response=self.response();response.headers['Content-Type']='text/html'
  with self.assertRaises(self.errors.SourceError):self.run_transport([response])
 def test_six_hour_negative_changes_scope_when_fallback_enabled(self):
  art=importlib.import_module('programme_art46');event=dict(key='a'*64,title='Known series',placeholder='',season=1,episode=1)
  self.options.update(programme_tmdb46=False,programme_helper57=False,programme_catalog57=False,programme_tvmaze67=False)
  scope=importlib.import_module('programme_policy68').negative_scope
  before=scope(event);self.options['programme_tvmaze67']=True;self.assertNotEqual(scope(event),before)
  from collections import OrderedDict
  with mock.patch.object(art,'ensure'),mock.patch.object(art,'_pending',set()),mock.patch.object(art,'_queue',OrderedDict()),mock.patch.object(art,'_memory',OrderedDict()),mock.patch.object(art,'_stop') as stop:
   stop.is_set.return_value=False
   self.assertTrue(art.enqueue(event))
  with art._lock:art._queue.pop(event['key'],None);art._pending.discard(event['key'])
 def test_expired_origin_is_not_returned_from_day_long_positive_session(self):
  session=importlib.import_module('programme_session69');event=dict(key='a'*64,pid='p',sid='1',start=self.now,stop=self.now+300,title='Known')
  session.remember(event,dict(code='READY',source='xmltv_event',image='https://no-lease.example.org/p.png',until=time.time()+300))
  self.assertIsNone(session.get(event))

if __name__=='__main__':unittest.main()
