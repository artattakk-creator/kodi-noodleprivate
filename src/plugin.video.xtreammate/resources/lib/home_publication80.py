"""Provider-role proof, distinct from theme fallbacks and event artwork.

Only previously admitted references are retained, with exact current source
identity and file/lease validity. No stale event picture is frozen here.
"""
import os

def capture(row,image):
 from programme_assets47 import sources,fingerprint
 from widget_assets69 import renderable
 return {role:dict(source=fingerprint(source),uri=image[role]) for role,source in sources(row,provider_only=True).items() if source and renderable(image.get(role))}

def reconcile(portal,kind,item,previous,row):
 from programme_assets47 import sources,fingerprint,local_uri
 from widget_refs74 import read
 from render_cache81 import references as disk81
 current=item.setdefault('_provider80',{});prior=previous.get('_provider80',{})
 references=None
 durable81=disk81(portal,kind,[row]).get(str(row['sid']),{})
 for role,source in sources(row,provider_only=True).items():
  if not source:continue
  field='icon' if kind=='live' and role=='poster' else role
  if durable81.get(role):
   evidence81=__import__('render_cache81').record_for(portal,kind,row,role,source) or {}
   origin81=evidence81.get('source81') or fingerprint(source)
   item['art'][field]=durable81[role];current[role]=dict(source=origin81,uri=durable81[role])
   if origin81!=fingerprint(source):current[role]['pending81']=fingerprint(source)
   if role=='poster':
    if kind=='live':item['props']['XCMate.ProgrammeLogo46']=durable81[role];item['props']['channellogo']=durable81[role]
    else:
     for name in ('thumb','icon'):item['art'][name]=durable81[role]
     if not item['art'].get('fanart'):item['art']['landscape']=durable81[role]
  proof=current.get(role,{})
  if proof.get('source')==fingerprint(source) and proof.get('uri')==item['art'].get(field):continue
  proof=prior.get(role,{})
  uri=proof.get('uri','')
  if proof.get('source')!=fingerprint(source) or not uri or previous['art'].get(field)!=uri:continue
  valid=bool(local_uri(uri))
  if not valid:
   if references is None:references=read(portal,kind,[row]).get(str(row['sid']),{})
   valid=references.get(role)==uri
  if not valid:continue
  item['art'][field]=uri;current[role]=dict(proof)
  if role=='poster':
   if kind=='live':
    item['props']['XCMate.ProgrammeLogo46']=uri;item['props']['channellogo']=uri
   else:
    for name in ('thumb','icon'):item['art'][name]=uri
    if not current.get('fanart'):item['art']['landscape']=uri
 if kind in ('vod','series') and 'XCMate.ArtPending69' in item['props']:
  item['props']['XCMate.ArtPending69']='false' if current.get('poster',{}).get('uri')==item['art'].get('poster') else 'true'
 return item
