"""Drive native Start/Back and actual Kodi media-widget directory readback."""
import json
from pathlib import Path
import time
import urllib.request
opener=urllib.request.build_opener(urllib.request.ProxyHandler({})) # loopback JSON-RPC only
def rpc(method,params=None):
    req=urllib.request.Request('http://127.0.0.1:18080/jsonrpc',json.dumps(dict(jsonrpc='2.0',id=72,method=method,params=params or {})).encode(),{'Content-Type':'application/json'})
    with opener.open(req,timeout=15) as response:value=json.loads(response.read(4*1024*1024))
    if 'error' in value:raise RuntimeError(str(value['error']))
    return value['result']
for i in range(150):
    try:version=rpc('Application.GetProperties',{'properties':['version']})['version'];break
    except (OSError,ValueError,RuntimeError):time.sleep(.2)
else:raise RuntimeError('KODI_UNAVAILABLE')
assert version['major']==21
for aid in ('plugin.video.xtreammate','script.xcmate.vod72'):rpc('Addons.SetAddonEnabled',{'addonid':aid,'enabled':True})
for i in range(10):
    cur=rpc('GUI.GetProperties',{'properties':['currentwindow','currentcontrol']})
    if cur['currentwindow']['id']!=10100:break
    heading=rpc('XBMC.GetInfoLabels',{'labels':['Control.GetLabel(1)']})['Control.GetLabel(1)']
    assert heading=='Disabled add-ons' and cur['currentcontrol']['label']=='No'
    rpc('Input.Select');time.sleep(.2)
rpc('Addons.ExecuteAddon',{'addonid':'script.xcmate.vod72'})
for i in range(300):
    cur=rpc('GUI.GetProperties',{'properties':['currentwindow','currentcontrol']})
    if cur['currentwindow']['id']==10100:
        heading=rpc('XBMC.GetInfoLabels',{'labels':['Control.GetLabel(1)']})['Control.GetLabel(1)']
        if heading=='Disabled add-ons' and cur['currentcontrol']['label']=='No':rpc('Input.Select')
    if cur['currentwindow']['id']>=13000 and cur['currentcontrol']['label']=='Starten':break
    time.sleep(.1)
else:raise RuntimeError('VOD72_WINDOW_NOT_READY')
rpc('Input.Select')
for i in range(600):
    cur=rpc('GUI.GetProperties',{'properties':['currentwindow','currentcontrol']})
    if Path('/root/vod72-worker.json').exists() and cur['currentcontrol']['label']=='Ergebnis':break
    time.sleep(.1)
else:raise RuntimeError('VOD72_OWNER_COMPLETION_FAILED')
rpc('Input.Back')
for i in range(100):
    if Path('/root/vod72-finished.json').exists():break
    time.sleep(.1)
else:raise RuntimeError('VOD72_BACK_FAILED')
report=json.loads(Path('/root/vod72-finished.json').read_text());report['kodi']=version
report['native_directories']={}
for kind in ('vod','series'):
    values=rpc('Files.GetDirectory',{'directory':'plugin://plugin.video.xtreammate/?action=widget_recent_'+kind+'&pid=vod72','media':'video','properties':['title']})
    rows=values.get('files',[])
    assert len(rows)==1,(kind,rows)
    assert 'Synthetic' in rows[0].get('label','')
    assert 'action=media_detail' in rows[0]['file']
    report['native_directories'][kind]='PASS (1 real Kodi directory item)'
assert rpc('Player.GetActivePlayers')==[]
print(json.dumps(report,indent=2))
