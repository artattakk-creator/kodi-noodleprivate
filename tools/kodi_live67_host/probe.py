"""Drive real native Kodi decoding; all URLs and credentials are synthetic."""
import json,time,urllib.request
from pathlib import Path
opener=urllib.request.build_opener(urllib.request.ProxyHandler({}))
def rpc(method,params=None):
 request=urllib.request.Request('http://127.0.0.1:18080/jsonrpc',json.dumps(dict(jsonrpc='2.0',id=67,method=method,params=params or {})).encode(),{'Content-Type':'application/json'})
 with opener.open(request,timeout=5) as response:value=json.loads(response.read())
 if 'error' in value:raise RuntimeError(str(value['error']))
 return value['result']
for _ in range(200):
 try:version=rpc('Application.GetProperties',dict(properties=['version']))['version'];break
 except Exception:time.sleep(.2)
else:raise RuntimeError('NATIVE_KODI_NOT_AVAILABLE')
rpc('Addons.SetAddonEnabled',dict(addonid='plugin.video.xtreammate',enabled=True))
rpc('Addons.SetAddonEnabled',dict(addonid='script.xcmate.live67',enabled=True))
rpc('Files.GetDirectory',dict(directory='plugin://plugin.video.xtreammate/?fixture67=seed',media='files'))
def configured(value):rpc('Files.GetDirectory',dict(directory='plugin://plugin.video.xtreammate/?fixture67=configure&format='+value,media='files'))
def active():return [p for p in rpc('Player.GetActivePlayers') if p['type']=='video']
def stop():
 for p in active():rpc('Player.Stop',dict(playerid=p['playerid']))
 for _ in range(100):
  if not active():return
  time.sleep(.1)
 raise RuntimeError('NATIVE_STOP_NOT_RETURNED')
def wait_video():
 for _ in range(150):
  ids=active()
  if ids:
   props=rpc('Player.GetProperties',dict(playerid=ids[0]['playerid'],properties=['time','currentvideostream','speed']))
   video=props.get('currentvideostream') or {}
   if video.get('width')==320 and props.get('speed')==1:return dict(width=video['width'],height=video.get('height'),codec=video.get('codec'),time=props['time'])
  time.sleep(.1)
 raise RuntimeError('NATIVE_FRAME_NOT_DECODED')
results=[]
configured('0')
rpc('Player.Open',dict(item=dict(file='plugin://plugin.video.xtreammate/?action=play_live&pid=fixture67&sid=1&name=Synthetic')))
results.append(dict(route='BINGIE-compatible playable resolver',transport='TS',video=wait_video()));stop()
configured('2')
rpc('Player.Open',dict(item=dict(file='plugin://plugin.video.xtreammate/?action=play_start&pid=fixture67')))
results.append(dict(route='XCMate configured start resolver',transport='HLS',video=wait_video()));stop()
configured('0')
for kind in ('guide','mini'):
 Path('/root/command67.json').write_text(json.dumps(dict(kind=kind)))
 rpc('Addons.ExecuteAddon',dict(addonid='script.xcmate.live67'))
 results.append(dict(route='released guide handoff (synthetic owner)' if kind=='guide' else 'mini tune (synthetic controller)',transport='TS',video=wait_video()));stop()
assert json.loads(Path('/root/guide67.json').read_text())['dispatched']
rpc('Player.Open',dict(item=dict(file='plugin://plugin.video.xtreammate/?action=play_live&pid=fixture67&sid=3&url=http%3A%2F%2F127.0.0.1%3A18081%2Flive%2Fsynthetic%2Ffixture%2F3')))
results.append(dict(route='extensionless legacy live resolver',transport='native automatic TS',video=wait_video()));stop()
errors=[]
for sid in ('5','6'):
 rpc('Player.Open',dict(item=dict(file='plugin://plugin.video.xtreammate/?action=play_live&pid=fixture67&sid='+sid)))
 for _ in range(100):
  with opener.open('http://127.0.0.1:18081/stats') as response:stats=json.loads(response.read())
  if stats.get(sid+'.ts',0):break
  time.sleep(.1)
 else:raise RuntimeError('ERROR_SOURCE_NOT_REQUESTED')
 time.sleep(2)
 assert not active(),('INVALID_SOURCE_ACCEPTED',sid)
 rpc('Input.Back');errors.append(dict(sid=sid,native_rejected=True))
with opener.open('http://127.0.0.1:18081/stats') as response:stats=json.loads(response.read())
assert stats.get('api',0)==0,stats
report=dict(kodi=version,cases=results,errors=errors,short_epg_calls=0,guide='intentionally corrupt synthetic SQLite',android='NOT_TESTED',private_data='NONE',controller_scope='released handoff and mini tune core; real Android IR/window lifecycle NOT_TESTED')
Path('/root/live67-result.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
