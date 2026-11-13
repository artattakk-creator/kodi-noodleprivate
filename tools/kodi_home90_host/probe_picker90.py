"""Native Kodi JSON-RPC supervisor, never a physical Android connection."""
import json,time,urllib.request
from pathlib import Path
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def rpc(method,params=None):
 request=urllib.request.Request('http://127.0.0.1:18080/jsonrpc',json.dumps(dict(jsonrpc='2.0',id=90,method=method,params=params or {})).encode(),{'Content-Type':'application/json'})
 with opener.open(request,timeout=30) as response:data=json.load(response)
 if 'error' in data:raise RuntimeError(str(data['error']))
 return data['result']

def pids90():
 result=set()
 for path in Path('/proc').iterdir():
  if not path.name.isdigit():continue
  try:command=(path/'cmdline').read_bytes().split(b'\0')[0]
  except OSError:continue
  if command==b'/usr/lib/x86_64-linux-gnu/kodi/kodi.bin':result.add(path.name)
 return result
for _ in range(150):
 try:rpc('JSONRPC.Ping');break
 except Exception:time.sleep(.2)
else:raise RuntimeError('PICKER90_KODI_NOT_STARTED')
state=rpc('GUI.GetProperties',dict(properties=['currentwindow','currentcontrol']))
if state['currentwindow']['id']==10100 and state['currentcontrol']['label']=='No':rpc('Input.Select')
for addon in ('script.module.unidecode','script.module.simpleeval','plugin.video.xtreammate','script.skinshortcuts','skin.titan.bingie.mod','script.xcmate.picker90','plugin.video.themoviedb.helper','plugin.audio.m3sr2019'):rpc('Addons.SetAddonEnabled',dict(addonid=addon,enabled=True))
assert rpc('Settings.SetSettingValue',dict(setting='audiooutput.audiodevice',value='PULSE:xcmate_native'))
assert rpc('Settings.SetSettingValue',dict(setting='lookandfeel.skin',value='skin.titan.bingie.mod'))
initial90=pids90();assert initial90,'PICKER90_INITIAL_PROCESS_MISSING'
try:rpc('Application.Quit')
except OSError:pass  # The requested shutdown may close this response socket.
for _ in range(200):
 # A ping can still reach the old server while it is shutting down. Require
 # actual process replacement, as in the three later cold cycles below.
 if pids90().intersection(initial90):time.sleep(.2);continue
 try:
  assert pids90();rpc('JSONRPC.Ping');break
 except Exception:time.sleep(.2)
else:raise RuntimeError('PICKER90_INITIAL_PROCESS_NOT_REPLACED')
rpc('GUI.ActivateWindow',dict(window='home'));time.sleep(2)
state=rpc('GUI.GetProperties',dict(properties=['currentwindow','currentcontrol']))
print('PICKER90_INITIAL_WINDOW '+json.dumps(state),flush=True)
if state['currentwindow']['id']==10100 and state['currentcontrol']['label']=='No':rpc('Input.Select')
rpc('Settings.SetSettingValue',dict(setting='debug.showloginfo',value=True))
rpc('Addons.ExecuteAddon',dict(addonid='script.xcmate.picker90'))
for _ in range(4800):
 if Path('/root/picker90-error.txt').exists():raise RuntimeError(Path('/root/picker90-error.txt').read_text(encoding='utf-8'))
 if Path('/root/picker90.json').exists():
  report=json.loads(Path('/root/picker90.json').read_text(encoding='utf-8'));assert report['status']=='PASS';print(json.dumps(report));break
 time.sleep(.1)
else:raise RuntimeError('PICKER90_NATIVE_TIMEOUT')

cold90=[]
for cycle90 in range(1,4):
 for _ in range(200):
  if Path('/root/picker90-returned').exists():break
  if Path('/root/picker90-error.txt').exists():raise RuntimeError(Path('/root/picker90-error.txt').read_text())
  time.sleep(.05)
 else:raise RuntimeError('PICKER90_OBSERVER_NOT_RETURNED')
 Path('/root/picker90-returned').unlink();old90=pids90();assert old90
 Path('/root/picker90-cycle.txt').write_text(str(cycle90));rpc('Application.Quit')
 for _ in range(600):
  if not pids90().intersection(old90):break
  time.sleep(.1)
 else:raise RuntimeError('PICKER90_PREVIOUS_PROCESS_NOT_EXITED')
 for _ in range(200):
  try:
   assert pids90();rpc('JSONRPC.Ping');break
  except Exception:time.sleep(.2)
 else:raise RuntimeError('PICKER90_COLD_PROCESS_NOT_STARTED')
 rpc('GUI.ActivateWindow',dict(window='home'));time.sleep(2);rpc('Addons.ExecuteAddon',dict(addonid='script.xcmate.picker90'))
 output90=Path('/root/picker90-cold-'+str(cycle90)+'.json')
 for _ in range(1800):
  if Path('/root/picker90-error.txt').exists():raise RuntimeError(Path('/root/picker90-error.txt').read_text())
  if output90.exists():
   value90=json.loads(output90.read_text());assert value90['status']=='PASS';cold90.append(value90);break
  time.sleep(.1)
 else:raise RuntimeError('PICKER90_COLD_CONSUMER_TIMEOUT')
report['cold_restarts']=cold90;report['native_cold_restarts']=3
Path('/root/picker90.json').write_text(json.dumps(report,indent=2));print('PICKER90_COMPLETE '+json.dumps(report),flush=True)
