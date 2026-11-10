"""Optional gateway protocol mocks, never a production server or real token."""
import hashlib,hmac,importlib,io,json,os,secrets,time,unittest
from pathlib import Path
from unittest import mock
from xcmate027_fixture import Fixture
from test_xcmate_tmdb_token_02961 import FIXTURE
class Gateway87(Fixture,unittest.TestCase):
 def setUp(self):
  super().setUp();self.g=importlib.import_module('tmdb_gateway_client87');self.options.update(tmdb_gateway_endpoint87='https://gateway.example.org',tmdb_research43=True,programme_tmdb46=True)
  self.device=secrets.token_urlsafe(40);self.credential=secrets.token_urlsafe(48);self.code=secrets.token_urlsafe(48);self.approved=False;self.revoked=False;self.calls=[];self.nonces=set();self.challenge=''
  self.g._transport_hook=self.server
 def tearDown(self):self.g._transport_hook=None;super().tearDown()
 def reply(self,value,status=200,headers=None):
  raw=value if isinstance(value,bytes) else json.dumps(value).encode();stream=io.BytesIO(raw)
  return type('Response',(),dict(status=status,headers=headers or {'Content-Type':'application/json'},read=stream.read,close=stream.close))()
 def server(self,base,operation,body,headers,cancel):
  self.calls.append(operation);data=json.loads(body)
  if operation=='pair/start':self.challenge=data['challenge'];return self.reply(dict(device_code=self.code,user_code='ABCD-EFGH',expires_in=600,interval=5))
  if operation=='pair/poll':
   if data['device_code']!=self.code or hashlib.sha256(data['verifier'].encode()).hexdigest()!=self.challenge:return self.reply({},403)
   if not self.approved:return self.reply(dict(status='PENDING'))
   if self.revoked:return self.reply(dict(status='DENIED'))
   return self.reply(dict(status='PAIRED',credential=self.credential,device_id=self.device))
  if self.revoked or headers.get('X-Device-Id')!=self.device:return self.reply({},403)
  nonce=headers['X-Device-Nonce'];stamp=headers['X-Device-Time'];message='\n'.join((operation,stamp,nonce,hashlib.sha256(body).hexdigest())).encode()
  proof=hmac.new(self.credential.encode(),message,hashlib.sha256).hexdigest()
  if nonce in self.nonces or abs(time.time()-int(stamp))>30 or not hmac.compare_digest(proof,headers['X-Device-Proof']):return self.reply({},403)
  self.nonces.add(nonce)
  if operation=='status':return self.reply(dict(authorized=True))
  if operation=='revoke':self.revoked=True;return self.reply(dict(revoked=True))
  if operation=='tmdb':return self.reply(dict(results=[dict(id=1,name='Mock work')]))
  return self.reply({},404)
 def pair(self):
  self.assertEqual(self.g.begin(),'PENDING');self.approved=True
  with mock.patch.object(self.g.time,'time',return_value=time.time()+6):self.assertEqual(self.g.poll(),'GATEWAY_PAIRED')
 def test_no_server_default_and_no_network_without_explicit_endpoint(self):
  self.options['tmdb_gateway_endpoint87']='';self.assertEqual(self.g.begin(),'NOT_CONFIGURED');self.assertEqual(self.calls,[])
 def test_approval_is_separate_code_cannot_access_and_pair_survives_reload(self):
  self.assertEqual(self.g.begin(),'PENDING');self.assertEqual(self.g.poll(),'PENDING');self.assertEqual(self.calls,['pair/start'])
  with mock.patch.object(self.g.time,'time',return_value=time.time()+6):self.assertEqual(self.g.poll(),'PENDING')
  self.approved=True
  with mock.patch.object(self.g.time,'time',return_value=time.time()+12):self.assertEqual(self.g.poll(),'GATEWAY_PAIRED')
  path=Path(self.g._path());self.assertEqual(path.stat().st_mode&0o777,0o600);raw=path.read_bytes();self.assertNotIn(self.code.encode(),raw);self.assertNotIn(b'verifier',raw)
  self.g=importlib.reload(self.g);self.g._transport_hook=self.server;self.assertEqual(self.g.status(),'GATEWAY_PAIRED');self.assertEqual(path.read_bytes(),raw)
  self.assertEqual(self.g.query('https://api.themoviedb.org/3/search/tv?query=Monk')['results'][0]['id'],1)
  self.assertEqual(self.g.revoke(),'REVOKED');self.assertNotEqual(self.g.status(),'GATEWAY_PAIRED')
 def test_local_token_and_optout_never_pair_or_overwrite_existing_file(self):
  token=importlib.import_module('tmdb_token61');path=Path(token.location());path.write_bytes(FIXTURE);os.chmod(path,0o600);before=path.read_bytes(),path.stat().st_mode
  self.assertEqual(self.g.begin(),'LOCAL_TOKEN_VALID');self.assertEqual((path.read_bytes(),path.stat().st_mode),before);self.assertEqual(self.calls,[])
  self.options['programme_tmdb_optout77']=True;self.assertEqual(self.g.begin(),'OPTED_OUT');self.assertEqual(self.calls,[])
 def test_bad_existing_local_token_is_not_bypassed_by_gateway(self):
  Path(importlib.import_module('tmdb_token61').location()).write_bytes(b'invalid');self.assertEqual(self.g.begin(),'LOCAL_TOKEN_INVALID');self.assertEqual(self.calls,[])
 def test_pending_expiry_cancel_and_write_failure_do_not_install_permission(self):
  self.assertEqual(self.g.begin(),'PENDING');data=self.g._read()
  with mock.patch.object(self.g.time,'time',return_value=data['expires']+1):self.assertNotEqual(self.g.poll(),'GATEWAY_PAIRED')
  self.approved=True
  with mock.patch.object(self.g.time,'time',return_value=time.time()+6),mock.patch.object(self.g.os,'replace',side_effect=OSError('private detail')):
   with self.assertRaisesRegex(self.g.GatewayError,'PERSISTENCE_BLOCKED'):self.g.poll()
  self.assertEqual(self.g.status(),'PENDING');self.assertFalse(list(Path(self.g._path()).parent.glob('.gateway87-*')))
 def test_profile_revision_and_cancel_before_replace_fail_closed(self):
  self.g.begin();before=self.g._read();updated=dict(before,next_poll=0)
  with self.assertRaisesRegex(self.g.GatewayError,'PROFILE_CHANGED'):self.g._write(updated,scope=self.g._path(),expected={})
  with self.assertRaisesRegex(self.g.GatewayError,'USER_CANCELLED'):self.g._write(updated,scope=self.g._path(),expected=before,cancel=lambda:True)
  self.assertEqual(self.g._read(),before)
 def test_tls_redirect_response_limit_mime_and_auth_are_distinct_without_secret_echo(self):
  import ssl
  for result,code in [(self.reply({},302),'REDIRECT_BLOCKED'),(self.reply({},401),'AUTH_FAILED'),(self.reply({},429),'RATE_LIMITED'),(self.reply(b'x'*(1024*1024+1)),'GATEWAY_RESPONSE_LIMIT'),(self.reply({},headers={'Content-Type':'text/html'}),'GATEWAY_RESPONSE_INVALID'),(self.reply(dict(tmdb_token='must-not-be-accepted')),'GATEWAY_RESPONSE_INVALID')]:
   with mock.patch.object(self.g,'_transport_hook',return_value=result),self.assertRaisesRegex(self.g.GatewayError,code):self.g._call(self.g.configured(),'pair/start',{})
  with mock.patch.object(self.g,'_transport_hook',side_effect=ssl.SSLError('private certificate detail')),self.assertRaisesRegex(self.g.GatewayError,'GATEWAY_TLS_FAILED'):self.g._call(self.g.configured(),'pair/start',{})
 def test_endpoint_and_api_allowlist_reject_ssrf_credentials_and_arbitrary_proxy_targets(self):
  for value in ['http://gateway.example.org','https://user:pass@gateway.example.org','https://127.0.0.1','https://[::1]','https://gateway.example.org/token?secret=x','https://gateway.example.org:8443','https://gateway.example.org/#x']:
   with self.assertRaises(self.g.GatewayError):self.g.endpoint(value)
  for url in ['https://api.themoviedb.org/3/search/tv?api_key=x','https://api.themoviedb.org/3/../../foo','https://evil.example/3/search/tv','https://api.themoviedb.org/3/tv/1?url=http://127.0.0.1','https://api.themoviedb.org/3/tv/1?query=a&query=b']:
   with self.assertRaises(self.g.GatewayError):self.g.tmdb_operation(url)
  with mock.patch('download_redirect.addresses',side_effect=ValueError('private DNS')),mock.patch.object(self.g.socket,'create_connection',side_effect=AssertionError('must not connect')):
   with self.assertRaises(ValueError):self.g._transport(self.g.configured(),'status',b'{}',{},lambda:False)
 def test_real_tmdb_caller_uses_gateway_marker_only_after_pairing(self):
  self.pair();sources=importlib.import_module('media_sources43');token=sources.tmdb_token();self.assertEqual(token,self.g.MARKER)
  with mock.patch('download_redirect._connect',side_effect=AssertionError('no anonymous public TMDB request')):
   value=importlib.import_module('tmdb_connection60').request('https://api.themoviedb.org/3/search/tv?query=Monk',token=token)
  self.assertEqual(value['results'][0]['id'],1)
 def test_update_zip_and_module_restart_preserve_private_token_bytes_mode_and_optout(self):
  import zipfile
  token=importlib.import_module('tmdb_token61');path=Path(token.location());path.write_bytes(FIXTURE);os.chmod(path,0o600);before=path.read_bytes(),path.stat().st_mode
  self.options['programme_tmdb_optout77']=True
  package=Path(__file__).parents[1]/'docs/XCMate/test-builds/02987/plugin.video.xtreammate-0.1.29.87.zip'
  with zipfile.ZipFile(package) as z:
   self.assertFalse(any('addon_data/' in n or n.endswith('tmdb_read_access_token.txt') or n.endswith('tmdb_gateway87.json') for n in z.namelist()))
   z.extractall(self.folder/'updated-addon')
  token=importlib.reload(token);self.assertEqual(token.status(),'FILE_VALID');self.assertEqual((path.read_bytes(),path.stat().st_mode),before);self.assertTrue(self.options['programme_tmdb_optout77'])
