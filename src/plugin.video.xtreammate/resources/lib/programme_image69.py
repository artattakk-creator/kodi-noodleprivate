"""Pure display admission for verified public URL references and local images."""
import json,math,os,time
FIELDS=('key','fingerprint','code','source','match','image','thumbnail','source_url','url_version55','url_verified69','scope69','profile69','until','image_scope57','persisted69','storage69','storage_code69','policy69','display84','display_key84','temp85','sha256','provisional85','manual85','mapping_epoch85')
def url(art):
 from programme_urls55 import safe,OPTIONS
 value=art.get('source_url','') if isinstance(art,dict) else ''
 from programme_sources57 import PROOFS
 match69=art.get('match') in ('EXACT_EVENT','EXACT_TITLE_YEAR','EXACT_SEASON_EPISODE','EXACT_UNIQUE_FILM_TITLE')+PROOFS
 return bool(match69 and art.get('url_version55')==1 and art.get('url_verified69') is True and safe(value) and art.get('image')==value+OPTIONS)
def eligible(art,event=None):
 if not isinstance(art,dict) or art.get('code') not in ('READY','READY_STALE') or art.get('source') in (None,'','placeholder'):return False
 from utils import setting_bool
 source=art.get('source','')
 if source.startswith('tmdb') and setting_bool('programme_tmdb_optout77',False) or source.startswith('tvmaze') and setting_bool('programme_tvmaze_optout77',False):return False
 if event is not None and art.get('fingerprint') and art['fingerprint']!=__import__('programme_art46').fingerprint(event):return False
 image=art.get('image')
 if not isinstance(image,str) or not image:return False
 if event is not None and art.get('scope69'):
  from programme_requests68 import identity
  if art['scope69']!=identity(event):return False
 if art.get('display84') and not __import__('programme_display84').verify(art,event):return False
 if os.path.isabs(image) and not art.get('url_version55'):
  if art.get('temp85'):
   if not 0<art.get('until',0)-time.time()<=30 or not __import__('artwork_temp85').present(art.get('sha256')):return False
   __import__('artwork_temp85').touch(art.get('sha256'))
  return True
 if not url(art):return False
 from programme_policy68 import negative_scope
 if art.get('policy69')!=negative_scope({}):return False
 until=art.get('until',0)
 if type(until) not in (int,float) or not math.isfinite(until) or not time.time()<until<=time.time()+86400:return False
 from epg_handoff63 import profile_scope
 if art.get('profile69')!=profile_scope():return False
 if event is not None:
  from programme_requests68 import identity
  if art.get('scope69')!=identity(event):return False
 return isinstance(art.get('scope69'),str) and len(art['scope69'])==64
def reference(art,event=None):return art.get('image','') if eligible(art,event) else ''
def proof(art):
 return json.dumps({k:art[k] for k in FIELDS if k in art},separators=(',',':')) if eligible(art) else ''
def unpack(raw,event=None):
 if not isinstance(raw,str) or len(raw)>8192:return {}
 try:value=json.loads(raw)
 except (ValueError,TypeError):return {}
 return value if eligible(value,event) else {}

def adopt(event,value):
 """Upgrade an unexpired legacy reference only after its complete binding check."""
 if not isinstance(value,dict) or value.get('url_version55')!=1:return value
 from programme_urls55 import display
 valid=display(event,value)
 if not valid or valid.get('code') not in ('READY','READY_STALE') or valid.get('source')=='placeholder':return value
 from programme_requests68 import identity,scope
 return dict(valid,url_verified69=True,scope69=identity(event),profile69=scope(),policy69=__import__('programme_policy68').negative_scope({}),until=min(valid['until'],time.time()+86400))
