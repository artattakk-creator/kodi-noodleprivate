"""Native GUI RPC stays usable while production catalog worker imports."""
import json,time,urllib.request
from pathlib import Path
opener=urllib.request.build_opener(urllib.request.ProxyHandler({})) # loopback only

def rpc(method,params=None):
 req=urllib.request.Request('http://127.0.0.1:18080/jsonrpc',json.dumps(dict(jsonrpc='2.0',id=73,method=method,params=params or {})).encode(),{'Content-Type':'application/json'})
 with opener.open(req,timeout=8) as r:value=json.loads(r.read(4*1024*1024))
 if 'error' in value:raise RuntimeError(str(value['error']))
 return value['result']
for _ in range(150):
 try:version=rpc('Application.GetProperties',{'properties':['version']})['version'];break
 except (OSError,ValueError,RuntimeError):time.sleep(.2)
else:raise RuntimeError('KODI_UNAVAILABLE')
for aid in ('plugin.video.xtreammate','script.xcmate.catalog73'):rpc('Addons.SetAddonEnabled',{'addonid':aid,'enabled':True})
for _ in range(10):
 cur=rpc('GUI.GetProperties',{'properties':['currentwindow','currentcontrol']})
 if cur['currentwindow']['id']!=10100:break
 assert cur['currentcontrol']['label']=='No';rpc('Input.Select');time.sleep(.2)
rpc('Addons.ExecuteAddon',{'addonid':'script.xcmate.catalog73'})
for _ in range(300):
 cur=rpc('GUI.GetProperties',{'properties':['currentwindow','currentcontrol']})
 if cur['currentwindow']['id']==10100 and cur['currentcontrol']['label']=='No':rpc('Input.Select')
 if Path('/root/catalog73-observe.json').exists():break
 time.sleep(.1)
else:raise RuntimeError('PROGRESS_NOT_OBSERVED')
assert rpc('GUI.GetProperties',{'properties':['currentwindow']})['currentwindow']['id']==10000
rpc('Input.Down');rpc('Input.Up')
for _ in range(300):
 if Path('/root/catalog73-finished.json').exists():break
 time.sleep(.1)
else:raise RuntimeError('CATALOG_NOT_COMPLETED')
result=json.loads(Path('/root/catalog73-finished.json').read_text());result['kodi']=version;result['native_input_during_import']='PASS'
for kind in ('vod','series'):
 reply=rpc('Files.GetDirectory',{'directory':'plugin://plugin.video.xtreammate/?action=widget_recent_'+kind+'&pid=catalog73','media':'video'})
 assert len(reply.get('files',[]))==1
assert rpc('Player.GetActivePlayers')==[]
print(json.dumps(result,indent=2))
