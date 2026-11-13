"""Read actual original-builder output and native consumers after saved picks.

Disposable Linux profile only. Never writes WidgetPath or compiler output.
"""
import ast,hashlib,io,json,time,threading,sys,os,math,xml.etree.ElementTree as E
from pathlib import Path
import xbmc,xbmcgui
from PIL import Image

def write_receipt90(path,report):
 # Native supervisor runs concurrently. Publish the complete fixture result
 # atomically so exists() cannot expose an empty/partial JSON document.
 # Disposable test data only; all renderer/PCM/ownership assertions precede it.
 path=Path(path);temporary=path.with_name(path.name+'.writing')
 temporary.write_text(json.dumps(report,indent=2),encoding='utf-8')
 temporary.replace(path)

def home_position90(labels):
 positions=[i for i,label in enumerate(labels) if label.strip().casefold() in ('home','startseite')]
 if len(positions)!=1:raise RuntimeError(('PICKER90_HOME_MENU_NOT_UNIQUE',labels))
 return positions[0]

def service_poll90():
 __import__('hero_epg63').poll();__import__('widget_notice46').poll()

def spinner_receipts438(home,bindings,kinds=None,label=""):
 """Native animation/visibility under explicit UI-state fault injection.

 This tests the real texture and renderer. Actual queue ownership/deadlines
 are tested separately on the host; this is not a provider or Android PASS.
 Every injected property is restored, and native ListItems remain untouched.
 """
 from PIL import ImageChops
 receipts=[]
 from widget_six_sources import SPECS
 for kind,prefix in [(r[0],85+i) for i,r in enumerate(SPECS) if r[0] in (kinds or ('vod','series'))]:
  cid=bindings[kind];spinner=int(str(prefix)+str(cid))
  namespace='XCMate.Home85.' if kind in ('vod','series') else 'XCMate.SixRows.'
  keys=[namespace+kind+'.'+field for field in ('Busy','State','Text','Kind','Deadline')]
  saved={key:home.getProperty(key) for key in keys}
  if home.getFocusId()!=cid:
   xbmc.executebuiltin('Action('+('Up' if kind=='vod' else 'Down')+')',wait=False)
   deadline=time.monotonic()+3
   while home.getFocusId()!=cid and time.monotonic()<deadline:xbmc.sleep(50)
  if home.getFocusId()!=cid:raise RuntimeError(('SPINNER438_ROW_NOT_FOCUSED',kind,home.getFocusId()))
  home.getControl(cid).selectItem(0);xbmc.sleep(300)
  before=xbmc.getInfoLabel('Container('+str(cid)+').NumItems')
  def frame438(name):
   path=Path('/root/'+name+'.png');xbmc.executebuiltin('TakeScreenshot('+str(path)+')',wait=False)
   for _ in range(30):
    try:
     with Image.open(io.BytesIO(path.read_bytes())) as image:return path,image.convert('RGB')
    except (OSError,ValueError,SyntaxError):xbmc.sleep(50)
   raise RuntimeError(('SPINNER438_SCREENSHOT_NOT_READY',name,path.exists(),path.stat().st_size if path.exists() else None,xbmcgui.getCurrentWindowId()))
  _,baseline438=frame438('picker90-spinner438-'+kind+label+'-baseline')
  sx438,sy438=baseline438.width/1920,baseline438.height/1080
  roi438=tuple(round(value*scale) for value,scale in zip((250,640,1890,1040),(sx438,sy438,sx438,sy438)))
  # Measure native pixels, not a resized screenshot. A 24 logical-pixel
  # texture at 720p spans 16 pixels plus at most one raster edge pixel.
  max438=(math.ceil(24*sx438)+1,math.ceil(24*sy438)+1)
  try:
   home.setProperty(keys[0],'true');home.setProperty(keys[1],'LOADING_ART' if kind in ('vod','series') else 'LOADING');home.setProperty(keys[2],'Wird geladen …');home.setProperty(keys[3],kind);home.setProperty(keys[4],str(time.monotonic()+60))
   frames=[];files=[]
   deadline=time.monotonic()+3
   while not xbmc.getCondVisibility('Control.IsVisible('+str(spinner)+')') and time.monotonic()<deadline:xbmc.sleep(50)
   if not xbmc.getCondVisibility('Control.IsVisible('+str(spinner)+')'):
    source437=xbmc.getInfoLabel('Container('+str(cid)+').ListItem.Property(XCMate.WidgetKind41)')
    facts=dict(kind=kind,focus=home.getFocusId(),row=xbmc.getCondVisibility('Control.IsVisible(75'+str(cid)+')'),header=xbmc.getCondVisibility('Control.IsVisible(84'+str(cid)+')'),busy=home.getProperty(keys[0]),state=home.getProperty(keys[1]),item_kind=source437,busy_condition=xbmc.getCondVisibility('String.IsEqual(Window(Home).Property('+keys[0]+'),true)'),kind_condition=xbmc.getCondVisibility('String.IsEqual(Container('+str(cid)+').ListItem.Property(XCMate.WidgetKind41),'+kind+')'))
    try:facts['native_size']=[home.getControl(spinner).getWidth(),home.getControl(spinner).getHeight()]
    except RuntimeError:facts['native_size']='PYTHON_CONTROL_UNSUPPORTED_OR_MISSING'
    print('SPINNER438_DIAGNOSTIC '+json.dumps(facts),flush=True)
   for index in range(4):
    xbmc.sleep(170)
    path,frame=frame438('picker90-spinner438-'+kind+label+'-'+str(index))
    frames.append(frame.crop(roi438));files.append(path.name)
   changes=[ImageChops.difference(frames[0],frame).getbbox() for frame in frames[1:]]
   animated=any(box and 1<=box[2]-box[0]<=max438[0] and 1<=box[3]-box[1]<=max438[1] for box in changes)
   if not animated:raise RuntimeError(('SPINNER438_ANIMATION_PIXELS_MISSING',kind,changes))
   rect=next(box for box in changes if box and 1<=box[2]-box[0]<=max438[0] and 1<=box[3]-box[1]<=max438[1])
   rect=(rect[0]+roi438[0],rect[1]+roi438[1],rect[2]+roi438[0],rect[3]+roi438[1])
   terminal=[]
   for state in ('READY','EMPTY','ERROR_RETRYABLE'):
    home.setProperty(keys[0],'');home.setProperty(keys[1],state);xbmc.sleep(250)
    _,terminal438=frame438('picker90-spinner438-'+kind+label+'-'+state)
    if terminal438.crop(rect).tobytes()!=baseline438.crop(rect).tobytes():raise RuntimeError(('SPINNER438_STUCK_PIXELS',kind,state,rect))
    if xbmc.getInfoLabel('Container('+str(cid)+').NumItems')!=before:raise RuntimeError(('SPINNER438_LISTITEMS_RESET',kind,state))
    terminal.append(state)
   receipts.append(dict(kind=kind,control=spinner,animation_pixels=True,logical_texture=[24,24],native_scale=[sx438,sy438],native_limit=list(max438),frames=files,changes=changes,terminal_hidden=terminal,listitems_preserved=int(before),injection='UI_STATE_ONLY_NOT_PROVIDER_JOB',android='ANDROID_NOT_TESTED'))
  finally:
   for key,value in saved.items():home.setProperty(key,value)
 return receipts

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
    widget_runtime79.prepare([portal]);__import__('home_activation78').prepare()
    if stop.wait(.1):return
   publish(portal,'live',rows)
   # Same existing service policy as the retained native Home test: do not
   # start media preparation before the real Live receiver acknowledges it.
   while json.loads(xbmcgui.Window(10000).getProperty(home_schedule75.KEY) or '{}').get('phase',0)<1:
    widget_runtime79.prepare([portal]);__import__('home_activation78').prepare()
    if stop.wait(.1):return
   for kind in ('vod','series'):
    rows,_=snapshot(portal,kind);prepare(portal,kind,rows)
    while len(read(portal,kind,rows))<5:
     widget_runtime79.prepare([portal]);__import__('home_activation78').prepare()
     if stop.wait(.1):return
    publish(portal,kind,rows);home_schedule75.prepared(kind,len(rows),portal=portal,rows=rows)
   while not stop.is_set():
    widget_runtime79.prepare([portal]);__import__('home_activation78').prepare();hero_epg63.prepare(portal['id']);stop.wait(.25)
  except Exception as error:errors.append(type(error).__name__)
 lane=threading.Thread(target=lane90,name='Native-picker-existing-service-lane');lane.start()
 try:return check90(cycle,errors)
 finally:
  stop.set();lane.join(2)
  for module90 in ('widget_assets69','programme_requests68','programme_urls55','programme_art46','decoded_assets88'):
   owner90=__import__(module90);owner90.shutdown()
   threads90=[getattr(owner90,'_thread',None)]+list(getattr(owner90,'_workers',[]))
   for thread90 in threads90:
    if thread90 and thread90 is not threading.current_thread():thread90.join(5)
   if any(t and t.is_alive() for t in threads90):raise RuntimeError('PICKER90_WORKER_DID_NOT_STOP '+module90)

def home_activation_pending438():
 value=json.loads(xbmcgui.Window(10000).getProperty('XCMate.Home78.Activation') or '{}')
 return bool(value and value.get('phase')!='RUNTIME_READY' or xbmcgui.Window(10000).getProperty('skinshortcuts-isrunning'))

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
  diagnostics90['outer_visible']={str(cid):xbmc.getCondVisibility('Control.IsVisible('+str(cid)+')') for cid in (752510,752520,752530)}
  Path('/root/picker90-diagnostic.json').write_text(json.dumps(diagnostics90,indent=2));xbmc.executebuiltin('TakeScreenshot(/root/picker90-home-'+str(cycle)+'-diagnostic.png)',wait=False);xbmc.sleep(200)
  if cycle==0 and isinstance(reason,tuple) and reason[0]=='PICKER90_NATIVE_ROWS_MISSING':
   try:__import__('diagnostic_picker90').run(reason,service_poll90)
   except Exception as error90:Path('/root/picker90-experiment-error.txt').write_text(type(error90).__name__+': '+str(error90))
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
 if cycle==0:
  until(lambda:json.loads(xbmcgui.Window(10000).getProperty('XCMate.Home78.Activation') or '{}').get('phase')=='RUNTIME_READY','PICKER90_NATIVE_CONSUMER_ACTIVATION_PENDING')
 document=E.parse(tree).getroot();bindings={}
 __import__('widget_hooks45').prepare()
 for node in document.iter('include'):
  values={p.get('name'):p.get('value','') for p in node.findall('param')}
  for kind,route in (('live','widget_live_start_group'),('vod','widget_recent_vod'),('series','widget_recent_series')):
   if route in values.get('widgetPath','') and values.get('widgetid','').isdigit():bindings[kind]=int(values['widgetid'])
 check(set(bindings)=={'live','vod','series'},('PICKER90_COMPILED_BINDING_MISSING',bindings))
 if os.environ.get('XCMATE_CLOCK437')=='true':
  check(bindings==dict(live=1510,vod=1520,series=1530),('CLOCK437_WRONG_NATIVE_CONTAINERS',bindings))
  for kind,route in (('vod','widget_recent_vod'),('series','widget_recent_series')):
   consumers=[n for n in document.iter('include') if route in next((p.get('value','') for p in n.findall('param') if p.get('name')=='widgetPath'),'')]
   # Upstream emits both the active media branch and an intentionally false
   # LiveRow branch for each slot. Count the actual converted media consumer,
   # rather than mistaking that dormant branch for a second active row.
   media437=[n for n in consumers if n.get('content')=='XCMate80.MediaRow']
   check(len(media437)==1,('CLOCK437_MEDIA_CONVERSION_MISSING',kind))
   check(all(n is media437[0] or n.get('content')=='XCMate50.LiveRow' and '[false]' in n.get('condition','') for n in consumers),('CLOCK437_UNEXPECTED_DUPLICATE_CONSUMER',kind))
 until(lambda:xbmcgui.getCurrentWindowId()==10000 and xbmcgui.getCurrentWindowDialogId() in (0,-1,9999),'PICKER90_NATIVE_HOME_NOT_READY')
 # A cold process can still complete its existing guarded consumer reload.
 # Do not race that legitimate activation with synthetic focus assertions.
 until(lambda:not home_activation_pending438(), 'PICKER90_COLD_ACTIVATION_PENDING')
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
  home=xbmcgui.Window(10000)
  if kind=='live':home.setFocusId(cid)
  until(lambda:xbmc.getInfoLabel('Container('+str(cid)+').NumItems')==str(total),('PICKER90_NATIVE_ROWS_MISSING',kind,cid))
  home=xbmcgui.Window(10000)
  if kind!='live':
   xbmc.executebuiltin('Action(Down)',wait=False)
   until(lambda:xbmcgui.Window(10000).getFocusId()==cid,('PICKER90_NATIVE_IR_DID_NOT_ENTER',kind,cid),12)
  else:home.setFocusId(cid)
  home.getControl(cid).selectItem(0)
  picture=Path('/root/picker90-home-'+str(cycle)+'-'+kind+'.png');pixels=0
  for attempt in range(30):
   service_poll90();xbmc.sleep(200);xbmc.executebuiltin('TakeScreenshot('+str(picture)+')',wait=False);xbmc.sleep(150)
   try:
    with Image.open(io.BytesIO(picture.read_bytes())) as image:rgb=image.convert('RGB').resize((1920,1080))
    pixels=sum(max(abs(a-b) for a,b in zip(p,color))<=8 for p in rgb.crop((260,640,1890,1040)).getdata())
    if pixels>1500:break
   except (OSError,ValueError):continue
  if pixels<=1500 and cycle==0:
   try:__import__('diagnostic_picker90').run(('PICKER90_NATIVE_PIXELS_MISSING',kind,cid,pixels),service_poll90)
   except Exception as error90:Path('/root/picker90-experiment-error.txt').write_text(type(error90).__name__+': '+str(error90))
  check(pixels>1500,('PICKER90_NATIVE_PIXELS_MISSING',kind,cid,pixels))
  check(home.getFocusId()==cid,('PICKER90_NATIVE_FOCUS_LOST',kind,home.getFocusId(),home.getProperty('XCMate.Home78.Activation')))
  cases.append(dict(kind=kind,control=cid,rows=total,pixels=pixels,screenshot=picture.name))
 spinners438=spinner_receipts438(home,bindings) if cycle==0 and hasattr(__import__('widget_skin90'),'media_spinners') else []
 six438=__import__('six_rows438').run(home,bindings,spinner_receipts438,service_poll90,cycle=cycle)
 # Run the actual native groups/IR contract early as well as in the long
 # retention rig. Fast feedback must not remove its 20x137/paging assertions.
 groups92=None
 if cycle==0:
  import library_index
  groups92_data=[dict(category_id=str(i),category_name='Native group '+str(i)) for i in range(20)]
  streams92=[dict(stream_id=str(i*1000+j+1),category_id=str(i),name='Native station '+str(j)) for i in range(20) for j in range(137)]
  library_index.replace_catalog('navigation90','live',streams92,groups92_data)
  def group_capture92(name):
   picture=Path('/root/'+name+'.png');xbmc.executebuiltin('TakeScreenshot('+str(picture)+')',wait=False)
   for _ in range(100):
    xbmc.sleep(50)
    try:
     with Image.open(picture) as frame:frame.load();rgb=frame.convert('RGB').resize((1920,1080))
     return picture,rgb
    except (OSError,ValueError):continue
   raise RuntimeError('GROUP92_SCREENSHOT_INCOMPLETE')
  portals92=__import__('portals').get_active();check(bool(portals92),'GROUP92_FIXTURE_NO_PORTAL')
  groups92=__import__('groups90').run(portals92[0],service_poll90,group_capture92,check)
 rows=ast.literal_eval(props.read_text(encoding='utf-8'));foreign=[r for r in rows if r[2].startswith('widgetPath') and 'plugin://script.skin.helper.widgets/' in r[3]]
 check(len(foreign)>=2 and foreign==before['foreign_paths'],'PICKER90_FOREIGN_DEFINITIONS_CHANGED')
 check(hashlib.sha256(props.read_bytes()).hexdigest()==before['properties_sha256'],'PICKER90_NATIVE_REFRESH_CHANGED_PROPERTIES')
 report=dict(status='PASS',cycle=cycle,groups92=groups92,native_cases=cases,native_spinner438=spinners438,six_rows438=six438,foreign_definitions=len(foreign),properties_sha256=before['properties_sha256'],original_compiler_sha256=hashlib.sha256(tree.read_bytes()).hexdigest(),android='ANDROID_NOT_TESTED')
 write_receipt90('/root/picker90-cold-'+str(cycle)+'.json',report);print('PICKER90_COLD '+json.dumps(report),flush=True);return report
