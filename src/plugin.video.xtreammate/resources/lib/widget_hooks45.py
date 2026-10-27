"""Read existing skin reload bindings; no writes to skins/shortcuts/settings."""
import hashlib,html,json,os,re,tempfile,time
from urllib.parse import urlsplit,parse_qs
LIMIT=8*1024*1024
ROUTES={'widget_live_start_group':'live','widget_recent_vod':'vod','widget_recent_series':'series'}
URL=re.compile(r'plugin://plugin\.video\.xtreammate/\?[^<>"\'\s]+')
HOOK=re.compile(r'\$INFO\[Window\((?:Home|10000)\)\.Property\(([A-Za-z0-9_.-]{1,96})\)\]')

def sources(text):
 import xml.etree.ElementTree as ET
 if len(text.encode())>LIMIT or '<!DOCTYPE' in text or '<!ENTITY' in text:raise ValueError('UNSAFE_LAYOUT')
 ET.fromstring(text)
 result=[]
 for match in URL.finditer(text):
  raw=match.group();query=parse_qs(urlsplit(html.unescape(raw)).query)
  action=query.get('action',[]);pid=query.get('pid',[])
  if len(action)!=1 or action[0] not in ROUTES or len(pid)!=1 or not 0<len(pid[0])<=128 or '$' in pid[0]:continue
  hooks=[]
  for key in ('reload','xcmate_reload45','widgetreload'):
   for value in query.get(key,[]):
    for name in HOOK.findall(value):
     if name.startswith('XCMate.Widget45.Reload.') or name in ('widgetreload','widgetreload2','widgetreloadmovies','widgetreloadtvshows'):hooks.append(name)
  result.append(dict(start=match.start(),stop=match.end(),raw=raw,pid=pid[0],kind=ROUTES[action[0]],action=action[0],hooks=sorted(set(hooks))))
 return result

def probe():
 import xbmc,xbmcaddon,xbmcvfs
 if xbmc.getSkinDir()!='skin.titan.bingie.mod':return dict(code='UNSUPPORTED_SKIN',bindings=[])
 addon=xbmcaddon.Addon('skin.titan.bingie.mod');version=addon.getAddonInfo('version')
 for uri in ('special://skin/xml/script-skinshortcuts-includes.xml','special://skin/1080i/script-skinshortcuts-includes.xml','special://skin/720p/script-skinshortcuts-includes.xml'):
  if not xbmcvfs.exists(uri):continue
  f=xbmcvfs.File(uri)
  try:raw=bytes(f.readBytes(LIMIT+1))
  finally:f.close()
  if len(raw)>LIMIT:return dict(code='LAYOUT_LIMIT',bindings=[])
  rows=sources(raw.decode('utf-8'));bindings=[];seen=set()
  for row in rows:
   key=(row['pid'],row['kind'],tuple(row['hooks']))
   if key not in seen:bindings.append({k:row[k] for k in ('pid','kind','hooks')});seen.add(key)
  return dict(code='READY' if bindings and all(r['hooks'] for r in bindings) else 'BLOCKED_NO_RELOAD_HOOK' if bindings else 'NO_BINDING',bindings=bindings,version=version,uri=uri,sha256=hashlib.sha256(raw).hexdigest(),text=raw.decode('utf-8'))
 return dict(code='NO_GENERATED_LAYOUT',bindings=[])

def path():
 from utils import addon_data_dir
 return os.path.join(addon_data_dir(),'widget_bindings45.json')
_next=0

def prepare():
 global _next
 if time.monotonic()<_next:return
 _next=time.monotonic()+60
 try:
  value=probe();value.pop('text',None);value.pop('uri',None);value['at']=time.time()
  data=json.dumps(value).encode()
  if len(data)>65536:return
  fd,temp=tempfile.mkstemp(prefix='.widget-bindings45-',dir=os.path.dirname(path()))
  try:
   with os.fdopen(fd,'wb') as f:f.write(data)
   os.replace(temp,path())
  finally:
   if os.path.exists(temp):os.unlink(temp)
 except (ImportError,AttributeError,OSError,ValueError,RuntimeError,TypeError):pass

def read():
 try:
  with open(path(),encoding='utf-8') as f:data=f.read(65537)
  value=json.loads(data) if len(data)<=65536 else {}
  if not isinstance(value,dict) or not 0<=time.time()-value.get('at',0)<180:return {}
  return value
 except (OSError,ValueError,TypeError):return {}
