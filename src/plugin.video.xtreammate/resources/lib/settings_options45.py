"""Explicit per-setting editor; same seven native categories and legacy IDs."""
import os,xml.etree.ElementTree as ET
from localization import tr
from settings_sections45 import SECTIONS

def label(value):
 return tr(int(value)) if str(value).isdigit() else str(value or '')

def definitions(group):
 import xbmcaddon
 target=dict((key,str(ident)) for ident,key in SECTIONS).get(group)
 root=ET.parse(os.path.join(xbmcaddon.Addon().getAddonInfo('path'),'resources/settings.xml')).getroot()
 cat=next((c for c in root if c.get('label')==target),None)
 hidden={'experimental_open45','active_portal_id','xcmate_ui_language','autoplay_diagnostics_safe','downloads_folder_enabled'}
 return [dict(n.attrib) for n in cat if n.get('id') and n.get('type')!='lsep' and n.get('id') not in hidden] if cat is not None else []

def show(router,group):
 if group=='tmdb_access61':
  from tmdb_access61 import show as access
  access();return
 if group=='tmdb_test60':
  from tmdb_connection60 import launch
  launch();return
 import xbmcaddon,xbmcgui
 from menu_icons45 import select
 addon=xbmcaddon.Addon();dialog=xbmcgui.Dialog();rows=definitions(group)
 while True:
  choice=select(dialog,label(dict((key,ident) for ident,key in SECTIONS).get(group,36005)),[label(r.get('label')) for r in rows],actions=[r.get('id','settings') for r in rows])
  if not isinstance(choice,int) or not 0<=choice<len(rows):return
  row=rows[choice];kind=row['type'];key=row['id'];old=addon.getSetting(key)
  if kind=='action':
   from urllib.parse import urlsplit,parse_qsl
   raw=row.get('action','')
   if raw.startswith('RunPlugin(plugin://plugin.video.xtreammate/?') and raw.endswith(')'):
    previous=router._params;handle=router._handle
    try:
     router._handle=-1
     router._params=dict(parse_qsl(urlsplit(raw[10:-1]).query));router.dispatch()
    finally:router._params=previous;router._handle=handle
   continue
  if kind=='bool':
   value=select(dialog,label(row.get('label')),[tr(36028),tr(36029)],actions=['back','check'],preselect=1 if old=='true' else 0)
   if value not in (0,1):continue
   value='true' if value else 'false'
  elif kind in ('enum','labelenum'):
   values=row.get('values','')
   options=label(values).split('|') if values.isdigit() else [label(v) for v in values.split('|')]
   if not options:continue
   chosen=select(dialog,label(row.get('label')),options,default='settings')
   if not 0<=chosen<len(options):continue
   value=str(chosen) if kind=='enum' else options[chosen]
  elif kind=='folder':
   value=dialog.browseSingle(0,label(row.get('label')),'files',defaultt=old)
   if not value:continue
  else:
   value=dialog.input(label(row.get('label')),defaultt=old,type=getattr(xbmcgui,'INPUT_ALPHANUM',0),option=getattr(xbmcgui,'ALPHANUM_HIDE_INPUT',1) if row.get('option')=='hidden' else 0)
   if value=='':continue
   if kind in ('number','slider'):
    try:
     number=float(value)
     if not __import__('math').isfinite(number) or number<0:raise ValueError()
     if row.get('range'):
      limits=[float(v) for v in row['range'].split(',')]
      if not limits[0]<=number<=limits[-1]:raise ValueError()
     value=format(number,'g')
    except ValueError:dialog.ok('XCMate',tr(36026));continue
  if value==old:continue
  if select(dialog,label(row.get('label')),[tr(36012),tr(36025)],actions=['back','check'],preselect=0)!=1:continue
  addon.setSetting(key,value);dialog.notification('XCMate',tr(36027))
