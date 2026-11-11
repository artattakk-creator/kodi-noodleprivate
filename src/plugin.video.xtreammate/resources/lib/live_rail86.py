"""Identity-only first native directory. One group read + one logo manifest.

No EPG/SQL artwork, image decoding, HTTP/DNS or background thread per row.
Later EPG/Hero enrichment stays with the existing service and focus banks.
"""
import hashlib,json,os,time
from urllib.parse import urlencode

def values(portal,rows):
 if not rows:return []
 import xbmcaddon
 from epg_handoff63 import profile_scope
 from logo_manifest86 import read,remote
 from widget_focus41 import token
 from localization import tr
 from live_text63 import apply
 logos=read(portal,rows);leases=remote(portal,rows);result=[];scope=profile_scope();identity=str(portal.get('name',''))
 placeholder=os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources','media','tv.png')
 from epg_handoff63 import get
 # get() reads the published RAM snapshot, never opens a guide database.
 labels=(tr(36102),tr(36668,'{0}'))
 for row in rows:
  sid=str(row['sid']);name=str(row.get('name') or '');logo=logos.get(sid,'') or leases.get(sid,('',''))[0]
  props={'XCMate.WidgetKind41':'live','XCMate.PortalId':str(portal['id']),'XCMate.MediaId':sid,'XCMate.Account':identity,'IsPlayable':'true','XCMate.Home50':'true','XCMate.EpgProfile63':scope,'XCMate.ProgrammeChannel46':name,'XCMate.ProgrammeLogo46':logo,'XCMate.ProgrammeImage46':'','XCMate.ProgrammeKey47':'','XCMate.Home86.IdentityReady':'true'}
  props['XCMate.LogoProof86']=leases.get(sid,('',''))[1] if sid not in logos else ''
  if logo.startswith(('http://127.0.0.1:','smb://')):
   props['XCMate.LogoProof88']=__import__('logo_manifest86').key(portal,row)
   props['XCMate.LogoSource88']=__import__('station_logos87').source(row)
  props['XCMate.WidgetToken41']=token(portal,row)
  params=dict(action='play_live' if portal.get('type')=='xtream' else 'source_play',pid=portal['id'],sid=sid,name=name)
  url='plugin://plugin.video.xtreammate/?'+urlencode(params)
  props['XCMate.ClickTarget44']=url
  props['XCMate.ProgrammeDetails46']='plugin://plugin.video.xtreammate/?'+urlencode(dict(action='programme_details46',pid=portal['id'],sid=sid))
  item=dict(label=name,url=url,folder=False,props=props,info=dict(title=name),art=dict(icon=logo or placeholder,thumb=logo or placeholder,poster=logo or placeholder,landscape=logo or placeholder,fanart=''),menus=[])
  apply(item,portal,row,get(str(portal['id']),sid),labels=labels)
  result.append(item)
 ram88=sum(value.startswith('http://127.0.0.1:') for value in logos.values())
 external89=sum(value.startswith('smb://') for value in logos.values())
 if external89:__import__('home_status86').rail(portal,len(rows),len(logos)-ram88-external89,ram=ram88,external=external89)
 elif ram88:__import__('home_status86').rail(portal,len(rows),len(logos)-ram88,ram=ram88)
 else:__import__('home_status86').rail(portal,len(rows),len(logos))
 return result
