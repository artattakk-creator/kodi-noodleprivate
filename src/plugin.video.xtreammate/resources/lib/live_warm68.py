"""Service-only policy/first-list warming, independent of bulk imports."""
import hashlib,json,time
_next=0
def portal_key(portal):
 from epg_handoff63 import profile_scope
 values=[profile_scope()]+[portal.get(k) for k in ('id','type','xc_host','xc_user','xc_pass','enabled','include_live','start_group_id','start_stream_id')]
 return hashlib.sha256(json.dumps(values,sort_keys=True).encode()).hexdigest()
def policy_key(portal):return 'XCMate.LivePolicy68.'+portal_key(portal)
def token(portal):
 import xbmcgui
 return xbmcgui.Window(10000).getProperty(policy_key(portal))
def prepare(cancel=lambda:False):
 global _next
 now=time.monotonic()
 if now<_next or cancel():return
 _next=now+5
 from portals import get_active
 from xtream import XtreamClient
 from widget_data41 import policy
 from live_catalog import prepare as catalog
 import xbmcgui
 for portal in get_active()[:4]:
  if cancel():return
  if portal.get('type')!='xtream' or not portal.get('include_live',True):continue
  marker=xbmcgui.Window(10000);key=policy_key(portal);value=policy(portal,'live')
  if marker.getProperty(key)!=value:marker.setProperty(key,value)
  client=XtreamClient(portal['xc_host'],portal['xc_user'],portal['xc_pass'])
  future=catalog(portal,client)
  # No waiting for full provider groups; snapshot construction stays in its
  # existing local catalogue thread. Guide preparation is separately bounded.
  model=getattr(future,'first_model47',None) or getattr(future,'model47',None)
  if not model:continue
  channels=model['channels'][:8]
  if channels:
   from local_epg import now_next
   from epg_sources import configuration
   now_next(portal['id'],channels,configuration(portal['id']).get('mappings',{}))
