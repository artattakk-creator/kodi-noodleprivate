"""Real Kodi JSON-RPC; preapproved synthetic profile, never an Android device."""
import json,time,urllib.request
from pathlib import Path
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def rpc(method,params=None):
 request=urllib.request.Request('http://127.0.0.1:18080/jsonrpc',json.dumps(dict(jsonrpc='2.0',id=84,method=method,params=params or {})).encode(),{'Content-Type':'application/json'})
 with opener.open(request,timeout=30) as response:data=json.load(response)
 if 'error' in data:raise RuntimeError(str(data['error']))
 return data['result']
for _ in range(150):
 try:rpc('JSONRPC.Ping');break
 except Exception:time.sleep(.2)
else:raise RuntimeError('KODI84_START_TIMEOUT')
# Dismiss only the known fresh-fixture disabled-addons prompt.
current=rpc('GUI.GetProperties',{'properties':['currentwindow','currentcontrol']})
if current['currentwindow']['id']==10100 and current['currentcontrol']['label']=='No':rpc('Input.Select')
for addon in ('plugin.video.xtreammate','script.skinshortcuts','skin.titan.bingie.mod','script.xcmate.guicontract59'):rpc('Addons.SetAddonEnabled',{'addonid':addon,'enabled':True})
rpc('Files.GetDirectory',{'directory':'plugin://plugin.video.xtreammate/?fixture59=seed','media':'files'})
assert rpc('Settings.SetSettingValue',{'setting':'lookandfeel.skin','value':'skin.titan.bingie.mod'})
rpc('Application.Quit');time.sleep(2)
for _ in range(150):
 try:rpc('JSONRPC.Ping');break
 except Exception:time.sleep(.2)
rpc('GUI.ActivateWindow',{'window':'home'});time.sleep(2)
rpc('Addons.ExecuteAddon',{'addonid':'script.xcmate.guicontract59'})
for _ in range(2400):
 if Path('/root/gui66-error.txt').exists():raise RuntimeError(Path('/root/gui66-error.txt').read_text())
 if Path('/root/visible84.json').exists():
  result=json.loads(Path('/root/visible84.json').read_text());assert result['status']=='PASS';print(json.dumps(result));break
 time.sleep(.1)
else:raise RuntimeError('VISIBLE84_TIMEOUT')
