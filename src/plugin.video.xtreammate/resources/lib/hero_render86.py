"""Preload behind the last good bank, then require Kodi texture-cache decode.

A renderer cache receipt permits a switch; Android visible-pixel acceptance is
still a separate test. No GUI network/SQL/file access and no foreign-event hold.
"""
import hashlib,json,time
PREFIX='XCMate.Hero86.'
def window():
 import xbmcgui
 return xbmcgui.Window(10000)
def tag(event,value):
 return hashlib.sha256(json.dumps([__import__('event_art81').key(event),value.get('image'),value.get('source'),value.get('sha256'),value.get('mapping_epoch85')],sort_keys=True).encode()).hexdigest()
def prepare(event,value):
 from hero_art86 import classify
 import xbmc
 if str(value.get('image','')).startswith('/') and not classify(value):
  try:
   from media_sources43 import validate_image,MAX_IMAGE
   with open(value['image'],'rb') as stream:body86=stream.read(MAX_IMAGE+1)
   if value.get('sha256') and hashlib.sha256(body86).hexdigest()!=value['sha256']:
    window().setProperty(PREFIX+'Invalid',tag(event,value));return
   width86,height86=validate_image(body86)
   value=dict(value,image_width77=width86,image_height77=height86)
  except (OSError,ValueError,__import__('media_sources43').SourceError):
   window().setProperty(PREFIX+'Invalid',tag(event,value));return
 kind=classify(value)
 if not kind:return
 key=tag(event,value);win=window()
 try:
  ready=json.loads(win.getProperty(PREFIX+'Ready') or '{}')
  if ready.get('key')==key and time.monotonic()-ready.get('at',0)<30:return
 except ValueError:pass
 win.setProperty(PREFIX+'Pending',value['image'])
 # Only the actual native image control causes Kodi to obtain/cache pixels.
 from widget_cache82 import variants,decoded
 image=value['image']
 if image.startswith('/'):
  try:
   from media_sources43 import validate_image,MAX_IMAGE
   import os
   if os.path.islink(image):return
   before=os.stat(image)
   if not 0<before.st_size<=MAX_IMAGE:return
   with open(image,'rb') as stream:body=stream.read(MAX_IMAGE+1)
   width,height=validate_image(body);after=os.stat(image)
   if value.get('sha256') and hashlib.sha256(body).hexdigest()!=value['sha256']:return
   if (before.st_ino,before.st_mtime_ns,before.st_size)!=(after.st_ino,after.st_mtime_ns,after.st_size):return
   if not classify(dict(value,image_width77=width,image_height77=height)):return
   win.setProperty(PREFIX+'Ready',json.dumps(dict(key=key,at=time.monotonic(),kind=kind[0],rank=kind[1],width=width,height=height,role=value.get('role81',''),evidence='LOCAL_DECODE_REQUESTED_NOT_PIXEL_PROOF')))
  except (OSError,ValueError,__import__('media_sources43').SourceError):pass
  return
 wanted=variants(image.split('|',1)[0]) if image.startswith('https://') else [image]
 try:
  raw=xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0',id=86,method='Textures.GetTextures',params=dict(filter={'or':[dict(field='url',operator='is',value=v) for v in wanted]},properties=['url','cachedurl','sizes']))))
  if not isinstance(raw,str) or len(raw)>262144:return
  rows=json.loads(raw).get('result',{}).get('textures',[])
  if not isinstance(rows,list):return
  for row in rows[:32]:
   if row.get('url') not in wanted:continue
   record=decoded(row,image)
   if not record:continue
   # Quality was proved against the original image above. Kodi may store a
   # downsampled texture: verify its aspect, never upgrade a small source.
   width=value.get('image_width77',value.get('width',0));height=value.get('image_height77',value.get('height',0))
   if not width or not height or record['width']<64 or record['height']<64:continue
   if abs((record['width']/record['height'])/(width/height)-1)>.08:continue
   win.setProperty(PREFIX+'Ready',json.dumps(dict(key=key,at=time.monotonic(),kind=kind[0],rank=kind[1],width=width,height=height,decoded_width=record['width'],decoded_height=record['height'],role=value.get('role81',''))))
   __import__('art_trace81').note(event,'RENDER_READY','KODI_TEXTURE_DECODED',width=record['width'],height=record['height'])
   return
 except (ValueError,TypeError,AttributeError,RuntimeError,OSError):return

def choose(event,value,values,win):
 from hero_art86 import classify
 from event_art81 import allowed,key
 event_key=key(event) if event else ''
 bank=win.getProperty('XCMate.Hero63.Active');prefix='XCMate.Hero63.'+bank+'.'
 old_image=win.getProperty(prefix+'Image');old_source=win.getProperty(prefix+'ArtSource')
 same=bool(event_key and win.getProperty(PREFIX+'Event')==event_key)
 try:old_rank=int(win.getProperty(prefix+'Rank86') or '9')
 except ValueError:old_rank=9
 invalid=bool(event and win.getProperty(PREFIX+'Invalid')==tag(event,value) and old_image==value.get('image'))
 old_allowed=not invalid and value.get('code') not in ('FILE_INVALID','POLICY_CHANGED','SOURCE_CHANGED') and same and old_image and (old_source=='station_logo' or allowed(dict(source=old_source)))
 # Opt-out, mapping changes and source revocation are never sticky.
 if old_allowed and old_source!='station_logo':
  source_url=win.getProperty(prefix+'SourceUrl86')
  if source_url and __import__('widget_refs74').revoked(source_url):old_allowed=False
 try:ready=json.loads(win.getProperty(PREFIX+'Ready') or '{}')
 except ValueError:ready={}
 if event and ready.get('key')==tag(event,value):
  value=dict(value,image_width77=ready.get('width',value.get('image_width77',0)),image_height77=ready.get('height',value.get('image_height77',0)))
 accepted=classify(value)
 can_switch=bool(event and accepted and __import__('programme_image69').eligible(value,event) and allowed(value) and ready.get('key')==tag(event,value) and 0<=time.monotonic()-ready.get('at',0)<30)
 if not old_allowed:
  win.setProperty('XCMate.Hero81.PreviousImage','')
  win.setProperty(PREFIX+'PreviousEvent','')
 if can_switch and (not old_allowed or accepted[1]<old_rank or old_image==value.get('image')):
  if old_allowed and old_image!=value['image']:
   win.setProperty('XCMate.Hero81.PreviousImage',old_image)
   win.setProperty(PREFIX+'PreviousEvent',event_key)
  values.update(Image=value['image'],ArtSource=value['source'],Kind86=accepted[0],Rank86=str(accepted[1]),SourceUrl86=value.get('source_url',''))
 elif old_allowed:
  values.update(Image=old_image,ArtSource=old_source,Kind86=win.getProperty(prefix+'Kind86'),Rank86=str(old_rank),SourceUrl86=win.getProperty(prefix+'SourceUrl86'))
 else:
  # Always the focused station's logo; no small feed cover/foreign event.
  import xbmc
  logo=xbmc.getInfoLabel('ListItem.Property(XCMate.ProgrammeLogo46)')
  values.update(Image=logo,ArtSource='station_logo' if logo else '',Kind86='station_logo',Rank86='9',SourceUrl86='')
 win.setProperty(PREFIX+'Event',event_key)
 return values

def recovered_candidate(event,candidate,url):
 """Worker-only reuse after independent work matching, not guessed cache art.

 The exact current candidate URL, consent and full owned-file decode are
 mandatory. Actual cached dimensions must meet the source quality threshold.
 """
 from event_art81 import allowed
 from programme_urls55 import safe
 from programme_sources57 import PROOFS
 if candidate.get('match') not in ('EXACT_EVENT','EXACT_TITLE_YEAR','EXACT_SEASON_EPISODE','EXACT_UNIQUE_FILM_TITLE')+PROOFS:return None
 if not allowed(candidate) or not safe(url) or candidate.get('provisional85'):return None
 from widget_cache82 import variants,decoded
 import xbmc
 wanted=variants(url)
 try:
  raw=xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0',id=86,method='Textures.GetTextures',params=dict(filter={'or':[dict(field='url',operator='is',value=v) for v in wanted]},properties=['url','cachedurl','sizes']))))
  if not isinstance(raw,str) or len(raw)>262144:return None
  records=json.loads(raw).get('result',{}).get('textures',[])
  if not isinstance(records,list):return None
  for texture in records[:32]:
   if not isinstance(texture,dict) or texture.get('url') not in wanted:continue
   record=decoded(texture,url)
   if not record:continue
   typed=dict(candidate,image_width77=record['width'],image_height77=record['height'])
   if not __import__('hero_art86').classify(typed):continue
   from programme_requests68 import identity,scope
   from programme_art46 import fingerprint
   return dict(typed,code='READY',key=event['key'],fingerprint=fingerprint(event),image=record['file'],thumbnail=record['file'],sha256=record['sha256'],scope69=identity(event),profile69=scope(),policy69=__import__('programme_policy68').negative_scope({}),until=min(time.time()+86400,float(event.get('stop',0))),persisted69=False,storage69='KODI_TEXTURE_CACHE',decoded77=True,mapping_epoch85=__import__('programme_mapping85').epoch(event))
 except (OSError,ValueError,TypeError,AttributeError,RuntimeError):return None
 return None
