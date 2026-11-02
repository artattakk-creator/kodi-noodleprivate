"""Pure display admission for verified public URL references and local images."""
import json,math,os,time
FIELDS=('key','fingerprint','code','source','match','image','thumbnail','source_url','url_version55','url_verified69','scope69','profile69','until','image_scope57','persisted69','storage69','storage_code69')
def url(art):
 from programme_urls55 import safe,OPTIONS
 value=art.get('source_url','') if isinstance(art,dict) else ''
 return bool(art.get('url_version55')==1 and art.get('url_verified69') is True and safe(value) and art.get('image')==value+OPTIONS)
def eligible(art,event=None):
 if not isinstance(art,dict) or art.get('code') not in ('READY','READY_STALE') or art.get('source') in (None,'','placeholder'):return False
 image=art.get('image')
 if not isinstance(image,str) or not image:return False
 if os.path.isabs(image) and not art.get('url_version55'):return True
 if not url(art):return False
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
