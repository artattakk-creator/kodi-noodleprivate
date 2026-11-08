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
 current=item.setdefault('_provider80',{});prior=previous.get('_provider80',{})
 references=None
 for role,source in sources(row,provider_only=True).items():
  if not source:continue
  field='icon' if kind=='live' and role=='poster' else role
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
