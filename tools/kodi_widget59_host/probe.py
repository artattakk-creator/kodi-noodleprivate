"""Real native directory invocation; synthetic provider, never Android PASS."""
import hashlib,json,time,urllib.request
from urllib.parse import parse_qs,urlsplit
opener=urllib.request.build_opener(urllib.request.ProxyHandler({})) # local container loopback only

def rpc(method,params=None):
 req=urllib.request.Request('http://127.0.0.1:18080/jsonrpc',json.dumps(dict(jsonrpc='2.0',id=59,method=method,params=params or {})).encode(),{'Content-Type':'application/json'})
 with opener.open(req,timeout=30) as response:value=json.loads(response.read(2*1024*1024))
 if 'error' in value:raise RuntimeError(str(value['error']))
 return value['result']
for attempt in range(100):
 try:version=rpc('Application.GetProperties',{'properties':['version']})['version'];break
 except Exception:time.sleep(.2)
else:raise RuntimeError('LOCAL_KODI_UNAVAILABLE')
rpc('Addons.SetAddonEnabled',{'addonid':'plugin.video.xtreammate','enabled':True})
seed=rpc('Files.GetDirectory',{'directory':'plugin://plugin.video.xtreammate/?fixture59=seed','media':'files'})
assert seed['limits']['total']==1
report=dict(kodi=version,synthetic_provider=True,android='NOT_TESTED',bingie_home='UNVERIFIED',directories={})
for kind in ('vod','series'):
 value=rpc('Files.GetDirectory',dict(directory='plugin://plugin.video.xtreammate/?action=widget_recent_'+kind+'&pid=fixture59',media='video',properties=['title','art'],limits=dict(start=0,end=24)))
 rows=value['files'];assert len(rows)==24
 assert len({r['art'].get('poster') for r in rows})==24
 for row in rows:
  query=parse_qs(urlsplit(row['file']).query)
  assert query['action']==['media_detail'] and query['kind']==[kind] and query['pid']==['fixture59']
  uri='https://provider.example.test/'+kind+'/'+query['sid'][0]+'.png'
  assert hashlib.sha256(uri.encode()).hexdigest() in row['art']['poster']
 report['directories'][kind]=dict(items=len(rows),distinct_posters=len({r['art'].get('poster') for r in rows}),native_directory='PASS')

# The disposable, freshly created test profile shows Kodi's own disabled-addons
# welcome prompt. Dismiss only that exact fixture prompt; never close arbitrary
# dialogs, and this code is not installed in the production add-on.
current=rpc('GUI.GetProperties',{'properties':['currentwindow']})['currentwindow']
if current['id']==10100:
 heading=rpc('XBMC.GetInfoLabels',{'labels':['Control.GetLabel(1)']})['Control.GetLabel(1)']
 assert heading=='Disabled add-ons' and rpc('Player.GetActivePlayers')==[]
 assert rpc('GUI.GetProperties',{'properties':['currentcontrol']})['currentcontrol']['label']=='No'
 rpc('Input.Select');time.sleep(.3)
rpc('Addons.SetAddonEnabled',{'addonid':'script.xcmate.guicontract59','enabled':True})
rpc('Addons.ExecuteAddon',{'addonid':'script.xcmate.guicontract59'})
for i in range(300):
 current=rpc('GUI.GetProperties',{'properties':['currentwindow','currentcontrol']})
 if current['currentwindow']['id']==10100:
  heading=rpc('XBMC.GetInfoLabels',{'labels':['Control.GetLabel(1)']})['Control.GetLabel(1)']
  if heading=='Disabled add-ons' and current['currentcontrol']['label']=='No':rpc('Input.Select')
 value=rpc('XBMC.GetInfoLabels',{'labels':['Window(Home).Property(NativeWidget59.Result)']}).get('Window(Home).Property(NativeWidget59.Result)','')
 if value:
  report['gui_containers']=json.loads(value);break
 time.sleep(.1)
else:raise RuntimeError('NATIVE_GUI_CONTAINERS_NOT_READY')
from pathlib import Path
from PIL import Image,UnidentifiedImageError
# Kodi encodes screenshots asynchronously. Existence is not a complete PNG.
for i in range(100):
 try:
  with Image.open('/root/native-widget59.png') as loaded:
   loaded.load();picture=loaded.convert('RGB')
  break
 except (OSError,UnidentifiedImageError):time.sleep(.1)
else:raise RuntimeError('NATIVE_SCREENSHOT_NOT_COMPLETE')
w,h=picture.size
# Ten distinct provider textures from each row, decoded into real Kodi pixels.
verified=[]
for y,base in ((70,(40,70,120)),(350,(100,50,20))):
 for i in range(10):
  expected=tuple((v+i*step)%240 for v,step in zip(base,(19,31,13)))
  actual=picture.getpixel((int((30+2+120*i+20)*w/1280),int((y+30)*h/720)))
  if max(abs(a-b) for a,b in zip(expected,actual))>8:raise RuntimeError('POSTER_PIXEL_MISMATCH '+str((i,y,actual,expected)))
  verified.append(actual)
assert len(set(verified))==20
report['decoded_provider_posters']=len(verified)
report['gui_pixels']='PASS_SYNTHETIC_NATIVE_KODI_ONLY'
report['no_player_start']=rpc('Player.GetActivePlayers')==[]
assert report['no_player_start']
print(json.dumps(report,indent=2))
