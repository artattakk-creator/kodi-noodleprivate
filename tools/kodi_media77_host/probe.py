"""20 real native Stop/ACK cycles per media type, isolated Linux; not Android."""
from pathlib import Path
import json,time,urllib.request
# Existing real native Kodi RPC/bootstrap helpers, no assertion stripping.
source=Path('/base_probe77.py').read_text().split('results=[]',1)[0]
exec(compile(source,'native77-rpc-helpers','exec'),globals())
# Fresh synthetic Kodi may show its known disabled-addons confirmation.
# Acknowledge only that exact initial fixture prompt; never close foreign UI
# in the product or during the Stop assertions.
current=rpc('GUI.GetProperties',dict(properties=['currentwindow','currentcontrol']))
if current['currentwindow']['id']==10100:
 heading=rpc('XBMC.GetInfoLabels',dict(labels=['Control.GetLabel(1)']))['Control.GetLabel(1)']
 if heading!='Disabled add-ons':raise RuntimeError('UNEXPECTED_FIXTURE_PROMPT '+heading)
 if current['currentcontrol']['label']!='No':rpc('Input.Right')
 rpc('Input.Select');time.sleep(.3)
idle()
results=[]
for kind in ('vod','episode','live'):
 for cycle in range(20):
  Path('/root/media77-result.json').unlink(missing_ok=True);Path('/root/media77-error.txt').unlink(missing_ok=True);Path('/root/media77-stop-request').unlink(missing_ok=True)
  if kind=='live':
   configured('0');rpc('Player.Open',dict(item=dict(file='plugin://plugin.video.xtreammate/?action=play_live&pid=fixture67&sid=1&name=Synthetic')));video=wait_video()
   command=dict(action='live_stop')
  else:
   command=dict(action='start',kind=kind)
  Path('/root/media77-command.json').write_text(json.dumps(command));rpc('Addons.ExecuteAddon',dict(addonid='script.xcmate.live67'))
  if kind!='live':
   video=wait_video();ids=active();rpc('Player.Seek',dict(playerid=ids[0]['playerid'],value=dict(seconds=65)))
   for _ in range(60):
    times=rpc('Player.GetProperties',dict(playerid=ids[0]['playerid'],properties=['time','totaltime']))
    seconds=lambda t:t['hours']*3600+t['minutes']*60+t['seconds']
    if seconds(times['time'])>=60 and seconds(times['totaltime'])>=120:break
    time.sleep(.1)
   else:raise RuntimeError('NATIVE77_RESUME_SAMPLE_NOT_READY '+json.dumps(times))
   current=rpc('GUI.GetProperties',dict(properties=['currentwindow','currentcontrol']))
   if current['currentwindow']['id']==10100:
    heading=rpc('XBMC.GetInfoLabels',dict(labels=['Control.GetLabel(1)']))['Control.GetLabel(1)']
    if heading!='Disabled add-ons':raise RuntimeError('UNEXPECTED_FIXTURE_PROMPT_BEFORE_STOP '+heading)
    # Exactly the fixture setup prompt, after the asynchronous initial load.
    if current['currentcontrol']['label']!='No':rpc('Input.Right')
    rpc('Input.Select');time.sleep(.3)
   Path('/root/media77-stop-request').touch()
  for _ in range(160):
   if Path('/root/media77-error.txt').exists():raise RuntimeError(Path('/root/media77-error.txt').read_text())
   if Path('/root/media77-result.json').exists():break
   time.sleep(.1)
  else:raise RuntimeError('NATIVE77_RESULT_MISSING')
  value=json.loads(Path('/root/media77-result.json').read_text());assert value['native_ack'] and value['stops']==1 and not active(),value
  if kind!='live':assert value['progress_position']>=60,value
  value.update(cycle=cycle,width=video['width']);results.append(value)
  assert Path('/root/kodi67-start-count').read_text()==start_count,'NATIVE77_KODI_RESTARTED'
  # A real GUI RPC still completes after each native Stop. Exact Android
  # WindowXML-origin return remains a separate on-device acceptance gate.
  rpc('GUI.GetProperties',dict(properties=['currentwindow']))
  time.sleep(.1)
report=dict(status='PASS',cycles=results,count=len(results),android='ANDROID_NOT_TESTED',scope='actual Linux video decode + XCMate owned native Stop/ACK + progress; Android fullscreen/origin return NOT_TESTED')
Path('/root/media77.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
