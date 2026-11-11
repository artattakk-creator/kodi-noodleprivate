"""Native Kodi JSON-RPC supervisor, never a physical Android connection."""
import json,time,urllib.request
from pathlib import Path
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def rpc(method,params=None):
 request=urllib.request.Request('http://127.0.0.1:18080/jsonrpc',json.dumps(dict(jsonrpc='2.0',id=90,method=method,params=params or {})).encode(),{'Content-Type':'application/json'})
 with opener.open(request,timeout=30) as response:data=json.load(response)
 if 'error' in data:raise RuntimeError(str(data['error']))
 return data['result']
for _ in range(150):
 try:rpc('JSONRPC.Ping');break
 except Exception:time.sleep(.2)
else:raise RuntimeError('PICKER90_KODI_NOT_STARTED')
state=rpc('GUI.GetProperties',dict(properties=['currentwindow','currentcontrol']))
if state['currentwindow']['id']==10100 and state['currentcontrol']['label']=='No':rpc('Input.Select')
for addon in ('script.module.unidecode','script.module.simpleeval','plugin.video.xtreammate','script.skinshortcuts','skin.titan.bingie.mod','script.xcmate.picker90'):rpc('Addons.SetAddonEnabled',dict(addonid=addon,enabled=True))
assert rpc('Settings.SetSettingValue',dict(setting='lookandfeel.skin',value='skin.titan.bingie.mod'))
rpc('Application.Quit');time.sleep(3)
for _ in range(200):
 try:rpc('JSONRPC.Ping');break
 except Exception:time.sleep(.2)
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
