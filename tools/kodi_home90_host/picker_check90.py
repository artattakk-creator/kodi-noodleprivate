"""Read actual original-builder output and native consumers after saved picks.

Disposable Linux profile only. Never writes WidgetPath or compiler output.
"""
import ast,hashlib,io,json,time,threading,sys,xml.etree.ElementTree as E
from pathlib import Path
import xbmc,xbmcgui
from PIL import Image

def home_position90(labels):
 positions=[i for i,label in enumerate(labels) if label.strip().casefold() in ('home','startseite')]
 if len(positions)!=1:raise RuntimeError(('PICKER90_HOME_MENU_NOT_UNIQUE',labels))
 return positions[0]

def service_poll90():
 __import__('hero_epg63').poll();__import__('widget_notice46').poll()

def run(cycle):
 sys.path.insert(0,'/root/.kodi/addons/plugin.video.xtreammate')
 from fixture66 import install
 install()
 from portals import get_active
 import widget_runtime79,hero_epg63,home_schedule75
 portal=get_active()[0];home_schedule75.configure([portal]);stop=threading.Event();errors=[]
 def lane90():
  try:
   from widget_group46 import snapshot as live_rows
   from widget_data41 import snapshot
   from widget_assets69 import prepare,read
   from widget_live47 import publish
   widget_runtime79.prepare([portal]);__import__('home_activation78').prepare()
   rows=live_rows(portal);prepare(portal,'live',rows)
   while len(read(portal,'live',rows))<5:
    if stop.wait(.1):return
   publish(portal,'live',rows)
   # Same existing service policy as the retained native Home test: do not
   # start media preparation before the real Live receiver acknowledges it.
   while json.loads(xbmcgui.Window(10000).getProperty(home_schedule75.KEY) or '{}').get('phase',0)<1:
    if stop.wait(.1):return
   for kind in ('vod','series'):
    rows,_=snapshot(portal,kind);prepare(portal,kind,rows)
    while len(read(portal,kind,rows))<5:
     if stop.wait(.1):return
    publish(portal,kind,rows);home_schedule75.prepared(kind,len(rows),portal=portal,rows=rows)
   while not stop.is_set():
    widget_runtime79.prepare([portal]);hero_epg63.prepare(portal['id']);stop.wait(.25)
  except Exception as error:errors.append(type(error).__name__)
 lane=threading.Thread(target=lane90,name='Native-picker-existing-service-lane');lane.start()
 try:return check90(cycle,errors)
 finally:
  stop.set();lane.join(2);__import__('widget_assets69').shutdown();__import__('decoded_assets88').shutdown()

def check90(cycle,errors):
 def check(value,reason):
  if not value:raise RuntimeError(str(reason))
 def until(predicate,reason,seconds=60):
  end=time.monotonic()+seconds
  while time.monotonic()<end:
   check(not errors,('PICKER90_SERVICE_LANE_FAILED',errors))
   if predicate():return
   service_poll90()
   xbmc.sleep(100)
  diagnostics90=dict(reason=str(reason),focus=xbmcgui.Window(10000).getFocusId(),menu=xbmc.getInfoLabel('Container(900).ListItem.Property(submenuVisibility)'),controls={str(cid):dict(rows=xbmc.getInfoLabel('Container('+str(cid)+').NumItems'),visible=xbmc.getCondVisibility('Control.IsVisible('+str(cid)+')')) for cid in (2510,2520,2530)})
  diagnostics90['skin']={key:xbmc.getInfoLabel('Skin.String('+key+')') for key in ('HomeLayout','WidgetsGlobalLimit','widgetstyle')}
  diagnostics90['conditions']={expr:xbmc.getCondVisibility(expr) for expr in ('String.IsEqual(Skin.String(HomeLayout),bingie)','Skin.HasSetting(New_Circular)','Skin.HasSetting(ShowAllWidgets)','String.IsEqual(Container(900).ListItem.Property(submenuVisibility),num-10000)')}
  diagnostic_path90=Path('/root/picker90-diagnostic.json');diagnostic_path90.write_text(json.dumps(diagnostics90,indent=2))
  diagnostics90['resolved_parameters']={str(cid):xbmc.getInfoLabel('Control.GetLabel('+str(cid)+')') for cid in (912520,922520,932520,912530,922530,932530)}
  diagnostics90['outer_visible']={str(cid):xbmc.getCondVisibility('Control.IsVisible('+str(cid)+')') for cid in (752510,752520,752530)}
  Path('/root/picker90-diagnostic.json').write_text(json.dumps(diagnostics90,indent=2));xbmc.executebuiltin('TakeScreenshot(/root/picker90-home-'+str(cycle)+'-diagnostic.png)',wait=False);xbmc.sleep(200)
  raise RuntimeError(reason)
 folder=Path('/root/.kodi/userdata/addon_data/script.skinshortcuts')
 props=folder/'skin.titan.bingie.mod.properties';before=json.loads(Path('/root/picker90-baseline.json').read_text(encoding='utf-8'))
 check(hashlib.sha256(props.read_bytes()).hexdigest()==before['properties_sha256'],'PICKER90_COLD_PROPERTIES_CHANGED')
 tree=Path('/root/.kodi/addons/skin.titan.bingie.mod/xml/script-skinshortcuts-includes.xml')
 if cycle==0:
  xbmc.executebuiltin('RunScript(script.skinshortcuts,type=buildxml&mainmenuID=900&group=mainmenu|powermenu)',wait=False)
  def compiled_ready90():
   if xbmcgui.Window(10000).getProperty('skinshortcuts-isrunning'):return False
   try:
    raw90=tree.read_bytes()
    if hashlib.sha256(raw90).hexdigest()==before['initial_template_sha256']:return False
    E.fromstring(raw90)
    return all(route.encode() in raw90 for route in ('widget_live_start_group','widget_recent_vod','widget_recent_series'))
   except (OSError,E.ParseError):return False
  until(compiled_ready90,'PICKER90_ORIGINAL_BUILD_NOT_PUBLISHED')
 document=E.parse(tree).getroot();bindings={}
 __import__('widget_hooks45').prepare()
 for node in document.iter('include'):
  values={p.get('name'):p.get('value','') for p in node.findall('param')}
  for kind,route in (('live','widget_live_start_group'),('vod','widget_recent_vod'),('series','widget_recent_series')):
   if route in values.get('widgetPath','') and values.get('widgetid','').isdigit():bindings[kind]=int(values['widgetid'])
 check(set(bindings)=={'live','vod','series'},('PICKER90_COMPILED_BINDING_MISSING',bindings))
 until(lambda:xbmcgui.getCurrentWindowId()==10000 and xbmcgui.getCurrentWindowDialogId() in (0,-1,9999),'PICKER90_NATIVE_HOME_NOT_READY')
 home=xbmcgui.Window(10000);home.setFocusId(900)
 selection90=[]
 def home_ready90():
  names90=[xbmc.getInfoLabel('Container(900).ListItemAbsolute('+str(i)+').Label') for i in range(int(xbmc.getInfoLabel('Container(900).NumItems') or 0))]
  try:position90=home_position90(names90)
  except RuntimeError:return False
  selection90[:]=[position90];return True
 until(home_ready90,'PICKER90_HOME_MENU_NOT_READY')
 home.getControl(900).selectItem(selection90[0]);xbmc.sleep(300)
 xbmc.executebuiltin('Action(Right)',wait=False);xbmc.sleep(500)
 cases=[]
 for kind,total,color in (('live',88,(25,100,160)),('vod',24,(180,100,30)),('series',24,(100,60,180))):
  cid=bindings[kind]
  # BINGIE's native grouplist virtualizes rows below the viewport. Enter
  # the real control first; waiting for its hidden consumer creates a test
  # deadlock even after Kodi has returned all directory items.
  home=xbmcgui.Window(10000);home.setFocusId(cid)
  until(lambda:xbmc.getInfoLabel('Container('+str(cid)+').NumItems')==str(total),('PICKER90_NATIVE_ROWS_MISSING',kind,cid))
  home.getControl(cid).selectItem(0)
  picture=Path('/root/picker90-home-'+str(cycle)+'-'+kind+'.png');pixels=0
  for attempt in range(30):
   service_poll90();xbmc.sleep(200);xbmc.executebuiltin('TakeScreenshot('+str(picture)+')',wait=False);xbmc.sleep(150)
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
