"""Worker-only cold recovery of exact-event Kodi texture receipts.

The bounded receipt contains hashes and fixed provenance enums, never a URL,
credential, title or token. Kodi persists its own texture; XCMate writes no
archive/metadata under the reserve. This is not current GUI pixel evidence.
"""
import base64,hashlib,json,os,re,time
_ram={};_due={}
SOURCES=('tmdb_movie','tmdb_series','tmdb_episode','xmltv_event','provider_event','tvmaze_series','tvmaze_episode')
def clean(value):
 if not isinstance(value,dict) or set(value)-{'source','match','role81','image_scope57','manual85','mapping_epoch85','source_hash88','dns_hash88','vote_average88','vote_count88'}:raise ValueError('CACHE88_PROOF')
 from programme_sources57 import PROOFS
 if value.get('source') not in SOURCES or value.get('match') not in ('EXACT_EVENT','EXACT_TITLE_YEAR','EXACT_SEASON_EPISODE','EXACT_UNIQUE_FILM_TITLE')+PROOFS or value.get('match')=='PROVISIONAL_TV85':raise ValueError('CACHE88_PROOF')
 if value.get('role81','') not in ('','backdrop','poster') or value.get('image_scope57','') not in ('','movie','episode','series','series_fallback'):raise ValueError('CACHE88_PROOF')
 if type(value.get('manual85',False)) is not bool or type(value.get('mapping_epoch85',0)) is not int or not 0<=value.get('mapping_epoch85',0)<2**63 or not re.fullmatch('[a-f0-9]{64}',value.get('source_hash88','')):raise ValueError('CACHE88_PROOF')
 if not re.fullmatch('[a-f0-9]{64}',value.get('dns_hash88','')):raise ValueError('CACHE88_DNS')
 if 'vote_average88' in value and (type(value['vote_average88']) not in (int,float) or not 0<=value['vote_average88']<=10):raise ValueError('CACHE88_RATING')
 if 'vote_count88' in value and (type(value['vote_count88']) is not int or value['vote_count88']<0):raise ValueError('CACHE88_RATING')
 return dict(value)
def encode(key,value):
 if not value:return ''
 if not re.fullmatch('[a-f0-9]{64}\\.[a-f0-9]{64}',key):raise ValueError('CACHE88_KEY')
 return base64.urlsafe_b64encode(json.dumps(clean(value),sort_keys=True,separators=(',',':')).encode()).decode().rstrip('=')
def receipt(value):
 from urllib.parse import urlsplit
 if value.get('source') not in SOURCES:return None
 proof={k:value[k] for k in ('source','match','role81','image_scope57','manual85','mapping_epoch85') if value.get(k) is not None}
 proof.update(source_hash88=hashlib.sha256(value.get('source_url','').encode()).hexdigest(),dns_hash88=hashlib.sha256((urlsplit(value.get('source_url','')).hostname or '').encode()).hexdigest())
 rating=value.get('vote_average88');votes=value.get('vote_count88')
 if type(rating) in (int,float) and 0<=rating<=10 and type(votes) is int and votes>0:proof.update(vote_average88=rating,vote_count88=votes)
 return clean(proof)
def admitted(proof,event):
 if not __import__('event_art81').allowed(proof) or proof.get('mapping_epoch85',0)!=__import__('programme_mapping85').epoch(event):return False
 from artwork_visible import _dns_cache,_lock
 with _lock:
  return not any(hashlib.sha256(host.encode()).hexdigest()==proof['dns_hash88'] and verdict[0]>time.monotonic() and not verdict[1] and not __import__('dns_verdict78').temporary((host,port)) for (host,port),verdict in _dns_cache.items())
def recover(event):
 from urllib.parse import urlsplit,parse_qs,unquote
 from sticky_art88 import key
 from widget_cache82 import decoded
 from programme_requests68 import identity,scope
 from programme_art46 import fingerprint
 from programme_policy68 import negative_scope
 import xbmc
 context=key(event)
 if not event.get('start',0)<=time.time()<event.get('stop',0):return None
 try:
  hit=_ram.get(context)
  if hit and admitted(hit['proof'],event) and hit['value']['until']>time.time():
   stamp=os.stat(hit['value']['image'])
   if [stamp.st_mtime_ns,stamp.st_size]==hit['stamp']:return dict(hit['value'])
  if time.monotonic()<_due.get(context,0):return None
  _due[context]=time.monotonic()+30
  while len(_due)>256:_due.pop(next(iter(_due)))
  query=dict(jsonrpc='2.0',id=88,method='Textures.GetTextures',params=dict(filter=dict(field='url',operator='contains',value='event88='+context),properties=['url','cachedurl','sizes']))
  raw=xbmc.executeJSONRPC(json.dumps(query))
  if not isinstance(raw,str) or len(raw)>262144:return None
  textures=json.loads(raw).get('result',{}).get('textures',[])
  if not isinstance(textures,list):return None
  for texture in reversed(textures[:32]):
   try:
    if not isinstance(texture,dict):continue
    uri=texture.get('url','')
    if uri.startswith('image://'):uri=unquote(uri[8:].removesuffix('/'))
    from artwork_visible import KODI_OPTIONS
    if uri.endswith(KODI_OPTIONS):uri=uri[:-len(KODI_OPTIONS)]
    parsed=urlsplit(uri);params=parse_qs(parsed.query,strict_parsing=True)
    if parsed.scheme!='http' or parsed.hostname!='127.0.0.1' or parsed.username is not None or parsed.password is not None or not parsed.port or parsed.fragment or not re.fullmatch('/xcmate88/[a-f0-9]{64}/[a-f0-9]{64}\\.(png|jpg)',parsed.path):continue
    if set(params)!={'event88','body88','proof88'} or any(len(v)!=1 for v in params.values()) or params['event88']!=[context] or not re.fullmatch('[a-f0-9]{64}',params['body88'][0]):continue
    asset=context+'.'+params['body88'][0]
    if parsed.path.rsplit('/',1)[1].split('.')[0]!=hashlib.sha256(asset.encode()).hexdigest():continue
    encoded=params['proof88'][0]
    if len(encoded)>768 or not re.fullmatch('[a-zA-Z0-9_-]+',encoded):continue
    proof=clean(json.loads(base64.urlsafe_b64decode(encoded+'='*(-len(encoded)%4))))
    if not admitted(proof,event):continue
    record=decoded(texture,texture.get('url',''))
    if not record:continue
    result=dict(proof,key=event['key'],fingerprint=fingerprint(event),code='READY',image=record['file'],thumbnail=record['file'],sha256=record['sha256'],scope69=identity(event),profile69=scope(),policy69=negative_scope({}),until=min(time.time()+600,event['stop']),decoded77=True,image_width77=record['width'],image_height77=record['height'],persisted69=False,storage69='KODI_TEXTURE_CACHE')
    result.pop('source_hash88',None);result.pop('dns_hash88',None)
    result['attribution']='TMDB · '+__import__('tmdb_connection60').ATTRIBUTION if result['source'].startswith('tmdb') else 'TVmaze · Daten CC BY-SA; Bildrechte beim Rechteinhaber' if result['source'].startswith('tvmaze') else 'XMLTV' if result['source']=='xmltv_event' else 'Provider'
    if record.get('stamp'):_ram[context]=dict(value=result,proof=proof,stamp=record['stamp'])
    while len(_ram)>128:_ram.pop(next(iter(_ram)))
    return result
   except (OSError,ValueError,TypeError,KeyError,AttributeError):continue
 except (OSError,ValueError,TypeError,KeyError,AttributeError,RuntimeError):return None
 return None
