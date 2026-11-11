"""Read actual original-builder output and native consumers after saved picks.

Disposable Linux profile only. Never writes WidgetPath or compiler output.
"""
import ast,hashlib,io,json,time,xml.etree.ElementTree as E
from pathlib import Path
import xbmc,xbmcgui
from PIL import Image

def run(cycle):
 def check(value,reason):
  if not value:raise RuntimeError(str(reason))
 def until(predicate,reason,seconds=60):
  end=time.monotonic()+seconds
  while time.monotonic()<end:
   if predicate():return
   xbmc.sleep(100)
  raise RuntimeError(reason)
 folder=Path('/root/.kodi/userdata/addon_data/script.skinshortcuts')
 props=folder/'skin.titan.bingie.mod.properties';before=json.loads(Path('/root/picker90-baseline.json').read_text(encoding='utf-8'))
 check(hashlib.sha256(props.read_bytes()).hexdigest()==before['properties_sha256'],'PICKER90_COLD_PROPERTIES_CHANGED')
 tree=Path('/root/.kodi/addons/skin.titan.bingie.mod/xml/script-skinshortcuts-includes.xml')
 if cycle==0:
  xbmc.executebuiltin('RunScript(script.skinshortcuts,type=buildxml&mainmenuID=900&group=mainmenu|powermenu)',wait=False)
  until(lambda:tree.is_file() and hashlib.sha256(tree.read_bytes()).hexdigest()!=before['initial_template_sha256'] and all(route in tree.read_text(encoding='utf-8') for route in ('widget_live_start_group','widget_recent_vod','widget_recent_series')),'PICKER90_ORIGINAL_BUILD_NOT_PUBLISHED')
 document=E.parse(tree).getroot();bindings={}
 for node in document.iter('include'):
  values={p.get('name'):p.get('value','') for p in node.findall('param')}
  for kind,route in (('live','widget_live_start_group'),('vod','widget_recent_vod'),('series','widget_recent_series')):
   if route in values.get('widgetPath','') and values.get('widgetid','').isdigit():bindings[kind]=int(values['widgetid'])
 check(set(bindings)=={'live','vod','series'},('PICKER90_COMPILED_BINDING_MISSING',bindings))
 until(lambda:xbmcgui.getCurrentWindowId()==10000 and xbmcgui.getCurrentWindowDialogId() in (0,-1,9999),'PICKER90_NATIVE_HOME_NOT_READY')
 home=xbmcgui.Window(10000);home.setFocusId(900);home.getControl(900).selectItem(0);xbmc.sleep(500)
 cases=[]
 for kind,total,color in (('live',88,(25,100,160)),('vod',24,(180,100,30)),('series',24,(100,60,180))):
  cid=bindings[kind]
  until(lambda:xbmc.getInfoLabel('Container('+str(cid)+').NumItems')==str(total),('PICKER90_NATIVE_ROWS_MISSING',kind,cid))
  home=xbmcgui.Window(10000);home.setFocusId(cid);home.getControl(cid).selectItem(0)
  picture=Path('/root/picker90-home-'+str(cycle)+'-'+kind+'.png');pixels=0
  for attempt in range(30):
   xbmc.sleep(200);xbmc.executebuiltin('TakeScreenshot('+str(picture)+')',wait=False);xbmc.sleep(150)
   try:
    with Image.open(io.BytesIO(picture.read_bytes())) as image:rgb=image.convert('RGB').resize((1920,1080))
    pixels=sum(max(abs(a-b) for a,b in zip(p,color))<=8 for p in rgb.crop((260,640,1890,1040)).getdata())
    if pixels>1500:break
   except (OSError,ValueError):continue
  check(pixels>1500,('PICKER90_NATIVE_PIXELS_MISSING',kind,cid,pixels))
  check(home.getFocusId()==cid,('PICKER90_NATIVE_FOCUS_LOST',kind))
  cases.append(dict(kind=kind,control=cid,rows=total,pixels=pixels,screenshot=picture.name))
 rows=ast.literal_eval(props.read_text(encoding='utf-8'));foreign=[r for r in rows if r[2].startswith('widgetPath') and 'plugin://script.skin.helper.widgets/' in r[3]]
 check(len(foreign)>=2 and foreign==before['foreign_paths'],'PICKER90_FOREIGN_DEFINITIONS_CHANGED')
 check(hashlib.sha256(props.read_bytes()).hexdigest()==before['properties_sha256'],'PICKER90_NATIVE_REFRESH_CHANGED_PROPERTIES')
 report=dict(status='PASS',cycle=cycle,native_cases=cases,foreign_definitions=len(foreign),properties_sha256=before['properties_sha256'],original_compiler_sha256=hashlib.sha256(tree.read_bytes()).hexdigest(),android='ANDROID_NOT_TESTED')
 Path('/root/picker90-cold-'+str(cycle)+'.json').write_text(json.dumps(report,indent=2));print('PICKER90_COLD '+json.dumps(report),flush=True);return report
