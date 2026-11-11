"""Saved definitions -> native consumer evidence for own AND foreign widgets.

Read-only: never invents a missing row, changes shortcuts, regenerates Home or
hides a source. Public receipts contain hashes, IDs and fixed state codes only.
"""
import hashlib,json,re,time
from pathlib import Path
from urllib.parse import urlsplit
PREFIX='XCMate.WidgetAudit89.'
_plan=[];_stamp=None;_addons={}

def inventory(profile,skin):
 from widget_inventory87 import widgets
 from widget_skin78 import parse
 rows=widgets(profile);file=Path(skin)/'xml/script-skinshortcuts-includes.xml'
 if file.is_symlink() or not file.is_file() or file.stat().st_size>8*1024*1024:raise ValueError('GENERATED_UNAVAILABLE')
 tree=parse(file.read_bytes());parents={c:p for p in tree.iter() for c in p};consumers=[]
 for call in tree.iter('include'):
  params={n.get('name'):n.get('value',n.text or '') for n in call.findall('param')}
  route=params.get('widgetPath','');ident=params.get('widgetid','')
  if route and re.fullmatch('[0-9]{1,8}',ident):consumers.append((route,int(ident),call.get('content','')))
 for content in tree.iter('content'):
  if not content.text:continue
  control=parents.get(content)
  while control is not None and not (control.tag=='control' and re.fullmatch('[0-9]{1,8}',control.get('id',''))):control=parents.get(control)
  if control is not None:consumers.append((content.text,int(control.get('id')),control.get('type','')))
 result=[]
 for row in rows[:128]:
  route=row['path'];matched=[(cid,node) for path,cid,node in consumers if path==route]
  # Reload query parameters added to our own sources must not conceal the
  # fact that a real generated route still consumes the saved source.
  if not matched and not row['external']:
   from widget_consumer58 import identity
   from urllib.parse import parse_qs
   pid=parse_qs(urlsplit(route).query).get('pid',[''])[0];kind=identity(route,pid)
   matched=[(cid,node) for path,cid,node in consumers if kind and identity(path,pid)==kind]
  addon=urlsplit(route).netloc if route.startswith('plugin://') else ''
  result.append(dict(identity=hashlib.sha256(json.dumps([row['file'],row['menu'],row['identity'],row['slot'],route]).encode()).hexdigest(),order=row['order'],external=row['external'],addon=addon if re.fullmatch('[A-Za-z0-9_.-]{1,160}',addon) else '',ids=sorted(set(cid for cid,_ in matched)),templates=sorted(set(node for _,node in matched)),state='GENERATED_PRESENT' if matched else 'SAVED_NOT_GENERATED'))
 return result

def prepare(profile,skin):
 global _plan,_stamp
 from widget_inventory87 import fingerprint,widgets
 try:
  files=[Path(skin)/'xml/script-skinshortcuts-includes.xml']+list((Path(profile)/'addon_data/script.skinshortcuts').glob('*.properties'))
  stamp=[(str(p),p.stat().st_mtime_ns,p.stat().st_size) for p in files]
  if stamp==_stamp:return
  plan=inventory(profile,skin)
  import xbmc,xbmcgui
  for row in plan:
   addon=row.pop('addon')
   if addon:
    try:
     raw=xbmc.executeJSONRPC(json.dumps(dict(jsonrpc='2.0',id=89,method='Addons.GetAddonDetails',params=dict(addonid=addon,properties=['enabled']))));info=json.loads(raw).get('result',{}).get('addon',{})
     row['addon_state']='ENABLED' if info.get('enabled') else 'DISABLED' if info else 'MISSING'
    except (ValueError,TypeError,AttributeError):row['addon_state']='UNKNOWN'
   else:row['addon_state']='NOT_PLUGIN'
  _plan=plan;_stamp=stamp
 except (OSError,ValueError,TypeError,AttributeError):_plan=[]

def poll():
 import xbmc,xbmcgui
 if xbmcgui.getCurrentWindowId()!=10000 or xbmcgui.getCurrentWindowDialogId() not in (0,-1,9999):return
 values=[]
 for row in _plan:
  controls=[]
  for ident in row['ids'][:16]:
   number=xbmc.getInfoLabel('Container('+str(ident)+').NumItems');known=str(number).isdigit();visible=bool(xbmc.getCondVisibility('Control.IsVisible('+str(ident)+')'))
   controls.append(dict(control=ident,count=int(number) if known else -1,visible=visible,focus=bool(xbmc.getCondVisibility('Control.HasFocus('+str(ident)+')'))))
  value=dict(row,controls=controls,pixels='NOT_OBSERVABLE_VIA_LISTITEM')
  if controls:value['state']='NATIVE_ITEMS_VISIBLE' if any(c['visible'] and c['count']>0 for c in controls) else 'NATIVE_HIDDEN' if not any(c['visible'] for c in controls) else 'NATIVE_EMPTY' if all(c['count']==0 for c in controls) else 'NATIVE_UNKNOWN'
  values.append(value)
 from epg_handoff63 import profile_scope
 xbmcgui.Window(10000).setProperty(PREFIX+profile_scope(),json.dumps(dict(at=time.time(),widgets=values),separators=(',',':')))

def status():
 import xbmcgui
 from epg_handoff63 import profile_scope
 try:
  raw=xbmcgui.Window(10000).getProperty(PREFIX+profile_scope());value=json.loads(raw) if raw and len(raw)<128*1024 else {}
  return value if 0<=time.time()-value.get('at',0)<15 else dict(code='NOT_OBSERVED')
 except (ValueError,TypeError):return dict(code='NOT_OBSERVED')
