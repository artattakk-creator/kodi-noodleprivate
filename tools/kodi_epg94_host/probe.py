import json,time,urllib.request
from pathlib import Path
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def rpc(method,params=None):
 req=urllib.request.Request('http://127.0.0.1:18080/jsonrpc',json.dumps(dict(jsonrpc='2.0',id=94,method=method,params=params or {})).encode(),{'Content-Type':'application/json'})
 with opener.open(req,timeout=10) as r:value=json.load(r)
 if 'error' in value:raise RuntimeError(str(value['error']))
 return value['result']
for _ in range(200):
 try:version=rpc('Application.GetProperties',{'properties':['version']})['version'];break
 except (OSError,ValueError,RuntimeError):time.sleep(.1)
else:raise RuntimeError('KODI_UNAVAILABLE')
for aid in ('plugin.video.xtreammate','script.xcmate.epg94'):rpc('Addons.SetAddonEnabled',dict(addonid=aid,enabled=True))
for _ in range(12):
 cur=rpc('GUI.GetProperties',dict(properties=['currentwindow','currentcontrol']))
 if cur['currentwindow']['id']!=10100:break
 if cur['currentcontrol']['label']=='No':rpc('Input.Select')
 time.sleep(.2)
rpc('Addons.ExecuteAddon',dict(addonid='script.xcmate.epg94'))
for _ in range(600):
 if Path('/root/epg94-error.txt').exists() and Path('/root/epg94-error.txt').stat().st_size:raise RuntimeError(Path('/root/epg94-error.txt').read_text())
 if Path('/root/epg94-observe.json').exists():break
 time.sleep(.1)
else:raise RuntimeError('MANAGER_NOT_OBSERVED')
latencies=[]
for method in ('Input.Down','Input.Up','Input.Right','Input.Left'):
 before=time.monotonic();rpc(method);latencies.append(time.monotonic()-before)
Path('/root/epg94-input-complete').write_text('NATIVE_INPUT_SENT')
for _ in range(2400):  # Includes the additional two native mapping journeys.
 for kind482 in ('mini','grid'):
  marker482=Path('/root/epg482-source-'+kind482+'.json');done482=Path('/root/epg482-source-'+kind482+'-input')
  if marker482.exists() and not done482.exists():
   state482=rpc('GUI.GetProperties',dict(properties=['currentwindow','currentcontrol']))
   if state482['currentwindow']['id']!=12000:continue
   from PIL import ImageGrab
   time.sleep(.6)  # Actual select-dialog opening animation, not a mock frame.
   ImageGrab.grab(xdisplay=':99').save('/root/epg482-source-'+kind482+'.png')
   rpc('Input.Select');done482.write_text(json.dumps(dict(window=12000,selection='NATIVE_SOURCE_SELECTION')))
 if Path('/root/epg94-error.txt').exists() and Path('/root/epg94-error.txt').stat().st_size:raise RuntimeError(Path('/root/epg94-error.txt').read_text())
 if Path('/root/epg94-finished.json').exists():break
 time.sleep(.1)
else:
 for name in ('epg94-phase.txt','epg94-stacks.txt'):
  file=Path('/root')/name
  if file.exists():print('EPG94_DIAG '+name+'\n'+file.read_text(),flush=True)
 raise RuntimeError('EPG94_NOT_COMPLETED')
result=json.loads(Path('/root/epg94-finished.json').read_text());result.update(kodi=version,rpc_input_max_seconds=max(latencies))
assert result['status']=='PASS';print(json.dumps(result,indent=2))
