"""Optional private gateway protocol v1; no endpoint or central secret shipped.

TLS/pinned public DNS, fixed POST operations and installation-specific proof.
The server must implement authenticated admin approval, expiry, nonce replay
protection, per-device revoke/rate limits. No deploy is implied by this client.
"""
import hashlib,hmac,http.client,json,os,re,secrets,socket,ssl,threading,time
from urllib.parse import urlsplit,parse_qsl
NAME='tmdb_gateway87.json';MARKER='XCMATE_PRIVATE_GATEWAY87';_lock=threading.RLock()
class GatewayError(ValueError):
 def __init__(self,code):self.code=code;super().__init__(code)
def endpoint(value):
 try:
  p=urlsplit(value)
  if p.scheme!='https' or not p.hostname or p.port not in (None,443) or p.username is not None or p.password is not None or p.path not in ('','/') or p.query or p.fragment:raise ValueError()
  host=p.hostname.encode('idna').decode('ascii').lower()
  if not re.fullmatch(r'[a-z0-9]+(?:[a-z0-9.-]*[a-z0-9])?',host) or '.' not in host or any(not x or x.startswith('-') or x.endswith('-') for x in host.split('.')):raise ValueError()
  import ipaddress
  try:ipaddress.ip_address(host)
  except ValueError:pass
  else:raise ValueError()
  return 'https://'+host
 except (TypeError,ValueError,UnicodeError):raise GatewayError('GATEWAY_ENDPOINT_INVALID') from None
def configured():
 from utils import setting
 value=setting('tmdb_gateway_endpoint87','').strip()
 return endpoint(value) if value else ''
def allowed():
 from utils import setting_bool
 return not setting_bool('programme_tmdb_optout77',False)
def _path():
 from tmdb_token61 import location
 return os.path.join(os.path.dirname(location()),NAME)
def _read():
 import tmdb_token61 as tokens
 try:
  raw=tokens.read(_path(),missing=True)
  if raw is None:return {}
  data=json.loads(raw)
  if not isinstance(data,dict) or data.get('schema')!=1 or data.get('endpoint')!=endpoint(data.get('endpoint')):raise ValueError()
  for k in ('verifier','device_code','credential','device_id'):
   if k in data and not re.fullmatch(r'[A-Za-z0-9_-]{32,256}',data[k]):raise ValueError()
  if 'user_code' in data and not re.fullmatch(r'[A-Z0-9-]{4,24}',data['user_code']):raise ValueError()
  return data
 except (OSError,ValueError,TypeError,tokens.TokenError):raise GatewayError('GATEWAY_PROFILE_UNREADABLE') from None
def _write(data,*,scope=None,expected=None,cancel=lambda:False):
 import tmdb_token61 as tokens
 path=_path();fd=None;temp=None
 raw=json.dumps(data,separators=(',',':')).encode()
 if len(raw)>4096:raise GatewayError('GATEWAY_RESPONSE_INVALID')
 with _lock:
  try:
   before=tokens.read(path,missing=True)
   if scope is not None and (scope!=path or (json.loads(before) if before else {})!=expected):raise GatewayError('GATEWAY_PROFILE_CHANGED')
   if cancel() or not allowed() or configured()!=data['endpoint']:raise GatewayError('USER_CANCELLED')
   fd,_=tokens.private_parent(tokens.location());temp='.gateway87-'+secrets.token_hex(16)
   out=os.open(temp,os.O_CREAT|os.O_EXCL|os.O_WRONLY|os.O_NOFOLLOW,0o600,dir_fd=fd)
   with os.fdopen(out,'wb') as stream:stream.write(raw);stream.flush();os.fsync(stream.fileno())
   if path!=_path() or tokens.read(path,missing=True)!=before:raise GatewayError('GATEWAY_PROFILE_CHANGED')
   if cancel() or not allowed() or configured()!=data['endpoint']:raise GatewayError('USER_CANCELLED')
   os.replace(temp,NAME,src_dir_fd=fd,dst_dir_fd=fd);temp=None;os.fsync(fd)
   if path!=_path() or tokens.read(path)!=raw:raise GatewayError('GATEWAY_READBACK_FAILED')
   if data.get('credential') or expected and expected.get('credential'):
    import xbmcaddon
    xbmcaddon.Addon().setSetting('tmdb_gateway_revision87',secrets.token_hex(16))
  except (OSError,tokens.TokenError):raise GatewayError('GATEWAY_PERSISTENCE_BLOCKED') from None
  finally:
   if fd is not None:
    if temp:
     try:os.unlink(temp,dir_fd=fd)
     except FileNotFoundError:pass
    os.close(fd)
def status():
 try:
  if not allowed():return 'OPTED_OUT'
  from tmdb_token61 import effective_tmdb_read_token,TokenError
  try:
   if effective_tmdb_read_token():return 'LOCAL_TOKEN_VALID'
  except TokenError:return 'LOCAL_TOKEN_INVALID'
  base=configured()
  if not base:return 'NOT_CONFIGURED'
  data=_read()
  if not data:return 'NOT_PAIRED'
  if data.get('endpoint')!=base:return 'GATEWAY_ENDPOINT_CHANGED'
  if data.get('credential') and data.get('device_id'):return 'GATEWAY_PAIRED'
  if data.get('device_code') and data.get('expires',0)>time.time():return 'PENDING'
  return 'NOT_PAIRED'
 except GatewayError as error:return error.code
def tmdb_operation(url):
 from media_sources43 import TMDB
 p=urlsplit(url)
 if not url.startswith(TMDB+'/') or p.scheme!='https' or p.netloc!='api.themoviedb.org' or p.fragment:raise GatewayError('GATEWAY_OPERATION_BLOCKED')
 path=p.path[len('/3'):]
 if not re.fullmatch(r'/(?:configuration|search/(?:tv|movie|person)|(?:tv|movie)/[1-9][0-9]{0,9}(?:/(?:alternative_titles|external_ids|images|credits))?)',path):raise GatewayError('GATEWAY_OPERATION_BLOCKED')
 query=parse_qsl(p.query,keep_blank_values=True)
 if len(query)>8 or len({k for k,v in query})!=len(query) or any(k not in ('query','language','page','include_adult','year','first_air_date_year','append_to_response','include_image_language') or len(v)>256 or any(ord(c)<32 for c in v) for k,v in query):raise GatewayError('GATEWAY_OPERATION_BLOCKED')
 return dict(path=path,query=dict(query))
def _transport(base,operation,body,headers,cancel):
 from download_redirect import addresses,Response
 ips=addresses(base);connection=None;raw=None
 try:
  if cancel():raise GatewayError('USER_CANCELLED')
  raw=socket.create_connection((ips[0],443),timeout=4)
  raw=ssl.create_default_context().wrap_socket(raw,server_hostname=urlsplit(base).hostname)
  connection=http.client.HTTPConnection(urlsplit(base).hostname,443,timeout=4);connection.sock=raw
  connection.request('POST','/v1/'+operation,body=body,headers=headers)
  return Response(connection.getresponse(),connection,base)
 except BaseException:
  if connection:connection.close()
  elif raw:raw.close()
  raise
_transport_hook=None # Only tests inject a transport; never configurable from settings.
def _call(base,operation,payload,device=None,cancel=lambda:False):
 if operation not in ('pair/start','pair/poll','status','revoke','tmdb'):raise GatewayError('GATEWAY_OPERATION_BLOCKED')
 if not allowed():raise GatewayError('OPTED_OUT')
 base=endpoint(base);body=json.dumps(payload,separators=(',',':'),sort_keys=True).encode()
 if len(body)>4096:raise GatewayError('GATEWAY_OPERATION_BLOCKED')
 headers={'Content-Type':'application/json','Accept':'application/json','Accept-Encoding':'identity','Cache-Control':'no-store'}
 if device:
  stamp=str(int(time.time()));nonce=secrets.token_urlsafe(24)
  message='\n'.join((operation,stamp,nonce,hashlib.sha256(body).hexdigest())).encode()
  headers.update({'X-Device-Id':device['device_id'],'X-Device-Time':stamp,'X-Device-Nonce':nonce,'X-Device-Proof':hmac.new(device['credential'].encode(),message,hashlib.sha256).hexdigest()})
 response=None;deadline=time.monotonic()+6
 try:
  response=(_transport_hook or _transport)(base,operation,body,headers,cancel)
  if response.status in (401,403):raise GatewayError('AUTH_FAILED')
  if response.status==429:raise GatewayError('RATE_LIMITED')
  if response.status!=200:raise GatewayError('REDIRECT_BLOCKED' if 300<=response.status<400 else 'SERVER_UNAVAILABLE')
  if response.headers.get('Content-Type','').split(';')[0].lower()!='application/json' or response.headers.get('Content-Encoding','identity')!='identity':raise GatewayError('GATEWAY_RESPONSE_INVALID')
  chunks=[];size=0
  while True:
   if cancel():raise GatewayError('USER_CANCELLED')
   if time.monotonic()>deadline:raise GatewayError('GATEWAY_TIMEOUT')
   chunk=response.read(min(65536,1024*1024-size+1))
   if not chunk:break
   size+=len(chunk)
   if size>1024*1024:raise GatewayError('GATEWAY_RESPONSE_LIMIT')
   chunks.append(chunk)
  value=json.loads(b''.join(chunks))
  if not isinstance(value,dict) or any(k in value for k in ('tmdb_token','access_token','refresh_token','api_key')):raise GatewayError('GATEWAY_RESPONSE_INVALID')
  return value
 except GatewayError:raise
 except (ValueError,RecursionError):raise GatewayError('GATEWAY_RESPONSE_INVALID') from None
 except ssl.SSLError:raise GatewayError('GATEWAY_TLS_FAILED') from None
 except (socket.timeout,TimeoutError):raise GatewayError('GATEWAY_TIMEOUT') from None
 except OSError:raise GatewayError('SERVER_UNAVAILABLE') from None
 finally:
  if response:response.close()
def begin(cancel=lambda:False):
 state=status()
 if state in ('OPTED_OUT','LOCAL_TOKEN_VALID','LOCAL_TOKEN_INVALID','GATEWAY_PAIRED','NOT_CONFIGURED'):return state
 if state=='PENDING':return state
 if state not in ('NOT_PAIRED',):raise GatewayError(state)
 scope=_path();before=_read();base=configured();verifier=secrets.token_urlsafe(48)
 data=_call(base,'pair/start',dict(challenge=hashlib.sha256(verifier.encode()).hexdigest(),method='S256'),cancel=cancel)
 if set(data)!={'device_code','user_code','expires_in','interval'} or not re.fullmatch(r'[A-Za-z0-9_-]{32,256}',data.get('device_code','')) or not re.fullmatch(r'[A-Z0-9-]{4,24}',data.get('user_code','')) or type(data.get('expires_in')) is not int or not 30<=data['expires_in']<=600 or type(data.get('interval')) is not int or not 5<=data['interval']<=60:raise GatewayError('GATEWAY_RESPONSE_INVALID')
 _write(dict(schema=1,endpoint=base,verifier=verifier,device_code=data['device_code'],user_code=data['user_code'],expires=time.time()+data['expires_in'],interval=data['interval'],next_poll=time.time()+data['interval']),scope=scope,expected=before,cancel=cancel)
 return 'PENDING'
def public_pairing():
 data=_read()
 return dict(user_code=data.get('user_code',''),expires=data.get('expires',0))
def poll(cancel=lambda:False):
 if status()!='PENDING':return status()
 scope=_path();data=_read()
 if time.time()<data.get('next_poll',0):return 'PENDING'
 result=_call(data['endpoint'],'pair/poll',dict(device_code=data['device_code'],verifier=data['verifier']),cancel=cancel)
 code=result.get('status')
 if code=='PENDING':
  updated=dict(data,next_poll=time.time()+data['interval']);_write(updated,scope=scope,expected=data,cancel=cancel);return code
 if code!='PAIRED':raise GatewayError('AUTH_FAILED' if code=='DENIED' else 'PAIRING_EXPIRED')
 if set(result)!={'status','credential','device_id'} or any(not re.fullmatch(r'[A-Za-z0-9_-]{32,256}',result.get(k,'')) for k in ('credential','device_id')):raise GatewayError('GATEWAY_RESPONSE_INVALID')
 device=dict(schema=1,endpoint=data['endpoint'],credential=result['credential'],device_id=result['device_id'])
 if cancel():raise GatewayError('USER_CANCELLED')
 if _call(data['endpoint'],'status',{},device,cancel).get('authorized') is not True:raise GatewayError('AUTH_FAILED')
 if cancel():raise GatewayError('USER_CANCELLED')
 _write(device,scope=scope,expected=data,cancel=cancel);return 'GATEWAY_PAIRED'
def query(url,cancel=lambda:False):
 if status()!='GATEWAY_PAIRED':raise GatewayError('GATEWAY_NOT_PAIRED')
 data=_read();return _call(data['endpoint'],'tmdb',tmdb_operation(url),data,cancel)
def revoke(cancel=lambda:False):
 if status()!='GATEWAY_PAIRED':return status()
 scope=_path();data=_read()
 if _call(data['endpoint'],'revoke',{},data,cancel).get('revoked') is not True:raise GatewayError('AUTH_FAILED')
 _write(dict(schema=1,endpoint=data['endpoint']),scope=scope,expected=data,cancel=cancel);return 'REVOKED'

def check(cancel=lambda:False):
 if status()!='GATEWAY_PAIRED':return status()
 data=_read()
 return 'GATEWAY_AUTHORIZED' if _call(data['endpoint'],'status',{},data,cancel).get('authorized') is True else 'AUTH_FAILED'
